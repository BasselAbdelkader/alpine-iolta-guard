# IOLTA Guard - Production Deployment Package

**Version:** 2.0 Production
**Date:** 2025-10-13
**Production URL:** http://138.68.109.92

---

## Quick Start Deployment

### Prerequisites

- Ubuntu 22.04 LTS (or compatible Linux)
- Docker and Docker Compose installed
- Root/sudo access
- Port 80 open for HTTP

### Deploy in 3 Steps

```bash
# 1. Configure environment
cp .env.production-template .env
# Edit .env and set SECRET_KEY and DB_PASSWORD

# 2. Run deployment script
chmod +x deploy-production.sh
./deploy-production.sh

# 3. Access the system
# Frontend: http://138.68.109.92
# Login: http://138.68.109.92/html/login.html
```

---

## Security Architecture

### What's NOT Exposed Publicly

✅ **Backend (Django)** - Port 8000 is NOT accessible from internet
✅ **Database (PostgreSQL)** - Port 5432 is NOT accessible from internet
✅ **Internal Docker Network** - All inter-container communication is isolated

### What IS Exposed

✅ **Frontend (Nginx)** - Port 80 only
✅ **API access** - Through nginx proxy only: http://138.68.109.92/api/

### Architecture Diagram

```
Internet → Port 80 (Nginx) → Port 8000 (Django) → Database
           ✓ PUBLIC          ✗ PRIVATE           ✗ PRIVATE
```

---

## Container Details

This deployment runs 3 Docker containers:

1. **iolta_db** - PostgreSQL 16 database
2. **iolta_backend** - Django application (NOT publicly exposed)
3. **iolta_frontend** - Nginx web server (public port 80)

---

## Files in This Package

### Essential Files

- `deploy-production.sh` - One-script deployment (runs all 3 containers)
- `docker-compose-simple-production.yml` - Docker configuration
- `nginx-simple-production.conf` - Nginx reverse proxy config
- `.env.production-template` - Environment variables template

### Postman Testing

- `IOLTA_Guard_API_Postman_Collection_PRODUCTION.json` - API collection
- `IOLTA_Guard_Postman_Environment_PRODUCTION_v2.json` - Production environment

### Documentation

- `DEPLOYMENT_GUIDE_FINAL.md` - Complete deployment manual
- `POSTMAN_API_TESTING_GUIDE.md` - API testing guide
- `QA_BUG_REPORT.md` - Quality assurance report
- `DATABASE_RESET_GUIDE.md` - Database management

---

## Configuration

### 1. Environment Variables (.env)

```env
DJANGO_SECRET_KEY=<generate-with-command-below>
DEBUG=False
DB_NAME=iolta_guard_db
DB_USER=iolta_user
DB_PASSWORD=<strong-password-here>
DB_HOST=database
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1,backend,138.68.109.92
CORS_ORIGINS=http://138.68.109.92
```

Generate secret key:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 2. Database Schema

The database schema is automatically created during deployment. The migrations will:
- Create all tables (clients, cases, vendors, transactions, bank accounts, etc.)
- Set up indexes and foreign keys
- Apply all data model changes

Latest schema matches code version 2.0 with all bug fixes applied.

---

## Deployment Process

The `deploy-production.sh` script performs these steps:

1. ✅ **Pre-flight checks** - Docker, Docker Compose, .env validation
2. ✅ **Stop existing containers** - Clean shutdown
3. ✅ **Build Docker images** - Backend and frontend
4. ✅ **Start database** - PostgreSQL container
5. ✅ **Run migrations** - Create/update database schema
6. ✅ **Collect static files** - Django admin, DRF assets
7. ✅ **Start all services** - Database, backend, frontend
8. ✅ **Health checks** - Verify all containers are running
9. ✅ **Status report** - Show access points and container status

---

## Post-Deployment

### Create Admin User

```bash
docker-compose -f docker-compose-simple-production.yml exec backend python manage.py createsuperuser
```

### Verify Deployment

1. Frontend: http://138.68.109.92
2. Login page: http://138.68.109.92/html/login.html
3. Health check: http://138.68.109.92/health
4. API: http://138.68.109.92/api/

