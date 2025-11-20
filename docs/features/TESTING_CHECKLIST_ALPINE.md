# IOLTA Guard - Alpine Migration Testing Checklist

**Created:** November 7, 2025
**Purpose:** Comprehensive testing for Alpine Linux migration
**Critical:** PDF generation must be validated for IOLTA compliance

---

## Testing Overview

### Testing Phases

| Phase | Duration | Risk Level | Required |
|-------|----------|------------|----------|
| 1. Build & Deploy | 1-2 hours | Low | ✅ Mandatory |
| 2. Functional Testing | 4-8 hours | Medium | ✅ Mandatory |
| 3. PDF Comparison | 2-4 hours | **HIGH** | ✅ **CRITICAL** |
| 4. Performance Testing | 2-4 hours | Medium | ✅ Mandatory |
| 5. Security Testing | 2-4 hours | High | ✅ Mandatory |
| 6. Integration Testing | 4-8 hours | High | ✅ Mandatory |

**Total Estimated Time:** 15-30 hours

---

## Phase 1: Build & Deploy Testing

### 1.1 Pre-Build Validation

- [ ] Docker version 20.10+ installed
- [ ] Docker Compose 2.0+ installed
- [ ] Sufficient disk space (20GB+)
- [ ] `.env` file configured with secure values
- [ ] No placeholder values in `.env` (no "CHANGE_ME")
- [ ] `database/init/01-restore.sql` exists (95.5KB)

**Commands:**
```bash
docker --version
docker-compose --version
df -h
grep "CHANGE_ME" .env  # Should return nothing
ls -lh database/init/01-restore.sql
```

---

### 1.2 Build Process Testing

#### Backend Build

- [ ] Backend builds successfully (no errors)
- [ ] Build completes in <30 minutes
- [ ] All Python packages install correctly
- [ ] WeasyPrint dependencies installed
- [ ] Final image size <500MB

**Commands:**
```bash
time docker-compose -f docker-compose.alpine.yml build backend 2>&1 | tee backend-build.log

# Check for errors
grep -i error backend-build.log

# Check image size
docker images iolta-guard-backend-alpine:latest
```

**Success Criteria:**
- Build completes without errors
- Image size: 300-400MB
- Build time: 15-25 minutes (first build)

---

#### Frontend Build

- [ ] Frontend builds successfully
- [ ] Final image size <100MB

**Commands:**
```bash
docker-compose -f docker-compose.alpine.yml build frontend

# Check image size
docker images iolta-guard-frontend-alpine:latest
```

**Success Criteria:**
- Build completes without errors
- Image size: 40-60MB

---

### 1.3 Deployment Testing

- [ ] All services start successfully
- [ ] Database initializes from SQL backup
- [ ] Backend connects to database
- [ ] Frontend proxies to backend
- [ ] All health checks pass

**Commands:**
```bash
# Start services
docker-compose -f docker-compose.alpine.yml up -d

# Wait 2 minutes, then check status
sleep 120
docker-compose -f docker-compose.alpine.yml ps

# Check logs for errors
docker-compose -f docker-compose.alpine.yml logs | grep -i error
```

**Success Criteria:**
```
iolta_db_alpine          Up (healthy)
iolta_backend_alpine     Up (healthy)
iolta_frontend_alpine    Up
```

---

### 1.4 Service Health Checks

- [ ] Database responds to health check
- [ ] Backend /api/health/ returns 200 OK
- [ ] Frontend serves homepage

**Commands:**
```bash
# Database
docker-compose -f docker-compose.alpine.yml exec database pg_isready

# Backend
curl -f http://localhost/api/health/

# Frontend
curl -f http://localhost/
```

**Success Criteria:**
- All commands return success (exit code 0)
- Backend returns: `{"status":"healthy"}`

---

## Phase 2: Functional Testing

### 2.1 Authentication & Authorization

- [ ] Login page loads
- [ ] Can login with test credentials
- [ ] Session persists across page reloads
- [ ] Logout works correctly
- [ ] Invalid credentials rejected

**Test Users:**
```
Username: admin / Password: (from test data)
Username: testuser / Password: (from test data)
```

