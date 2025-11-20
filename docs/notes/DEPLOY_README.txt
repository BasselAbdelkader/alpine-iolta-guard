================================================================================
IOLTA GUARD - CUSTOMER DEPLOYMENT PACKAGE
================================================================================

Version: 1.0
Date: November 13, 2025
Status: PRODUCTION READY - SaaS Automation Complete

================================================================================
QUICK START (5 MINUTES)
================================================================================

On customer server, run:

    bash QUICK_DEPLOY.sh

That's it! The script will:
1. Build Docker images (~2 minutes)
2. Start all services (~20 seconds)
3. Wait for database (~2 minutes)
4. Run migrations (~1 second)
5. Import sample data (optional)
6. Create admin user (you provide credentials)
7. Verify deployment

Total time: ~5 minutes

================================================================================
WHAT YOU RECEIVED
================================================================================

Configuration Files:
  docker-compose.alpine.yml   - Container orchestration
  Dockerfile.alpine.backend   - Backend image definition
  Dockerfile.alpine.frontend  - Frontend image definition
  .env                        - Environment variables (CHECK THIS!)
  account.json                - Service account (if applicable)

Application Code:
  backend/                    - Django application + migrations
  frontend/                   - HTML/CSS/JavaScript
  database/                   - Database initialization scripts

Data:
  essential_data_only.sql     - Sample data (79 clients, 81 cases, 100 transactions)

Scripts:
  QUICK_DEPLOY.sh             - Automated deployment script

Documentation:
  CUSTOMER_DEPLOYMENT_WITH_DATA.md  - Detailed deployment guide
  MIGRATION_ARCHITECTURE.md         - Technical architecture
  DEPLOYMENT_READY_SUMMARY.md       - Complete summary
  DEPLOY_README.txt                 - This file

================================================================================
REQUIREMENTS
================================================================================

Server Requirements:
  - OS: Linux (Ubuntu 20.04+, Debian 11+, RHEL 8+)
  - RAM: 2GB minimum, 4GB recommended
  - Disk: 10GB free space minimum
  - Docker: Version 20.10+
  - Docker Compose: Version 1.29+

Network Requirements:
  - Port 80 available (web interface)
  - Port 5432 available (PostgreSQL - internal only)
  - Port 8000 available (Django API - internal only)

Permissions:
  - Root access OR sudo privileges
  - Ability to run Docker commands

================================================================================
MANUAL DEPLOYMENT (STEP-BY-STEP)
================================================================================

If you prefer not to use the script:

1. Build images:
   docker-compose -f docker-compose.alpine.yml build

2. Start services:
   docker-compose -f docker-compose.alpine.yml up -d

3. Wait 2 minutes for database to initialize:
   sleep 120

4. Run migrations (creates database schema):
   docker exec iolta_backend_alpine python manage.py migrate

5. (OPTIONAL) Import sample data:
   cat essential_data_only.sql | docker exec -i iolta_db_alpine psql -U iolta_user -d iolta_guard_db

6. Create admin user:
   docker exec -it iolta_backend_alpine python manage.py createsuperuser

7. Verify:
   docker-compose -f docker-compose.alpine.yml ps
   curl http://localhost/

================================================================================
DEPLOYMENT OPTIONS
================================================================================

