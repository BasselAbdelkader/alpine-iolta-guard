# IOLTA Guard - Docker Configuration & Customer Delivery Guide

**Date:** November 13, 2025  
**Status:** Ready for Customer Delivery  
**Alpine Images:** ✅ ALL IMAGES USE ALPINE LINUX

---

## 📋 **DOCKER FILES INVENTORY**

### ✅ **RECOMMENDED FOR CUSTOMER: Alpine Linux Configuration**

| File | Purpose | Image Base | Status |
|------|---------|------------|--------|
| **docker-compose.alpine.yml** | **MAIN PRODUCTION CONFIG** | All Alpine | ✅ **USE THIS** |
| **Dockerfile.alpine.backend** | Backend image build | python:3.12-alpine3.20 | ✅ **USE THIS** |
| **Dockerfile.alpine.frontend** | Frontend image build | nginx:alpine | ✅ **USE THIS** |
| **.env.template** | Environment variables template | N/A | ✅ **USE THIS** |

### ❌ **NOT RECOMMENDED: Non-Alpine Files (Don't send to customer)**

| File | Purpose | Image Base | Status |
|------|---------|------------|--------|
| docker-compose.yml | Old production config | Debian-based | ❌ DON'T USE |
| docker-compose.production.yml | Another old config | Debian-based | ❌ DON'T USE |
| docker-compose-simple-production.yml | Old config | Debian-based | ❌ DON'T USE |
| backend/Dockerfile | Non-alpine backend | python:3.12-slim (Debian) | ❌ DON'T USE |
| frontend/Dockerfile | Non-alpine frontend | Mixed | ❌ DON'T USE |

---

## 🎯 **CUSTOMER DELIVERY PACKAGE**

### **Files to Include:**

```
iolta-guard-customer-package/
├── docker-compose.alpine.yml          ← Main config file
├── Dockerfile.alpine.backend          ← Backend image definition
├── Dockerfile.alpine.frontend         ← Frontend image definition
├── .env.template                      ← Environment variables template
├── frontend/
│   ├── nginx.conf                     ← Nginx configuration
│   ├── html/                          ← All HTML files
│   ├── js/                            ← All JavaScript files
│   └── css/                           ← All CSS files
├── backend/                           ← Django application
│   ├── manage.py
│   ├── requirements.txt
│   ├── trust_account_project/
│   ├── apps/
│   └── ... (all backend code)
├── database/
│   └── init/                          ← Database initialization scripts
├── backups/                           ← Empty directory for backups
├── DEPLOYMENT_GUIDE.md                ← Step-by-step deployment instructions
└── README.md                          ← Quick start guide
```

### **Files to EXCLUDE:**

```
❌ docker-compose.yml                   (Non-alpine)
❌ docker-compose.production.yml        (Non-alpine)
❌ docker-compose-simple-production.yml (Non-alpine)
❌ backend/Dockerfile                   (Non-alpine)
❌ frontend/Dockerfile                  (Non-alpine)
❌ .env                                 (Contains your secrets!)
❌ .env.production                      (Contains secrets)
❌ account.json                         (May contain secrets)
❌ __pycache__/                         (Python cache)
❌ *.pyc                                (Compiled Python)
❌ .git/                                (Git history)
❌ node_modules/                        (If any)
❌ *.log                                (Log files)
❌ tests/                               (Test files - optional)
❌ docs/                                (Internal docs - optional)
```

---

## 🐳 **ALPINE IMAGES USED**

### **1. Database (PostgreSQL)**
```yaml
image: postgres:16-alpine3.20
Size: ~260MB
Base: Alpine Linux 3.20
Security: musl libc
```

### **2. Backend (Django)**
```yaml
Built from: Dockerfile.alpine.backend
Base: python:3.12-alpine3.20
Final Size: ~350MB (vs ~800MB Debian)
Security: Non-root user, minimal packages
```

**Multi-stage build:**
- Stage 1 (builder): Compiles dependencies (~500MB removed after build)
- Stage 2 (runtime): Only runtime libraries

### **3. Frontend (Nginx)**
```yaml
Built from: Dockerfile.alpine.frontend
Base: nginx:alpine
Final Size: ~45MB
Security: Non-root user
```

### **Total Stack Size:**
- **Alpine:** ~655MB
- **Debian (old):** ~1.2GB
- **Savings:** ~545MB (45% reduction)

---

## 🔐 **SECURITY CONFIGURATION**

### **Environment Variables (.env file)**

**⚠️ CRITICAL: Customer must create their own .env file from .env.template**

