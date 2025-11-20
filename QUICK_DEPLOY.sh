#!/bin/bash
# IOLTA Guard - Quick Customer Deployment Script
# Run this on customer server after transferring files

set -e  # Exit on error

echo "========================================="
echo "IOLTA Guard - Customer Deployment"
echo "========================================="
echo ""

# Step 1: Build images
echo "[Step 1/6] Building Docker images..."
docker-compose -f docker-compose.alpine.yml build
echo "✅ Images built"
echo ""

# Step 2: Start services
echo "[Step 2/6] Starting services..."
docker-compose -f docker-compose.alpine.yml up -d
echo "✅ Services started"
echo ""

# Step 3: Wait for database
echo "[Step 3/6] Waiting for services to be healthy (120 seconds)..."
sleep 120
echo "✅ Services ready"
echo ""

# Step 4: Run migrations
echo "[Step 4/6] Running database migrations..."
docker exec iolta_backend_alpine python manage.py migrate
echo "✅ Migrations applied"
echo ""

# Step 5: Create superuser
echo "[Step 5/6] Create admin user..."
echo "⚠️  You will be prompted to create an admin account"
docker exec -it iolta_backend_alpine python manage.py createsuperuser
echo "✅ Admin user created"
echo ""

# Step 6: Verify
echo "[Step 6/6] Verifying deployment..."
echo ""
echo "Container Status:"
docker-compose -f docker-compose.alpine.yml ps
echo ""
echo "Database Tables:"
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "SELECT schemaname, tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;" | head -15
echo ""
echo "Data Counts:"
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "
SELECT
  (SELECT COUNT(*) FROM clients) as clients,
  (SELECT COUNT(*) FROM cases) as cases,
  (SELECT COUNT(*) FROM vendors) as vendors,
  (SELECT COUNT(*) FROM bank_transactions) as transactions;
"
echo ""

# Test web interface
echo "Testing web interface..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Web interface responding (HTTP $HTTP_CODE)"
else
    echo "⚠️  Web interface returned HTTP $HTTP_CODE"
fi
echo ""

echo "========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "========================================="
echo ""
echo "Access your IOLTA Guard instance:"
echo "  URL: http://$(hostname -I | awk '{print $1}')/"
echo "  or:  http://localhost/"
echo ""
echo "Login with the admin credentials you just created."
echo ""
echo "For troubleshooting, check logs:"
echo "  docker-compose -f docker-compose.alpine.yml logs backend"
echo "  docker-compose -f docker-compose.alpine.yml logs database"
echo ""
echo "To stop services:"
echo "  docker-compose -f docker-compose.alpine.yml down"
echo ""
echo "To restart services:"
echo "  docker-compose -f docker-compose.alpine.yml restart"
echo "========================================="
