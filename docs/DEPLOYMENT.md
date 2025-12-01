# IOLTA Production Deployment Guide

## Production Server Information
- **IP Address**: 138.68.109.92
- **URL**: http://138.68.109.92
- **Login**: http://138.68.109.92/login

## What's Included

### Alpine-based Docker Containers
All containers use lightweight Alpine Linux images:
- **Database**: PostgreSQL 16 Alpine
- **Cache**: Redis 7 Alpine
- **Backend**: Python 3.12 Alpine with Django
- **Frontend**: Nginx Alpine

### Security Features Merged from amin-branch
1. **RBAC (Role-Based Access Control)** - 5 user roles with granular permissions
2. **IDOR Protection** - Client-to-user assignment filtering
3. **API Hardening** - Rate limiting, input validation
4. **Threat Detection** - Brute force protection middleware
5. **Redis Cache** - Persistent security state storage
6. **SQL Injection Protection** - Input validators

### Database Backup
- **File**: `database_backup.sql` (84KB)
- **Contents**: Complete schema + all current data
- **Includes**: Users, clients, vendors, bank accounts, transactions, settlements

## ONE-COMMAND DEPLOYMENT

### Step 1: Transfer Files to Server
```bash
# On your local machine
scp -r /Users/bassel/Desktop/merge/bassel-prod/iolta-production root@138.68.109.92:/opt/
```

### Step 2: SSH into Server
```bash
ssh root@138.68.109.92
cd /opt/iolta-production
```

### Step 3: Run Deployment Script
```bash
sudo bash deploy.sh
```

That's it! The script will:
1. Install Docker and Docker Compose (if needed)
2. Stop any existing containers
3. Build all Alpine containers
4. Start database service
5. Restore from `database_backup.sql`
6. Start all services (Redis, Backend, Frontend)
7. Verify deployment

## Expected Output

```
==================================================
IOLTA Guard Trust Account System - Deployment
Production Server: 138.68.109.92
==================================================

✓ Docker installed
✓ docker-compose installed
✓ Environment file created with secure keys
✓ Stopped
✓ Containers started
✓ Database ready
✓ Database restored from backup
✓ Superuser ready (admin/admin123)
✓ Static files collected

==================================================
Deployment Complete!
==================================================

Access your application at:
http://138.68.109.92

Default credentials:
  Username: admin
  Password: admin123
```

## Post-Deployment Verification

### 1. Check Container Status
```bash
docker ps --filter "name=iolta"
```

Expected output:
```
CONTAINER ID   NAME                  STATUS         PORTS
xxxxx          iolta_frontend_prod   Up 2 minutes   0.0.0.0:80->80/tcp
xxxxx          iolta_backend_prod    Up 2 minutes
xxxxx          iolta_redis_prod      Up 2 minutes
xxxxx          iolta_db_prod         Up 2 minutes
```

### 2. View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
```

### 3. Test Login
1. Open browser: http://138.68.109.92/login
2. Login with: `admin` / `admin123`
3. Change password immediately!

### 4. Verify Database Restoration
```bash
docker exec -it iolta_db_prod psql -U iolta_user -d iolta_guard_db

# Inside psql:
\dt                    -- List tables
SELECT COUNT(*) FROM clients;
SELECT COUNT(*) FROM vendors;
SELECT COUNT(*) FROM bank_accounts;
\q
```

## Architecture

### Network Flow
```
Internet → 138.68.109.92:80 → Nginx (Frontend)
                            ↓
                    Backend (Django API)
                            ↓
                ┌───────────┴───────────┐
                ↓                       ↓
        PostgreSQL 16              Redis 7
        (Database)                 (Cache)
```

### Container Details
1. **iolta_frontend_prod**
   - Nginx Alpine serving React SPA
   - Port 80 exposed to internet
   - Proxies /api requests to backend

2. **iolta_backend_prod**
   - Django 4.2.7 + DRF
   - Gunicorn with 4 workers
   - 120s timeout

3. **iolta_db_prod**
   - PostgreSQL 16 Alpine
   - Database: iolta_guard_db
   - User: iolta_user
   - Volume: postgres_data (persistent)

4. **iolta_redis_prod**
   - Redis 7 Alpine
   - Used for: Brute force tracking, rate limiting, session cache

## Security Configuration

### Settings Configured for Production
- `DEBUG = False`
- `ALLOWED_HOSTS = ['138.68.109.92', ...]`
- `CORS_ALLOWED_ORIGINS = ['http://138.68.109.92']`
- `SESSION_COOKIE_SECURE = False` (Set to True when HTTPS enabled)
- `CSRF protection` enabled
- `XSS protection` enabled
- `HSTS` configured (activate with HTTPS)

### Security Middleware Stack
```python
'trust_account_project.threat_detection.AdvancedThreatDetectionMiddleware'  # Brute force
'trust_account_project.security.BruteForceProtectionMiddleware'
'trust_account_project.api_hardening.APISecurityMiddleware'
'trust_account_project.middleware.SecurityHeadersMiddleware'
```

### User Roles
1. **System Admin** - Full system access
2. **Managing Attorney** - All client/financial access
3. **Bookkeeper** - Financial operations
4. **Staff Attorney** - Assigned clients only (IDOR protected)
5. **Paralegal** - Assigned clients only (IDOR protected)

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs backend

# Rebuild specific service
docker-compose -f docker-compose.prod.yml up -d --build backend
```