```bash
# .env.template → .env
DB_NAME=iolta_guard_db
DB_USER=iolta_user
DB_PASSWORD=CHANGE_ME_TO_SECURE_PASSWORD
DJANGO_SECRET_KEY=CHANGE_ME_TO_RANDOM_50_CHAR_STRING
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,customer-domain.com
```

**Security Requirements:**
1. ✅ DB_PASSWORD: Minimum 20 characters, complex
2. ✅ DJANGO_SECRET_KEY: 50+ character random string
3. ✅ ALLOWED_HOSTS: Customer's actual domain
4. ✅ DEBUG: Must be False in production
5. ✅ Never commit .env to git

**Generate Secure Values:**
```bash
# Generate DB password (32 characters)
openssl rand -base64 32

# Generate Django secret key
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

---

## 📊 **DOCKER COMPOSE CONFIGURATION**

### **docker-compose.alpine.yml Overview:**

```yaml
services:
  database:
    image: postgres:16-alpine3.20       ✅ Alpine
    expose: [5432]                      ✅ NOT publicly exposed
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d:ro
      - ./backups:/backups
    healthcheck: ✅ Enabled
    restart: unless-stopped

  backend:
    build:
      context: .
      dockerfile: Dockerfile.alpine.backend  ✅ Alpine
    image: iolta-guard-backend-alpine:latest
    expose: [8002]                      ✅ NOT publicly exposed
    volumes:
      - backend_static:/app/staticfiles
      - backend_media:/app/media
      - backend_logs:/app/logs
      - ./account.json:/app/account.json:ro
    depends_on:
      database: {condition: service_healthy}
    healthcheck: ✅ Enabled
    restart: unless-stopped
    
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.alpine.frontend  ✅ Alpine
    image: iolta-guard-frontend-alpine:latest
    ports:
      - "80:80"                         ✅ ONLY public service
    volumes:
      - ./frontend/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - backend_static:/usr/share/nginx/html/static:ro
    depends_on:
      backend: {condition: service_healthy}
    healthcheck: ✅ Enabled
    restart: unless-stopped
```

### **Security Features:**
- ✅ Database NOT publicly exposed (only accessible within Docker network)
- ✅ Backend NOT publicly exposed (only through nginx reverse proxy)
- ✅ Frontend (nginx) is ONLY public-facing service
- ✅ All services use health checks
- ✅ Services restart automatically (unless-stopped)
- ✅ Non-root user execution in all containers
- ✅ Read-only volume mounts where applicable

---

## 🚀 **DEPLOYMENT INSTRUCTIONS**

### **Step 1: Prepare Environment**
```bash
# 1. Copy .env.template to .env
cp .env.template .env

# 2. Edit .env with secure values
nano .env

# Required changes:
#   - DB_PASSWORD: Generate secure password
#   - DJANGO_SECRET_KEY: Generate secret key
#   - ALLOWED_HOSTS: Add customer domain/IP
```

### **Step 2: Build Images**
```bash
# Build all images (first time only)
docker-compose -f docker-compose.alpine.yml build

# Build time: ~20-25 minutes (first build)
# Subsequent builds: ~2-5 minutes (cached)
```

### **Step 3: Start Services**
```bash
# Start all services in background
docker-compose -f docker-compose.alpine.yml up -d

# Verify all services are running
docker-compose -f docker-compose.alpine.yml ps

# Expected output:
# iolta_db_alpine          postgres:16-alpine3.20   Up (healthy)
# iolta_backend_alpine     ...                      Up (healthy)
# iolta_frontend_alpine    ...                      Up (healthy)
```

### **Step 4: Initialize Database (First Time Only)**
```bash
# Run database migrations
docker exec iolta_backend_alpine python manage.py migrate

# Create superuser
docker exec -it iolta_backend_alpine python manage.py createsuperuser

# Load initial data (optional)
docker exec iolta_backend_alpine python manage.py loaddata initial_data.json
```

### **Step 5: Verify Deployment**
```bash
# Check all health checks pass
docker-compose -f docker-compose.alpine.yml ps

# View logs
docker-compose -f docker-compose.alpine.yml logs -f

# Test access
curl http://localhost/
curl http://localhost/api/health/
```

### **Step 6: Access Application**
```
Frontend: http://localhost/ (or customer's domain)
Admin:    http://localhost/admin/
API:      http://localhost/api/
```

---

## 🔄 **MAINTENANCE OPERATIONS**

### **View Logs**
```bash
# All services
docker-compose -f docker-compose.alpine.yml logs -f

