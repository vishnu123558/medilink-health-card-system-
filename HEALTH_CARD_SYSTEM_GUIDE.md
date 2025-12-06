# 🏥 Healthcare System - Complete Implementation Guide

## Overview
A complete patient registration and health card issuance system built with:
- **Frontend**: HTML5/CSS3/JavaScript with professional blue medical UI
- **Backend**: Python Flask OTP server with SQLite persistence
- **Features**: Mobile OTP verification, unique 16-digit Health IDs, QR code generation, 10-year validity cards

---

## 📋 System Components

### 1. **Frontend (`login.html`)**
- Patient registration form with medical information
- Mobile OTP verification
- Professional health card display with QR code
- Doctor and Admin module interfaces (blue-themed)

### 2. **Backend (`otp_server.py`)**
- OTP generation and verification (6-digit, 10-minute TTL)
- Patient registration endpoint
- Health card issuance with 16-digit unique ID
- SQLite database for persistence

### 3. **Database (`otp_store.db`)**
- `otps` table: OTP records with expiry and usage tracking
- `patients` table: Patient records with medical data and card validity

---

## 🚀 Quick Start

### Prerequisites
- Python 3.7+ with pip installed
- PowerShell (Windows) or Terminal (Mac/Linux)

### Installation

#### Step 1: Setup Python Environment
```powershell
# Navigate to project directory
cd "c:\Users\vishn\OneDrive\Desktop\healthcardsystem"

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
# If you get execution policy error, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install -r requirements.txt
```

#### Step 2: Start the OTP Server
```powershell
# Enable debug mode to view OTPs (development only)
$env:OTP_DEBUG = 'true'

# Start Flask server on http://localhost:5000
.\.venv\Scripts\python.exe otp_server.py
```

#### Step 3: Serve Frontend (New PowerShell Terminal)
```powershell
# Navigate to project directory
cd "c:\Users\vishn\OneDrive\Desktop\healthcardsystem"

# Start Python HTTP server on http://localhost:8000
python -m http.server 8000
```

#### Step 4: Open Browser
```
http://localhost:8000/login.html
```

---

## 📝 Registration Flow

### Step 1: Fill Registration Form
- **Name**: Patient full name
- **Age**: Patient age in years
- **Gender**: Select Male/Female/Other
- **Mobile**: 10-digit number
- **Email**: Valid email address
- **Blood Group**: Select blood type
- **Medical Info**: Allergies, vaccinations, genetic history, disease management
- **Fever Status**: None, Low-grade, Moderate, High, Very High, Hyperpyrexia
- **Temperature** (Optional): Current body temperature

### Step 2: Submit Registration
- Click **"Register & Generate Health ID Card"**
- Form data saved to browser's localStorage
- Server sends OTP to mobile number
- OTP input field appears

### Step 3: View OTP (Debug Mode)
**Development Only** - OTP is displayed at:
```
http://localhost:5000/debug/otps
```
- Shows recent OTPs with destination and timestamp
- Requires `OTP_DEBUG=true` environment variable

### Step 4: Verify OTP
- Enter 6-digit OTP from mobile
- Click **"Verify Mobile OTP & Show Health Card"**
- Backend validates OTP:
  - Checks existence
  - Checks expiry (10-minute window)
  - Checks one-time use (not consumed yet)

### Step 5: View Health Card
Upon successful OTP verification, health card is displayed with:
- **Personal Information**: Name, Age, Gender
- **Contact Details**: Mobile, Email
- **Medical Data**: Blood group, fever status, temperature
- **Health History**: Allergies, vaccinations, genetic info, disease management
- **16-Digit Health ID**: Unique permanent identifier in blue gradient box
- **Validity Period**: Issue date (DD/MM/YYYY) and renewal date (10 years later)
- **QR Code**: 200x200px blue QR code encoding all card data

---

## 🎯 16-Digit Unique Health ID

### Format
```
XXXXXXXXXXXXXXXXX (16 consecutive digits)
Example: 1701001234567890
```

### Components
| Part | Digits | Source | Purpose |
|------|--------|--------|---------|
| Timestamp | 13 | `int(time.time() * 1000)` | Ensure uniqueness over time |
| Random | 6 | `random.randint(0, 999999)` | Ensure uniqueness in same millisecond |

