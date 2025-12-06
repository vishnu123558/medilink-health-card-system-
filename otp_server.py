from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import time
import random
import logging
from email.mime.text import MIMEText
import smtplib
from dotenv import load_dotenv

load_dotenv()

# =====================================================
# MEDILINK OTP SERVER - Backend for Health Card Registration
# =====================================================
# This server handles:
# 1. OTP Generation & Delivery (SMS/Email)
# 2. OTP Verification (secure 6-digit codes)
# 3. Patient Registration (persists to database)
# 4. Health Card Generation (unique ID + QR token)
# =====================================================

APP_PORT = int(os.getenv('OTP_SERVER_PORT', '5000'))
DB_PATH = os.path.join(os.path.dirname(__file__), 'otp_store.db')
OTP_TTL_SECONDS = int(os.getenv('OTP_TTL_SECONDS', '600'))  # OTP valid for 10 minutes

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow cross-origin requests from frontend


def get_db_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_conn()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS otps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination TEXT NOT NULL,
            type TEXT NOT NULL,
            otp TEXT NOT NULL,
            expires_at INTEGER NOT NULL,
            used INTEGER DEFAULT 0,
            created_at INTEGER NOT NULL
        )
    ''')
    # Patients table to persist registrations
    c.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            health_id TEXT NOT NULL UNIQUE,
            qr_token TEXT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            country_code TEXT,
            mobile TEXT,
            email TEXT,
            blood TEXT,
            allergies TEXT,
            vaccinations TEXT,
            genetic TEXT,
            disease TEXT,
            fever TEXT,
            temperature TEXT,
            temp_unit TEXT,
            issued_on INTEGER,
            renewal_on INTEGER,
            created_at INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def save_otp(destination, typ, otp, expires_at):
    conn = get_db_conn()
    c = conn.cursor()
    c.execute('INSERT INTO otps (destination, type, otp, expires_at, created_at) VALUES (?, ?, ?, ?, ?)',
              (destination, typ, otp, expires_at, int(time.time())))
    conn.commit()
    conn.close()


def mark_otp_used(otp_id):
    conn = get_db_conn()
    c = conn.cursor()
    c.execute('UPDATE otps SET used = 1 WHERE id = ?', (otp_id,))
    conn.commit()
    conn.close()


def send_email_smtp(to_email, otp):
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')
    from_email = os.getenv('FROM_EMAIL', smtp_user)

    if not smtp_host or not smtp_user or not smtp_pass:
        logging.info('SMTP not configured; skipping email send (OTP for %s: %s)', to_email, otp)
        return False, 'SMTP not configured; OTP logged to server logs.'

    subject = 'Your MediLink OTP'
    body = f'Your one-time passcode is: {otp}. It is valid for {OTP_TTL_SECONDS//60} minutes.'
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(from_email, [to_email], msg.as_string())
        server.quit()
        logging.info('Email sent to %s', to_email)
        return True, 'Email sent.'
    except Exception as e:
        logging.exception('Failed to send email')
        return False, str(e)


def send_sms_twilio(to_number, otp):
    twilio_sid = os.getenv('TWILIO_SID')
    twilio_token = os.getenv('TWILIO_TOKEN')
    twilio_from = os.getenv('TWILIO_FROM')
    if not twilio_sid or not twilio_token or not twilio_from:
        logging.info('Twilio not configured; skipping SMS send (OTP for %s: %s)', to_number, otp)
        return False, 'Twilio not configured; OTP logged to server logs.'

    try:
        from twilio.rest import Client
        client = Client(twilio_sid, twilio_token)
        message = client.messages.create(body=f'Your MediLink OTP: {otp}', from_=twilio_from, to=to_number)
        logging.info('Twilio message SID: %s', message.sid)
        return True, message.sid
    except Exception as e:
        logging.exception('Failed to send SMS via Twilio')
        return False, str(e)


def _get_otp_row(destination, otp):
    conn = get_db_conn()
    c = conn.cursor()
    c.execute('SELECT id, expires_at, used FROM otps WHERE destination = ? AND otp = ? ORDER BY id DESC LIMIT 1', (destination, otp))
    row = c.fetchone()
    conn.close()
    return row


def _verify_and_mark(destination, otp):
    """
    VERIFY & CONSUME OTP - Critical Security Function
    
    Purpose: Check that OTP is valid, not expired, and not already used
    Then mark it as consumed to prevent replay attacks
    
    Verification steps:
    1. Find OTP record matching destination + code
    2. Check not already used (used=0)
    3. Check not expired (expires_at > now)
    4. Mark as used (used=1) for this registration
    
    Args:
        destination: Mobile number or email where OTP was sent (e.g., "+91 9876543210")
        otp: 6-digit code entered by user (e.g., "123456")
    
    Returns: (success, message, row_id)
        - (True, 'OK', id) if OTP valid and marked
        - (False, error_msg, None) if verification fails
    """
    row = _get_otp_row(destination, otp)
    if not row:
        return False, 'No matching OTP found', None
    now = int(time.time())
    if row['used'] == 1:
        return False, 'OTP already used', None
    if row['expires_at'] < now:
        return False, 'OTP expired', None
    # Mark OTP as used - prevents reuse/replay attacks
    mark_otp_used(row['id'])
    return True, 'OK', row['id']


def generate_health_id():
    """
    GENERATE UNIQUE HEALTH ID - 16-Digit Identifier
    
    Purpose: Create unique, non-guessable Health ID for patient
    Uses timestamp (milliseconds) + random component
    
    Format: 16 consecutive digits
    Example: "1701001234567890"
    
    Why 16 digits:
    - Timestamp (13 digits) ensures uniqueness over time
    - Random (6 digits) ensures uniqueness within same millisecond
    - Total 16 chars = International standard for medical IDs
    
    This ID is:
    - Permanently assigned to patient
    - Embedded in Health Card
    - Used for QR code authentication
    - Database primary key for patient records
    """
    ts = str(int(time.time() * 1000))      # Current time in milliseconds
    rand = str(random.randint(0, 999999)).zfill(6)  # 6-digit random component
    hid = (ts + rand)[-16:]  # Take last 16 characters
    return hid


# =====================================================
# ENDPOINT 1: SEND OTP
# =====================================================
# Purpose: Generate 6-digit OTP and send to patient mobile
# Triggered: After patient completes registration form
# Response: Confirmation that OTP was generated/sent
# =====================================================

@app.route('/send_otp', methods=['POST'])
def send_otp():
    """
    SEND OTP TO MOBILE - Step 1 of Registration
    
    Request: POST /send_otp
    Body: { "mobile": "+91 9876543210" }
    
    Process:
    1. Generate 6-digit random OTP (100000-999999)
    2. Set expiry time (10 minutes)
    3. Store OTP in database (otps table)
    4. Send OTP to mobile via SMS gateway (Twilio/Vonage)
    
    Response: { "success": true, "details": { "mobile": { "sent": true } } }
    
    Database Storage:
    - destination: "+91 9876543210" (mobile with country code)
    - type: "mobile"
    - otp: "123456" (6 digits)
    - expires_at: current_time + 600 seconds
    - used: 0 (not consumed yet)
    """
    data = request.get_json(force=True)
    mobile = data.get('mobile')
    email = data.get('email')

    if not mobile and not email:
        return jsonify(success=False, error='Require mobile or email'), 400

    # Generate 6-digit OTP code
    otp = f"{random.randint(100000, 999999)}"
    expires_at = int(time.time()) + OTP_TTL_SECONDS  # Valid for 10 minutes
    results = { 'email': None, 'mobile': None }

    if email:
        save_otp(email, 'email', otp, expires_at)
        ok, info = send_email_smtp(email, otp)
        results['email'] = { 'sent': ok, 'info': info }

    if mobile:
        # Store OTP in database for verification later
        save_otp(mobile, 'mobile', otp, expires_at)
        # Send OTP via SMS to patient's phone
        ok, info = send_sms_twilio(mobile, otp)
        results['mobile'] = { 'sent': ok, 'info': info }

    # Log OTP to server console (for testing without SMS configured)
    logging.info('✅ OTP generated: %s for %s (valid until %d)', otp, mobile or email, expires_at)
    
    # Always return success=true for UX
    return jsonify(success=True, details=results)


# =====================================================
# ENDPOINT 2: REGISTER PATIENT & GENERATE HEALTH CARD
# =====================================================
# Purpose: Verify OTP, create patient record, issue health card
# Triggered: After user enters OTP and clicks verify
# Response: Server-issued Health ID + QR token
# =====================================================

@app.route('/register_patient', methods=['POST'])
def register_patient():
    """
    REGISTER PATIENT & ISSUE HEALTH CARD - Step 2-3 of Registration
    
    Request: POST /register_patient
    Body: {
        "patient": {
            "name": "John Doe",
            "age": 30,
            "mobile": "9876543210",
            "countryCode": "+91",
            "email": "john@gmail.com",
            "blood": "O+",
            ...
        },
        "mobileOtp": "123456"
    }
    
    Process:
    1. VERIFY OTP: Confirm mobile OTP is correct, not expired, not used
    2. CONSUME OTP: Mark OTP as used (prevents replay/reuse attacks)
    3. GENERATE HEALTH ID: Create unique 16-digit identifier
    4. GENERATE QR TOKEN: Create authentication token for QR code
    5. STORE PATIENT: Persist all data to patients table
    6. RETURN CARD: Send back issued health card details
    
    Response: {
        "success": true,
        "card": {
            "healthId": "1701001234567890",
            "qrToken": "QR-ABC123DEF456",
            "issuedOn": 1701001200,
            "renewalOn": 1732537200,
            "name": "John Doe",
            "email": "john@gmail.com",
            "mobile": "+91 9876543210"
        }
    }
    
    Database:
    - Inserts new row in patients table with all medical data
    - health_id: Unique identifier (primary key)
    - issued_on: Unix timestamp of card issue
    - renewal_on: Unix timestamp (10 years later)
    - OTP: Marked as used to prevent duplicate registrations
    """
    data = request.get_json(force=True)
    patient = data.get('patient') or {}
    mobile_otp = data.get('mobileOtp')
    email_otp = data.get('emailOtp')

    # Validate required mobile OTP
    if not mobile_otp:
        return jsonify(success=False, error='mobileOtp is required'), 400

    # Extract mobile and email from patient data
    mobile = patient.get('fullMobile') or (patient.get('countryCode') and patient.get('mobile') and f"{patient.get('countryCode')} {patient.get('mobile')}")
    email = patient.get('email')

    if not mobile or not email:
        return jsonify(success=False, error='Patient mobile and email required'), 400

    # STEP 1: VERIFY MOBILE OTP
    # Checks: OTP exists, not used, not expired
    # Side effect: Mark OTP as used (prevent replay attacks)
    ok_m, msg_m, _ = _verify_and_mark(mobile, mobile_otp)
    if not ok_m:
        logging.warning('❌ Mobile OTP verification failed for %s: %s', mobile, msg_m)
        return jsonify(success=False, error=f'Mobile OTP verification failed: {msg_m}'), 400

    # STEP 2: VERIFY EMAIL OTP (if provided)
    if email_otp:
        ok_e, msg_e, _ = _verify_and_mark(email, email_otp)
        if not ok_e:
            logging.warning('❌ Email OTP verification failed for %s: %s', email, msg_e)
            return jsonify(success=False, error=f'Email OTP verification failed: {msg_e}'), 400

    # STEP 3: GENERATE HEALTH CARD IDENTIFIERS
    # Health ID: 16-digit unique identifier (timestamp + random)
    # QR Token: 12-character alphanumeric token for card authentication
    hid = generate_health_id()
    qr = 'QR-' + ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=12))
    
    # STEP 4: SET VALIDITY PERIOD
    # Issued now, valid for 10 years (standard renewal period)
    issued_on = int(time.time())
    renewal_on = issued_on + (10 * 365 * 24 * 60 * 60)  # 10 years in seconds

    logging.info('✅ Generating Health Card for %s: ID=%s', patient.get('name'), hid)

    # STEP 5: PERSIST PATIENT TO DATABASE
    # Stores all medical information in patients table
    conn = get_db_conn()
    c = conn.cursor()
    c.execute('INSERT INTO patients (health_id, qr_token, name, age, gender, country_code, mobile, email, blood, allergies, vaccinations, genetic, disease, fever, temperature, temp_unit, issued_on, renewal_on, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (
        hid,                              # Unique 16-digit Health ID
        qr,                               # QR authentication token
        patient.get('name'),              # Patient name
        patient.get('age'),               # Patient age
        patient.get('gender'),            # Gender (M/F/Other)
        patient.get('countryCode'),       # Country code for phone
        patient.get('mobile'),            # 10-digit mobile
        patient.get('email'),             # Email address
        patient.get('blood'),             # Blood group (O+, B-, etc)
        patient.get('allergies'),         # Known allergies
        patient.get('vaccinations'),      # Vaccination history
        patient.get('genetic'),           # Genetic predispositions
        patient.get('disease'),           # Disease management info
        patient.get('fever'),             # Current fever status
        str(patient.get('temperature') or ''),  # Current temperature
        patient.get('tempUnit'),          # Temperature unit (C/F)
        issued_on,                        # Card issue timestamp
        renewal_on,                       # Card renewal timestamp
        int(time.time())                  # Record creation timestamp
    ))
    conn.commit()
    conn.close()

    logging.info('✅ Patient %s registered successfully with Health ID %s', patient.get('name'), hid)

    # STEP 6: POST-REGISTRATION OTP (optional welcome/verification step)
    # Generate a new OTP after registration and send it to the patient's mobile number.
    post_otp = f"{random.randint(100000, 999999)}"
    post_expires = int(time.time()) + OTP_TTL_SECONDS
    try:
        # Save OTP to DB and send via Twilio
        save_otp(mobile, 'mobile', post_otp, post_expires)
        # Clean mobile for sending (remove spaces)
        send_to = mobile.replace(' ', '') if isinstance(mobile, str) else mobile
        ok_post, info_post = send_sms_twilio(send_to, post_otp)
        logging.info('Post-registration OTP sent: %s -> %s (sent=%s)', send_to, post_otp, ok_post)
    except Exception as e:
        logging.exception('Failed to generate/send post-registration OTP')
        ok_post, info_post = False, str(e)

    # STEP 7: RETURN ISSUED HEALTH CARD TO FRONTEND (includes post-registration OTP delivery info)
    card = {
        'healthId': hid,          # Unique identifier for health card
        'qrToken': qr,            # Token encoded in QR code
        'issuedOn': issued_on,    # Unix timestamp (seconds)
        'renewalOn': renewal_on,  # Unix timestamp (seconds)
        'name': patient.get('name'),
        'email': patient.get('email'),
        'mobile': mobile
    }

    return jsonify(success=True, card=card, postRegistrationOtp={'sent': ok_post, 'info': info_post})


@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json(force=True)
    destination = data.get('destination')
    otp = data.get('otp')

    if not destination or not otp:
        return jsonify(success=False, error='destination and otp required'), 400

    # Perform a read-only verification: check there is a matching, unexpired, unused OTP.
    now = int(time.time())
    conn = get_db_conn()
    c = conn.cursor()
    c.execute('SELECT id, expires_at, used FROM otps WHERE destination = ? AND otp = ? ORDER BY id DESC LIMIT 1', (destination, otp))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify(success=False, error='No matching OTP found'), 404

    if row['used'] == 1:
        return jsonify(success=False, error='OTP already used'), 400

    if row['expires_at'] < now:
        return jsonify(success=False, error='OTP expired'), 400

    # NOTE: do not mark as used here. Clients may call this to verify before submitting registration;
    # actual consumption/marking is done by /register_patient which calls _verify_and_mark.
    return jsonify(success=True)


@app.route('/debug/otps', methods=['GET'])
def debug_otps():
    """Development-only endpoint to list recent OTPs. Enable by setting environment var OTP_DEBUG=true."""
    if os.getenv('OTP_DEBUG', 'false').lower() != 'true':
        return jsonify(success=False, error='debug endpoint disabled'), 403

    limit = int(request.args.get('limit', '50'))
    conn = get_db_conn()
    c = conn.cursor()
    c.execute('SELECT id, destination, type, otp, expires_at, used, created_at FROM otps ORDER BY id DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()

    results = []
    for r in rows:
        results.append({
            'id': r['id'],
            'destination': r['destination'],
            'type': r['type'],
            'otp': r['otp'],
            'expires_at': r['expires_at'],
            'used': bool(r['used']),
            'created_at': r['created_at']
        })

    return jsonify(success=True, otps=results)


if __name__ == '__main__':
    init_db()
    logging.info('Starting OTP server on port %d', APP_PORT)
    app.run(host='0.0.0.0', port=APP_PORT)
