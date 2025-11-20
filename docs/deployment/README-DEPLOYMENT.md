# IOLTA Guard - Production Deployment Guide

**Target Server:** http://138.68.109.92  
**Deployment Method:** Single-script Docker deployment  
**Database:** Automatic restoration from SQL backup

---

## Quick Start (5 Minutes)

```bash
# 1. Configure environment
cp .env.production .env.production.local
# Edit .env.production.local and set passwords

# 2. Deploy
./deploy.sh

# 3. Access application
# Open: http://138.68.109.92
```

---

## Prerequisites

**Required Software:**
- Docker 20.10+
- Docker Compose 1.29+
- Linux server (Ubuntu 22.04 LTS recommended)
- Port 80 open for HTTP

**NOT Required:**
- NO Python installation needed (runs in Docker)
- NO PostgreSQL installation needed (runs in Docker)
- NO Node.js needed (static frontend)
- NO manual database setup (auto-restored from SQL)

---

## Architecture

```
Internet (Port 80) → Nginx → Django Backend → PostgreSQL
                      ↓
                   Frontend
                   Static Files
```

**What's Exposed:**
- ✅ Frontend/Nginx on port 80 (PUBLIC)

**What's NOT Exposed:**
- ❌ Backend port 8002 (INTERNAL ONLY)
- ❌ Database port 5432 (INTERNAL ONLY)

---

## Step-by-Step Deployment

### Step 1: Prepare Environment File

```bash
# Copy template
cp .env.production .env.production.local

# Generate secure DB password
openssl rand -base64 32

# Generate secure Django secret key
python3 -c "import secrets; print(secrets.token_urlsafe(50))"

# Edit file and replace placeholders
nano .env.production.local
```

**Required Values:**
```env
DB_PASSWORD=<paste-generated-password>
DJANGO_SECRET_KEY=<paste-generated-key>
```

### Step 2: Rename Environment File

```bash
# Rename to .env.production (deploy.sh looks for this)
mv .env.production.local .env.production
```

### Step 3: Deploy

```bash
# Make script executable (if not already)
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

**What the script does:**
1. ✅ Validates prerequisites (Docker, Docker Compose)
2. ✅ Checks .env.production exists and is configured
3. ✅ Verifies SQL backup file exists
4. ✅ Stops existing containers (if any)
5. ✅ Optionally removes old database for clean restore
6. ✅ Builds Docker images (frontend, backend)
7. ✅ Starts database container
8. ✅ **Automatically restores database from SQL backup**
9. ✅ Starts backend container (NO migrations)
10. ✅ Starts frontend container
11. ✅ Runs health checks
12. ✅ Shows access points

**Deployment Time:** 5-10 minutes (first run)

### Step 4: Verify Deployment

```bash
# Check all containers are running
docker-compose -f docker-compose.production.yml ps

# Expected output:
#   iolta_db_production         Up (healthy)
#   iolta_backend_production    Up (healthy)
#   iolta_frontend_production   Up (healthy)

# Check frontend is accessible
curl http://138.68.109.92/

# Check API is accessible through nginx
curl http://138.68.109.92/api/health/

# View logs
docker-compose -f docker-compose.production.yml logs -f
```

---

## Database Details

### Automatic Database Restoration

**How it works:**
1. SQL backup file is located at: `database/init/01-restore.sql`
2. Docker mounts this directory: `/docker-entrypoint-initdb.d`
3. PostgreSQL automatically runs all `.sql` files in this directory on first startup
4. Database is fully restored with schema + data
5. **NO migrations are run** in the backend (data comes from SQL)

**Important:**
- Restoration happens **ONCE** on first database container start
- If you remove the database volume, it will restore again
- To update database, either:
  - Use application to make changes
  - OR update SQL file and recreate database volume

### Database Backup

```bash
# Create backup
docker-compose -f docker-compose.production.yml exec database \
  pg_dump -U iolta_user iolta_guard_db > backup_$(date +%Y%m%d).sql

