# IOLTA Guard - Quick Start Guide

## 🚀 Deploy in 5 Minutes

### 1. Extract Package
```bash
tar -xzf iolta-production-deployment-20251104.tar.gz
cd iolta-deployment
```

### 2. Load Docker Images
```bash
docker load -i iolta-backend-image.tar
docker load -i iolta-frontend-image.tar
```

### 3. Configure Environment
```bash
cp .env.template .env
nano .env  # Edit with your passwords and settings
```

### 4. Prepare Files
```bash
mkdir -p backups database/init
cp source/docker-compose-simple-production.yml docker-compose.yml
cp source/account.json ./
```

### 5. Start Application
```bash
docker-compose up -d
```

### 6. Initialize Database (First Time)
```bash
# Wait 30 seconds for containers to start
sleep 30

# Run migrations
docker exec -it iolta_backend python manage.py migrate

# Optional: Load demo data
docker cp source/insurance_demo_data.sql iolta_db:/tmp/
docker exec -it iolta_db psql -U iolta_user -d iolta_guard_db -f /tmp/insurance_demo_data.sql
```

### 7. Access Application
Open browser: `http://your-server-ip/`

---

## 📋 Essential Commands

```bash
# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Stop application
docker-compose down

# Restart
docker-compose restart

# Backup database
docker exec -it iolta_db pg_dump -U iolta_user iolta_guard_db > backup.sql
```

---

## 🔧 What's New in This Version

✅ Fixed reissue logic - "TO PRINT" checks properly reissued
✅ Wider modals for better visibility
✅ "To Print" checkbox auto-shows on Withdrawal selection
✅ Updated cache busting (v=1762170895)
✅ Database sequences fixed

---

## 📖 Full Instructions

See `DEPLOYMENT_INSTRUCTIONS.md` for complete documentation

---

**Package Date:** November 4, 2025
**Ready for Production:** ✓ Yes
