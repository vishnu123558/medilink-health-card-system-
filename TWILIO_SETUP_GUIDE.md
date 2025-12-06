# 🚀 Twilio SMS Setup Guide for MediLink

## Quick Start: 3 Steps to Enable SMS OTP

### Step 1️⃣: Get Twilio Credentials

#### **Option A: If You Already Have Twilio Account**
1. Go to: https://www.twilio.com/console
2. Login with your credentials
3. Find these on the dashboard:
   - **Account SID** (starts with `AC...`)
   - **Auth Token** (long alphanumeric string)
4. Go to "Phone Numbers" → Find your **Twilio Phone Number** (e.g., `+1234567890`)

#### **Option B: If You DON'T Have Twilio Account**
1. Sign up free: https://www.twilio.com/try-twilio
2. Verify your phone number (Twilio will call/SMS you)
3. You'll get:
   - Free trial account with $15-20 credits
   - A Twilio phone number automatically assigned
   - Account SID and Auth Token

---

### Step 2️⃣: Configure `.env` File

Edit the `.env` file in your project folder:

```
c:\Users\vishn\OneDrive\Desktop\healthcardsystem\.env
```

Replace the placeholder values with YOUR Twilio credentials:

```env
# COPY FROM TWILIO CONSOLE DASHBOARD
TWILIO_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx      # ← Your Account SID
TWILIO_TOKEN=your_auth_token_here_example          # ← Your Auth Token
TWILIO_FROM=+1234567890                            # ← Your Twilio Phone Number

OTP_DEBUG=true
OTP_TTL_SECONDS=600
OTP_SERVER_PORT=5000
```

**Important:**
- `TWILIO_SID` must start with `AC`
- `TWILIO_FROM` must include `+` and country code (e.g., `+1` for USA, `+44` for UK)
- Copy EXACTLY as shown in Twilio console (no extra spaces)

---

### Step 3️⃣: Start Backend Server

#### Terminal 1: Start Flask OTP Server

```powershell
cd "C:\Users\vishn\OneDrive\Desktop\healthcardsystem"

# Activate virtual environment (if not already active)
.\.venv\Scripts\Activate.ps1

# Start server
python otp_server.py
```

**Expected output:**
```
 * Running on http://0.0.0.0:5000
 * WARNING: This is a development server...
```

#### Terminal 2: Start Frontend Server

```powershell
cd "C:\Users\vishn\OneDrive\Desktop\healthcardsystem"

python -m http.server 8000
```

#### Terminal 3: Open in Browser

```
http://localhost:8000/login.html
```

---

## 🧪 Test SMS OTP Flow

1. **Fill Registration Form:**
   - Name: John Doe
   - Mobile: Your actual phone number (e.g., `+91 9876543210`)
   - Email: your.email@gmail.com
   - Blood Type: O+

2. **Click "Register"**

3. **Check Your Phone:**
   - You'll receive SMS: **"Your MediLink OTP: 654321"**
   - SMS comes FROM your Twilio phone number

4. **Enter OTP in App:**
   - Type the 6-digit code in the app
   - Click "Verify OTP"

5. **Get Health Card:**
   - Professional blue card displayed
   - 16-digit unique Health ID
   - Valid for 10 years
   - QR code generated

---

## ❌ Troubleshooting

### Problem: "SMS not received"

**Solution:**
1. Check `.env` file has correct credentials (copy-paste from Twilio console)
2. Verify `TWILIO_FROM` phone number has `+` and country code
3. Check that phone number receiving SMS is correct format (`+1234567890`)
4. View Flask logs for error message

### Problem: "Twilio not configured" message

**Cause:** One or more env variables missing in `.env`

**Solution:**
1. Check `.env` exists in project root: `c:\Users\vishn\OneDrive\Desktop\healthcardsystem\.env`
2. Verify all three variables set:
   ```env
   TWILIO_SID=ACxxxxxxx
   TWILIO_TOKEN=xxxxx
   TWILIO_FROM=+1xxxxxx
   ```
3. Restart Flask server after editing `.env`

### Problem: "Cannot contact OTP server"

**Cause:** Flask backend not running on port 5000

