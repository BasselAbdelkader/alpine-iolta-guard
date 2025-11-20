# IOLTA Guard - Production Deployment to 138.68.109.92

**Date Created:** November 4, 2025
**Version:** 1.0.0
**Production Server:** 138.68.109.92

## Quick Deployment Commands

### Step 1: Transfer to Production Server

```bash
# From your local machine (/Users/bassel/Desktop/ve_demo)
scp -i sonbol-opn ve_demo-20251104.tar.gz root@138.68.109.92:/root
```

### Step 2: On Production Server - Backup Existing (if any)

```bash
# SSH into production
ssh -i sonbol-opn root@138.68.109.92

# Backup existing installation if present
cd /root
if [ -d "ve_demo" ]; then
    mv ve_demo ve_demo_backup_$(date +%Y%m%d_%H%M%S)
fi
```

### Step 3: Extract and Setup

```bash
# Extract the package
tar -xzf ve_demo-20251104.tar.gz
cd ve_demo

# Load Docker images
docker load -i iolta-backend-image.tar
docker load -i iolta-frontend-image.tar

# Verify images loaded
docker images | grep iolta-guard
```

### Step 4: Configure Environment

```bash
# Create environment file from template
cp .env.template .env
nano .env
```

Update these values in `.env`:
```env
DB_NAME=iolta_guard_db
DB_USER=iolta_user
DB_PASSWORD=YOUR_SECURE_PASSWORD_HERE

DJANGO_SECRET_KEY=YOUR_DJANGO_SECRET_KEY_HERE
DEBUG=False

ALLOWED_HOSTS=138.68.109.92,localhost,127.0.0.1
```

Generate Django secret key:
```bash
docker run --rm iolta-guard-backend:latest python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 5: Prepare Directory Structure

```bash
# Create necessary directories
mkdir -p backups database/init

# Copy docker-compose file
cp source/docker-compose-simple-production.yml docker-compose.yml

# Copy account.json
cp source/account.json ./
```

### Step 6: Start Application

```bash
# Start all containers
docker-compose up -d

# Check status (wait about 30 seconds)
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 7: Initialize Database (First Time Only)

```bash
# Run migrations
docker exec -it iolta_backend python manage.py migrate

# Load demo data (optional)
docker cp source/insurance_demo_data.sql iolta_db:/tmp/
docker exec -it iolta_db psql -U iolta_user -d iolta_guard_db -f /tmp/insurance_demo_data.sql

# Create superuser (optional)
docker exec -it iolta_backend python manage.py createsuperuser
```

### Step 8: Verify Deployment

```bash
# Test from server
curl http://localhost/

# From your local machine
curl http://138.68.109.92/

# In browser
http://138.68.109.92/
```

## What's New in This Deployment (November 4, 2025)

### 1. ✅ Fixed Reissue Logic for "TO PRINT" Checks
When reissuing a check that had "TO PRINT" reference:
- **Voided transaction**: Preserves original date, reference becomes "Voided"
- **Reversal deposit**: Blank reference (displays transaction number: DEPO-2025-xxx)
- **New withdrawal**: Reference set to "TO PRINT" (ready for printing)

**Files Changed:**
- `trust_account/apps/bank_accounts/api/views.py` (lines 441-500)

### 2. ✅ Modal Width Increases
- **Case detail modal**: 60vw → 85vw
- **Bank transactions modal**: 60% → 70%

**Files Changed:**
- `frontend/html/case-detail.html` (line 430)
- `frontend/html/bank-transactions.html` (line 250)

### 3. ✅ "To Print" Checkbox Auto-Show
- Checkbox now appears automatically when "Withdrawal" is selected
- Container width: 90px → 120px
- Label: Added `white-space: nowrap` to prevent wrapping

**Files Changed:**
- `frontend/js/bank-transactions.js` (lines 451, 662, 1045)

### 4. ✅ Cache Busting Updated
All HTML files now use cache version: `v=1762170895`

### 5. ✅ Database Sequences Fixed
All PostgreSQL sequences reset after demo data load to prevent duplicate key errors.

**Files Changed:**
- `insurance_demo_data.sql` (lines 161-168)

## Updating Existing Production

If you already have a running production installation:

```bash
# SSH to server
ssh -i sonbol-opn root@138.68.109.92

# Go to existing directory
cd /root/ve_demo

# Stop containers
docker-compose down

# Backup current version
cd /root
cp -r ve_demo ve_demo_backup_$(date +%Y%m%d_%H%M%S)

# Remove old deployment
rm -rf ve_demo

# Upload new package (from local machine)
scp -i sonbol-opn ve_demo-20251104.tar.gz root@138.68.109.92:/root

# Back on server - extract
tar -xzf ve_demo-20251104.tar.gz
cd ve_demo

# Load new images
docker load -i iolta-backend-image.tar
docker load -i iolta-frontend-image.tar

# Copy environment from backup (if you want to keep settings)
cp ../ve_demo_backup_*/​.env .

# Setup directories
mkdir -p backups database/init
cp source/docker-compose-simple-production.yml docker-compose.yml
cp source/account.json ./

# Start with new images
docker-compose up -d

# Run any new migrations
docker exec -it iolta_backend python manage.py migrate

# Check logs
docker-compose logs -f
```