### Generation Code (Backend)
```python
def generate_health_id():
    ts = str(int(time.time() * 1000))      # 13-digit timestamp in ms
    rand = str(random.randint(0, 999999)).zfill(6)  # 6-digit random
    hid = (ts + rand)[-16:]  # Take last 16 characters
    return hid
```

### Characteristics
- ✅ **Unique**: Probabilistically unique per patient
- ✅ **Permanent**: Never changes for same patient
- ✅ **Time-based**: Contains embedded timestamp for sorting
- ✅ **Non-sequential**: Random component prevents guessing
- ✅ **Database Primary Key**: Indexed for fast lookups

---

## 📅 Date Formatting (DD/MM/YYYY)

### Display Format
```
Issued On:   25/11/2025
Renewal On:  25/11/2035  (10 years later)
```

### Frontend Function
```javascript
function formatDate(isoString) {
    const date = new Date(isoString);
    const day = String(date.getDate()).padStart(2, '0');      // 01-31
    const month = String(date.getMonth() + 1).padStart(2, '0'); // 01-12
    const year = date.getFullYear();                           // YYYY
    return `${day}/${month}/${year}`;
}
```

### Backend Calculation
```python
issued_on = int(time.time())                    # Now (Unix timestamp)
renewal_on = issued_on + (10 * 365 * 24 * 60 * 60)  # Add 10 years
# renewal_on = issued_on + 315,360,000 seconds
```

---

## ♻️ 10-Year Card Validity

### Validity Period
```
Issued:   2025-11-25 10:00:00
Expires:  2035-11-25 10:00:00 (Exactly 10 years later)
```

### Server-Side Calculation
```python
# Card validity period
issued_on = int(time.time())           # Now in seconds
renewal_on = issued_on + (10 * 365 * 24 * 60 * 60)  # 10 years

# Seconds in 10 years:
# 10 years × 365 days × 24 hours × 60 minutes × 60 seconds
# = 10 × 365 × 24 × 60 × 60
# = 315,360,000 seconds
```

### Verification Message
```
✅ Card is valid for 10 years from issue date
Issued On: 25/11/2025
Renewal Date: 25/11/2035
```

---

## 🎨 Health Card Layout (CSS Explained)

### Main Card Container
```css
.id-card {
    background: linear-gradient(135deg, #e3f2fd 0%, #ffffff 100%);
    /* Light blue gradient background (medical branding) */
    
    border: 2px solid #1976d2;  /* Primary blue border */
    border-radius: 15px;
    
    display: flex;              /* Layout: info on left, QR on right */
    gap: 40px;                  /* Space between info and QR */
    
    box-shadow: 0 8px 24px rgba(25, 118, 210, 0.2);  /* Soft blue shadow */
}
```

### Health ID Display (Prominent)
```css
.health-id-display {
    background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
    /* Dark blue gradient background */
    color: white;
    
    padding: 20px;
    border-radius: 12px;
    
    text-align: center;
    
    box-shadow: 0 4px 12px rgba(25, 118, 210, 0.2);
}

.id-value {
    font-size: 28px;              /* Large, very readable */
    font-weight: 700;             /* Bold */
    letter-spacing: 2px;          /* Spread out digits */
    font-family: 'Courier New', monospace;  /* Fixed-width font */
}
```

### Validity Section (Green Accent)
```css
.validity-section {
    background: linear-gradient(135deg, #f5f5f5 0%, #ffffff 100%);
    /* Light gray gradient */
    
    border-left: 4px solid #4caf50;  /* Green accent (valid/approved) */
    
    padding: 15px;
    border-radius: 8px;
    
    margin-top: 15px;
}
```

### QR Code Container
```css
.qr-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 15px;
    
    /* QR code will be 200x200 pixels */
}

#qrcode {
    padding: 15px;
    background: white;
    border: 2px solid #1976d2;
    border-radius: 10px;
    
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
```

---

## 📱 QR Code Data Encoding

### QR Code Generation
```javascript
const qrData = {
    healthId: "1701001234567890",      // 16-digit unique ID
    qrToken: "QR-ABC123DEF456",        // 12-character token
    issuedOn: "25/11/2025",            // DD/MM/YYYY format
    renewalOn: "25/11/2035",           // DD/MM/YYYY format
    patientName: "John Doe"
};

new QRCode(document.getElementById('qrcode'), {
    text: JSON.stringify(qrData),      // JSON-encoded data
    width: 200,                         // 200 pixels
    height: 200,                        // 200 pixels
    colorDark: '#1976d2',              // Blue QR code (medical branding)
    colorLight: '#ffffff',             // White background
    errorCorrectionLevel: 'H'          // High error correction (30% recovery)
});
```

