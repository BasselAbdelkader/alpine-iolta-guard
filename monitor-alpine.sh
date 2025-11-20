#!/bin/bash

# ============================================================================
# IOLTA Guard - Alpine Stack Monitoring Script
# ============================================================================
# Purpose: Monitor health and performance of Alpine containers
# Usage: ./monitor-alpine.sh [OPTIONS]
# ============================================================================

set -e

COMPOSE_FILE="docker-compose.alpine.yml"
INTERVAL=5
DURATION=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ============================================================================
# FUNCTIONS
# ============================================================================

print_header() {
    clear
    echo "============================================================================"
    echo "  IOLTA Guard - Alpine Stack Monitor"
    echo "  $(date)"
    echo "============================================================================"
    echo ""
}

check_service_status() {
    echo -e "${CYAN}SERVICE STATUS${NC}"
    echo "----------------------------------------------------------------------------"

    local services=$(docker-compose -f "$COMPOSE_FILE" ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}")

    while IFS= read -r line; do
        if echo "$line" | grep -q "Up (healthy)"; then
            echo -e "${GREEN}$line${NC}"
        elif echo "$line" | grep -q "Up"; then
            echo -e "${YELLOW}$line${NC}"
        elif echo "$line" | grep -q "Exit"; then
            echo -e "${RED}$line${NC}"
        else
            echo "$line"
        fi
    done <<< "$services"

    echo ""
}

check_health_endpoints() {
    echo -e "${CYAN}HEALTH ENDPOINTS${NC}"
    echo "----------------------------------------------------------------------------"

    # Frontend
    if curl -f -s -m 5 http://localhost/ > /dev/null 2>&1; then
        echo -e "${GREEN}[✓]${NC} Frontend:    http://localhost/ - OK"
    else
        echo -e "${RED}[✗]${NC} Frontend:    http://localhost/ - FAILED"
    fi

    # Backend API health
    if curl -f -s -m 5 http://localhost/api/health/ > /dev/null 2>&1; then
        echo -e "${GREEN}[✓]${NC} Backend API: http://localhost/api/health/ - OK"
    else
        echo -e "${RED}[✗]${NC} Backend API: http://localhost/api/health/ - FAILED"
    fi

    # Database
    if docker-compose -f "$COMPOSE_FILE" exec -T database pg_isready -U iolta_user > /dev/null 2>&1; then
        echo -e "${GREEN}[✓]${NC} Database:    PostgreSQL - Ready"
    else
        echo -e "${RED}[✗]${NC} Database:    PostgreSQL - Not Ready"
    fi

    echo ""
}

show_resource_usage() {
    echo -e "${CYAN}RESOURCE USAGE${NC}"
    echo "----------------------------------------------------------------------------"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}" | grep "iolta"
    echo ""
}

show_recent_logs() {
    echo -e "${CYAN}RECENT ERRORS (Last 10)${NC}"
    echo "----------------------------------------------------------------------------"

    local error_count=$(docker-compose -f "$COMPOSE_FILE" logs --tail=100 2>&1 | grep -i error | wc -l)

    if [ "$error_count" -gt 0 ]; then
        echo -e "${RED}Found $error_count errors:${NC}"
        docker-compose -f "$COMPOSE_FILE" logs --tail=100 2>&1 | grep -i error | tail -10
    else
        echo -e "${GREEN}No errors found in recent logs${NC}"
    fi

    echo ""
}

show_disk_usage() {
    echo -e "${CYAN}DISK USAGE${NC}"
    echo "----------------------------------------------------------------------------"

    # Docker volumes
    echo "Docker Volumes:"
    docker system df -v | grep "ve_demo" | head -10

    echo ""
    echo "Container Sizes:"
    docker ps --size --format "table {{.Names}}\t{{.Size}}" | grep iolta

    echo ""
}

show_network_stats() {
    echo -e "${CYAN}NETWORK CONNECTIVITY${NC}"
    echo "----------------------------------------------------------------------------"

    # Test internal connectivity
    if docker-compose -f "$COMPOSE_FILE" exec -T backend ping -c 1 database > /dev/null 2>&1; then
        echo -e "${GREEN}[✓]${NC} Backend → Database: Connected"
    else
        echo -e "${RED}[✗]${NC} Backend → Database: Failed"
    fi

    if docker-compose -f "$COMPOSE_FILE" exec -T backend ping -c 1 frontend > /dev/null 2>&1; then
        echo -e "${GREEN}[✓]${NC} Backend → Frontend: Connected"
    else
        echo -e "${RED}[✗]${NC} Backend → Frontend: Failed"
    fi

    echo ""
}