## Essential Management Commands

### View Logs
```bash
# All containers
docker-compose logs -f

# Specific container
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Container Management
```bash
# Check status
docker-compose ps

# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend

# Stop all
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

### Database Management

#### Backup Database
```bash
docker exec -it iolta_db pg_dump -U iolta_user iolta_guard_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

#### Restore Database
```bash
docker cp backup.sql iolta_db:/tmp/
docker exec -it iolta_db psql -U iolta_user -d iolta_guard_db -f /tmp/backup.sql
```

#### Access Database Shell
```bash
docker exec -it iolta_db psql -U iolta_user -d iolta_guard_db
```

### Django Management

#### Run Migrations
```bash
docker exec -it iolta_backend python manage.py migrate
```

#### Create Superuser
```bash
docker exec -it iolta_backend python manage.py createsuperuser
```

#### Collect Static Files
```bash
docker exec -it iolta_backend python manage.py collectstatic --noinput
```

#### Django Shell
```bash
docker exec -it iolta_backend python manage.py shell
```

## Troubleshooting

### Port 80 Already in Use
```bash
# Check what's using port 80
sudo netstat -tlnp | grep :80

# Stop the service (e.g., Apache)
sudo systemctl stop apache2
# or
sudo systemctl stop nginx

# Then start your containers
docker-compose up -d
```

### Containers Won't Start
```bash
# Check logs
docker-compose logs

# Check disk space
df -h

# Check Docker status
docker info

# Rebuild images if needed
docker-compose build --no-cache
```

### Database Connection Issues
```bash
# Check if database is running
docker ps | grep iolta_db

# Check database logs
docker logs iolta_db

# Verify environment variables
cat .env

# Test connection
docker exec -it iolta_backend python -c "import django; django.setup(); from django.db import connection; connection.ensure_connection(); print('DB connection OK')"
```

### Application Not Accessible from Browser
```bash
# Check firewall
sudo ufw status

# Allow port 80
sudo ufw allow 80/tcp

# Check if application is listening
curl http://localhost/

# Check nginx logs
docker logs iolta_frontend
```

### Clear Browser Cache Issues
Users experiencing old UI should:
1. Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
2. Clear browser cache
3. Try incognito/private mode

## Security Checklist

- [ ] Changed `DB_PASSWORD` to a strong password
- [ ] Generated new `DJANGO_SECRET_KEY`
- [ ] Updated `ALLOWED_HOSTS` with server IP
- [ ] Set `DEBUG=False`
- [ ] Configured firewall (only allow ports 22, 80)
- [ ] Set up regular database backups
- [ ] Enabled fail2ban for SSH protection
- [ ] Consider adding SSL/HTTPS (not included in this setup)

## Testing the Deployment

### 1. Access Application
```bash
http://138.68.109.92/
```

### 2. Test "To Print" Feature
1. Navigate to a case detail page
2. Click "Add New Transaction"
3. Modal should be wider (85vw)
4. Select "Withdrawal" from Type dropdown
5. "To Print" checkbox should appear automatically
6. Check the checkbox
7. Fill in other required fields
8. Save transaction

### 3. Test Reissue Feature
1. Find a transaction with "TO PRINT" reference
2. Click the reissue button
3. Verify three transactions are created:
   - Original: Status "Voided", keeps original date
   - Reversal: Status "Cleared", reference shows DEPO-2025-xxx
   - New check: Status "Pending", reference shows "TO PRINT"

## Support

### Log Files Location
- Backend logs: `docker-compose logs backend`
- Frontend logs: `docker-compose logs frontend`
- Database logs: `docker-compose logs database`

### Common Issues
See troubleshooting section above

### Emergency Rollback
```bash
# Stop current deployment
docker-compose down

# Restore from backup
cd /root
rm -rf ve_demo
cp -r ve_demo_backup_YYYYMMDD_HHMMSS ve_demo
cd ve_demo

# Start old version
docker-compose up -d
```

---

**Deployment Package:** ve_demo-20251104.tar.gz
**Production Server:** 138.68.109.92
**Package Date:** November 4, 2025
**Ready for Production:** ✅ YES

**Contact Information:**
- Server IP: 138.68.109.92
- SSH Key: sonbol-opn
- SSH User: root
