# Customer Deployment - Production Ready

## Files to Transfer

```bash
# On localhost
cd /home/amin/Projects/ve_demo

# Transfer to customer (NO data file needed)
scp docker-compose.alpine.yml Dockerfile.alpine.* .env account.json root@customer-server:/root/iolta/
scp -r backend/ frontend/ database/ root@customer-server:/root/iolta/
```

---

## On Customer Server - Fresh Deployment

```bash
cd /root/iolta

# Step 1: Build images
docker-compose -f docker-compose.alpine.yml build

# Step 2: Start all services
docker-compose -f docker-compose.alpine.yml up -d

# Step 3: Wait for services to be healthy (2 minutes)
sleep 120

# Step 4: Run migrations (creates schema)
docker exec iolta_backend_alpine python manage.py migrate

# Step 5: Create superuser
docker exec -it iolta_backend_alpine python manage.py createsuperuser

# Step 6: Verify
docker-compose -f docker-compose.alpine.yml ps
curl http://localhost/
```

---

## What This Does

1. **Build** - Compiles Docker images with all code
2. **Start** - Launches database, backend, frontend
3. **Migrate** - Creates all tables, indexes, constraints (EMPTY database)
4. **Superuser** - Creates admin account
5. **Verify** - Checks everything is running

---

## Result

- ✅ Fully working IOLTA Guard system
- ✅ Empty database ready for customer data
- ✅ All tables, indexes, constraints created
- ✅ Admin account ready
- ✅ Web interface accessible

**Customer can immediately start:**
- Adding their clients
- Creating cases
- Entering transactions
- Managing trust accounts

---

## For Customers Who Need Migration from Old System

If customer has existing data to import:

1. **They export their data** from old system
2. **They provide CSV files** (clients.csv, cases.csv, etc.)
3. **Use the CSV Import feature** in IOLTA Guard web interface
   - Settings → Import CSV Data
   - Upload their files
   - Review preview
   - Confirm import

---

## Troubleshooting

**If migrations fail:**
```bash
docker-compose -f docker-compose.alpine.yml logs backend
```

**If containers unhealthy:**
```bash
docker-compose -f docker-compose.alpine.yml restart
docker-compose -f docker-compose.alpine.yml ps
```

**If web interface doesn't load:**
```bash
# Check all services
docker-compose -f docker-compose.alpine.yml ps

# Check backend logs
docker-compose -f docker-compose.alpine.yml logs backend

# Check frontend logs
docker-compose -f docker-compose.alpine.yml logs frontend
```

---

## Summary

- **Migrations**: ✅ Working (creates schema automatically)
- **Empty Database**: ✅ Ready for customer data
- **SaaS Ready**: ✅ Fully automated provisioning
- **CSV Import**: ✅ Available via web interface

**Deployment time:** ~5 minutes
**Result:** Production-ready IOLTA Guard system