show_database_stats() {
    echo -e "${CYAN}DATABASE STATISTICS${NC}"
    echo "----------------------------------------------------------------------------"

    # Connection count
    local connections=$(docker-compose -f "$COMPOSE_FILE" exec -T database \
        psql -U iolta_user -d iolta_guard_db -t -c "SELECT count(*) FROM pg_stat_activity;" 2>/dev/null | tr -d ' ')

    echo "Active Connections: ${connections:-N/A}"

    # Database size
    local db_size=$(docker-compose -f "$COMPOSE_FILE" exec -T database \
        psql -U iolta_user -d iolta_guard_db -t -c "SELECT pg_size_pretty(pg_database_size('iolta_guard_db'));" 2>/dev/null | tr -d ' ')

    echo "Database Size: ${db_size:-N/A}"

    # Table counts
    local client_count=$(docker-compose -f "$COMPOSE_FILE" exec -T database \
        psql -U iolta_user -d iolta_guard_db -t -c "SELECT COUNT(*) FROM clients_client;" 2>/dev/null | tr -d ' ')

    local txn_count=$(docker-compose -f "$COMPOSE_FILE" exec -T database \
        psql -U iolta_user -d iolta_guard_db -t -c "SELECT COUNT(*) FROM bank_accounts_transaction;" 2>/dev/null | tr -d ' ')

    echo "Clients: ${client_count:-N/A}"
    echo "Transactions: ${txn_count:-N/A}"

    echo ""
}

show_alpine_info() {
    echo -e "${CYAN}ALPINE LINUX INFO${NC}"
    echo "----------------------------------------------------------------------------"

    echo "Backend Alpine version:"
    docker-compose -f "$COMPOSE_FILE" exec -T backend cat /etc/os-release 2>/dev/null | grep "PRETTY_NAME" || echo "N/A"

    echo ""
    echo "Backend libc (should be musl):"
    docker-compose -f "$COMPOSE_FILE" exec -T backend ldd --version 2>&1 | head -1 || echo "N/A"

    echo ""
}

show_summary() {
    print_header
    check_service_status
    check_health_endpoints
    show_resource_usage
    show_recent_logs

    echo ""
    echo "Press Ctrl+C to exit, or wait for next refresh in ${INTERVAL}s..."
}

continuous_monitor() {
    local count=0
    local max_iterations=$((DURATION / INTERVAL))

    while true; do
        show_summary

        if [ "$DURATION" -gt 0 ]; then
            count=$((count + 1))
            if [ $count -ge $max_iterations ]; then
                echo ""
                echo "Monitoring duration completed."
                break
            fi
        fi

        sleep "$INTERVAL"
    done
}

full_report() {
    print_header
    check_service_status
    check_health_endpoints
    show_resource_usage
    show_disk_usage
    show_network_stats
    show_database_stats
    show_alpine_info
    show_recent_logs
}

show_help() {
    cat << 'EOF'
IOLTA Guard - Alpine Stack Monitor

Usage: ./monitor-alpine.sh [OPTIONS]

Options:
  --watch           Continuous monitoring (refresh every 5s)
  --interval N      Set refresh interval (default: 5s)
  --duration N      Run for N seconds then exit
  --full            Show full detailed report (one-time)
  --status          Show status only (one-time)
  --health          Check health endpoints only
  --logs            Show recent error logs
  --db              Show database statistics
  --help            Show this help

Examples:
  ./monitor-alpine.sh                    # Full report (one-time)
  ./monitor-alpine.sh --watch            # Continuous monitoring
  ./monitor-alpine.sh --watch --interval 10  # Monitor every 10s
  ./monitor-alpine.sh --duration 300     # Monitor for 5 minutes
  ./monitor-alpine.sh --health           # Just check health endpoints
  ./monitor-alpine.sh --db               # Just show database stats

EOF
}

# ============================================================================
# MAIN
# ============================================================================

case "${1:-}" in
    --watch)
        INTERVAL="${2:-5}"
        continuous_monitor
        ;;
    --interval)
        INTERVAL="${2:-5}"
        continuous_monitor
        ;;
    --duration)
        DURATION="${2:-60}"
        continuous_monitor
        ;;
    --full)
        full_report
        ;;
    --status)
        check_service_status
        ;;
    --health)
        check_health_endpoints
        ;;
    --logs)
        show_recent_logs
        ;;
    --db)
        show_database_stats
        ;;
    --help|-h)
        show_help
        ;;
    *)
        full_report
        ;;
esac
