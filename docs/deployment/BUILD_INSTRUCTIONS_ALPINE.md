# IOLTA Guard - Alpine Linux Build Instructions

**Created:** November 7, 2025
**Target:** Multi-tenant deployment (100+ legal firms)
**Architecture:** Alpine Linux 3.20 + Python 3.12 + PostgreSQL 16
**Security:** musl libc, minimal attack surface

---

## Prerequisites

### Required Software

| Software | Minimum Version | Check Command |
|----------|----------------|---------------|
| Docker | 20.10+ | `docker --version` |
| Docker Compose | 2.0+ | `docker-compose --version` |
| Git | 2.0+ | `git --version` |

### System Requirements

**Minimum (Development/Testing):**
- CPU: 2 cores
- RAM: 4GB
- Disk: 20GB free space

**Recommended (Production - 100+ firms):**
- CPU: 8+ cores
- RAM: 16GB+
- Disk: 100GB+ SSD
- Network: 100Mbps+

---

## Step 1: Environment Configuration

### 1.1 Copy Environment Template

```bash
cd /home/amin/Projects/ve_demo
cp .env.template .env
```

### 1.2 Generate Secure Credentials

**Database Password:**
```bash
openssl rand -base64 32
```

**Django Secret Key:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 1.3 Edit Environment File

```bash
nano .env
```

**Required Changes:**
```env
# Database Configuration
DB_NAME=iolta_guard_db
DB_USER=iolta_user
DB_PASSWORD=<PASTE_GENERATED_PASSWORD_HERE>

# Django Configuration
DJANGO_SECRET_KEY=<PASTE_GENERATED_SECRET_KEY_HERE>
DEBUG=False

# Server Configuration
ALLOWED_HOSTS=localhost,127.0.0.1,138.68.109.92
PRODUCTION_DOMAIN=138.68.109.92
```

**Save and exit:** Ctrl+X, Y, Enter

### 1.4 Verify Configuration

```bash
# Check .env file exists
ls -la .env

# Verify no placeholder values remain
grep "CHANGE_ME" .env
# Should return nothing
```

---

## Step 2: Build Docker Images

### 2.1 Build All Images (First Time)

```bash
# Build with verbose output
docker-compose -f docker-compose.alpine.yml build --no-cache --progress=plain

# Expected build time: 20-25 minutes (first build)
```

### 2.2 Build Individual Services (If Needed)

```bash
# Build only backend
docker-compose -f docker-compose.alpine.yml build backend

# Build only frontend
docker-compose -f docker-compose.alpine.yml build frontend

# Database uses pre-built image (no build needed)
```

### 2.3 Verify Images Built Successfully

```bash
docker images | grep iolta-guard

# Expected output:
# iolta-guard-backend-alpine    latest    <IMAGE_ID>    <SIZE>    <TIME>
# iolta-guard-frontend-alpine   latest    <IMAGE_ID>    <SIZE>    <TIME>
```

**Expected Image Sizes:**
- Backend: ~300-400MB
- Frontend: ~40-50MB
- Database: ~260MB (pre-built)

---

## Step 3: Start Services

### 3.1 Start All Services

```bash
# Start in detached mode (background)
docker-compose -f docker-compose.alpine.yml up -d

# Expected startup time: 1-2 minutes
```

### 3.2 Monitor Startup

```bash
# Watch logs in real-time
docker-compose -f docker-compose.alpine.yml logs -f

# Or watch specific service
docker-compose -f docker-compose.alpine.yml logs -f backend
```

**Expected Log Sequence:**
1. Database starts and initializes (30-60 seconds)
2. Database runs SQL init scripts from `database/init/`
3. Backend waits for database health check
4. Backend runs collectstatic
5. Backend starts Gunicorn
6. Frontend starts Nginx

### 3.3 Verify All Services Running

```bash
docker-compose -f docker-compose.alpine.yml ps
```

**Expected Output:**
```
NAME                      STATUS              PORTS
iolta_db_alpine          Up (healthy)        5432/tcp
iolta_backend_alpine     Up (healthy)        8002/tcp
iolta_frontend_alpine    Up                  0.0.0.0:80->80/tcp
```

All services should show "Up" status, with health checks passing.

---

## Step 4: Database Initialization

### 4.1 Automatic Initialization

The database automatically initializes on first startup:

```bash
# Check if initialization completed
docker-compose -f docker-compose.alpine.yml logs database | grep "database system is ready"
```

### 4.2 Verify Database Content

