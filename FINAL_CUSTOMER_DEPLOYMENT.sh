#!/bin/bash
# IOLTA Guard - Customer Deployment Script
# For SaaS automated provisioning

set -e

echo "========================================="
echo "IOLTA Guard - Automated Deployment"
echo "========================================="

# Step 1: Build images
echo "Step 1/6: Building Docker images..."
docker-compose -f docker-compose.alpine.yml build

# Step 2: Start database
echo "Step 2/6: Starting database..."
docker-compose -f docker-compose.alpine.yml up -d database
sleep 30

# Step 3: Initialize database schema
echo "Step 3/6: Initializing database schema..."
cat localhost_full_dump.sql | docker exec -i iolta_db_alpine psql -U iolta_user -d iolta_guard_db

# Step 4: Start all services
echo "Step 4/6: Starting all services..."
docker-compose -f docker-compose.alpine.yml up -d

# Step 5: Mark migrations as applied (schema from dump)
echo "Step 5/6: Syncing Django migrations..."
sleep 30
docker exec iolta_backend_alpine python manage.py migrate --fake-initial

# Step 6: Create superuser
echo "Step 6/6: System ready - create admin user..."
echo "Run: docker exec -it iolta_backend_alpine python manage.py createsuperuser"

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "Access: http://localhost/"
echo "========================================="