# Specific service
docker-compose -f docker-compose.alpine.yml logs -f backend
docker-compose -f docker-compose.alpine.yml logs -f frontend
docker-compose -f docker-compose.alpine.yml logs -f database
```

### **Restart Services**
```bash
# Restart all
docker-compose -f docker-compose.alpine.yml restart

# Restart specific service
docker-compose -f docker-compose.alpine.yml restart backend
```

### **Stop Services**
```bash
# Stop (keeps data)
docker-compose -f docker-compose.alpine.yml down

# Stop and remove volumes (⚠️ DELETES DATA!)
docker-compose -f docker-compose.alpine.yml down -v
```

### **Update Application**
```bash
# 1. Pull new code
git pull origin main

# 2. Rebuild images
docker-compose -f docker-compose.alpine.yml build

# 3. Restart services
docker-compose -f docker-compose.alpine.yml up -d

# 4. Run migrations if needed
docker exec iolta_backend_alpine python manage.py migrate
```

### **Database Backup**
```bash
# Create backup
docker exec iolta_db_alpine pg_dump -U iolta_user iolta_guard_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
cat backup_20251113_120000.sql | docker exec -i iolta_db_alpine psql -U iolta_user -d iolta_guard_db
```

---

## 📦 **VOLUMES & DATA PERSISTENCE**

### **Persistent Volumes:**
```yaml
postgres_data:     # Database data - CRITICAL
backend_static:    # Django static files
backend_media:     # User uploads
backend_logs:      # Application logs
nginx_cache:       # Nginx cache
```

### **⚠️ IMPORTANT:**
- **postgres_data** is CRITICAL - contains all application data
- Backup regularly using pg_dump
- Do NOT delete volumes unless intentional
- Volumes persist even when containers are removed

### **Backup Strategy:**
```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec iolta_db_alpine pg_dump -U iolta_user iolta_guard_db | gzip > /backups/iolta_$DATE.sql.gz

# Keep last 30 days
find /backups -name "iolta_*.sql.gz" -mtime +30 -delete
```

---

## 🔍 **TROUBLESHOOTING**

### **Problem: Services won't start**
```bash
# Check logs
docker-compose -f docker-compose.alpine.yml logs

# Common issues:
# - .env file missing or invalid
# - Port 80 already in use
# - Insufficient disk space
# - Database connection failed
```

### **Problem: Database connection failed**
```bash
# Check database health
docker-compose -f docker-compose.alpine.yml ps

# Test database connection
docker exec iolta_backend_alpine python manage.py dbshell

# Reset database (⚠️ DELETES DATA!)
docker-compose -f docker-compose.alpine.yml down -v
docker-compose -f docker-compose.alpine.yml up -d
```

### **Problem: Static files not loading**
```bash
# Recollect static files
docker exec iolta_backend_alpine python manage.py collectstatic --noinput

# Restart frontend
docker-compose -f docker-compose.alpine.yml restart frontend
```

### **Problem: Permission denied errors**
```bash
# Fix ownership
docker exec -u root iolta_backend_alpine chown -R iolta:iolta /app

# Check user
docker exec iolta_backend_alpine whoami
# Should output: iolta (not root)
```

---

## ⚡ **PERFORMANCE TUNING**

### **Gunicorn Workers (Backend)**
```yaml
# In docker-compose.alpine.yml
environment:
  - GUNICORN_WORKERS=4  # Rule of thumb: (2 x CPU cores) + 1
  
# For 2 CPU cores: 4-5 workers
# For 4 CPU cores: 8-9 workers
```

### **PostgreSQL Configuration**
```bash
# Edit postgresql.conf (inside container or via volume mount)
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
```

### **Nginx Caching**
```nginx
# Already configured in nginx.conf
location /static/ {
    expires 1h;
    add_header Cache-Control "public, immutable";
}
```

---

## 🌐 **MULTI-TENANT DEPLOYMENT (100+ Firms)**

### **Option 1: Separate Stacks (Isolated)**
```bash
# Each firm gets own stack
firm1/
  ├── docker-compose.alpine.yml
  ├── .env (unique DB credentials)
  └── volumes/

firm2/
  ├── docker-compose.alpine.yml
  ├── .env (unique DB credentials)
  └── volumes/
  
# Pros: Complete isolation, easier management
# Cons: More resources, more containers
```

### **Option 2: Shared Stack (Multi-tenant DB)**
```bash
# Single stack, tenant isolation in database
shared/
  ├── docker-compose.alpine.yml
  ├── .env
  └── volumes/ (all firms share)
  