Option A: Empty Database (New Law Firm)
  - Skip step 5 (don't import essential_data_only.sql)
  - Database will be completely empty
  - Ready for customer to enter their own data

Option B: With Sample Data (Demo/Testing)
  - Include step 5 (import essential_data_only.sql)
  - Database will have 79 clients, 81 cases, 100 transactions
  - Good for evaluation and testing

================================================================================
WHAT GETS CREATED
================================================================================

Docker Containers:
  iolta_db_alpine         - PostgreSQL 16 database
  iolta_backend_alpine    - Django backend (Python 3.11)
  iolta_frontend_alpine   - Nginx frontend

Database Tables (20+):
  clients, cases, vendors, bank_accounts, bank_transactions,
  settlements, law_firm, settings, and more...

Network:
  iolta_network           - Internal Docker network

Volumes:
  iolta_db_data           - PostgreSQL data persistence
  iolta_static_files      - Django static files
  iolta_media_files       - Uploaded media

================================================================================
ACCESSING THE APPLICATION
================================================================================

Web Interface:
  URL: http://SERVER_IP/
  or:  http://localhost/ (if on server directly)

Login:
  Username: (what you created in step 6)
  Password: (what you created in step 6)

Admin Panel:
  URL: http://SERVER_IP/admin/

API Endpoints:
  Base: http://SERVER_IP/api/v1/
  Docs: http://SERVER_IP/api/v1/docs/

================================================================================
VERIFICATION
================================================================================

Check container status:
  docker-compose -f docker-compose.alpine.yml ps

All should show "Up" and "healthy":
  iolta_db_alpine         Up (healthy)
  iolta_backend_alpine    Up (healthy)
  iolta_frontend_alpine   Up

Check logs:
  docker-compose -f docker-compose.alpine.yml logs backend
  docker-compose -f docker-compose.alpine.yml logs database
  docker-compose -f docker-compose.alpine.yml logs frontend

Check database:
  docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "\dt"

Should show 20+ tables including:
  clients, cases, vendors, bank_accounts, bank_transactions, etc.

Check data counts:
  docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "
    SELECT
      (SELECT COUNT(*) FROM clients) as clients,
      (SELECT COUNT(*) FROM cases) as cases,
      (SELECT COUNT(*) FROM bank_transactions) as transactions;
  "

If you imported sample data:
  clients: 79
  cases: 81
  transactions: 100

If you didn't import sample data:
  clients: 0
  cases: 0
  transactions: 0

================================================================================
COMMON ISSUES
================================================================================

Issue: "Port 80 already in use"
Fix:
  - Stop existing web server: sudo systemctl stop apache2 nginx
  - Or change port in docker-compose.alpine.yml:
    ports:
      - "8080:80"  # Use port 8080 instead

Issue: "Cannot connect to Docker daemon"
Fix:
  - Start Docker: sudo systemctl start docker
  - Add user to docker group: sudo usermod -aG docker $USER
  - Log out and back in

Issue: "Containers unhealthy"
Fix:
  - Wait longer (database needs ~2 minutes first start)
  - Check logs: docker-compose logs
  - Restart: docker-compose restart

Issue: "Migration fails"
Fix:
  - Check backend logs: docker-compose logs backend
  - Verify database is running: docker exec iolta_db_alpine pg_isready
  - Try again: docker exec iolta_backend_alpine python manage.py migrate

Issue: "Can't access web interface"
Fix:
  - Check firewall: sudo ufw allow 80
  - Check container status: docker-compose ps
  - Check nginx logs: docker-compose logs frontend

================================================================================
MAINTENANCE
================================================================================

Stop services:
  docker-compose -f docker-compose.alpine.yml down

Start services:
  docker-compose -f docker-compose.alpine.yml up -d

Restart services:
  docker-compose -f docker-compose.alpine.yml restart

View logs (real-time):
  docker-compose -f docker-compose.alpine.yml logs -f backend

Backup database:
  docker exec iolta_db_alpine pg_dump -U iolta_user -d iolta_guard_db > backup.sql

Restore database:
  cat backup.sql | docker exec -i iolta_db_alpine psql -U iolta_user -d iolta_guard_db

Update application (new version):
  1. Stop services: docker-compose down
  2. Replace files with new version
  3. Rebuild: docker-compose build
  4. Start: docker-compose up -d
  5. Run migrations: docker exec iolta_backend_alpine python manage.py migrate

================================================================================
SECURITY NOTES
================================================================================

IMPORTANT - Before Production:

1. Change .env file:
   - Generate new SECRET_KEY
   - Change DATABASE_PASSWORD
   - Set DEBUG=False

2. Set up SSL/TLS:
   - Install Let's Encrypt certificate
   - Update nginx configuration
   - Redirect HTTP to HTTPS

3. Configure firewall:
   - Allow only port 80 (HTTP) and 443 (HTTPS)
   - Block direct access to 5432 (PostgreSQL)
   - Block direct access to 8000 (Django)

4. Set up backups:
   - Daily database dumps
   - Store backups off-server
   - Test restore procedures

5. Set up monitoring:
   - Container health checks
   - Database performance
   - Disk space alerts

================================================================================
SUPPORT
================================================================================

For deployment issues:
  1. Check logs: docker-compose logs
  2. Review documentation: MIGRATION_ARCHITECTURE.md
  3. Check container status: docker-compose ps
  4. Verify .env settings

For application issues:
  1. Check Django logs: docker-compose logs backend
  2. Check database logs: docker-compose logs database
  3. Access Django shell: docker exec -it iolta_backend_alpine python manage.py shell

For data issues:
  1. Access database: docker exec -it iolta_db_alpine psql -U iolta_user -d iolta_guard_db
  2. Check migrations: docker exec iolta_backend_alpine python manage.py showmigrations
  3. Check data counts: SELECT COUNT(*) FROM clients;

================================================================================
TECHNICAL DETAILS
================================================================================

Architecture:
  - 3-tier: Frontend (Nginx) → Backend (Django) → Database (PostgreSQL)
  - Microservices: Each component in separate container
  - Persistent storage: Database volume persists across restarts

Technology Stack:
  - Frontend: HTML5, JavaScript, Bootstrap 5
  - Backend: Django 5.1.3, Django REST Framework
  - Database: PostgreSQL 16
  - Server: Gunicorn WSGI
  - Web Server: Nginx
  - Containers: Docker with Alpine Linux

Database Size:
  - Empty: ~15 MB
  - With sample data: ~18 MB
  - Expected growth: ~50 MB per 1000 clients

Container Sizes:
  - Backend: ~350 MB (Alpine Linux + Python + Django)
  - Frontend: ~50 MB (Alpine Linux + Nginx)
  - Database: ~240 MB (PostgreSQL 16 Alpine)

Performance:
  - Build time: ~2 minutes
  - Startup time: ~20 seconds
  - Migration time: <1 second
  - First request: ~500ms
  - Typical request: <100ms

================================================================================
WHAT'S INCLUDED IN SAMPLE DATA
================================================================================

If you imported essential_data_only.sql:

Law Firm:
  - IOLTA Guard Insurance Law
  - New York, NY
  - Full contact information

Clients: 79
  - Personal injury cases
  - Workers compensation
  - Medical malpractice
  - Product liability

Cases: 81
  - Various case types
  - Different statuses (Open, Pending Settlement, Closed)
  - Date ranges from 2024-2025

Vendors: 9
  - Medical providers
  - Legal services
  - Court filing services
  - Medical records companies

Bank Transactions: 100
  - Deposits (client funds)
  - Withdrawals (vendor payments)
  - Date range: Last 6 months
  - Realistic amounts

Bank Account: 1
  - Chase Bank IOLTA Trust Account
  - Account #****9876

Settings:
  - Case statuses
  - Transaction types
  - Vendor types
  - System settings

================================================================================
NEXT STEPS AFTER DEPLOYMENT
================================================================================

1. Login to web interface
2. Review law firm settings (Settings → Law Firm Information)
3. Update law firm information with customer details
4. If sample data imported, review and delete sample records
5. Create real client records
6. Set up bank account information
7. Begin transaction tracking
8. Train customer on system usage

================================================================================
MIGRATION-BASED DEPLOYMENT
================================================================================

This deployment uses Django migrations for full SaaS automation:

Benefits:
  ✅ No manual database setup required
  ✅ Schema created automatically
  ✅ Version-controlled schema changes
  ✅ Repeatable deployments
  ✅ Easy updates (new migrations apply automatically)

How it works:
  1. docker-compose build → Includes migration files in container
  2. python manage.py migrate → Reads migrations, creates tables
  3. Result → Fully working database schema

For new customers:
  - Same process, no changes needed
  - Migrations ensure identical schema every time

For updates:
  - New migration files included in update
  - Run migrate → Schema upgraded automatically
  - Zero manual SQL required

================================================================================
FILES YOU CAN MODIFY
================================================================================

SAFE TO MODIFY:
  ✅ .env - Environment variables (MUST customize for production)
  ✅ Law firm info via web interface (Settings → Law Firm Information)
  ✅ docker-compose.alpine.yml ports (if port 80 conflicts)

DO NOT MODIFY:
  ❌ backend/ folder (application code)
  ❌ frontend/ folder (web interface)
  ❌ Dockerfile.alpine.* (image definitions)
  ❌ Migration files (database schema)

================================================================================
CLEANUP (IF NEEDED)
================================================================================

Complete removal (WARNING: Deletes all data):

  # Stop and remove containers
  docker-compose -f docker-compose.alpine.yml down -v

  # Remove images
  docker rmi iolta-guard-backend-alpine:latest
  docker rmi iolta-guard-frontend-alpine:latest

  # Remove files
  rm -rf /root/iolta

================================================================================
SUCCESS INDICATORS
================================================================================

Deployment successful if:
  ✅ All 3 containers show "Up (healthy)"
  ✅ Web interface loads at http://localhost/
  ✅ Login page appears
  ✅ Can login with created admin credentials
  ✅ Dashboard loads after login
  ✅ 20+ database tables exist
  ✅ No errors in logs

================================================================================
PRODUCTION CHECKLIST
================================================================================

Before going live:
  [ ] Changed SECRET_KEY in .env
  [ ] Changed DATABASE_PASSWORD in .env
  [ ] Set DEBUG=False in .env
  [ ] Updated law firm information
  [ ] Deleted sample data (if imported)
  [ ] Set up SSL/TLS certificate
  [ ] Configured firewall
  [ ] Set up automated backups
  [ ] Tested backup restore
  [ ] Configured monitoring
  [ ] Documented admin credentials (securely)
  [ ] Trained customer on system
  [ ] Verified all features work

================================================================================
END OF DEPLOYMENT README
================================================================================

For detailed technical documentation, see:
  - MIGRATION_ARCHITECTURE.md (technical details)
  - CUSTOMER_DEPLOYMENT_WITH_DATA.md (step-by-step guide)
  - DEPLOYMENT_READY_SUMMARY.md (complete summary)

Questions? Review the documentation or check Docker logs.

Good luck with your deployment!

================================================================================