**Manual Steps:**
1. Navigate to http://localhost/
2. Login with credentials
3. Verify dashboard loads
4. Refresh page, verify still logged in
5. Logout, verify redirect to login

---

### 2.2 Client Management

- [ ] Client list loads
- [ ] Can view client details
- [ ] Can create new client
- [ ] Can edit existing client
- [ ] Can search clients
- [ ] Client filtering works (active/inactive)

**Test Data:**
- Create client: "Test Firm Alpine"
- Edit client: Update phone number
- Search: Find client by name
- Filter: Show only active clients

---

### 2.3 Case Management

- [ ] Case list loads
- [ ] Can create new case
- [ ] Can view case details
- [ ] Case linked to client correctly
- [ ] Can edit case information

---

### 2.4 Bank Transactions

- [ ] Transaction list loads
- [ ] Can create deposit transaction
- [ ] Can create withdrawal transaction
- [ ] Balance calculations correct
- [ ] Transaction status updates (pending → cleared)
- [ ] Can filter transactions by type
- [ ] Can filter by date range

**Critical Tests:**
- [ ] Create deposit: $1,000.00
- [ ] Verify balance increases
- [ ] Create withdrawal: $100.00
- [ ] Verify balance decreases
- [ ] Check running balance accuracy

---

### 2.5 Vendor Management

- [ ] Vendor list loads
- [ ] Can create new vendor
- [ ] Can edit vendor
- [ ] Vendor search works
- [ ] Vendor notes field accessible (MAJOR-1 bug)

**Note:** This tests the bug fix for missing notes field.

---

### 2.6 Dashboard & Reports

- [ ] Dashboard loads
- [ ] Trust balance displays correctly
- [ ] Bank register balance displays correctly
- [ ] Recent transactions shown
- [ ] Account health indicators visible

---

## Phase 3: PDF Generation Testing (CRITICAL)

### 3.1 Check Printing (HIGHEST PRIORITY)

**Critical:** Check printing MUST be pixel-perfect for bank acceptance.

#### Test Setup
- [ ] Obtain actual check stock paper
- [ ] Set up test printer
- [ ] Create test transactions for check printing

#### Generate Test Checks

- [ ] Generate check #1: $100.00 to "Test Payee"
- [ ] Generate check #2: $1,250.50 to "Alpine Test Vendor"
- [ ] Generate check #3: $999.99 to "Multi-Word Payee Name"

**Commands:**
```bash
# Access check printing endpoint
# (URL depends on implementation)
curl http://localhost/api/checks/print/TRANSACTION_ID/ -o check_alpine.pdf
```

---

#### PDF Visual Inspection

Compare Alpine-generated checks with Debian-generated checks:

**Checklist per check:**
- [ ] Payee name position correct
- [ ] Amount (numbers) position correct
- [ ] Amount (words) position correct
- [ ] Date position correct
- [ ] Signature line position correct
- [ ] MICR line position correct (if applicable)
- [ ] Bank routing information correct
- [ ] Check number displays correctly
- [ ] No text overflow or truncation
- [ ] Font rendering identical
- [ ] Line spacing identical
- [ ] All text readable and clear

**Comparison Tools:**
```bash
# Generate from Debian (comparison baseline)
docker-compose up -d  # Original Debian version
curl http://localhost/api/checks/print/TRANSACTION_ID/ -o check_debian.pdf

# Generate from Alpine
docker-compose -f docker-compose.alpine.yml up -d
curl http://localhost/api/checks/print/TRANSACTION_ID/ -o check_alpine.pdf

# Visual diff (if tools available)
diff-pdf check_debian.pdf check_alpine.pdf
```

---

#### Physical Print Testing

- [ ] Print Alpine check on test stock
- [ ] Print Debian check on same stock
- [ ] Compare physical prints side-by-side
- [ ] Measure positions with ruler if needed
- [ ] Verify MICR line prints correctly (if applicable)

**Success Criteria:**
- **ZERO visual differences between Debian and Alpine checks**
- **All elements within 1-2mm of expected position**
- **Bank validation approval required before production**

---

### 3.2 Client Ledger Reports