**Solution:**
```powershell
# Terminal 1: Check if Flask is running
netstat -ano | findstr :5000

# If not running, start it:
cd "C:\Users\vishn\OneDrive\Desktop\healthcardsystem"
.\.venv\Scripts\python.exe otp_server.py
```

---

## 🐛 Debug: View Generated OTPs

If SMS isn't working, view OTPs generated on the server:

```
http://localhost:5000/debug/otps
```

Shows all OTPs from last hour (requires `OTP_DEBUG=true` in `.env`)

**Example response:**
```json
{
  "recent_otps": [
    {
      "destination": "+91 9876543210",
      "type": "mobile",
      "otp": "654321",
      "expires_at": 1701072453
    }
  ]
}
```

---

## 💡 How It Works (Technical Overview)

### Registration Flow

```
1. User fills form → POST /send_otp
   ↓
2. Backend generates 6-digit OTP (100000-999999)
   ↓
3. OTP saved to database with 10-minute expiry
   ↓
4. Twilio SMS sent automatically
   ↓
5. User receives SMS: "Your MediLink OTP: XXXXXX"
   ↓
6. User enters OTP → POST /verify_otp
   ↓
7. Backend verifies OTP is valid & not expired
   ↓
8. OTP marked as "used" (can't reuse)
   ↓
9. Patient data saved, Health ID generated
   ↓
10. POST /register_patient returns health card
    ↓
11. Frontend displays card with QR code
```

### Backend Code Integration

**File:** `otp_server.py` (lines 121-145)

```python
def send_sms_twilio(to_number, otp):
    """Send SMS via Twilio"""
    twilio_sid = os.getenv('TWILIO_SID')        # Read from .env
    twilio_token = os.getenv('TWILIO_TOKEN')    # Read from .env
    twilio_from = os.getenv('TWILIO_FROM')      # Read from .env
    
    if not twilio_sid or not twilio_token or not twilio_from:
        logging.info('Twilio not configured...')
        return False, 'Skipped'
    
    try:
        from twilio.rest import Client
        client = Client(twilio_sid, twilio_token)
        message = client.messages.create(
            body=f'Your MediLink OTP: {otp}',
            from_=twilio_from,
            to=to_number
        )
        logging.info('✅ SMS sent. Message SID: %s', message.sid)
        return True, message.sid
    except Exception as e:
        logging.exception('❌ Failed to send SMS')
        return False, str(e)
```

Called automatically by `/send_otp` endpoint when user registers.

---

## 🔐 Security Notes

- **OTP is 6 digits:** 1,000,000 possible combinations
- **Valid for 10 minutes:** Expires after 600 seconds
- **One-time use:** OTP marked "used" after verification
- **Database encrypted:** Stored in SQLite, not transmitted
- **HTTPS recommended:** In production, use HTTPS instead of HTTP

---

## 📞 Twilio Pricing

**Free Trial:**
- $15-20 free credits
- Enough for ~50-100 SMS tests (depending on country)
- Expires after 30 days

**After Free Trial:**
- SMS typically costs $0.0075-0.02 per message (varies by country)
- Per-message basis (no monthly fee)
- Pay as you go

Check: https://www.twilio.com/sms/pricing

---

## ✅ Complete Setup Checklist

- [ ] Create free Twilio account at https://www.twilio.com/try-twilio
- [ ] Verify phone number during signup
- [ ] Go to Twilio Console: https://www.twilio.com/console
- [ ] Copy Account SID from dashboard
- [ ] Copy Auth Token from dashboard
- [ ] Copy your Twilio Phone Number from "Phone Numbers"
- [ ] Edit `.env` file with three values
- [ ] Save `.env` file
- [ ] Start Flask backend: `python otp_server.py`
- [ ] Start HTTP frontend: `python -m http.server 8000`
- [ ] Open `http://localhost:8000/login.html`
- [ ] Test registration with real phone number
- [ ] Verify SMS received on your phone
- [ ] Enter OTP in app and get health card

---

## 🎯 Next Steps

1. Get Twilio credentials (free account takes 5 minutes)
2. Update `.env` file with your credentials
3. Restart Flask server
4. Test SMS flow with your phone number
5. Backend is ready for patient registrations!

**Questions?** Check the Flask server logs for detailed error messages.
