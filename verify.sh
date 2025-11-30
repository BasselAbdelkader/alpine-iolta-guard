#!/bin/bash
# Verification Script - Check all required files

echo "=== IOLTA Production Package Verification ==="
echo ""

MISSING=0

check_file() {
    if [ -f "$1" ]; then
        echo "✓ $1"
    else
        echo "✗ MISSING: $1"
        MISSING=$((MISSING + 1))
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo "✓ $1/"
    else
        echo "✗ MISSING: $1/"
        MISSING=$((MISSING + 1))
    fi
}

echo "Core Files:"
check_file "deploy.sh"
check_file "docker-compose.prod.yml"
check_file ".env.production"
check_file "README.md"
check_file "QUICKSTART.txt"
check_file "backup.sh"
check_file "restore.sh"

echo ""
echo "Directories:"
check_dir "backend"
check_dir "frontend"
check_dir "nginx"
check_dir "sql"

echo ""
echo "Critical Backend Files:"
check_file "backend/manage.py"
check_file "backend/requirements.txt"
check_dir "backend/apps"
check_dir "backend/trust_account_project"

echo ""
echo "Critical Frontend Files:"
check_dir "frontend/html"
check_dir "frontend/js"
check_dir "frontend/css"

echo ""
echo "Configuration Files:"
check_file "nginx/nginx.conf"
check_file "sql/init.sql"

echo ""
echo "══════════════════════════════════════"
if [ $MISSING -eq 0 ]; then
    echo "✓ ALL FILES PRESENT - Package is complete!"
    exit 0
else
    echo "✗ $MISSING files/directories missing!"
    exit 1
fi