- [ ] Generate client ledger for test client
- [ ] Compare Alpine vs Debian output
- [ ] Verify transaction history complete
- [ ] Verify running balances accurate
- [ ] Check date formatting
- [ ] Verify page breaks correct
- [ ] Check headers/footers present

**Test Cases:**
- Client with 5 transactions
- Client with 50 transactions (multi-page)
- Client with $0 balance
- Client with negative balance (if allowed)

---

### 3.3 Trust Account Reports

- [ ] Generate trust balance report
- [ ] Compare Alpine vs Debian output
- [ ] Verify all client balances shown
- [ ] Verify total calculations
- [ ] Check formatting and layout

---

### 3.4 Bank Reconciliation Reports

- [ ] Generate reconciliation report
- [ ] Compare Alpine vs Debian output
- [ ] Verify cleared transactions
- [ ] Verify pending transactions
- [ ] Check differential calculation

---

### 3.5 Font Rendering Tests

- [ ] Test special characters (é, ñ, ü, etc.)
- [ ] Test long payee names (40+ characters)
- [ ] Test currency symbols ($, €, £)
- [ ] Test numbers with decimals
- [ ] Test date formats

**Test Data:**
- Payee: "José María García-López & Associates LLC"
- Amount: $12,345,678.90
- Date: Various formats

---

### 3.6 PDF Metadata Comparison

```bash
# Extract metadata
pdfinfo check_debian.pdf > debian_meta.txt
pdfinfo check_alpine.pdf > alpine_meta.txt

# Compare
diff debian_meta.txt alpine_meta.txt
```

**Check:**
- [ ] PDF version same
- [ ] Page size identical
- [ ] Producer/Creator info
- [ ] File size similar (within 10%)

---

## Phase 4: Performance Testing

### 4.1 Startup Performance

- [ ] Cold start time <2 minutes
- [ ] Warm restart time <30 seconds
- [ ] Database ready time <60 seconds

**Commands:**
```bash
# Cold start (from scratch)
docker-compose -f docker-compose.alpine.yml down -v
time docker-compose -f docker-compose.alpine.yml up -d

# Warm restart
time docker-compose -f docker-compose.alpine.yml restart
```

---

### 4.2 Response Time Testing

Test API endpoint response times:

- [ ] /api/health/ responds <100ms
- [ ] /api/v1/clients/ responds <500ms
- [ ] /api/v1/transactions/ responds <1s
- [ ] Dashboard loads <2s
- [ ] PDF generation <5s per document

**Commands:**
```bash
# Simple response time test
time curl -s http://localhost/api/health/

# More comprehensive (if Apache Bench installed)
ab -n 100 -c 10 http://localhost/api/health/
```

---

### 4.3 Resource Usage

Monitor resource consumption:

- [ ] Backend memory <512MB idle
- [ ] Backend memory <1GB under load
- [ ] Database memory <1GB
- [ ] Frontend memory <128MB
- [ ] CPU usage <50% average

**Commands:**
```bash
# Monitor for 5 minutes
docker stats --no-stream

# Continuous monitoring
docker stats
```

---

### 4.4 Load Testing

Simulate concurrent users:

- [ ] 10 concurrent users
- [ ] 50 concurrent users
- [ ] 100 concurrent users (if production scale)

**Tools:**
- Apache Bench (`ab`)
- JMeter
- Locust

**Test Scenarios:**
1. Login requests
2. Dashboard loads
3. Transaction creation
4. PDF generation (most resource-intensive)

---

### 4.5 PDF Generation Performance

- [ ] Single check generation <2s
- [ ] Batch of 10 checks <20s
- [ ] 100-transaction ledger <10s

**Commands:**
```bash
time curl http://localhost/api/checks/print/123/ -o test.pdf
```

---

## Phase 5: Security Testing

### 5.1 Container Security

- [ ] Backend runs as non-root user
- [ ] No unnecessary packages installed
- [ ] Base images from official sources
- [ ] No secrets in environment variables exposed

**Commands:**
```bash
# Check user
docker-compose -f docker-compose.alpine.yml exec backend whoami
# Should return: iolta

# Check exposed ports
docker-compose -f docker-compose.alpine.yml port backend 8002
# Should return: nothing (port not exposed publicly)

# Scan for vulnerabilities (if Trivy installed)
trivy image iolta-guard-backend-alpine:latest
```