# Restore from backup (if needed)
# 1. Stop containers
docker-compose -f docker-compose.production.yml down

# 2. Remove database volume
docker volume rm iolta-guard-production-v2_postgres_data

# 3. Replace SQL file
cp backup_20251014.sql database/init/01-restore.sql

# 4. Redeploy
./deploy.sh
```

---

## Container Management

### View Logs

```bash
# All services
docker-compose -f docker-compose.production.yml logs -f

# Specific service
docker-compose -f docker-compose.production.yml logs -f backend
docker-compose -f docker-compose.production.yml logs -f database
docker-compose -f docker-compose.production.yml logs -f frontend
```

### Restart Services

```bash
# Restart all
docker-compose -f docker-compose.production.yml restart

# Restart specific service
docker-compose -f docker-compose.production.yml restart backend
```

### Stop Services

```bash
# Stop (keeps data)
docker-compose -f docker-compose.production.yml stop

# Stop and remove containers (keeps data)
docker-compose -f docker-compose.production.yml down

# Stop and remove everything including data (DANGEROUS)
docker-compose -f docker-compose.production.yml down -v
```

### Access Container Shell

```bash
# Backend shell
docker-compose -f docker-compose.production.yml exec backend bash

# Database shell
docker-compose -f docker-compose.production.yml exec database psql -U iolta_user -d iolta_guard_db

# Frontend shell
docker-compose -f docker-compose.production.yml exec frontend sh
```

---

## Troubleshooting

### Frontend shows 502 Bad Gateway

**Cause:** Nginx can't reach backend

**Solution:**
```bash
# Check backend is running
docker-compose -f docker-compose.production.yml ps backend

# Check backend logs
docker-compose -f docker-compose.production.yml logs backend

# Restart backend
docker-compose -f docker-compose.production.yml restart backend
```

### Database connection errors

**Cause:** Database not ready or wrong credentials

**Solution:**
```bash
# Check database is running
docker-compose -f docker-compose.production.yml ps database

# Check database logs
docker-compose -f docker-compose.production.yml logs database

# Test connection
docker-compose -f docker-compose.production.yml exec database \
  psql -U iolta_user -d iolta_guard_db -c "SELECT 1;"
```

### Application not accessible

**Cause:** Port 80 blocked or containers not running

**Solution:**
```bash
# Check if port 80 is open
sudo ufw status
sudo ufw allow 80/tcp

# Check containers
docker-compose -f docker-compose.production.yml ps

# Restart all services
docker-compose -f docker-compose.production.yml restart
```

### "Database already exists" error

**Cause:** Trying to restore backup but database already has data

**Solution:**
```bash
# Remove old database volume for clean restore
docker-compose -f docker-compose.production.yml down
docker volume rm iolta-guard-production-v2_postgres_data
./deploy.sh
```

---

## Security Checklist

### ✅ What's Already Configured

- [x] Backend NOT publicly exposed
- [x] Database NOT publicly exposed  
- [x] Only frontend accessible (port 80)
- [x] Session-based authentication
- [x] CSRF protection enabled
- [x] XSS protection enabled
- [x] Brute force protection (5 attempts, 15-min lockout)
- [x] Rate limiting (100/hour anonymous, 1000/hour authenticated)
- [x] DEBUG mode disabled
- [x] Secret keys in environment variables

### ⚠️ Additional Security Steps (Recommended)

```bash
# 1. Enable firewall
sudo ufw enable
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw status

# 2. Verify backend NOT accessible
curl http://138.68.109.92:8002  # Should FAIL

# 3. Verify database NOT accessible
nc -zv 138.68.109.92 5432  # Should FAIL

# 4. Setup automated backups (cron job)
crontab -e
# Add: 0 2 * * * /path/to/backup-script.sh
```

---

## Updating the Application

### Update Code Only (Keep Database)

```bash
# 1. Pull latest code
git pull

# 2. Rebuild containers
docker-compose -f docker-compose.production.yml build --no-cache

# 3. Restart services
docker-compose -f docker-compose.production.yml up -d

