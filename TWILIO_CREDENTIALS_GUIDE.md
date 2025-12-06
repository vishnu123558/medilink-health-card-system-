# 🔑 **WHERE TO FIND TWILIO CREDENTIALS - Complete Visual Guide**

---

## **🎯 STEP 1: Create Free Twilio Account**

### **Go to:** https://www.twilio.com/try-twilio

**Click "Sign up free"** and follow these steps:

1. **Enter Email & Password**
   - Email: your@gmail.com
   - Password: Create a strong password
   - Click "Create Account"

2. **Verify Your Email**
   - Check your email inbox
   - Click verification link
   - Your account is activated

3. **Verify Your Phone Number**
   - Twilio will ask for your phone number
   - Enter: +91 9876543210 (your actual Indian phone number)
   - Choose SMS (you'll get a verification code via SMS)
   - Enter the code → Verified! ✅

4. **You're Done with Signup!**
   - Twilio gives you:
     - **Free $20 trial credits** (good for ~100 SMS)
     - A **free Twilio phone number** (assigned automatically)
     - **Account SID & Auth Token** (see below)

---

## **📍 STEP 2: Find Your Credentials in Twilio Console**

### **Go to:** https://www.twilio.com/console

**This is the Twilio Dashboard. You'll see:**

```
┌─────────────────────────────────────────────────────────┐
│                 TWILIO CONSOLE (Dashboard)              │
│  ─────────────────────────────────────────────────────  │
│                                                           │
│  Welcome back!                                            │
│                                                           │
│  PROJECT INFO                                             │
│  ─────────────────────────────────────────────────────  │
│                                                           │
│  Account SID                                              │
│  ┌────────────────────────────────────────────────────┐ │
│  │ ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx │ │  ← COPY THIS!
│  └────────────────────────────────────────────────────┘ │
│                                                           │
│  Auth Token                                               │
│  ┌────────────────────────────────────────────────────┐ │
│  │ a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0 │ │  ← COPY THIS!
│  └────────────────────────────────────────────────────┘ │
│                   [Hide Token]                            │
│                                                           │
│  Account Balance: $20.00 (Free Trial)                    │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### **🔴 Credential #1: TWILIO_SID**

**What it is:** Your unique Twilio Account identifier

**Where to find it:**
1. Login to https://www.twilio.com/console
2. Look at "PROJECT INFO" section
3. You'll see **"Account SID"** label
4. It starts with **AC** followed by 32 characters
5. Example: `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**Copy it:**
- Click the value field
- Select all (Ctrl+A)
- Copy (Ctrl+C)
- Paste into `.env` file

```env
TWILIO_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
            ↑ Starts with AC
```

---

### **🔴 Credential #2: TWILIO_TOKEN**

**What it is:** Your secret authentication token (like a password)

**Where to find it:**
1. Same console page
2. Look for **"Auth Token"** label
3. It's a long alphanumeric string (40+ characters)
4. Example: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0`

**⚠️ SECURITY WARNING:**
- This is like your password
- **Never share it publicly**
- **Never commit it to GitHub**
- Keep it secret!

**Copy it:**
- Click on the "Auth Token" field
- It may show as dots `••••••••` for security
- Click **"Show Token"** or similar button
- Now you'll see the actual string
- Copy (Ctrl+C)
- Paste into `.env` file

```env
TWILIO_TOKEN=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
              ↑ Long string, keep it secret!
```

---

### **🔴 Credential #3: TWILIO_FROM (Your Twilio Phone Number)**

**What it is:** The phone number that will SEND SMS to patients

**Where to find it:**
1. In Twilio console, look for left sidebar menu
2. Click **"Phone Numbers"** or **"Explore Products"** → **"Phone Numbers"**
3. You'll see your assigned phone number

```
┌─────────────────────────────┐
│ MANAGE PHONE NUMBERS        │
│ ───────────────────────────│
│                             │
│ Active Numbers:             │
│ • +1 (555) 123-4567        │  ← Your Twilio number
│   (Assigned to your account)│
│                             │
└─────────────────────────────┘
```

**Format it correctly:**
- Twilio numbers are in format: `+1 (555) 123-4567`
- **Remove spaces and parentheses:** `+15551234567`
- Keep the **+1** (country code for US)
- Or for India: `+91 9876543210` → `+919876543210`

**Copy it:**
```env
TWILIO_FROM=+15551234567
            ↑ Format: +[country code][number]
            ↑ No spaces or parentheses!
```

---

## **📝 STEP 3: Edit Your `.env` File**

**Location:** `c:\Users\vishn\OneDrive\Desktop\healthcardsystem\.env`

### **Before (Template):**
```env
TWILIO_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_TOKEN=your_auth_token_here_example
TWILIO_FROM=+1234567890
OTP_DEBUG=true
```

### **After (Your Real Credentials):**
```env
TWILIO_SID=AC1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6
TWILIO_TOKEN=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
TWILIO_FROM=+15551234567
OTP_DEBUG=true
```

---

## **🚀 STEP 4: Start Your System**

### **Terminal 1: Start Flask Backend**

```powershell
cd "C:\Users\vishn\OneDrive\Desktop\healthcardsystem"

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start OTP server (reads credentials from .env)
python otp_server.py
```

**Expected output:**
```
 * Running on http://0.0.0.0:5000
 * WARNING: This is a development server. Do not use it in production.
 * Press CTRL+C to quit
```

✅ **Backend is now reading your `.env` file automatically!**

### **Terminal 2: Start Frontend**

```powershell
cd "C:\Users\vishn\OneDrive\Desktop\healthcardsystem"

python -m http.server 8000
```

### **Terminal 3: Open Browser**

```
http://localhost:8000/login.html
```

---

## **📱 STEP 5: How It Works - The SMS Flow**

### **Registration Form → SMS Delivery**

```
┌─────────────────────────────────────────────────────────┐
│ PATIENT FILLS REGISTRATION FORM                         │
├─────────────────────────────────────────────────────────┤
│ Name: John Doe                                          │
│ Mobile: +91 9876543210                                  │
│ Email: john@gmail.com                                   │
│ Blood: O+                                               │
│                                                         │
│ [REGISTER BUTTON]                                       │
└─────────────────────────────────────────────────────────┘
                          ↓
                   POST /send_otp
                   (to backend)
                          ↓
┌─────────────────────────────────────────────────────────┐
│ BACKEND (otp_server.py) RECEIVES REQUEST                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 1. Read from .env file:                                │
│    TWILIO_SID = AC1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6     │
│    TWILIO_TOKEN = a1b2c3d4e5f6g7h8i9...                │
│    TWILIO_FROM = +15551234567                           │
│                                                         │
│ 2. Generate random OTP: 654321                          │
│                                                         │
│ 3. Save OTP to database                                │
│                                                         │
│ 4. Call send_sms_twilio("+91 9876543210", "654321")   │
│                                                         │
│ 5. Create Twilio client with credentials:              │
│    client = Client(TWILIO_SID, TWILIO_TOKEN)           │
│                                                         │
│ 6. Send SMS:                                            │
│    From: +15551234567 (TWILIO_FROM)                    │
│    To: +91 9876543210 (patient's number)               │
│    Message: "Your MediLink OTP: 654321"                │
│                                                         │
└─────────────────────────────────────────────────────────┘
                          ↓
                    TWILIO SERVERS
                     (Twilio sends
                      the SMS to patient)
                          ↓
┌─────────────────────────────────────────────────────────┐
│ PATIENT'S PHONE RECEIVES SMS                            │
├─────────────────────────────────────────────────────────┤
│ From: +15551234567                                      │
│ Message: "Your MediLink OTP: 654321"                    │
│                                                         │
│ ✅ SMS Received!                                         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ PATIENT ENTERS OTP IN APP                               │
├─────────────────────────────────────────────────────────┤
│ Enter OTP: [654321]                                     │
│                                                         │
│ [VERIFY OTP]                                            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ BACKEND VERIFIES OTP                                    │
├─────────────────────────────────────────────────────────┤
│ 1. Check if OTP matches database                        │
│ 2. Check if OTP expired (must be within 10 min)         │
│ 3. Check if OTP already used (one-time only)            │
│ 4. Mark OTP as "used"                                   │
│                                                         │
│ ✅ OTP Valid!                                            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ GENERATE & RETURN HEALTH CARD                           │
├─────────────────────────────────────────────────────────┤
│ Health ID: 1701072123456654321                          │
│ Issued On: 27/11/2025                                   │
│ Renewal On: 27/11/2035                                  │
│ QR Code: [■■■■■■■■■■■■■■■■]                           │
│                                                         │
│ ✅ Card Displayed!                                       │
└─────────────────────────────────────────────────────────┘
```

---

## **🔍 How `.env` Variables Are Used**

### **Backend Code:**

**File:** `otp_server.py` (line 131-136)

```python
def send_sms_twilio(to_number, otp):
    # READS FROM .env FILE (automatically via python-dotenv)
    twilio_sid = os.getenv('TWILIO_SID')        # Gets: ACxxxxxxx
    twilio_token = os.getenv('TWILIO_TOKEN')    # Gets: a1b2c3d4...
    twilio_from = os.getenv('TWILIO_FROM')      # Gets: +15551234567
    
    # If any variable is missing, SMS won't send
    if not twilio_sid or not twilio_token or not twilio_from:
        logging.info('Twilio not configured')
        return False, 'Credentials missing'
    
    # Creates Twilio client using credentials
    from twilio.rest import Client
    client = Client(twilio_sid, twilio_token)
    
    # Sends SMS from TWILIO_FROM to patient's number
    message = client.messages.create(
        body=f'Your MediLink OTP: {otp}',
        from_=twilio_from,                      # +15551234567
        to=to_number                            # +91 9876543210
    )
    return True, message.sid
```

---

## **✅ VERIFICATION CHECKLIST**

Before testing, verify:

- [ ] You created Twilio account at https://www.twilio.com/try-twilio
- [ ] You verified your phone number (received SMS code)
- [ ] You logged into Twilio console: https://www.twilio.com/console
- [ ] You found your **Account SID** (starts with `AC`)
- [ ] You found your **Auth Token** (long string)
- [ ] You found your **Twilio Phone Number** (the one that will send SMS)
- [ ] You edited `.env` file with all three credentials
- [ ] You saved `.env` file (Ctrl+S)
- [ ] You started Flask backend: `python otp_server.py`
- [ ] Backend shows: "Running on http://0.0.0.0:5000"
- [ ] You started HTTP server: `python -m http.server 8000`
- [ ] You opened: http://localhost:8000/login.html

---

## **🧪 TEST IT NOW**

### **Fill Registration Form:**
```
Name: Your Name
Mobile: Your actual phone number (e.g., +91 9876543210)
Email: your@gmail.com
Blood: O+
```

### **Click "Register"**

### **Check Your Phone:**
You should see SMS within 5-10 seconds:
```
From: +15551234567
Message: "Your MediLink OTP: 654321"
```

### **If You Get SMS:**
✅ **Twilio is working!**
- Enter the 6-digit code in the app
- Click "Verify OTP"
- Get your health card!

### **If You DON'T Get SMS:**

**Check these (in order):**

1. **Is backend running?**
   ```powershell
   netstat -ano | findstr :5000
   ```
   Should show listening port. If not, backend crashed.

2. **Check Flask logs for errors:**
   - Look at Terminal 1 where you started Flask
   - Does it show red error messages?

3. **Is `.env` file saved?**
   - Edit `.env` and verify credentials are there
   - Restart Flask server

4. **Are credentials correct?**
   - Copy EXACTLY from Twilio console
   - No extra spaces
   - Account SID must start with `AC`

5. **Is phone number in correct format?**
   - Must have `+` and country code
   - Example: `+919876543210` (India)
   - Example: `+15551234567` (USA)

6. **Do you have trial credits?**
   - Check Twilio console for "Account Balance"
   - Should show $20 (free trial)

---

## **💰 TWILIO PRICING**

**Free Trial:**
- $20 free credits
- Good for ~100-150 SMS (India) or 1000+ SMS (USA)
- Expires after 30 days

**After Trial:**
- India SMS: ~₹1.50 per SMS (~$0.018)
- USA SMS: ~$0.0075 per SMS
- Worldwide: $0.0075-0.02 per SMS

Check: https://www.twilio.com/sms/pricing

---

## **📞 SUPPORT**

**Twilio Dashboard:** https://www.twilio.com/console

**Twilio Support:** https://support.twilio.com

**Your Trial Account:** Free $20 credits (enough for testing!)

---

## **🎉 YOU'RE READY!**

Once you fill in the `.env` file with real credentials, SMS will work automatically. The backend reads the `.env` file when it starts, so no code changes needed!
