# IOLTA Guard - Production Deployment Package

**Date Created:** November 4, 2025
**Version:** 1.0.0

## What's Included

This deployment package contains:

1. **Docker Images** (pre-built and ready to run):
   - `iolta-backend-image.tar` - Django/Python backend application
   - `iolta-frontend-image.tar` - Nginx frontend with HTML/JS/CSS

2. **Source Code** (in `source/` directory):
   - `trust_account/` - Django backend source code
   - `frontend/` - HTML, JavaScript, CSS files
   - `docker-compose-simple-production.yml` - Docker Compose configuration
   - `account.json` - Service account configuration
   - `insurance_demo_data.sql` - Demo data SQL script

## Recent Changes (November 4, 2025)

### 1. Reissue Logic Fix
- When reissuing a check with "TO PRINT" reference:
  - Voided transaction: Preserves original date, reference changed to "Voided"
  - Reversal deposit: Blank reference (shows transaction number)
  - New withdrawal: Reference set to "TO PRINT" (ready for printing with new check number)

### 2. Modal Width Updates
- Case detail modal: Increased to 85vw for better field visibility
- Bank transactions modal: Increased to 70%
- "To Print" checkbox now properly visible when selecting Withdrawal

### 3. Cache Busting
- All HTML files updated with new cache version: `v=1762170895`
- JavaScript files include cache bust parameters

## Production Deployment Steps

### Step 1: Transfer Files to Production Server

```bash
# On your local machine
cd /Users/bassel/Desktop/ve_demo
tar -czf iolta-deployment.tar.gz iolta-deployment/

# Transfer to production server (replace with your server IP)
scp iolta-deployment.tar.gz user@your-server-ip:/home/user/
```

### Step 2: Extract and Load on Production Server

```bash
# SSH into your production server
ssh user@your-server-ip

# Extract the deployment package
tar -xzf iolta-deployment.tar.gz
cd iolta-deployment

# Load the Docker images
docker load -i iolta-backend-image.tar
docker load -i iolta-frontend-image.tar

# Verify images are loaded
docker images | grep iolta-guard
```

### Step 3: Configure Environment Variables

Create a `.env` file in the deployment directory:

```bash
nano .env
```

Add the following (replace with your actual values):

```env
# Database Configuration
DB_NAME=iolta_guard_db
DB_USER=iolta_user
DB_PASSWORD=YOUR_SECURE_PASSWORD_HERE

# Django Configuration
DJANGO_SECRET_KEY=YOUR_DJANGO_SECRET_KEY_HERE
DEBUG=False

# Optional: Customize these if needed
ALLOWED_HOSTS=your-domain.com,your-server-ip
```

### Step 4: Set Up Production Environment

```bash
# Create necessary directories
mkdir -p backups database/init

# Copy docker-compose file to root
cp source/docker-compose-simple-production.yml docker-compose.yml

# Copy account.json
cp source/account.json ./
```

### Step 5: Start the Application

```bash
# Start all containers
docker-compose up -d

# Check container status
docker ps

# View logs
docker-compose logs -f
```

### Step 6: Initialize Database (First Time Only)

```bash
# Wait for containers to be healthy (about 30-60 seconds)
docker-compose ps

# Run migrations
docker exec -it iolta_backend python manage.py migrate

# Load demo data (optional)
docker cp source/insurance_demo_data.sql iolta_db:/tmp/
docker exec -it iolta_db psql -U iolta_user -d iolta_guard_db -f /tmp/insurance_demo_data.sql

# Create superuser (optional)
docker exec -it iolta_backend python manage.py createsuperuser
```

### Step 7: Verify Deployment

1. **Check application is running:**
   ```bash
   curl http://localhost/
   ```

2. **Access the application:**
   - Open browser: `http://your-server-ip/`
   - Login with demo credentials or your created superuser

3. **Test key features:**
   - Add a new transaction with "TO PRINT" checkbox (when Withdrawal selected)
   - Reissue a check and verify:
     - New withdrawal shows "TO PRINT" reference
     - Reversal deposit shows transaction number
     - Voided check shows "Voided" reference

## Updating an Existing Deployment

If you're updating an existing production deployment:

```bash
# Stop containers
docker-compose down

# Load new images
docker load -i iolta-backend-image.tar
docker load -i iolta-frontend-image.tar

# Start with new images
docker-compose up -d

# Run any new migrations
docker exec -it iolta_backend python manage.py migrate

# Check logs for any issues
docker-compose logs -f
```

## Troubleshooting

### Containers won't start
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs database

# Check disk space
df -h

# Verify environment variables
cat .env
```

### Database connection issues
```bash
# Check database is running
docker exec -it iolta_db psql -U iolta_user -d iolta_guard_db -c "\l"

# Reset database password if needed
docker exec -it iolta_db psql -U postgres -c "ALTER USER iolta_user WITH PASSWORD 'new_password';"
```

### Application not accessible
```bash
# Check if port 80 is open
sudo netstat -tlnp | grep :80

# Check firewall
sudo ufw status

# Check Nginx logs
docker logs iolta_frontend
```

### Cache issues in browser
```bash
# Verify cache version in HTML files
docker exec -it iolta_frontend cat /usr/share/nginx/html/html/case-detail.html | grep "v="

# If needed, instruct users to:
# - Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
# - Clear browser cache
```

## Database Backup

### Manual Backup
```bash
docker exec -it iolta_db pg_dump -U iolta_user iolta_guard_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore from Backup
```bash
docker cp backup.sql iolta_db:/tmp/
docker exec -it iolta_db psql -U iolta_user -d iolta_guard_db -f /tmp/backup.sql
```

## Security Recommendations

1. **Change default passwords** in `.env` file
2. **Enable SSL/HTTPS** (not included in this simple production setup)
3. **Set up regular backups** (daily recommended)
4. **Monitor logs** for security issues
5. **Keep Docker images updated** regularly
6. **Restrict network access** to necessary ports only
7. **Use firewall rules** to limit access

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review Django admin: `http://your-server-ip/admin/`
- Check database: `docker exec -it iolta_db psql -U iolta_user -d iolta_guard_db`

## Version History

### v1.0.0 (November 4, 2025)
- Fixed reissue logic for "TO PRINT" checks
- Increased modal widths for better visibility
- Updated cache busting for all HTML files
- "To Print" checkbox now shows/hides based on transaction type
- Database sequences fixed after demo data load
- Preserved original transaction dates when voiding during reissue

---

**Package Generated:** November 4, 2025
**Django Version:** 5.1.3
**Python Version:** 3.12
**PostgreSQL Version:** 16
**Nginx Version:** Alpine latest