### View Logs

```bash
# All logs
docker-compose -f docker-compose-simple-production.yml logs -f

# Specific container
docker-compose -f docker-compose-simple-production.yml logs -f backend
```

### Container Management

```bash
# Stop services
docker-compose -f docker-compose-simple-production.yml stop

# Restart services
docker-compose -f docker-compose-simple-production.yml restart

# Shutdown completely
docker-compose -f docker-compose-simple-production.yml down
```

---

## Testing with Postman

### Import Collection

1. Open Postman
2. Import `IOLTA_Guard_API_Postman_Collection_PRODUCTION.json`
3. Import `IOLTA_Guard_Postman_Environment_PRODUCTION_v2.json`
4. Select "IOLTA Guard - Production (138.68.109.92)" environment
5. Run "Login" request first
6. Test other endpoints

All endpoints are pre-configured for http://138.68.109.92

---

## Troubleshooting

### Backend not responding

```bash
# Check backend container
docker-compose -f docker-compose-simple-production.yml ps backend

# Check backend logs
docker-compose -f docker-compose-simple-production.yml logs backend

# Restart backend
docker-compose -f docker-compose-simple-production.yml restart backend
```

### Database connection issues

```bash
# Check database container
docker-compose -f docker-compose-simple-production.yml ps database

# Test database connection
docker-compose -f docker-compose-simple-production.yml exec database psql -U iolta_user -d iolta_guard_db -c "SELECT 1;"
```

### Frontend 502 error

This means nginx can't reach backend:

```bash
# Check both containers
docker-compose -f docker-compose-simple-production.yml ps

# Check if they're on same network
docker network inspect iolta-guard-production-v2_iolta_network

# Restart both
docker-compose -f docker-compose-simple-production.yml restart backend frontend
```

---

## Backup & Restore

### Manual Backup

```bash
docker-compose -f docker-compose-simple-production.yml exec database pg_dump -U iolta_user iolta_guard_db > backup_$(date +%Y%m%d).sql
```

### Restore from Backup

```bash
docker-compose -f docker-compose-simple-production.yml exec -T database psql -U iolta_user iolta_guard_db < backup_20251013.sql
```

---

## Updates

### Deploy New Version

```bash
# Stop services
docker-compose -f docker-compose-simple-production.yml down

# Backup database first!
docker-compose -f docker-compose-simple-production.yml up -d database
docker-compose -f docker-compose-simple-production.yml exec database pg_dump -U iolta_user iolta_guard_db > backup_before_update.sql
docker-compose -f docker-compose-simple-production.yml down

# Extract new version over existing files
# Then run deployment script
./deploy-production.sh
```

---

## Support

- **Documentation:** See DEPLOYMENT_GUIDE_FINAL.md for detailed manual
- **API Guide:** See POSTMAN_API_TESTING_GUIDE.md
- **Database Guide:** See DATABASE_RESET_GUIDE.md

---

## What's Fixed in This Version

### All Critical & Major Bugs Fixed (100%)

✅ Firm info API endpoints fixed (3 critical bugs)
✅ Session-based authentication implemented
✅ Rate limiting enabled (brute force protection)
✅ Client search filters working
✅ Currency formatting corrected
✅ Transaction status values fixed
✅ Vendor notes field added
✅ Success/error toast notifications
✅ Payee dropdown matching client/case flow

### Security Hardening Complete

✅ All API endpoints require authentication
✅ Backend not publicly exposed
✅ Database not publicly exposed
✅ Security headers enabled
✅ CORS configured for production IP

---

## Production Ready ✅

- ✅ All URLs point to http://138.68.109.92 (no localhost)
- ✅ Backend security: NOT publicly accessible
- ✅ Database schema: Latest matching code v2.0
- ✅ Docker architecture: 3 containers, proper isolation
- ✅ One-script deployment: `./deploy-production.sh`
- ✅ Postman collection: Production endpoints configured
- ✅ Documentation: Cleaned up and organized

---

**Deployed and tested:** 2025-10-13
**Status:** Ready for production use