```bash
# Connect to database
docker-compose -f docker-compose.alpine.yml exec database psql -U iolta_user -d iolta_guard_db

# List tables
\dt

# Count records (example)
SELECT COUNT(*) FROM clients_client;
SELECT COUNT(*) FROM bank_accounts_transaction;

# Exit psql
\q
```

### 4.3 Manual Database Import (If Needed)

```bash
# Copy SQL file to container
docker cp /path/to/backup.sql iolta_db_alpine:/tmp/

# Import
docker-compose -f docker-compose.alpine.yml exec database \
  psql -U iolta_user -d iolta_guard_db -f /tmp/backup.sql
```

---

## Step 5: Verification & Testing

### 5.1 Health Checks

```bash
# Frontend (public)
curl http://localhost/

# API health endpoint (through frontend proxy)
curl http://localhost/api/health/

# Expected: {"status": "healthy"}
```

### 5.2 Backend Direct Check (Internal)

```bash
# From inside backend container
docker-compose -f docker-compose.alpine.yml exec backend curl http://localhost:8002/api/health/
```

### 5.3 Check Service Logs

```bash
# No errors should be present
docker-compose -f docker-compose.alpine.yml logs | grep -i error
docker-compose -f docker-compose.alpine.yml logs | grep -i warning
```

### 5.4 Resource Usage

```bash
# Check memory and CPU usage
docker stats

# Check disk usage
docker system df
```

---

## Step 6: Access Application

### 6.1 Web Browser Access

**Local:**
- Frontend: http://localhost/
- API: http://localhost/api/

**Production:**
- Frontend: http://138.68.109.92/
- API: http://138.68.109.92/api/

### 6.2 Django Admin (If Needed)

**First, create superuser:**
```bash
docker-compose -f docker-compose.alpine.yml exec backend \
  python manage.py createsuperuser
```

**Then access:**
- Admin: http://localhost/admin/

---

## Common Commands Reference

### Service Management

```bash
# Start services
docker-compose -f docker-compose.alpine.yml up -d

# Stop services
docker-compose -f docker-compose.alpine.yml stop

# Restart services
docker-compose -f docker-compose.alpine.yml restart

# Stop and remove containers (keeps data)
docker-compose -f docker-compose.alpine.yml down

# Stop and remove everything including data (DANGEROUS)
docker-compose -f docker-compose.alpine.yml down -v
```

### Logs

```bash
# All services
docker-compose -f docker-compose.alpine.yml logs -f

# Specific service
docker-compose -f docker-compose.alpine.yml logs -f backend

# Last 100 lines
docker-compose -f docker-compose.alpine.yml logs --tail=100

# Since specific time
docker-compose -f docker-compose.alpine.yml logs --since 2h
```

### Shell Access

```bash
# Backend shell
docker-compose -f docker-compose.alpine.yml exec backend sh

# Database shell
docker-compose -f docker-compose.alpine.yml exec database sh

# PostgreSQL client
docker-compose -f docker-compose.alpine.yml exec database \
  psql -U iolta_user -d iolta_guard_db
```

### Database Backup

```bash
# Create backup
docker-compose -f docker-compose.alpine.yml exec database \
  pg_dump -U iolta_user iolta_guard_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker cp backup.sql iolta_db_alpine:/tmp/
docker-compose -f docker-compose.alpine.yml exec database \
  psql -U iolta_user -d iolta_guard_db -f /tmp/backup.sql
```

---

## Troubleshooting

### Issue: Database Won't Start

**Symptoms:**
```
database  | ... FATAL: password authentication failed
```

**Solution:**
1. Check .env file has correct DB_PASSWORD
2. Remove volume and restart:
   ```bash
   docker-compose -f docker-compose.alpine.yml down -v
   docker-compose -f docker-compose.alpine.yml up -d
   ```

### Issue: Backend Build Fails

**Symptoms:**
```
ERROR: failed to solve: executor failed running ...
```

**Solutions:**

**1. Clean Docker cache:**
```bash
docker builder prune -a
docker-compose -f docker-compose.alpine.yml build --no-cache
```

**2. Check disk space:**
```bash
df -h
docker system df
```

**3. Check Docker memory:**
```bash
docker info | grep Memory
```

**4. Build with verbose output:**
```bash
docker-compose -f docker-compose.alpine.yml build --progress=plain 2>&1 | tee build.log
```

### Issue: WeasyPrint/PDF Errors

