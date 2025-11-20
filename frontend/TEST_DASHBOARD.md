# Testing Dashboard (Page 1/8)

## ✅ What's Complete

**Backend:**
- ✅ CORS enabled
- ✅ JWT authentication enabled
- ✅ Dashboard API endpoint: `http://localhost:8002/api/v1/dashboard/`

**Frontend:**
- ✅ Login page: `frontend/html/login.html`
- ✅ Dashboard page: `frontend/html/dashboard.html`
- ✅ API client library: `frontend/js/api-client.js`
- ✅ Dashboard logic: `frontend/js/dashboard.js`

---

## 🧪 How to Test

### Step 1: Start Django Backend (if not running)

```bash
docker-compose up -d
```

Wait 10 seconds for the backend to start.

### Step 2: Start Frontend Server

```bash
cd frontend
python3 serve.py
```

You should see:
```
✅ Frontend server running at http://localhost:8003/
📂 Open: http://localhost:8003/html/login.html
```

### Step 3: Test Login

1. Open browser: **http://localhost:8003/html/login.html**
2. Login with:
   - Username: `admin`
   - Password: `admin` (or your password)
3. Should redirect to dashboard automatically

### Step 4: Test Dashboard

After login, you should see:

**✅ Expected Results:**

1. **Top Header:**
   - Law firm name and address

2. **4 Metric Cards:**
   - Trust Balance (cyan/blue card)
   - Bank Register (green card if balanced, red if not)
   - Clients with Funds (green card with count)
   - Next Reconciliation (purple card with date)

3. **Trust Health Assessment:**
   - Health score (0-100) with colored circle
   - Status badge (EXCELLENT/GOOD/FAIR/POOR/CRITICAL)
   - Warnings count
   - Issues count

4. **Top 5 Clients Table:**
   - Client names
   - Balances formatted as currency
   - Last activity dates
   - Case numbers listed below each client

5. **Stale Clients Table:**
   - Clients with no deposits in 2+ years
   - Their balances
   - Last deposit dates

6. **Outstanding Checks Table:**
   - Check numbers
   - Date issued
   - Payee names
   - Amounts (in parentheses)
   - Days outstanding with red badges

7. **Sidebar:**
   - Law firm info at top
   - Navigation links (Dashboard active)
   - User name at bottom
   - Logout button

---

## 🐛 If Something's Wrong

### Error: "CORS policy blocked"
```bash
# Check Django settings
grep CORS_ALLOWED_ORIGINS trust_account/trust_account_project/settings.py
# Should include: "http://localhost:8003"
```

### Error: "401 Unauthorized"
```bash
# Test JWT endpoint
curl -X POST http://localhost:8002/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

### Error: "Dashboard data not loading"
Open browser DevTools (F12) → Console tab → Look for errors

### Error: "Cannot connect to backend"
```bash
# Check Django is running
curl http://localhost:8002/admin/login/
# Should return HTML (not error)
```

---

## 📊 What to Check

**Visual Comparison:**
- [ ] Cards have same colors as original
- [ ] Trust Balance shows in cyan/blue
- [ ] Bank Register green if balanced, red if not
- [ ] Health score shows with colored circle
- [ ] Tables show data properly formatted
- [ ] Sidebar looks identical

**Functionality:**
- [ ] Login redirects to dashboard
- [ ] Logout button works
- [ ] All numbers format correctly (currency with commas)
- [ ] Negative numbers show in parentheses
- [ ] Dates format as MM/DD/YYYY

**Data Accuracy:**
- [ ] Trust Balance matches current Django dashboard
- [ ] Bank Register matches current Django dashboard
- [ ] Client counts match
- [ ] All client names appear correctly

---

## 📸 Take Screenshots

If you find issues, take screenshots of:
1. Browser console (F12 → Console tab)
2. Network tab showing failed requests
3. The page showing the error

---

## ✅ When Done Testing

Tell me:
1. ✅ "Dashboard works perfectly" - Move to Clients page
2. ⚠️ "Found issues" - Share screenshots and I'll fix
3. ❌ "Not working" - Share error messages

---

**Next Page:** Clients (Page 2/8)