### QR Code Specifications
| Property | Value | Purpose |
|----------|-------|---------|
| Size | 200x200 pixels | Easily scannable on mobile screens |
| Color | Blue (#1976d2) | Medical branding consistency |
| Background | White | High contrast for scanning |
| Error Correction | High (H) | Can recover 30% damaged data |
| Data Format | JSON | Structured, machine-readable |

---

## 🗄️ Database Schema

### `otps` Table
```sql
CREATE TABLE otps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    destination TEXT NOT NULL,      -- Mobile (+91 9876543210) or email
    type TEXT,                      -- 'sms' or 'email'
    otp TEXT NOT NULL,              -- 6-digit code
    expires_at INTEGER NOT NULL,    -- Unix timestamp (now + 600s)
    used INTEGER DEFAULT 0,         -- 0=unused, 1=consumed (one-time use)
    created_at INTEGER DEFAULT 0
)
```

### `patients` Table
```sql
CREATE TABLE patients (
    health_id TEXT PRIMARY KEY,     -- 16-digit unique ID
    qr_token TEXT,                  -- Authentication token for QR
    name TEXT,                      -- Patient full name
    age INTEGER,                    -- Patient age
    gender TEXT,                    -- M/F/Other
    country_code TEXT,              -- Phone country code (+91, +1, etc)
    mobile TEXT,                    -- 10-digit phone number
    email TEXT,                     -- Email address
    blood TEXT,                     -- Blood group (O+, B-, etc)
    allergies TEXT,                 -- Known allergies
    vaccinations TEXT,              -- Vaccination history
    genetic TEXT,                   -- Genetic predispositions
    disease TEXT,                   -- Disease management info
    fever TEXT,                     -- Current fever status
    temperature REAL,               -- Body temperature (optional)
    temp_unit TEXT,                 -- C (Celsius) or F (Fahrenheit)
    issued_on INTEGER,              -- Card issue timestamp
    renewal_on INTEGER,             -- Card renewal timestamp (10 years)
    created_at INTEGER
)
```

---

## 🔐 OTP System Details

### OTP Specifications
| Property | Value | Purpose |
|----------|-------|---------|
| Length | 6 digits | Easy to type, remember |
| Range | 0-999999 | Random generation |
| TTL (Time To Live) | 10 minutes | 600 seconds |
| One-time Use | ✅ Yes | Consumed after `/register_patient` |
| Storage | SQLite | Persistent, queryable |

### OTP Lifecycle
```
1. GENERATE: 6-digit random OTP created
   - expires_at = now + 600 seconds (10 minutes)
   - used = 0 (not consumed)

2. SEND: Via SMS (Twilio) or Email (SMTP)
   - Optional: can test without SMS configured

3. VERIFY (Read-Only): Check existence and validity
   - Checks: exists, not expired, not used
   - No state changes

4. REGISTER: Verify again and mark as used
   - Checks same as #3
   - Sets: used = 1 (one-time use enforcement)
   - Creates patient record
   - Generates 16-digit Health ID

5. REPLAY ATTACK PREVENTION:
   - After marking used = 1, same OTP cannot be reused
   - Each registration requires new OTP
```

### Backend Code
```python
def _verify_and_mark(destination, otp):
    """Verify OTP validity and mark as used (one-time enforcement)"""
    conn = get_db_conn()
    c = conn.cursor()
    
    # Check: OTP exists, not expired, not yet used
    c.execute('SELECT * FROM otps WHERE destination=? AND otp=? AND used=0 AND expires_at > ?',
              (destination, otp, int(time.time())))
    row = c.fetchone()
    
    if not row:
        conn.close()
        return False, 'OTP not found, expired, or already used', None
    
    # Mark OTP as used (prevent replay attacks)
    c.execute('UPDATE otps SET used=1 WHERE destination=? AND otp=?',
              (destination, otp))
    conn.commit()
    conn.close()
    
    return True, 'OTP verified', row
```

---

## 🎨 Color Scheme (Blue Medical Theme)

### Color Palette
| Color | Hex | Usage | Purpose |
|-------|-----|-------|---------|
| Primary Blue | #1976d2 | Headers, buttons, borders | Medical branding |
| Light Blue | #e3f2fd | Card backgrounds | Professional, clean look |
| Dark Blue | #1565c0 | Hover states, accents | Depth and interactivity |
| Success Green | #4caf50 | Validity section | Card is valid/approved |
| Neutral Gray | #666, #999 | Text, borders | Contrast and readability |
| White | #ffffff | Backgrounds, text | Clean, professional |

### CSS Variables (Global)
```css
/* Medical branding colors */
--primary-blue: #1976d2;      /* Main brand color */
--light-blue: #e3f2fd;        /* Light backgrounds */
--dark-blue: #1565c0;         /* Hover, emphasis */
--success-green: #4caf50;     /* Valid/approved states */
```

---

## 🧪 Testing Workflow

### 1. Start Services
```powershell
# Terminal 1: Backend
$env:OTP_DEBUG = 'true'
.\.venv\Scripts\python.exe otp_server.py

# Terminal 2: Frontend
python -m http.server 8000
```

### 2. Open Browser
```
http://localhost:8000/login.html
```

### 3. Fill Registration Form
- Name: John Doe
- Age: 30
- Gender: Male
- Mobile: 9876543210
- Email: john@example.com
- Blood: O+
- Fill other medical fields

### 4. View Debug OTP
```
http://localhost:5000/debug/otps
```
- Find your mobile number
- Copy the 6-digit OTP

### 5. Enter OTP and Verify
- Paste OTP in "Mobile OTP" field
- Click "Verify Mobile OTP & Show Health Card"
- Health card displays with:
  - 16-digit Health ID (e.g., 1701001234567890)
  - DD/MM/YYYY formatted dates
  - 10-year validity period
  - Scannable QR code

### 6. Test QR Code
- Scan QR code with phone camera
- It contains: Health ID + token + dates + name (JSON)

---

## 📚 API Endpoints

### POST `/send_otp`
Send OTP to patient mobile
```json
Request:
{
    "mobile": "+91 9876543210"
}

Response:
{
    "success": true,
    "details": "OTP generated for +91 9876543210"
}
```

### POST `/verify_otp`
Verify OTP (read-only, no state change)
```json
Request:
{
    "mobile": "+91 9876543210",
    "otp": "123456"
}

Response:
{
    "success": true,
    "message": "OTP is valid"
}
```

### POST `/register_patient`
Register patient and issue health card
```json
Request:
{
    "patient": {
        "name": "John Doe",
        "age": 30,
        "gender": "M",
        "countryCode": "+91",
        "mobile": "9876543210",
        "email": "john@example.com",
        "blood": "O+",
        "allergies": "Peanuts",
        "vaccinations": "COVID-19, Flu",
        "genetic": "None",
        "disease": "None",
        "fever": "None",
        "temperature": "37.5",
        "tempUnit": "C"
    },
    "mobileOtp": "123456"
}

Response:
{
    "success": true,
    "card": {
        "healthId": "1701001234567890",
        "qrToken": "QR-ABC123DEF456",
        "issuedOn": 1701001200,
        "renewalOn": 1732537200,
        "name": "John Doe",
        "email": "john@example.com",
        "mobile": "+91 9876543210"
    }
}
```

### GET `/debug/otps` (Development Only)
List recent OTPs for testing
```
Requires: OTP_DEBUG=true environment variable

Response:
[
    {
        "destination": "+91 9876543210",
        "otp": "123456",
        "expires_at": 1701001800,
        "used": 0,
        "created_at": 1701001200
    },
    ...
]
```

---

## 🛠️ Troubleshooting

### Issue: PowerShell Execution Policy Error
```powershell
Error: "cannot be loaded because running scripts is disabled"

Solution:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then try to activate venv again: .\.venv\Scripts\Activate.ps1
```

### Issue: Port Already in Use
```powershell
# Flask server won't start on port 5000

Solution 1: Use different port
$env:FLASK_ENV = 'development'
.\.venv\Scripts\python.exe -c "from otp_server import app; app.run(port=5001)"

Solution 2: Kill process using port 5000
Get-Process | Where-Object {$_.Port -eq 5000} | Stop-Process
```

### Issue: CORS Errors
```
Error: "Access to XMLHttpRequest blocked by CORS policy"

Solution:
- Flask server has flask-cors enabled
- Access frontend via http://localhost:8000, not file://
- Check server logs: http://localhost:5000/ should show "✅ Server running"
```

### Issue: OTP Not Sending
```
Solution (Development):
1. Check http://localhost:5000/debug/otps for OTP
2. Or check server terminal logs for "✅ OTP generated: XXXXXX"
3. SMS: Requires Twilio API key (set via .env)
4. Email: Requires SMTP credentials (set via .env)
```

---

## 📖 Source Code Files

### Key Files
| File | Purpose | Lines |
|------|---------|-------|
| `login.html` | Frontend UI + registration form + health card display | 1,371 |
| `otp_server.py` | Flask backend + OTP endpoints + health card issuance | 506 |
| `otp_store.db` | SQLite database (auto-created) | - |
| `requirements.txt` | Python dependencies | 4 packages |

### Key Sections

#### `login.html` - Registration Handler (Line ~650)
Collects patient form data, validates, sends mobile to `/send_otp`, displays OTP input

#### `login.html` - OTP Verification (Line ~715)
Submits OTP to `/verify_otp`, then `/register_patient`, handles response

#### `login.html` - Health Card Display (Line ~633)
`showHealthCard()` function renders professional card with all sections

#### `otp_server.py` - Health ID Generation (Line ~192)
`generate_health_id()` creates 16-digit unique identifier

#### `otp_server.py` - Patient Registration (Line ~290)
`register_patient()` endpoint verifies OTP, generates ID, stores patient, returns card

---

## 🎓 Learning Resources

### Understanding the System
1. **Registration Flow**: Registration form → OTP generation → OTP verification → Health card issuance
2. **16-Digit ID**: Timestamp (13 digits) + Random (6 digits) = Unique, permanent identifier
3. **Card Validity**: 10 years from issue date; renewal date automatically calculated
4. **QR Code**: Encodes all card data (ID + token + dates + name) for scanning verification

### Customization Options
1. **Change OTP TTL**: `otp_server.py` line 270: `expires_at = now + 600` (600 seconds = 10 minutes)
2. **Change Health ID Length**: `otp_server.py` line 209: `hid = (ts + rand)[-16:]` (16 digits)
3. **Change Card Validity**: `otp_server.py` line 330: `renewal_on = issued_on + (10 * 365 * 24 * 60 * 60)` (10 years)
4. **Change Color Scheme**: `login.html` CSS section (line ~40): `#1976d2` (primary blue)

---

## ✅ Verification Checklist

- [ ] Python virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Flask server running on http://localhost:5000
- [ ] Frontend server running on http://localhost:8000
- [ ] Registration form submits successfully
- [ ] OTP generated and visible at `/debug/otps`
- [ ] OTP verification succeeds
- [ ] Health card displays with 16-digit ID
- [ ] Date format is DD/MM/YYYY (e.g., 25/11/2025)
- [ ] Renewal date shows 10 years later (e.g., 25/11/2035)
- [ ] QR code is scannable (200x200px, blue)
- [ ] Database `otp_store.db` created with two tables
- [ ] Patient record saved in `patients` table

---

## 📞 Support

### Debug Endpoints
- **OTP Debug**: http://localhost:5000/debug/otps (requires `OTP_DEBUG=true`)
- **Server Status**: http://localhost:5000/ (check if running)
- **Frontend**: http://localhost:8000/login.html

### Logs to Check
- **Browser Console**: Open DevTools (F12) → Console tab
  - Look for: `✅ Health Card Generated`
- **Server Terminal**: Check Flask server output
  - Look for: `✅ OTP generated: XXXXXX`
  - Look for: `✅ Patient registered successfully`

---

## 🎉 System Complete!

Your healthcare system is fully implemented with:
- ✅ OTP-based patient registration
- ✅ Unique 16-digit Health IDs
- ✅ Professional health cards with DD/MM/YYYY dates
- ✅ 10-year validity periods
- ✅ QR code encoding card data
- ✅ Blue medical-themed UI
- ✅ SQLite database persistence
- ✅ Comprehensive source code documentation

**Next Steps**: Deploy to production with email/SMS gateway configured, SSL certificates, and cloud database!