**Symptoms:**
```
OSError: cannot load library 'gobject-2.0-0'
```

**Solution:**
Verify all WeasyPrint dependencies installed:
```bash
docker-compose -f docker-compose.alpine.yml exec backend sh -c "apk info | grep -E 'cairo|pango|gdk'"
```

### Issue: Frontend 502 Bad Gateway

**Symptoms:**
Frontend shows "502 Bad Gateway"

**Solution:**
```bash
# Check backend is running
docker-compose -f docker-compose.alpine.yml ps backend

# Check backend logs
docker-compose -f docker-compose.alpine.yml logs backend

# Restart backend
docker-compose -f docker-compose.alpine.yml restart backend
```

### Issue: Slow Build Times

**Solutions:**

**1. Enable BuildKit:**
```bash
export DOCKER_BUILDKIT=1
docker-compose -f docker-compose.alpine.yml build
```

**2. Use build cache:**
```bash
# Don't use --no-cache unless necessary
docker-compose -f docker-compose.alpine.yml build
```

**3. Increase Docker resources:**
- Docker Desktop: Preferences → Resources → Increase CPU/Memory

---

## Performance Optimization

### Build Time Optimization

**1. Layer Caching:**
```dockerfile
# Copy requirements first (changes less frequently)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy code last (changes frequently)
COPY . .
```

**2. Pre-build Base Image:**
```bash
# Build base image with dependencies
docker build -t iolta-base:alpine -f Dockerfile.base .

# Use in main Dockerfile
FROM iolta-base:alpine
```

### Runtime Optimization

**1. Adjust Gunicorn Workers:**
Edit docker-compose.alpine.yml:
```yaml
environment:
  - GUNICORN_WORKERS=8  # 2 * CPU cores
```

**2. PostgreSQL Tuning:**
Add to database service:
```yaml
command: >
  postgres
  -c shared_buffers=256MB
  -c effective_cache_size=1GB
  -c max_connections=100
```

---

## Security Best Practices

### 1. Environment File Protection

```bash
# .env file should NEVER be committed to git
echo ".env" >> .gitignore

# Set restrictive permissions
chmod 600 .env

# Verify
ls -la .env
# Should show: -rw------- (600)
```

### 2. Regular Updates

```bash
# Pull latest Alpine base images
docker pull python:3.12-alpine3.20
docker pull postgres:16-alpine3.20
docker pull nginx:1.25-alpine3.20

# Rebuild with updated bases
docker-compose -f docker-compose.alpine.yml build --pull
```

### 3. Security Scanning

```bash
# Scan images for vulnerabilities (if Trivy installed)
trivy image iolta-guard-backend-alpine:latest
trivy image iolta-guard-frontend-alpine:latest
```

### 4. Non-Root Execution

Verify services run as non-root:
```bash
docker-compose -f docker-compose.alpine.yml exec backend whoami
# Should return: iolta (not root)
```

---

## Multi-Tenant Deployment (100+ Firms)

### Strategy A: Separate Stack Per Firm

```bash
# Firm 1
docker-compose -f docker-compose.alpine.yml -p firm1 up -d

# Firm 2
docker-compose -f docker-compose.alpine.yml -p firm2 up -d

# List all stacks
docker-compose ls
```

**Pros:**
- Complete data isolation
- Independent scaling
- Easier backup/restore per firm

**Cons:**
- More resource usage
- More containers to manage

### Strategy B: Single Stack with Tenant Isolation

**Requires code changes for tenant_id filtering**

**Pros:**
- Lower resource usage
- Centralized management

**Cons:**
- More complex code
- Shared resource pool

---

## Next Steps

After successful build and deployment:

1. **Run Testing Checklist** (see TESTING_CHECKLIST_ALPINE.md)
2. **PDF Output Comparison** (compare Debian vs Alpine PDFs)
3. **Load Testing** (stress test at expected scale)
4. **Security Audit** (vulnerability scanning)
5. **Documentation** (document any customizations)

---

## Support & Resources

**Documentation:**
- Alpine Linux: https://alpinelinux.org/
- Docker: https://docs.docker.com/
- Django: https://docs.djangoproject.com/

**Troubleshooting:**
1. Check logs: `docker-compose -f docker-compose.alpine.yml logs`
2. Check status: `docker-compose -f docker-compose.alpine.yml ps`
3. Check resources: `docker stats`

---

**Build Date:** November 7, 2025
**Alpine Version:** 3.20
**Python Version:** 3.12
**Status:** Ready for Testing