# 4. Verify
docker-compose -f docker-compose.production.yml ps
```

### Update Everything (Including Database)

```bash
# 1. Backup current database first
docker-compose -f docker-compose.production.yml exec database \
  pg_dump -U iolta_user iolta_guard_db > backup_before_update.sql

# 2. Pull latest code
git pull

# 3. Update SQL file if provided
cp new_backup.sql database/init/01-restore.sql

# 4. Full redeploy
docker-compose -f docker-compose.production.yml down -v
./deploy.sh
```

---

## Files Created/Modified

### Created Files

| File | Purpose |
|------|---------|
| `docker-compose.production.yml` | Production Docker configuration |
| `.env.production` | Environment variables template |
| `deploy.sh` | One-script deployment |
| `database/init/01-restore.sql` | SQL backup for database initialization |
| `README-DEPLOYMENT.md` | This file |

### Modified Files

| File | Changes |
|------|---------|
| `trust_account/trust_account_project/settings.py` | - SESSION_COOKIE_DOMAIN = None<br>- Clean CORS origins |
| `account.json` | - debug = false<br>- Port 8002<br>- Added production IP to allowed_hosts |

---

## Configuration Summary

### Docker Compose (docker-compose.production.yml)

**Database Service:**
- Image: postgres:16-alpine
- Container: iolta_db_production
- Network: Internal only (NOT exposed)
- Initialization: Automatic from SQL backup

**Backend Service:**
- Image: Built from trust_account/Dockerfile
- Container: iolta_backend_production
- Port: 8002 (internal only, NOT exposed)
- Command: collectstatic + gunicorn (NO migrations)

**Frontend Service:**
- Image: Built from frontend/Dockerfile
- Container: iolta_frontend_production
- Port: 80 (PUBLIC)
- Purpose: Serve static files + reverse proxy to backend

### Environment Variables (.env.production)

**Required:**
- `DB_PASSWORD` - Secure database password
- `DJANGO_SECRET_KEY` - Secure Django secret key

**Optional (have defaults):**
- `DB_NAME` - Default: iolta_guard_db
- `DB_USER` - Default: iolta_user
- `ALLOWED_HOSTS` - Default: 138.68.109.92,localhost,backend

---

## Production Checklist

Before going live, verify:

- [ ] .env.production configured with secure passwords
- [ ] Database backup file exists (database/init/01-restore.sql)
- [ ] Deploy script runs without errors
- [ ] All 3 containers are running and healthy
- [ ] Frontend accessible at http://138.68.109.92
- [ ] Backend NOT accessible at http://138.68.109.92:8002
- [ ] Database NOT accessible on port 5432
- [ ] Can login to application
- [ ] Can view dashboard
- [ ] Can create/edit clients
- [ ] Can create/edit transactions
- [ ] Can generate reports
- [ ] Firewall configured (port 80 open only)
- [ ] Automated backups configured
- [ ] Log rotation configured

---

## Support

**View Logs:**
```bash
docker-compose -f docker-compose.production.yml logs -f
```

**Container Status:**
```bash
docker-compose -f docker-compose.production.yml ps
```

**Health Checks:**
```bash
# Frontend
curl http://138.68.109.92/

# API
curl http://138.68.109.92/api/health/
```

---

## Summary

**Deployment Method:**
- ✅ Single script: `./deploy.sh`
- ✅ Database auto-restored from SQL backup
- ✅ NO manual migrations
- ✅ NO manual configuration
- ✅ Clean, reproducible deployment

**Time Required:**
- First deployment: 5-10 minutes
- Subsequent deployments: 2-5 minutes

**Security:**
- ✅ Backend not exposed
- ✅ Database not exposed
- ✅ Production-ready defaults

**Maintenance:**
- Easy updates (pull code, rebuild, restart)
- Simple backups (pg_dump)
- Clear logs (docker-compose logs)

---

**Created:** October 14, 2025  
**Version:** 1.0  
**Status:** ✅ Production Ready
