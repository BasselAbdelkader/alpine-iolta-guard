# IOLTA Guard - Clean Project Structure

**Date:** November 12, 2025
**Status:** ✅ SINGLE SOURCE OF TRUTH - No Confusion

---

## 📁 ACTIVE SOURCE CODE (Used by Docker)

### **1. Backend Source**
```
/home/amin/Projects/ve_demo/backend/
```

**Contains:**
- Django 5.1.3 application
- QuickBooks CSV import modules
- Pagination settings (max_page_size=10000)
- All 30 bug fixes applied
- Client/Case/Transaction/Vendor models

**Used by:** `Dockerfile.alpine.backend` (line 135)
```dockerfile
COPY backend/ /app/
```

---

### **2. Frontend Source**
```
/home/amin/Projects/ve_demo/frontend/
```

**Contains:**
- HTML pages (clients.html, vendors.html, etc.)
- JavaScript files with pagination UI (clients.js, vendors.js, etc.)
- CSS stylesheets
- Nginx configuration

**Used by:** `Dockerfile.alpine.frontend`
```dockerfile
COPY frontend/ /usr/share/nginx/html/
```

---

## 🗄️ ARCHIVED CODE (Not Used - Backup Only)

### **3. Old Backend Archive**
```
/home/amin/Projects/ve_demo/trust_account_oldcode/
```

**Status:** ❌ NOT USED BY DOCKER (archived Nov 4, 2025)

**Purpose:**
- Backup of old code
- Reference if needed in future
- Not deployed to containers

---

## 🔧 BUILD PROCESS

### **How Docker Builds Images:**

1. **Backend Image:**
   ```bash
   docker-compose -f docker-compose.alpine.yml build backend
   ```
   - Reads: `Dockerfile.alpine.backend`
   - Copies: `/home/amin/Projects/ve_demo/backend/` → `/app/` in container
   - Result: `iolta-guard-backend-alpine:latest`

2. **Frontend Image:**
   ```bash
   docker-compose -f docker-compose.alpine.yml build frontend
   ```
   - Reads: `Dockerfile.alpine.frontend`
   - Copies: `/home/amin/Projects/ve_demo/frontend/` → `/usr/share/nginx/html/` in container
   - Result: `iolta-guard-frontend-alpine:latest`

---

## ✅ VERIFICATION

### **Confirm Single Source:**

**Check what Dockerfile uses:**
```bash
grep "COPY" Dockerfile.alpine.backend
# Output: COPY backend/ /app/  ✅
```

**Check last modification dates:**
```bash
ls -la | grep -E "backend|frontend|trust_account"
# backend/                 Nov 12 20:15  ← Active (today)
# frontend/                Nov 12 19:37  ← Active (today)
# trust_account_oldcode/   Nov  4 14:11  ← Archive (old)
```

---

## 📦 DEPLOYMENT PACKAGES

### **Current Package:**
- **File:** `iolta_alpine_images_PAGINATION_FIX.tar` (587 MB)
- **Built from:** `backend/` + `frontend/` (active source)
- **Includes:**
  - Pagination UI (50 records per page)
  - QuickBooks import
  - All 30 bug fixes
  - Clean database

### **Previous Package:**
- **File:** `iolta_alpine_images_COMPLETE_FINAL.tar` (587 MB)
- **Built from:** `backend/` + `frontend/` (active source)
- **Difference:** Used page_size=10000 (no pagination UI)

---

## 🎯 WHERE TO MAKE CHANGES

### **Backend Changes (Django/Python):**
**Edit:** `/home/amin/Projects/ve_demo/backend/`

**Examples:**
- API endpoints: `backend/apps/api/`
- Models: `backend/apps/clients/models.py`
- Pagination: `backend/apps/api/pagination.py`
- QuickBooks: `backend/apps/clients/utils/quickbooks_*.py`

**After changes:**
```bash
docker-compose -f docker-compose.alpine.yml build backend
docker-compose -f docker-compose.alpine.yml up -d backend
```

---

### **Frontend Changes (HTML/JS/CSS):**
**Edit:** `/home/amin/Projects/ve_demo/frontend/`

**Examples:**
- HTML pages: `frontend/html/clients.html`
- JavaScript: `frontend/js/clients.js`
- Styles: `frontend/css/main.css`
- Nginx routes: `frontend/nginx.conf`

**After changes:**
```bash
docker-compose -f docker-compose.alpine.yml build frontend
docker-compose -f docker-compose.alpine.yml up -d frontend
```

---

## 🚫 DO NOT USE

### **❌ trust_account_oldcode/**
- This directory is archived
- Docker does NOT use this
- Only kept as backup/reference
- **Do not make changes here** - they will not be deployed

---

## 📝 HISTORY: How We Got Here

### **Previous Situation (Confusing):**
```
ve_demo/
├── source/trust_account/    ← Newer code (QuickBooks)
├── trust_account/            ← Older code (no QuickBooks)
└── Dockerfile pointed to source/
```
**Problem:** Two codebases, unclear which was active

### **What Was Done (Cleanup):**
1. Renamed `source/trust_account/` → `backend/`
2. Updated Dockerfile to use `backend/`
3. Removed `source/` directory
4. Kept `trust_account/` as `trust_account_oldcode/` (archive)

### **Current Situation (Clean):**
```
ve_demo/
├── backend/                  ← ✅ Single active backend source
├── frontend/                 ← ✅ Single active frontend source
├── trust_account_oldcode/    ← Archive (not used)
└── Dockerfile points to backend/
```
**Result:** Clear, single source of truth

---

## 🎉 BENEFITS

### **Before Cleanup:**
- ❌ Two backend codebases (source/ vs trust_account/)
- ❌ Unclear which was active
- ❌ Fixes applied to wrong directory
- ❌ Docker building from incomplete code

### **After Cleanup:**
- ✅ One backend source: `backend/`
- ✅ One frontend source: `frontend/`
- ✅ Clear directory names
- ✅ Docker builds from correct code
- ✅ All fixes properly applied
- ✅ Old code safely archived

---

## 📋 QUICK REFERENCE

| Directory | Status | Used By Docker | Purpose |
|-----------|--------|----------------|---------|
| `backend/` | ✅ ACTIVE | YES | Django backend source |
| `frontend/` | ✅ ACTIVE | YES | Frontend HTML/JS/CSS |
| `trust_account_oldcode/` | ❌ ARCHIVE | NO | Old code backup |

**Rule:** Only edit `backend/` and `frontend/` - these are deployed!

---

**Created:** November 12, 2025
**Last Updated:** November 12, 2025
**Status:** ✅ CLEAN - Single Source of Truth Established