### Database Connection Issues
```bash
# Check database health
docker exec iolta_db_prod pg_isready -U iolta_user

# Verify environment variables
docker exec iolta_backend_prod env | grep DB_
```

### Redis Connection Issues
```bash
# Test Redis
docker exec iolta_redis_prod redis-cli ping
# Should return: PONG

# Check backend Redis connection
docker exec iolta_backend_prod python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value')
>>> cache.get('test')
```

### Frontend Not Loading
```bash
# Check nginx logs
docker logs iolta_frontend_prod

# Verify nginx is running
docker exec iolta_frontend_prod nginx -t
```

## Management Commands

### Stop All Services
```bash
docker-compose -f docker-compose.prod.yml down
```

### Restart Single Service
```bash
docker-compose -f docker-compose.prod.yml restart backend
```

### Backup Database (Manual)
```bash
docker exec iolta_db_prod pg_dump -U iolta_user -d iolta_guard_db \
  --clean --if-exists --create > database_backup_$(date +%Y%m%d).sql
```

### Django Admin Commands
```bash
# Create superuser
docker exec -it iolta_backend_prod python manage.py createsuperuser

# Run migrations
docker exec -it iolta_backend_prod python manage.py migrate

# Collect static files
docker exec -it iolta_backend_prod python manage.py collectstatic --noinput
```

## Production Checklist

- [ ] Deploy using `sudo bash deploy.sh`
- [ ] Verify all 4 containers running
- [ ] Test login at http://138.68.109.92/login
- [ ] Change admin password immediately
- [ ] Create user profiles for staff
- [ ] Assign clients to staff attorneys/paralegals
- [ ] Test RBAC - verify staff only see assigned clients
- [ ] Test API rate limiting
- [ ] Monitor logs for 24 hours
- [ ] Set up automated backups
- [ ] Configure HTTPS/SSL (recommended)
- [ ] Set `SESSION_COOKIE_SECURE = True` after HTTPS

## HTTPS Setup (Recommended)

### Using Let's Encrypt with Certbot
```bash
# Install certbot
apt-get update
apt-get install certbot python3-certbot-nginx

# Get certificate
certbot --nginx -d 138.68.109.92

# Auto-renewal (runs daily)
systemctl enable certbot.timer
```

After HTTPS is configured:
1. Update `settings.py`: `SESSION_COOKIE_SECURE = True`
2. Update `settings.py`: `SECURE_SSL_REDIRECT = True`
3. Rebuild backend: `docker-compose -f docker-compose.prod.yml up -d --build backend`

## Support

For issues or questions:
1. Check logs: `docker-compose -f docker-compose.prod.yml logs -f`
2. Verify container health: `docker ps`
3. Check this deployment guide

## Files Summary

### Required Files for Deployment
```
iolta-production/
├── deploy.sh                    # ONE-COMMAND deployment script
├── database_backup.sql          # Complete DB backup (schema + data)
├── docker-compose.prod.yml      # Alpine containers orchestration
├── backend/
│   ├── Dockerfile              # Python 3.12 Alpine
│   ├── requirements.txt        # Dependencies including django-redis
│   ├── trust_account_project/
│   │   ├── settings.py         # Configured for 138.68.109.92
│   │   ├── security.py         # RBAC + Auth backend
│   │   ├── api_hardening.py    # API security middleware
│   │   ├── threat_detection.py # Brute force protection
│   │   └── validators.py       # SQL injection protection
│   └── apps/
│       ├── clients/
│       │   ├── models.py       # IDOR: assigned_users field
│       │   └── api/
│       │       ├── views.py    # IDOR: Role-based filtering
│       │       └── permissions.py  # CanAccessClient
│       └── settings/
│           └── permissions.py   # RBAC permission classes
└── frontend/
    ├── Dockerfile              # Nginx Alpine
    └── nginx.conf              # Proxy to backend
```

All files are ready. Just run `sudo bash deploy.sh`!