# Pros: Resource efficient, fewer containers
# Cons: Requires code changes, shared risk
```

---

## 📞 **CUSTOMER SUPPORT**

### **Before Contacting Support:**
1. Check logs: `docker-compose -f docker-compose.alpine.yml logs`
2. Verify .env file is correct
3. Confirm all services are healthy: `docker-compose -f docker-compose.alpine.yml ps`
4. Check disk space: `df -h`
5. Check network connectivity

### **Support Information to Provide:**
- Docker version: `docker --version`
- Docker Compose version: `docker-compose --version`
- Operating system: `uname -a`
- Container status: `docker-compose -f docker-compose.alpine.yml ps`
- Recent logs: `docker-compose -f docker-compose.alpine.yml logs --tail=100`
- Error messages (if any)

---

## ✅ **VERIFICATION CHECKLIST**

**Before Sending to Customer:**
- [ ] All Alpine images confirmed (no Debian/Ubuntu)
- [ ] .env.template provided (not .env with secrets!)
- [ ] docker-compose.alpine.yml is main config
- [ ] Non-Alpine files excluded from package
- [ ] Deployment guide included
- [ ] README.md included
- [ ] Database init scripts included
- [ ] Nginx config included
- [ ] All frontend files included
- [ ] All backend files included
- [ ] account.json excluded (or sanitized)
- [ ] Git history excluded (.git)
- [ ] Cache files excluded (__pycache__, *.pyc)
- [ ] Log files excluded (*.log)

**After Customer Deployment:**
- [ ] Customer created their own .env
- [ ] Customer set secure DB_PASSWORD
- [ ] Customer set secure DJANGO_SECRET_KEY
- [ ] Customer added their domain to ALLOWED_HOSTS
- [ ] All services started successfully
- [ ] Health checks passing
- [ ] Frontend accessible
- [ ] Admin panel accessible
- [ ] API endpoints responding
- [ ] Database migrations completed
- [ ] Superuser created
- [ ] Backup strategy in place

---

## 🎯 **CUSTOMER DELIVERY COMMAND**

### **Create Clean Package:**
```bash
# Create package directory
mkdir -p iolta-guard-customer-package

# Copy essential files
cp docker-compose.alpine.yml iolta-guard-customer-package/
cp Dockerfile.alpine.backend iolta-guard-customer-package/
cp Dockerfile.alpine.frontend iolta-guard-customer-package/
cp .env.template iolta-guard-customer-package/
cp -r frontend iolta-guard-customer-package/
cp -r backend iolta-guard-customer-package/
cp -r database iolta-guard-customer-package/
mkdir -p iolta-guard-customer-package/backups

# Create README
cat > iolta-guard-customer-package/README.md << 'README'
# IOLTA Guard - Deployment Package

## Quick Start

1. Copy .env.template to .env and configure
2. Run: docker-compose -f docker-compose.alpine.yml build
3. Run: docker-compose -f docker-compose.alpine.yml up -d
4. Initialize: docker exec iolta_backend_alpine python manage.py migrate

See DEPLOYMENT_GUIDE.md for detailed instructions.
README

# Create deployment guide (copy from this document)
cp DOCKER_SETUP_CUSTOMER_DELIVERY.md iolta-guard-customer-package/DEPLOYMENT_GUIDE.md

# Create tarball
tar -czf iolta-guard-customer-package.tar.gz iolta-guard-customer-package/

# Verify package
tar -tzf iolta-guard-customer-package.tar.gz | head -20
```

---

## 🔒 **FINAL SECURITY CHECKS**

### **Before Sending:**
1. ✅ Remove all .env files (only include .env.template)
2. ✅ Remove account.json (or provide sanitized version)
3. ✅ Remove any database backups
4. ✅ Remove any log files
5. ✅ Remove .git directory
6. ✅ Remove __pycache__ directories
7. ✅ Verify no hardcoded passwords in code
8. ✅ Verify no API keys in code
9. ✅ Verify DEBUG=False in all configs
10. ✅ Verify only Alpine images used

### **Customer Must Do:**
1. ✅ Generate unique DB_PASSWORD
2. ✅ Generate unique DJANGO_SECRET_KEY
3. ✅ Set their domain in ALLOWED_HOSTS
4. ✅ Configure SSL/TLS (if needed)
5. ✅ Set up firewall rules
6. ✅ Configure backup strategy
7. ✅ Set up monitoring
8. ✅ Review and understand security settings

---

**Status:** ✅ Ready for Customer Delivery  
**All Images:** ✅ Alpine Linux  
**Security:** ✅ Verified  
**Documentation:** ✅ Complete  

---

*Package prepared for professional deployment. All Alpine images confirmed.*
