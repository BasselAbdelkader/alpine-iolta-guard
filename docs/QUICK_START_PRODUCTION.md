# IOLTA Guard - Quick Start for Production (138.68.109.92)

## 🚀 Deploy in 5 Minutes

### Step 1: Transfer to Production Server
```bash
# From your local machine (/Users/bassel/Desktop/ve_demo)
scp -i sonbol-opn ve_demo-20251104.tar.gz root@138.68.109.92:/root
```

### Step 2: Connect to Production
```bash
ssh -i sonbol-opn root@138.68.109.92
```

### Step 3: Backup & Extract
```bash
# Backup existing if present
cd /root
if [ -d "ve_demo" ]; then
    mv ve_demo ve_demo_backup_$(date +%Y%m%d_%H%M%S)
fi

# Extract new package
tar -xzf ve_demo-20251104.tar.gz
cd ve_demo
```

### Step 4: Load Docker Images
```bash
docker load -i iolta-backend-image.tar
docker load -i iolta-frontend-image.tar

# Verify
docker images | grep iolta-guard
```

### Step 5: Configure Environment
```bash
cp .env.template .env
nano .env
```

**Required changes in .env:**
```env
DB_PASSWORD=YOUR_SECURE_PASSWORD
DJANGO_SECRET_KEY=YOUR_SECRET_KEY
ALLOWED_HOSTS=138.68.109.92,localhost,127.0.0.1
```

Generate Django secret key:
```bash
docker run --rm iolta-guard-backend:latest python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 6: Prepare Files
```bash
mkdir -p backups database/init
cp source/docker-compose-simple-production.yml docker-compose.yml
cp source/account.json ./
```

### Step 7: Start Application
```bash
docker-compose up -d
```

### Step 8: Initialize Database (First Time)
```bash
# Wait 30 seconds for containers to start
sleep 30

# Run migrations
docker exec -it iolta_backend python manage.py migrate

# Optional: Load demo data
docker cp source/insurance_demo_data.sql iolta_db:/tmp/
docker exec -it iolta_db psql -U iolta_user -d iolta_guard_db -f /tmp/insurance_demo_data.sql
```

### Step 9: Access Application
```
Browser: http://138.68.109.92/
```

---

## 📋 Essential Commands

```bash
# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Restart
docker-compose restart

# Stop
docker-compose down

# Backup database
docker exec -it iolta_db pg_dump -U iolta_user iolta_guard_db > backup.sql
```

---

## 🔧 What's New (November 4, 2025)

✅ **Fixed**: "TO PRINT" reissue logic
✅ **Fixed**: Wider modals (85vw case, 70% bank)
✅ **Fixed**: "To Print" checkbox auto-shows
✅ **Fixed**: Cache updated (v=1762170895)
✅ **Fixed**: Database sequences

---

## 🔒 Production Server Info

**Server IP:** 138.68.109.92
**SSH Key:** sonbol-opn
**SSH User:** root
**Package:** ve_demo-20251104.tar.gz
**Date:** November 4, 2025

---

## 📖 Full Documentation

See `DEPLOYMENT_INSTRUCTIONS_PRODUCTION.md` for complete details

---

**Ready to Deploy:** ✅ YES
