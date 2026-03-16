# 🚨 Backend Not Responsive - Troubleshooting Guide

## 🔧 Quick Fix Steps:

### 1. **Start Backend Properly**
```bash
# Method 1: Use the fixed startup script
double-click: start_server_fixed.bat

# Method 2: Manual start
pip install flask flask-cors
python VANIE.py

# Method 3: Alternative start
python -m flask run --host=0.0.0.0 --port=5000
```

### 2. **Check if Backend is Running**
Open browser and test these URLs:
- **Health Check:** http://localhost:5000/health
- **API Test:** http://localhost:5000/api/chat

### 3. **Test with Test Script**
```bash
python test_backend.py
```

## 🐛 Common Issues & Solutions:

### **Issue: "python not recognized"**
**Solution:**
1. Install Python from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Restart command prompt

### **Issue: Port 5000 already in use**
**Solution:**
1. Close other Python processes
2. Use different port: `python VANIE.py --port 5001`
3. Kill process: `taskkill /f /im python.exe`

### **Issue: ModuleNotFoundError**
**Solution:**
```bash
pip install flask flask-cors
```

### **Issue: Backend starts but no response**
**Solution:**
1. Check firewall settings
2. Try `http://127.0.0.1:5000` instead of `http://localhost:5000`
3. Disable debug mode in VANIE.py: `app.run(debug=False)`

### **Issue: CORS errors**
**Solution:**
1. Make sure `flask-cors` is installed
2. Check if CORS is properly configured in VANIE.py

## 📋 Verification Steps:

### ✅ **Step 1: Backend Status Check**
1. Run `start_server_fixed.bat`
2. Look for: "Server will be available at: http://localhost:5000"
3. Should see: "Running on http://0.0.0.0:5000"

### ✅ **Step 2: Health Check**
Open browser: http://localhost:5000/health
Should see:
```json
{
  "status": "healthy",
  "service": "VANIE AI Backend"
}
```

### ✅ **Step 3: API Test**
Open browser: http://localhost:5000/api/chat
Send POST request with:
```json
{
  "message": "hello",
  "session_id": "test"
}
```

### ✅ **Step 4: Frontend Connection**
1. Open VANIE.html in browser
2. Type "hello" and send
3. Should get AI response from backend

## 🚀 **Expected Output:**

When backend starts successfully, you should see:
```
🚀 VANIE AI Backend Server Starting...
📡 Server will be available at: http://localhost:5000
🔗 API Endpoint: http://localhost:5000/api/chat
 * Serving Flask app 'VANIE'
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

## 🆘 **Still Not Working?**

1. **Check Python Version:** `python --version` (should be 3.7+)
2. **Reinstall Dependencies:** 
   ```bash
   pip uninstall flask flask-cors
   pip install flask flask-cors
   ```
3. **Try Different Port:** Edit VANIE.py, change `port=5000` to `port=5001`
4. **Check Antivirus:** Temporarily disable antivirus/firewall
5. **Run as Administrator:** Right-click command prompt → "Run as administrator"

## 📞 **Need More Help?**

If issues persist:
1. Check error messages in terminal
2. Run `python test_backend.py` for detailed diagnostics
3. Make sure VANIE.py file is not corrupted

**Backend should be running on http://localhost:5000 within 30 seconds! 🚀**
