#!/bin/bash
set -e

echo "=================================================="
echo "IOLTA Guard Trust Account System - Deployment"
echo "Production Server: 138.68.109.92"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root or with sudo${NC}"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Installing...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl start docker
    systemctl enable docker
    echo -e "${GREEN}✓ Docker installed${NC}"
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${BLUE}Installing docker-compose...${NC}"
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✓ docker-compose installed${NC}"
fi

echo ""
echo -e "${BLUE}Step 1: Environment Configuration${NC}"
if [ ! -f .env ]; then
    echo -e "${BLUE}Creating .env file from template...${NC}"
    cp .env.production .env
    
    # Generate random SECRET_KEY
    SECRET_KEY=$(openssl rand -base64 48 | tr -d "=+/" | cut -c1-50)
    sed -i "s/SECRET_KEY=.*/SECRET_KEY=${SECRET_KEY}/" .env
    
    # Generate random DB password
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
    sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=${DB_PASSWORD}/" .env
    
    echo -e "${GREEN}✓ Environment file created with secure keys${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

echo ""
echo -e "${BLUE}Step 2: Stopping existing containers${NC}"
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
echo -e "${GREEN}✓ Stopped${NC}"

echo ""
echo -e "${BLUE}Step 3: Building and starting containers${NC}"
docker-compose -f docker-compose.prod.yml up -d --build
echo -e "${GREEN}✓ Containers started${NC}"

echo ""
echo -e "${BLUE}Step 4: Waiting for database to be ready...${NC}"
sleep 10
docker-compose -f docker-compose.prod.yml exec -T database pg_isready -U iolta_user -d iolta_guard_db || sleep 5
echo -e "${GREEN}✓ Database ready${NC}"

echo ""
echo -e "${BLUE}Step 5: Restoring database from backup${NC}"
if [ -f "database_backup.sql" ]; then
    echo "Found database_backup.sql - restoring..."
    docker cp database_backup.sql iolta_db_prod:/tmp/database_backup.sql
    docker exec -i iolta_db_prod psql -U iolta_user -d iolta_guard_db -f /tmp/database_backup.sql
    echo -e "${GREEN}✓ Database restored from backup${NC}"
else
    echo -e "${BLUE}No database_backup.sql found - running migrations instead${NC}"
    docker-compose -f docker-compose.prod.yml exec -T backend python manage.py migrate
    echo -e "${GREEN}✓ Migrations completed${NC}"
fi

echo ""
echo -e "${BLUE}Step 6: Creating superuser (if needed)${NC}"
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@ioltaguard.com', 'admin123')" | docker-compose -f docker-compose.prod.yml exec -T backend python manage.py shell
echo -e "${GREEN}✓ Superuser ready (admin/admin123)${NC}"

echo ""
echo -e "${BLUE}Step 7: Collecting static files${NC}"
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput || true
echo -e "${GREEN}✓ Static files collected${NC}"

echo ""
echo "=================================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=================================================="
echo ""
echo "Access your application at:"
echo -e "${BLUE}http://138.68.109.92${NC}"
echo ""
echo "Default credentials:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "Important: Change the admin password immediately!"
echo ""
echo "View logs:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "Stop services:"
echo "  docker-compose -f docker-compose.prod.yml down"
echo ""
