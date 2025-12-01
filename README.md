# IOLTA Guard Trust Account System - Production Deployment

## Quick Start

```bash
# 1. Extract the tarball
tar -xzf iolta-production.tar.gz
cd iolta-production

# 2. Run deployment script (as root/sudo)
sudo ./deploy.sh
```

That's it! The application will be available at http://138.68.109.92

## What's Included

- ✅ Complete backend (Django/Python)
- ✅ Complete frontend (HTML/JS)
- ✅ Database schema (twentysixnovember.sql)
- ✅ Docker configuration
- ✅ Nginx reverse proxy
- ✅ Automatic deployment script

## System Requirements

- Ubuntu 20.04+ (or any Linux with Docker support)
- 2GB RAM minimum (4GB recommended)
- 20GB disk space
- Docker & Docker Compose (auto-installed by deploy script)

## File Structure

```
iolta-production/
├── deploy.sh                    # Main deployment script
├── docker-compose.prod.yml      # Production Docker setup
├── .env.production              # Environment template
├── README.md                    # This file
├── backend/                     # Django application
│   ├── apps/                    # All Django apps
│   ├── manage.py
│   ├── requirements.txt
│   └── trust_account_project/   # Django project settings
├── frontend/                    # Static frontend files
│   ├── html/                    # HTML pages
│   ├── js/                      # JavaScript files
│   └── css/                     # Stylesheets
├── nginx/                       # Nginx configuration
│   └── nginx.conf
└── sql/                         # Database schema
    └── init.sql                 # Initial schema (twentysixnovember.sql)
```

## Manual Deployment Steps

If you prefer manual deployment:

### 1. Configure Environment
```bash
cp .env.production .env
# Edit .env and set secure passwords:
# - DB_PASSWORD
# - SECRET_KEY
nano .env
```

### 2. Start Services
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Wait for Database
```bash
docker-compose -f docker-compose.prod.yml exec database pg_isready -U iolta_user
```

### 4. Run Migrations
```bash
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

### 5. Create Superuser
```bash
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

## Database Schema

The database will be initialized with the **twentysixnovember.sql** schema, which includes:

### Key Features:
- ✅ Single `reference_number` field (consolidated check_number)
- ✅ Single `client_name` field (consolidated first_name/last_name)
- ✅ Check printing with `check_is_printed` boolean
- ✅ Check sequence management
- ✅ Complete audit trail
- ✅ 3-way settlement support

### Tables (28 total):
- bank_transactions
- clients
- cases
- vendors
- bank_accounts
- settlements
- check_sequences
- law_firm
- And 20 more...

## Default Credentials

**⚠️ IMPORTANT: Change these immediately after first login!**

- **Username:** admin
- **Password:** admin123

## Management Commands

### View Logs
```bash
docker-compose -f docker-compose.prod.yml logs -f

# Specific service logs
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
docker-compose -f docker-compose.prod.yml logs -f database
```

### Stop Services
```bash
docker-compose -f docker-compose.prod.yml down
```

### Restart Services
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Database Backup
```bash
docker-compose -f docker-compose.prod.yml exec database pg_dump -U iolta_user iolta_guard_db > backup_$(date +%Y%m%d).sql
```

### Database Restore
```bash
docker-compose -f docker-compose.prod.yml exec -T database psql -U iolta_user -d iolta_guard_db < backup.sql
```

## Accessing Services

- **Main Application:** http://138.68.109.92
- **Django Admin:** http://138.68.109.92/admin
- **API Endpoints:** http://138.68.109.92/api/
- **Health Check:** http://138.68.109.92/health

## Troubleshooting

### Check Container Status
```bash
docker-compose -f docker-compose.prod.yml ps
```

### Check Backend Health
```bash
docker-compose -f docker-compose.prod.yml exec backend python manage.py check
```

### Database Connection Test
```bash
docker-compose -f docker-compose.prod.yml exec database psql -U iolta_user -d iolta_guard_db -c "SELECT COUNT(*) FROM clients;"
```

### Rebuild Everything
```bash
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d --build
```

## Security Recommendations

1. **Change default admin password** immediately
2. **Set strong passwords** in .env file
3. **Enable HTTPS** (use Let's Encrypt)
4. **Configure firewall** (allow only ports 80, 443, 22)
5. **Regular backups** (database and files)
6. **Update regularly** (Docker images and system packages)

## SSL/HTTPS Setup (Optional)

To enable HTTPS with Let's Encrypt:

```bash
# Install certbot
apt-get update && apt-get install -y certbot python3-certbot-nginx

# Get certificate
certbot --nginx -d yourdomain.com

# Auto-renewal
certbot renew --dry-run
```

## Support

For issues or questions:
- Check logs: `docker-compose -f docker-compose.prod.yml logs`
- Review database: `docker-compose -f docker-compose.prod.yml exec database psql -U iolta_user -d iolta_guard_db`
- Verify environment: `cat .env`

## Version Info

- **Application:** IOLTA Guard Trust Account System v1.0.0
- **Database Schema:** twentysixnovember.sql (Nov 26, 2025)
- **Python:** 3.12
- **Django:** 5.1.3
- **PostgreSQL:** 16
- **Nginx:** Latest Alpine

## License

Proprietary - IOLTA Guard Trust Account System
