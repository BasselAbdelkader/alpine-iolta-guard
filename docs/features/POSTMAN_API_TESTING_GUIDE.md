# IOLTA Guard API Testing Guide for QA Team

## Overview

This guide provides comprehensive instructions for QA testers to test the IOLTA Guard Trust Account Management System API using Postman.

**System:** IOLTA Guard - Trust Account Management
**API Base URL:** `http://localhost:3000/api`
**Authentication:** Session-based (Django session cookies)
**Date:** October 12, 2025

---

## Table of Contents

1. [Setup Instructions](#setup-instructions)
2. [Authentication Flow](#authentication-flow)
3. [API Endpoint Categories](#api-endpoint-categories)
4. [Test Scenarios by Feature](#test-scenarios-by-feature)
5. [Common Test Cases](#common-test-cases)
6. [Error Handling Tests](#error-handling-tests)
7. [Data Validation Tests](#data-validation-tests)
8. [Expected Response Codes](#expected-response-codes)
9. [Troubleshooting](#troubleshooting)

---

## 1. Setup Instructions

### Prerequisites
- Postman Desktop App (latest version) or Postman Web
- Docker Desktop running with IOLTA Guard containers active
- Access to the application at `http://localhost:3000`

### Import Collection and Environment

1. **Import Collection:**
   - Open Postman
   - Click "Import" button (top left)
   - Select `IOLTA_Guard_API_Postman_Collection.json`
   - Collection will appear in left sidebar

2. **Import Environment:**
   - Click "Import" button again
   - Select `IOLTA_Guard_Postman_Environment.json`
   - Select environment from dropdown (top right): "IOLTA Guard - Local Development"

3. **Verify Environment Variables:**
   - Click eye icon (👁️) next to environment dropdown
   - Verify `base_url` is set to: `http://localhost:3000/api`
   - All other variables should have default values

### Enable Cookie Management

Postman automatically manages cookies, but verify settings:

1. Go to Settings (⚙️ icon)
2. Navigate to "Cookies" section
3. Ensure "Automatically follow redirects" is enabled
4. Ensure cookies are enabled for `localhost`

---

## 2. Authentication Flow

### Step 1: Login (REQUIRED FIRST)

**Endpoint:** `POST /api/auth/login/`

**Test Credentials:**
```json
{
    "username": "admin",
    "password": "admin123"
}
```

**Expected Response (200 OK):**
```json
{
    "success": true,
    "message": "Login successful",
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com"
    }
}
```

**What Happens:**
- Session cookie (`sessionid`) is automatically saved by Postman
- All subsequent requests will use this cookie for authentication
- Environment variable `authenticated` is set to `true`

### Step 2: Check Authentication (Optional)

**Endpoint:** `GET /api/auth/check/`

**Expected Response (200 OK):**
```json
{
    "authenticated": true,
    "username": "admin",
    "user_id": 1
}
```

### Step 3: Logout (When Finished)

**Endpoint:** `POST /api/auth/logout/`

**Expected Response (200 OK):**
```json
{
    "success": true,
    "message": "Logout successful"
}
```

---

## 3. API Endpoint Categories

### Overview of All Endpoints

| Category | Base Path | Description |
|----------|-----------|-------------|
| Authentication | `/api/auth/` | Login, logout, check auth |
| Dashboard | `/api/v1/dashboard/` | Dashboard data, law firm info |
| Clients | `/api/v1/clients/` | Client CRUD operations |
| Cases | `/api/v1/cases/` | Case CRUD operations |
| Bank Accounts | `/api/v1/bank-accounts/accounts/` | Bank account management |
| Transactions | `/api/v1/bank-accounts/bank-transactions/` | Transaction management |
| Vendors | `/api/v1/vendors/` | Vendor CRUD operations |
| Vendor Types | `/api/v1/vendors/types/` | Vendor categories |
| Checks | `/api/v1/checks/` | Check printing/management |
| Reconciliations | `/api/v1/bank-accounts/reconciliations/` | Bank reconciliation |

---

## 4. Test Scenarios by Feature

### A. Dashboard Testing

#### Test 1: Get Dashboard Data
```
GET /api/v1/dashboard/
Expected: 200 OK with complete dashboard metrics
```

**Verify Response Contains:**
- `trust_balance` (decimal)
- `bank_register_balance` (decimal)
- `active_clients_count` (integer)
- `next_reconciliation_date` (date or null)
- `pending_transactions_count` (integer)
- `health_assessment` (object with score, status, issues, warnings)
- `top_clients` (array of top 5 clients)
- `stale_clients` (array of clients with old deposits)
- `outstanding_checks` (array of checks over 90 days)

#### Test 2: Get Law Firm Information
```
GET /api/v1/dashboard/law-firm/
Expected: 200 OK with firm details
```

#### Test 3: Get Uncleared Transactions
```
GET /api/v1/dashboard/uncleared-transactions/
Expected: 200 OK with array of pending transactions
```

---

### B. Client Management Testing

#### Test 1: List All Clients
```
GET /api/v1/clients/
Expected: 200 OK with array of clients
```

**Verify Each Client Has:**
- `id`, `client_number` (auto-generated, starts at 1001)
- `first_name`, `last_name`, `full_name`
- `email`, `phone`, `address`, `city`, `state`, `zip_code`
- `trust_account_status`, `trust_status_display`
- `current_balance`, `formatted_balance`
- `is_active`, `created_at`, `updated_at`
- `has_cases`, `cases` (array)

#### Test 2: Get Specific Client
```
GET /api/v1/clients/1/
Expected: 200 OK with detailed client info
```

#### Test 3: Create New Client (Valid Data)
```
POST /api/v1/clients/
Body:
{
    "first_name": "Test",
    "last_name": "Client",
    "email": "test@example.com",
    "phone": "(555) 123-4567",
    "address": "123 Test St",
    "city": "New York",
    "state": "NY",
    "zip_code": "10001",
    "trust_account_status": "ACTIVE",
    "is_active": true
}
Expected: 201 Created
```

**Verify Response:**
- Auto-generated `client_number` (format: 1001, 1002, etc.)
- All submitted fields are present
- `current_balance` is 0.00
- `created_at` and `updated_at` timestamps

#### Test 4: Create Duplicate Client (Negative Test)
```
POST /api/v1/clients/
Body: Same first_name and last_name as existing client
Expected: 400 Bad Request
Error: "A client with this name already exists"
```

#### Test 5: Update Client (PUT)
```
PUT /api/v1/clients/1/
Body: All required fields with updated values
Expected: 200 OK
```

#### Test 6: Partial Update Client (PATCH)
```
PATCH /api/v1/clients/1/
Body:
{
    "email": "newemail@example.com",
    "phone": "(555) 999-8888"
}
Expected: 200 OK
```

#### Test 7: Get Client's Cases
```
GET /api/v1/clients/1/cases/
Expected: 200 OK with array of cases for that client
```

#### Test 8: Get Client Balance History
```
GET /api/v1/clients/1/balance_history/
Expected: 200 OK with balance breakdown by case
```

#### Test 9: Search Clients
```
GET /api/v1/clients/search/?q=john
Expected: 200 OK with filtered results
```

**Test Different Search Terms:**
- First name: `?q=john`
- Last name: `?q=smith`
- Client number: `?q=1001`
- Email: `?q=email@example.com`
- Phone: `?q=555`

#### Test 10: Get Trust Summary
```
GET /api/v1/clients/trust_summary/
Expected: 200 OK
Response should have: total_balance, client_count
```

#### Test 11: Delete Client
```
DELETE /api/v1/clients/{id}/
Expected: 204 No Content (successful deletion)
```

---

### C. Case Management Testing

#### Test 1: List All Cases
```
GET /api/v1/cases/
Expected: 200 OK with array of cases
```

#### Test 2: Create New Case
```
POST /api/v1/cases/
Body:
{
    "case_title": "Personal Injury Settlement",
    "client": 1,
    "case_description": "Vehicle accident case",
    "case_amount": "50000.00",
    "case_status": "Open",
    "opened_date": "2025-10-12",
    "is_active": true
}
Expected: 201 Created
```

**Verify:**
- Auto-generated `case_number` (format: CASE-1001)
- `current_balance` is 0.00 initially
- All fields match submitted data

#### Test 3: Create Case for Inactive Client (Negative Test)
```
POST /api/v1/cases/
Body: client = ID of inactive client
Expected: 400 Bad Request
Error: "Cannot create case for inactive client"
```

#### Test 4: Update Case Status to Closed
```
PATCH /api/v1/cases/1/
Body:
{
    "case_status": "Closed",
    "closed_date": "2025-10-12"
}
Expected: 200 OK
```

#### Test 5: Close Case Without Closed Date (Negative Test)
```
PATCH /api/v1/cases/1/
Body:
{
    "case_status": "Closed"
}
Expected: 400 Bad Request
Error: "Closed date is required when case status is 'Closed'"
```

#### Test 6: Get Case Balance
```
GET /api/v1/cases/1/balance/
Expected: 200 OK with balance info
```

#### Test 7: Get Case Transactions
```
GET /api/v1/cases/1/transactions/
Expected: 200 OK with array of transactions for that case
```

#### Test 8: Get Cases by Client
```
GET /api/v1/cases/by_client/?client_id=1
Expected: 200 OK with cases for specified client
```

---

### D. Bank Account Testing

#### Test 1: List All Bank Accounts
```
GET /api/v1/bank-accounts/accounts/
Expected: 200 OK with array of accounts
```

**Verify Each Account Has:**
- `account_number`, `bank_name`, `account_name`
- `routing_number`, `account_type`, `account_type_display`
- `opening_balance`, `trust_balance`, `register_balance`
- `formatted_trust_balance`, `pending_count`
- `is_active`, `created_at`, `updated_at`

#### Test 2: Get Account Summary
```
GET /api/v1/bank-accounts/accounts/summary/
Expected: 200 OK with summary of all accounts
```

#### Test 3: Create Bank Account
```
POST /api/v1/bank-accounts/accounts/
Body:
{
    "account_number": "987654321",
    "bank_name": "Test Bank",
    "bank_address": "123 Bank St, NY, NY 10001",
    "account_name": "IOLTA Trust Account",
    "routing_number": "021000089",
    "account_type": "CHECKING",
    "opening_balance": "1000.00",
    "is_active": true
}
Expected: 201 Created
```

#### Test 4: Create Account with Duplicate Number (Negative Test)
```
POST /api/v1/bank-accounts/accounts/
Body: account_number that already exists
Expected: 400 Bad Request
Error: "Account number already exists"
```

#### Test 5: Create Account with Negative Balance (Negative Test)
```
POST /api/v1/bank-accounts/accounts/
Body: opening_balance = "-500.00"
Expected: 400 Bad Request
Error: "Opening balance cannot be negative"
```

#### Test 6: Get Account Transactions
```
GET /api/v1/bank-accounts/accounts/1/transactions/
Expected: 200 OK with transactions for that account
```

#### Test 7: Get Account Balance History
```
GET /api/v1/bank-accounts/accounts/1/balance_history/
Expected: 200 OK with historical balance data
```

---

### E. Bank Transaction Testing

#### Test 1: List All Transactions
```
GET /api/v1/bank-accounts/bank-transactions/
Expected: 200 OK with array of transactions
```

**Verify Each Transaction Has:**
- `id`, `transaction_number` (auto-generated)
- `bank_account`, `client`, `case` (optional), `vendor` (optional)
- `transaction_type`, `transaction_date`, `amount`
- `status` (PENDING, CLEARED, VOIDED)
- `description`, `reference_number`, `check_number`
- `created_at`, `updated_at`, `created_by`

#### Test 2: Create Deposit Transaction
```
POST /api/v1/bank-accounts/bank-transactions/
Body:
{
    "bank_account": 1,
    "client": 1,
    "case": 1,
    "transaction_type": "DEPOSIT",
    "transaction_date": "2025-10-12",
    "amount": "5000.00",
    "description": "Initial retainer",
    "status": "CLEARED",
    "reference_number": "DEP-001"
}
Expected: 201 Created
```

**Verify:**
- Auto-generated `transaction_number`
- Bank account balance increases by 5000.00
- Client/case balance increases by 5000.00
- Audit trail is created

#### Test 3: Create Withdrawal Transaction
```
POST /api/v1/bank-accounts/bank-transactions/
Body:
{
    "bank_account": 1,
    "client": 1,
    "case": 1,
    "transaction_type": "WITHDRAWAL",
    "transaction_date": "2025-10-12",
    "amount": "1500.00",
    "description": "Legal fees",
    "status": "CLEARED",
    "check_number": "1001",
    "reference_number": "CHK-001"
}
Expected: 201 Created
```

**Verify:**
- Bank account balance decreases by 1500.00
- Client/case balance decreases by 1500.00
- Check number is recorded

#### Test 4: Create Payment to Vendor
```
POST /api/v1/bank-accounts/bank-transactions/
Body:
{
    "bank_account": 1,
    "client": 1,
    "case": 1,
    "vendor": 1,
    "transaction_type": "WITHDRAWAL",
    "transaction_date": "2025-10-12",
    "amount": "850.00",
    "description": "Expert witness fee",
    "payee": "Dr. John Expert",
    "check_memo": "Expert consultation - Case #1001",
    "status": "PENDING",
    "check_number": "1002",
    "reference_number": "VEN-001"
}
Expected: 201 Created
```

#### Test 5: Get Unmatched Transactions
```
GET /api/v1/bank-accounts/bank-transactions/unmatched/
Expected: 200 OK with only PENDING transactions
```

#### Test 6: Create Transaction with Invalid Amount (Negative Test)
```
POST /api/v1/bank-accounts/bank-transactions/
Body: amount = "-100.00" (negative)
Expected: 400 Bad Request
```

#### Test 7: Create Transaction Without Required Fields (Negative Test)
```
POST /api/v1/bank-accounts/bank-transactions/
Body: Missing bank_account or amount
Expected: 400 Bad Request
```

---

### F. Vendor Management Testing

#### Test 1: List All Vendors
```
GET /api/v1/vendors/
Expected: 200 OK with array of vendors
```

**Verify Each Vendor Has:**
- `id`, `vendor_number` (auto-generated)
- `vendor_name`, `contact_person`
- `email`, `phone`, `address`, `city`, `state`, `zip_code`
- `tax_id`, `is_active`
- `payment_count`, `total_paid`, `last_payment_date`

#### Test 2: Create New Vendor
```
POST /api/v1/vendors/
Body:
{
    "vendor_name": "ABC Court Reporting",
    "contact_person": "Mike Johnson",
    "email": "contact@abccourt.com",
    "phone": "(555) 777-8888",
    "address": "123 Court St",
    "city": "New York",
    "state": "NY",
    "zip_code": "10001",
    "tax_id": "12-3456789",
    "is_active": true
}
Expected: 201 Created
```

#### Test 3: Create Duplicate Vendor (Negative Test)
```
POST /api/v1/vendors/
Body: vendor_name that already exists
Expected: 400 Bad Request
Error: "Vendor with this name already exists"
```

#### Test 4: Get Vendor Payment History
```
GET /api/v1/vendors/1/payments/
Expected: 200 OK with payment transactions for that vendor
```

#### Test 5: Search Vendors
```
GET /api/v1/vendors/search/?q=court
Expected: 200 OK with filtered vendors
```

#### Test 6: List Vendor Types
```
GET /api/v1/vendors/types/
Expected: 200 OK with vendor type categories
```

#### Test 7: Create Vendor Type
```
POST /api/v1/vendors/types/
Body:
{
    "name": "Medical Providers",
    "description": "Doctors and hospitals",
    "is_active": true
}
Expected: 201 Created
```

---

### G. Check Management Testing

#### Test 1: List All Checks
```
GET /api/v1/checks/
Expected: 200 OK with check transactions
```

#### Test 2: Get Check Detail
```
GET /api/v1/checks/1/
Expected: 200 OK with check information
```

---

### H. Reconciliation Testing

#### Test 1: List All Reconciliations
```
GET /api/v1/bank-accounts/reconciliations/
Expected: 200 OK with reconciliation records
```

#### Test 2: Create Reconciliation (Balanced)
```
POST /api/v1/bank-accounts/reconciliations/
Body:
{
    "bank_account": 1,
    "reconciliation_date": "2025-10-31",
    "statement_balance": "45678.90",
    "book_balance": "45678.90",
    "is_reconciled": true,
    "reconciled_by": "admin",
    "notes": "October reconciliation - balanced"
}
Expected: 201 Created
```

**Verify:**
- `difference` is calculated as 0.00
- `is_balanced` is true

#### Test 3: Create Reconciliation (Unbalanced)
```
POST /api/v1/bank-accounts/reconciliations/
Body:
{
    "bank_account": 1,
    "reconciliation_date": "2025-10-31",
    "statement_balance": "45678.90",
    "book_balance": "45000.00",
    "is_reconciled": false,
    "notes": "October reconciliation - needs investigation"
}
Expected: 201 Created
```

**Verify:**
- `difference` is 678.90
- `is_balanced` is false

---

## 5. Common Test Cases

### Test Case Template

For each endpoint, perform these standard tests:

#### ✅ Happy Path Tests
1. Create with valid data → 201 Created
2. Read/List → 200 OK
3. Update with valid data → 200 OK
4. Delete → 204 No Content

#### ❌ Negative Tests
1. Create without authentication → 401 Unauthorized
2. Create with missing required fields → 400 Bad Request
3. Create with invalid data types → 400 Bad Request
4. Get non-existent resource → 404 Not Found
5. Update non-existent resource → 404 Not Found
6. Delete non-existent resource → 404 Not Found

#### 🔐 Authorization Tests
1. Access endpoint without login → 401 Unauthorized
2. Access endpoint with expired session → 401 Unauthorized

#### 📊 Data Validation Tests
1. Email format validation
2. Phone format validation
3. Date format validation (YYYY-MM-DD)
4. Amount validation (positive decimal)
5. Required field validation
6. Unique constraint validation

---

## 6. Error Handling Tests

### Test Invalid Authentication

#### Test 1: Access API Without Login
```
GET /api/v1/clients/
(without logging in first)
Expected: 401 Unauthorized
```

#### Test 2: Login with Wrong Password
```
POST /api/auth/login/
Body:
{
    "username": "admin",
    "password": "wrongpassword"
}
Expected: 401 Unauthorized
```

### Test Invalid Resource IDs

#### Test 3: Get Non-Existent Client
```
GET /api/v1/clients/99999/
Expected: 404 Not Found
```

#### Test 4: Update Non-Existent Case
```
PUT /api/v1/cases/99999/
Expected: 404 Not Found
```

### Test Invalid Data

#### Test 5: Create Client with Invalid Email
```
POST /api/v1/clients/
Body: email = "notanemail"
Expected: 400 Bad Request
```

#### Test 6: Create Transaction with Invalid Date
```
POST /api/v1/bank-accounts/bank-transactions/
Body: transaction_date = "13/40/2025"
Expected: 400 Bad Request
```

---

## 7. Data Validation Tests

### Email Validation
- Valid: `user@example.com`
- Invalid: `notanemail`, `user@`, `@example.com`

### Phone Validation
- Valid: `(555) 123-4567`, `555-123-4567`, `5551234567`
- Test edge cases

### Date Validation
- Valid: `2025-10-12` (YYYY-MM-DD)
- Invalid: `10/12/2025`, `2025-13-01`, `invalid`

### Amount Validation
- Valid: `1000.00`, `0.01`, `999999.99`
- Invalid: `-100.00`, `abc`, `1000.001` (too many decimals)

### Zip Code Validation
- Valid: `10001`, `12345`
- Invalid: `1234`, `abcde`, `123456`

---

## 8. Expected Response Codes

| Code | Meaning | When to Expect |
|------|---------|----------------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST (resource created) |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid data, validation errors |
| 401 | Unauthorized | Not authenticated |
| 403 | Forbidden | Authenticated but not permitted |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Backend error (report immediately) |

---

## 9. Troubleshooting

### Issue: 401 Unauthorized on All Requests

**Solution:**
1. Run the Login request first: `POST /api/auth/login/`
2. Verify response is 200 OK
3. Check that Postman saved the `sessionid` cookie
4. Try the request again

**Check Cookies:**
- Click "Cookies" link under the Send button
- Look for `sessionid` cookie for `localhost`
- If missing, login again

### Issue: 404 Not Found

**Solution:**
1. Verify the Docker containers are running: `docker ps`
2. Check the base URL in environment: `http://localhost:3000/api`
3. Verify the endpoint path is correct
4. Check if resource ID exists (try list endpoint first)

### Issue: 400 Bad Request

**Solution:**
1. Check response body for specific error message
2. Verify all required fields are included
3. Check data types (strings in quotes, numbers without quotes)
4. Verify date format is YYYY-MM-DD
5. Check for duplicate data (names, emails, account numbers)

### Issue: Session Expired

**Solution:**
1. Run logout: `POST /api/auth/logout/`
2. Run login again: `POST /api/auth/login/`
3. Continue testing with new session

### Issue: Cannot Create Transaction

**Solution:**
1. Verify bank account exists: `GET /api/v1/bank-accounts/accounts/`
2. Verify client exists: `GET /api/v1/clients/`
3. Verify case exists: `GET /api/v1/cases/`
4. Check that amount is positive decimal
5. Verify all required fields are present

---

## Test Execution Checklist

### Pre-Testing
- [ ] Docker containers are running
- [ ] Frontend accessible at http://localhost:3000
- [ ] Postman collection imported
- [ ] Postman environment imported and selected
- [ ] Environment variables verified

### Authentication Testing
- [ ] Login successful (200 OK)
- [ ] Check auth status (200 OK)
- [ ] Access endpoints without login (401 Unauthorized)
- [ ] Logout successful (200 OK)

### Dashboard Testing
- [ ] Get dashboard data (200 OK)
- [ ] Get law firm info (200 OK)
- [ ] Get uncleared transactions (200 OK)

### Client Management
- [ ] List clients (200 OK)
- [ ] Create client (201 Created)
- [ ] Get client detail (200 OK)
- [ ] Update client (200 OK)
- [ ] Search clients (200 OK)
- [ ] Get client cases (200 OK)
- [ ] Delete client (204 No Content)
- [ ] Duplicate client validation (400 Bad Request)

### Case Management
- [ ] List cases (200 OK)
- [ ] Create case (201 Created)
- [ ] Get case detail (200 OK)
- [ ] Update case (200 OK)
- [ ] Get case balance (200 OK)
- [ ] Get case transactions (200 OK)
- [ ] Delete case (204 No Content)
- [ ] Closed case validation (400 if no closed_date)

### Bank Account Management
- [ ] List accounts (200 OK)
- [ ] Create account (201 Created)
- [ ] Get account detail (200 OK)
- [ ] Get account transactions (200 OK)
- [ ] Account summary (200 OK)
- [ ] Duplicate account number (400 Bad Request)
- [ ] Negative balance validation (400 Bad Request)

### Transaction Management
- [ ] List transactions (200 OK)
- [ ] Create deposit (201 Created)
- [ ] Create withdrawal (201 Created)
- [ ] Create vendor payment (201 Created)
- [ ] Get unmatched transactions (200 OK)
- [ ] Balance calculations correct
- [ ] Negative amount validation (400 Bad Request)

### Vendor Management
- [ ] List vendors (200 OK)
- [ ] Create vendor (201 Created)
- [ ] Get vendor detail (200 OK)
- [ ] Get vendor payments (200 OK)
- [ ] Search vendors (200 OK)
- [ ] Duplicate vendor validation (400 Bad Request)

### Reconciliation Management
- [ ] List reconciliations (200 OK)
- [ ] Create balanced reconciliation (201 Created)
- [ ] Create unbalanced reconciliation (201 Created)
- [ ] Difference calculation correct

---

## Additional Notes

### Test Data Integrity

After running tests, verify:

1. **Balance Calculations:**
   - Trust balance = Sum of all client balances
   - Bank register = Sum of all non-voided transactions
   - Trust balance should match bank register

2. **Transaction Status:**
   - PENDING: Not yet cleared/reconciled
   - CLEARED: Posted and cleared
   - VOIDED: Cancelled, not counted in balance

3. **Audit Trail:**
   - All creates/updates/deletes should log to audit trail
   - Check Django admin or database for audit records

4. **Auto-Generated Numbers:**
   - Client numbers start at 1001
   - Case numbers format: CASE-1001
   - Transaction numbers auto-increment
   - Vendor numbers start at 1001

### Performance Notes

- List endpoints may return large datasets
- Use search/filter parameters when available
- Response times should be < 2 seconds for most endpoints

### Reporting Issues

When reporting bugs, include:

1. **Request Details:**
   - HTTP method (GET, POST, PUT, etc.)
   - Full URL
   - Request headers
   - Request body (if applicable)

2. **Response Details:**
   - Status code
   - Response body
   - Error messages

3. **Steps to Reproduce:**
   - Clear sequence of requests
   - Test data used
   - Expected vs actual behavior

4. **Environment:**
   - Docker container status
   - Browser/Postman version
   - Time of error

---

## Quick Reference - Common Variable IDs

Update these in your environment after creating test data:

```
client_id: 1
case_id: 1
account_id: 1
vendor_id: 1
transaction_id: 1
```

To update a variable in Postman:
1. Click eye icon (👁️) next to environment
2. Click "Edit" next to environment name
3. Update the "CURRENT VALUE" for the variable
4. Click "Save"

---

## Contact & Support

For technical issues or questions about testing:
- Check application logs in Docker: `docker logs iolta_backend`
- Review database in Django admin: http://localhost:3000/admin
- Consult the main test scenarios document: `COMPREHENSIVE_TEST_SCENARIOS.md`

---

**Document Version:** 1.0
**Last Updated:** October 12, 2025
**Prepared For:** QA Testing Team
