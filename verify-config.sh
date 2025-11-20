#!/bin/bash
# ============================================================================
# IOLTA Guard - Configuration Verification Script
# ============================================================================
# This script verifies the production deployment configuration
# ============================================================================

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_check() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

echo "========================================="
echo "IOLTA Guard Configuration Verification"
echo "========================================="
echo ""

# Check docker-compose.production.yml
if [ -f "docker-compose.production.yml" ]; then
    print_check 0 "docker-compose.production.yml exists"
    if docker-compose -f docker-compose.production.yml config > /dev/null 2>&1; then
        print_check 0 "docker-compose.production.yml syntax valid"
    else
        print_check 1 "docker-compose.production.yml syntax invalid"
    fi
else
    print_check 1 "docker-compose.production.yml missing"
fi

# Check .env.production
if [ -f ".env.production" ]; then
    print_check 0 ".env.production exists"
    if grep -q "CHANGE_ME" .env.production; then
        print_check 1 ".env.production contains placeholders (needs configuration)"
    else
        print_check 0 ".env.production configured"
    fi
else
    print_check 1 ".env.production missing"
fi

# Check deploy.sh
if [ -f "deploy.sh" ]; then
    print_check 0 "deploy.sh exists"
    if [ -x "deploy.sh" ]; then
        print_check 0 "deploy.sh is executable"
    else
        print_check 1 "deploy.sh not executable (run: chmod +x deploy.sh)"
    fi
else
    print_check 1 "deploy.sh missing"
fi

# Check database backup
if [ -f "database/init/01-restore.sql" ]; then
    SIZE=$(du -h database/init/01-restore.sql | cut -f1)
    print_check 0 "Database backup exists ($SIZE)"
else
    print_check 1 "Database backup missing (database/init/01-restore.sql)"
fi

# Check README-DEPLOYMENT.md
if [ -f "README-DEPLOYMENT.md" ]; then
    print_check 0 "README-DEPLOYMENT.md exists"
else
    print_check 1 "README-DEPLOYMENT.md missing"
fi

# Check modified files
if grep -q "SESSION_COOKIE_DOMAIN = None" trust_account/trust_account_project/settings.py; then
    print_check 0 "settings.py: SESSION_COOKIE_DOMAIN fixed"
else
    print_check 1 "settings.py: SESSION_COOKIE_DOMAIN not fixed"
fi

if grep -q '"app_port": 8002' account.json; then
    print_check 0 "account.json: Port set to 8002"
else
    print_check 1 "account.json: Port not set to 8002"
fi

if grep -q '"debug": false' account.json; then
    print_check 0 "account.json: Debug mode disabled"
else
    print_check 1 "account.json: Debug mode not disabled"
fi

echo ""
echo "========================================="
echo "Configuration Check Complete"
echo "========================================="
echo ""

# Final recommendation
if [ -f ".env.production" ] && grep -q "CHANGE_ME" .env.production; then
    echo -e "${YELLOW}⚠ NEXT STEP:${NC} Configure .env.production before deploying"
    echo ""
    echo "1. Generate passwords:"
    echo "   openssl rand -base64 32"
    echo "   python3 -c \"import secrets; print(secrets.token_urlsafe(50))\""
    echo ""
    echo "2. Edit .env.production and replace CHANGE_ME values"
    echo ""
    echo "3. Run: ./deploy.sh"
else
    echo -e "${GREEN}✓ Ready to deploy!${NC}"
    echo ""
    echo "Run: ./deploy.sh"
fi
echo ""
