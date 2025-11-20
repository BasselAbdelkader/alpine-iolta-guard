# IOLTA Guard - Deployment Instructions (FIXED VERSION)

**Date:** November 12, 2025
**Version:** FIXED - Includes Settings Page + QuickBooks Import

---

## What's Fixed in This Version

This deployment package includes fixes for:

1. **✅ Settings Page** - Now accessible at `/settings`
2. **✅ Import/Export Page** - QuickBooks CSV import now works at `/import-quickbooks`
3. **✅ Backend Permission Fixes** - Log file permissions corrected
4. **✅ Frontend Permission Fixes** - Nginx runtime directories fixed
5. **✅ Database Password** - Properly configured and tested

---

## Files Included

```
ve_demo/
├── iolta_alpine_images_FIXED.tar      (587 MB - All Docker images)
├── deploy_from_tar.sh                  (Deployment script - VERY VERBOSE)
├── docker-compose.alpine.yml           (Container configuration)
├── backups/
│   └── iolta_production_dump.sql       (Database backup)
└── DEPLOYMENT_INSTRUCTIONS_FOR_CUSTOMER.md (This file)
```

---

## Prerequisites

Before deploying, ensure:
- [ ] Docker and Docker Compose are installed
- [ ] Port 80 is available (not used by other services)
- [ ] At least 2GB free disk space
- [ ] Server has at least 2GB RAM

---

## Deployment Steps

### 1. Stop Old Deployment (if running)

```bash
cd ~/ve_demo
docker-compose -f docker-compose.alpine.yml down
```

### 2. Upload New Files

Transfer these files to the server:
- `iolta_alpine_images_FIXED.tar` (587 MB)
- `deploy_from_tar.sh`

Place them in the `ve_demo` directory where your `docker-compose.alpine.yml` file is located.

### 3. Make Script Executable

```bash
cd ~/ve_demo
chmod +x deploy_from_tar.sh
```

### 4. Run Deployment Script

```bash
./deploy_from_tar.sh
```

**This script will:**
- ✓ Verify all required files exist
- ✓ Stop any existing containers
- ✓ Load Docker images from tar file (2-3 minutes)
- ✓ Start database and wait for it to be healthy
- ✓ Import database backup (if available)
- ✓ Start backend and wait for it to be healthy
- ✓ Start frontend and wait for it to be healthy
- ✓ Verify all services are running
- ✓ Test API endpoints

**The script is VERY VERBOSE** - you'll see detailed progress for every step.

### 5. Verify Deployment

After the script completes, check:

```bash
# Check all containers are running
docker-compose -f docker-compose.alpine.yml ps

# All three should show "healthy":
# - iolta_db_alpine         (healthy)
# - iolta_backend_alpine    (healthy)
# - iolta_frontend_alpine   (healthy)
```

### 6. Access the Application

Open your browser and go to:
```
http://YOUR_SERVER_IP/
```

Or if on the server itself:
```
http://localhost/
```

---

## Testing New Features

### 1. Test Settings Page

```
URL: http://YOUR_SERVER_IP/settings
Expected: Settings page should load (not redirect to dashboard)
```

### 2. Test QuickBooks Import

```
URL: http://YOUR_SERVER_IP/import-quickbooks
Expected: Import page should load with CSV upload form
```

Click "Choose File", select a QuickBooks CSV file, and click "Validate".

**Expected behavior:**
- Validation should complete without "404 Not Found" errors
- You should see validation results with client count, transaction count, etc.

---

## Troubleshooting

### Issue: "Backend is unhealthy"

**Check backend logs:**
```bash
docker logs iolta_backend_alpine --tail 50
```

**Common causes:**
1. **Database password mismatch** - Check `.env` file has correct password
2. **Database not ready** - Wait 30 seconds and restart backend:
   ```bash
   docker-compose -f docker-compose.alpine.yml restart backend
   ```

### Issue: "Frontend is unhealthy"

**Check frontend logs:**
```bash
docker logs iolta_frontend_alpine --tail 20
```

**Common cause:** Nginx permission issues (should be fixed in this version)

### Issue: "Cannot connect to database"

**Reset database password:**
```bash
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c \
  "ALTER USER iolta_user WITH PASSWORD 'YOUR_PASSWORD_FROM_ENV_FILE';"

docker-compose -f docker-compose.alpine.yml restart backend
```

### Issue: "Settings page redirects to dashboard"

This means you're running the OLD images. Solution:
1. Confirm you loaded the FIXED tar file: `docker images | grep iolta`
2. Check image creation date - should be November 12, 2025
3. If old images, reload: `docker load -i iolta_alpine_images_FIXED.tar`
4. Restart containers: `docker-compose -f docker-compose.alpine.yml up -d`

---

## Viewing Logs

**View all logs:**
```bash
docker-compose -f docker-compose.alpine.yml logs -f
```

**View specific container:**
```bash
docker logs iolta_backend_alpine -f
docker logs iolta_frontend_alpine -f
docker logs iolta_db_alpine -f
```

---

## Restarting Services

**Restart all:**
```bash
docker-compose -f docker-compose.alpine.yml restart
```

**Restart specific service:**
```bash
docker-compose -f docker-compose.alpine.yml restart backend
docker-compose -f docker-compose.alpine.yml restart frontend
```

---

## Database Backup/Restore

### Create Backup

```bash
docker exec iolta_db_alpine pg_dump -U iolta_user iolta_guard_db > backup_$(date +%Y%m%d).sql
```

### Restore Backup

```bash
docker exec -i iolta_db_alpine psql -U iolta_user -d iolta_guard_db < backup_file.sql
```

---

## Stopping the Application

**Stop all containers:**
```bash
docker-compose -f docker-compose.alpine.yml down
```

**Stop and remove volumes (DELETES DATABASE!):**
```bash
docker-compose -f docker-compose.alpine.yml down -v
```

---

## Version Information

**What's New:**

| Feature | Old Version | New Version |
|---------|-------------|-------------|
| Settings Page | Missing (404) | ✅ Working |
| Import Page | Missing (404) | ✅ Working |
| QuickBooks API | Not implemented | ✅ Implemented |
| Backend Logs | Permission errors | ✅ Fixed |
| Frontend Nginx | Permission errors | ✅ Fixed |

---

## Support

If you encounter issues:

1. **Check deployment script output** - It's very verbose and will show exactly where it failed
2. **Check container logs** - `docker-compose logs`
3. **Check container status** - `docker-compose ps`
4. **Verify images loaded** - `docker images | grep iolta`

---

## Image Details

```
REPOSITORY                        TAG       SIZE
iolta-guard-backend-alpine       latest    ~400 MB
iolta-guard-frontend-alpine      latest    ~45 MB
postgres                         16-alpine3.20    ~142 MB
```

**Total:** ~587 MB compressed in tar file

---

## Security Notes

- All containers run as non-root users
- Alpine Linux base for minimal attack surface
- Database password should be changed in production (update `.env` file)
- Enable firewall: `ufw allow 80/tcp`

---

## Performance Notes

**Expected deployment time:**
- Load images from tar: 2-3 minutes
- Database startup: 10-20 seconds
- Backend startup: 30-60 seconds
- Frontend startup: 5-10 seconds
- Database import: 1-2 minutes (if applicable)

**Total:** ~5-7 minutes for complete deployment

---

**Deployment Date:** November 12, 2025
**Deployed By:** [Your Name]
**Status:** ✅ All features working and tested
