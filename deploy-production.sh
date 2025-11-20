#!/bin/bash
# ============================================================================
# IOLTA Guard - Production Deployment Script
# ============================================================================
# This script deploys IOLTA Guard to production on http://138.68.109.92
# All 3 Docker containers will be started: database, backend, frontend
# Backend is NOT exposed publicly - only accessible through nginx proxy
# ============================================================================

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_header() {
    echo ""
    echo "========================================="
    echo "$1"
    echo "========================================="
}

# ============================================================================
# Pre-flight Checks
# ============================================================================

print_header "IOLTA Guard - Production Deployment"
print_info "Target: http://138.68.109.92"
echo ""

# Check if running as root (needed for some operations)
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root. This is okay for production setup."
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi
print_success "Docker is installed"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi
print_success "Docker Compose is installed"

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    print_info "Please create .env file from .env.production-template"
    print_info "Run: cp .env.production-template .env"
    print_info "Then update SECRET_KEY and DB_PASSWORD"
    exit 1
fi
print_success ".env file found"

# Verify .env has required values
if grep -q "YOUR-SECRET-KEY-HERE" .env || grep -q "YOUR-SECURE-DATABASE-PASSWORD" .env; then
    print_error ".env file contains template values!"
    print_info "Please update SECRET_KEY and DB_PASSWORD in .env file"
    exit 1
fi
print_success ".env file configured"

# Check if account.json exists (optional)
if [ ! -f "account.json" ]; then
    print_warning "account.json not found. Creating default..."
    cat > account.json << 'EOF'
{
    "application": {
        "secret_key": "",
        "allowed_hosts": ["localhost", "127.0.0.1", "138.68.109.92"]
    },
    "database": {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "iolta_guard_db"
        }
    }
}
EOF
    print_success "Created default account.json"
else
    print_success "account.json found"
fi

# ============================================================================
# Deployment Steps
# ============================================================================

# Step 1: Stop existing containers
print_header "Step 1: Stopping existing containers"
docker-compose -f docker-compose-simple-production.yml down || true
print_success "Existing containers stopped"

# Step 2: Build Docker images
print_header "Step 2: Building Docker images"
print_info "This may take 5-10 minutes on first run..."
if docker-compose -f docker-compose-simple-production.yml build; then
    print_success "Docker images built successfully"
else
    print_error "Docker build failed"
    exit 1
fi

# Step 3: Start database
print_header "Step 3: Starting database"
docker-compose -f docker-compose-simple-production.yml up -d database
print_info "Waiting for database to be ready (30 seconds)..."
sleep 30
print_success "Database started"

# Step 4: Run database migrations
print_header "Step 4: Running database migrations"
if docker-compose -f docker-compose-simple-production.yml run --rm backend python manage.py migrate; then
    print_success "Database migrations completed"
else
    print_error "Database migrations failed"
    print_info "Check logs: docker-compose -f docker-compose-simple-production.yml logs backend"
    exit 1
fi

# Step 5: Collect static files
print_header "Step 5: Collecting static files"
if docker-compose -f docker-compose-simple-production.yml run --rm backend python manage.py collectstatic --noinput; then
    print_success "Static files collected"
else
    print_warning "Static files collection had issues (may not be critical)"
fi

# Step 6: Start all services
print_header "Step 6: Starting all services"
print_info "Starting: database, backend, frontend"
if docker-compose -f docker-compose-simple-production.yml up -d; then
    print_success "All services started"
else
    print_error "Service startup failed"
    exit 1
fi

# Step 7: Wait for services to be ready
print_header "Step 7: Waiting for services to be ready"
print_info "Waiting 20 seconds for services to initialize..."
sleep 20

# Step 8: Health checks
print_header "Step 8: Running health checks"

# Check backend health
if docker-compose -f docker-compose-simple-production.yml exec -T backend curl -f http://localhost:8000/api/health/ > /dev/null 2>&1; then
    print_success "Backend is healthy"
else
    print_warning "Backend health check failed (service may still be starting)"
fi

# Check frontend
if curl -f http://localhost:80/health > /dev/null 2>&1; then
    print_success "Frontend is accessible"
else
    print_warning "Frontend not accessible yet"
fi

# Step 9: Show running containers
print_header "Step 9: Container Status"
docker-compose -f docker-compose-simple-production.yml ps

# ============================================================================
# Deployment Complete
# ============================================================================

print_header "Deployment Complete!"
echo ""
echo "Access Points:"
echo "  Frontend:  http://138.68.109.92"
echo "  Login:     http://138.68.109.92/html/login.html"
echo "  Dashboard: http://138.68.109.92/html/dashboard.html"
echo "  API:       http://138.68.109.92/api/"
echo "  Health:    http://138.68.109.92/health"
echo ""
echo "Backend Security:"
echo "  ✓ Backend (port 8000) is NOT publicly exposed"
echo "  ✓ Database (port 5432) is NOT publicly exposed"
echo "  ✓ Only nginx (port 80) is accessible"
echo ""
echo "Container Names:"
echo "  - iolta_db         (PostgreSQL database)"
echo "  - iolta_backend    (Django application)"
echo "  - iolta_frontend   (Nginx web server)"
echo ""
echo "Useful Commands:"
echo "  View logs:        docker-compose -f docker-compose-simple-production.yml logs -f"
echo "  Stop services:    docker-compose -f docker-compose-simple-production.yml stop"
echo "  Restart:          docker-compose -f docker-compose-simple-production.yml restart"
echo "  Shutdown:         docker-compose -f docker-compose-simple-production.yml down"
echo "  Create superuser: docker-compose -f docker-compose-simple-production.yml exec backend python manage.py createsuperuser"
echo ""
print_success "System is ready for use!"
echo ""