---

### 5.2 Network Security

- [ ] Database NOT accessible from host
- [ ] Backend NOT accessible from host
- [ ] Only frontend accessible on port 80

**Commands:**
```bash
# These should FAIL (connection refused)
curl http://localhost:5432  # Database
curl http://localhost:8002  # Backend

# This should SUCCEED
curl http://localhost:80    # Frontend
```

---

### 5.3 musl libc Security Benefits

- [ ] Verify Alpine uses musl libc
- [ ] Compare CVE count: Alpine vs Debian

**Commands:**
```bash
# Check libc version
docker-compose -f docker-compose.alpine.yml exec backend ldd --version

# Should show: musl libc
```

---

### 5.4 Dependency Security

- [ ] Run security audit on Python packages
- [ ] Check for known vulnerabilities
- [ ] Verify all packages up to date

**Commands:**
```bash
# Inside backend container
docker-compose -f docker-compose.alpine.yml exec backend pip list --outdated

# Security audit (if safety installed)
docker-compose -f docker-compose.alpine.yml exec backend safety check
```

---

## Phase 6: Integration Testing

### 6.1 Database Integration

- [ ] Connection pooling works
- [ ] Transactions are atomic
- [ ] Concurrent writes handled correctly
- [ ] Database constraints enforced

**Test:**
1. Create 100 transactions simultaneously
2. Verify all saved correctly
3. Check for race conditions

---

### 6.2 Frontend-Backend Integration

- [ ] API calls work through Nginx proxy
- [ ] CORS headers correct
- [ ] Static files served correctly
- [ ] Session cookies work
- [ ] CSRF protection works

---

### 6.3 Multi-Container Coordination

- [ ] Services start in correct order
- [ ] Health checks prevent premature routing
- [ ] Service discovery works (DNS)
- [ ] Volume sharing works (static files)

**Commands:**
```bash
# Test DNS resolution
docker-compose -f docker-compose.alpine.yml exec backend ping database
docker-compose -f docker-compose.alpine.yml exec backend ping frontend

# Check static files shared
docker-compose -f docker-compose.alpine.yml exec frontend ls -la /usr/share/nginx/html/static/
```

---

## Phase 7: Data Integrity Testing

### 7.1 Database Consistency

- [ ] All tables populated from init SQL
- [ ] Foreign key relationships intact
- [ ] Indexes created correctly
- [ ] Sequences start at correct values

**Commands:**
```bash
docker-compose -f docker-compose.alpine.yml exec database psql -U iolta_user -d iolta_guard_db

-- List tables
\dt

-- Check counts
SELECT COUNT(*) FROM clients_client;
SELECT COUNT(*) FROM bank_accounts_transaction;
SELECT COUNT(*) FROM vendors_vendor;

-- Check constraints
\d clients_client

\q
```

---

### 7.2 Transaction Calculations

- [ ] Balance calculations match expected
- [ ] Deposits increase balance correctly
- [ ] Withdrawals decrease balance correctly
- [ ] Running balances accurate
- [ ] Voided transactions excluded from balance

**Test:**
```sql
-- Manual balance verification
SELECT
    c.id,
    c.first_name || ' ' || c.last_name as client_name,
    SUM(CASE WHEN t.transaction_type = 'DEPOSIT' AND t.status != 'voided'
        THEN t.amount ELSE 0 END) as total_deposits,
    SUM(CASE WHEN t.transaction_type = 'WITHDRAWAL' AND t.status != 'voided'
        THEN t.amount ELSE 0 END) as total_withdrawals,
    (SUM(CASE WHEN t.transaction_type = 'DEPOSIT' AND t.status != 'voided'
        THEN t.amount ELSE 0 END) -
     SUM(CASE WHEN t.transaction_type = 'WITHDRAWAL' AND t.status != 'voided'
        THEN t.amount ELSE 0 END)) as calculated_balance
FROM clients_client c
LEFT JOIN bank_accounts_transaction t ON t.client_id = c.id
GROUP BY c.id, c.first_name, c.last_name;
```

Compare with application-displayed balances.

---

## Phase 8: Regression Testing (Known Bugs)

