# Customer Deployment - Final Working Version

**Date:** November 13, 2025
**Status:** READY FOR DEPLOYMENT

---

## Files to Transfer

```bash
# On localhost - prepare package
cd /home/amin/Projects/ve_demo

tar -czf iolta-deploy.tar.gz \
  docker-compose.alpine.yml \
  Dockerfile.alpine.backend \
  Dockerfile.alpine.frontend \
  .env \
  account.json \
  backend/ \
  frontend/ \
  database/

# Transfer to customer
scp iolta-deploy.tar.gz root@customer-server:/root/
```

---

## Customer Server Deployment

```bash
# Extract package
cd /root
tar -xzf iolta-deploy.tar.gz
cd ve_demo

# Stop and clean everything
docker-compose -f docker-compose.alpine.yml down -v
docker volume prune -f

# Build images
docker-compose -f docker-compose.alpine.yml build

# Start all services
docker-compose -f docker-compose.alpine.yml up -d

# Wait for services to be healthy (2 minutes)
sleep 120

# Run migrations (will auto-merge bank_accounts)
docker exec iolta_backend_alpine python manage.py makemigrations --merge --noinput
docker exec iolta_backend_alpine python manage.py migrate

# Verify tables created correctly
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "\dt" | grep -E "clients|cases|law_firm|bank"

# Should show:
# clients                        | table
# cases                          | table
# law_firm                       | table
# bank_accounts                  | table
# bank_transactions              | table

# Create superuser
docker exec -it iolta_backend_alpine python manage.py createsuperuser

# Create law firm
docker exec iolta_backend_alpine python manage.py shell << 'PYTHON'
from apps.settings.models import LawFirm
if not LawFirm.objects.exists():
    LawFirm.objects.create(
        firm_name='Customer Law Firm',
        doing_business_as='',
        address_line1='123 Main Street',
        address_line2='',
        city='New York',
        state='NY',
        zip_code='10001',
        phone='(555) 123-4567',
        fax='',
        email='info@lawfirm.com',
        website='',
        principal_attorney='John Doe',
        attorney_bar_number='12345',
        attorney_state='NY',
        trust_account_required=True,
        iolta_compliant=True,
        tax_id='12-3456789',
        state_registration='',
        is_active=True
    )
    print('✅ Law firm created')
else:
    print('✅ Law firm already exists')
PYTHON
```

---

## Verification

```bash
# Check all containers healthy
docker-compose -f docker-compose.alpine.yml ps

# Expected output:
# iolta_db_alpine        Up (healthy)
# iolta_backend_alpine   Up (healthy)
# iolta_frontend_alpine  Up (healthy)

# Test application
curl http://localhost/
curl http://localhost/api/health/

# Check logs for errors
docker-compose -f docker-compose.alpine.yml logs --tail=50
```

---

## Migration Files Fixed

1. **clients/migrations/0001_initial.py** - Fixed with all fields matching database
2. **dashboard/migrations/0001_initial.py** - DELETED (duplicate law_firm creation)
3. **bank_accounts/migrations** - Will auto-merge on first run

---

## Troubleshooting

### If migrations fail:
```bash
# Check which migrations applied
docker exec iolta_backend_alpine python manage.py showmigrations

# If stuck, drop database and restart
docker-compose -f docker-compose.alpine.yml down -v
docker-compose -f docker-compose.alpine.yml up -d
# Wait and retry migrations
```

### If tables have wrong names (clients_client instead of clients):
```bash
# The migrations are now fixed - this shouldn't happen
# But if it does, the migration file has db_table specified
```

---

## What Was Fixed

1. ✅ Dashboard migration creating duplicate law_firm table - DELETED
2. ✅ Clients migration missing db_table specification - FIXED
3. ✅ Clients migration missing fields (is_active, client_type, import_batch_id) - FIXED
4. ✅ Sample data migrations with wrong fields - DELETED
5. ✅ Bank accounts migration conflicts - AUTO-MERGED

---

**Ready for automated deployment!**