Test all bugs from QA report have not regressed:

### 8.1 CRITICAL Issues

- [ ] Firm info API endpoint works (/api/v1/dashboard/)
- [ ] Vendors page loads firm information
- [ ] Bank transactions page loads firm information
- [ ] Vendor detail page loads firm information

---

### 8.2 MAJOR Issues

- [ ] Vendor notes field visible in API response
- [ ] Vendor form submission works
- [ ] Client filter works with search
- [ ] Transaction field names consistent
- [ ] Menu toggle works (or removed)

---

## Phase 9: Comparison Testing (Debian vs Alpine)

### 9.1 Side-by-Side Testing

Run both versions simultaneously:

**Debian (port 8080):**
```bash
# Edit docker-compose.yml to use port 8080
docker-compose up -d
```

**Alpine (port 80):**
```bash
docker-compose -f docker-compose.alpine.yml up -d
```

**Compare:**
- [ ] Same data displays on both
- [ ] Same functionality on both
- [ ] Response times similar
- [ ] PDF output identical

---

### 9.2 Data Migration Test

- [ ] Export data from Debian version
- [ ] Import to Alpine version
- [ ] Verify all data intact
- [ ] Verify relationships preserved

---

## Phase 10: Production Readiness

### 10.1 Pre-Production Checklist

- [ ] All tests passed
- [ ] PDF output validated by bank (for check printing)
- [ ] Performance meets requirements
- [ ] Security scan clean
- [ ] Documentation complete
- [ ] Rollback plan prepared
- [ ] Monitoring configured
- [ ] Backup strategy in place

---

### 10.2 Pilot Deployment

Before full rollout to 100+ firms:

- [ ] Deploy to 1-2 pilot firms
- [ ] Monitor for 1-2 weeks
- [ ] Collect user feedback
- [ ] Monitor error rates
- [ ] Check resource usage
- [ ] Verify PDF generation in production
- [ ] Test backup/restore procedures

---

## Test Results Summary

### Template

```
IOLTA Guard Alpine Testing - Results
Date: ___________
Tester: ___________

Phase 1 - Build & Deploy:        [ ] PASS  [ ] FAIL
Phase 2 - Functional Testing:    [ ] PASS  [ ] FAIL
Phase 3 - PDF Testing:           [ ] PASS  [ ] FAIL  (CRITICAL)
Phase 4 - Performance Testing:   [ ] PASS  [ ] FAIL
Phase 5 - Security Testing:      [ ] PASS  [ ] FAIL
Phase 6 - Integration Testing:   [ ] PASS  [ ] FAIL
Phase 7 - Data Integrity:        [ ] PASS  [ ] FAIL
Phase 8 - Regression Testing:    [ ] PASS  [ ] FAIL
Phase 9 - Comparison Testing:    [ ] PASS  [ ] FAIL
Phase 10 - Production Readiness: [ ] PASS  [ ] FAIL

Critical Issues Found: ___________
Major Issues Found: ___________
Minor Issues Found: ___________

PDF Check Printing Validated: [ ] YES  [ ] NO  (MUST BE YES)

Overall Status: [ ] READY FOR PRODUCTION  [ ] NEEDS WORK  [ ] BLOCKED

Notes:
______________________________________________________________________
______________________________________________________________________
______________________________________________________________________

Sign-off:
Developer: ________________  Date: ________
QA: ________________  Date: ________
Security: ________________  Date: ________
Business Owner: ________________  Date: ________
```

---

## Critical Success Criteria

**MUST PASS before production:**

1. ✅ All services build and start successfully
2. ✅ All functional tests pass
3. ✅ **PDF check printing identical to Debian version**
4. ✅ **Bank validates check format**
5. ✅ Performance meets or exceeds Debian version
6. ✅ Security scan shows no HIGH or CRITICAL vulnerabilities
7. ✅ No data loss during migration
8. ✅ Pilot deployment successful

**CANNOT GO TO PRODUCTION if:**

❌ Check printing has ANY visual differences
❌ Security vulnerabilities found
❌ Data integrity issues detected
❌ Performance significantly degraded

---

**Testing Document Version:** 1.0
**Created:** November 7, 2025
**Status:** Ready for Use
