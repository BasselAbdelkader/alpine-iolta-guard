# IOLTA Guard - Test Scripts

This directory contains test scripts used to verify implementations and bug fixes.

**Location:** `/home/amin/Projects/ve_demo/tests/`

---

## 📋 Test Scripts

### **1. check_api_formats.py** (8.1 KB)
Tests API response formats (dates and money).

**Purpose:** Initial analysis of date and money formats across all APIs

**Run:**
```bash
docker exec iolta_backend_alpine python /app/../tests/check_api_formats.py
```

**Tests:**
- Date format in API responses
- Money format in API responses
- Identifies APIs needing US format conversion

---

### **2. check_balance_api.py** (2.5 KB)
Tests case and client balance calculations.

**Purpose:** Verify balance fields in Case and Client serializers

**Run:**
```bash
docker cp /home/amin/Projects/ve_demo/tests/check_balance_api.py iolta_backend_alpine:/tmp/
docker exec iolta_backend_alpine python /tmp/check_balance_api.py
```

**Tests:**
- Case formatted_balance field
- Client formatted_balance field
- Balance calculation accuracy

---

### **3. test_api_responses.py** (Empty)
Template for testing API responses.

**Status:** Empty file (not used)

---

### **4. test_case_transactions.py** (3.0 KB)
Tests case transaction endpoint data.

**Purpose:** Verify transaction data for case detail page

**Run:**
```bash
docker cp /home/amin/Projects/ve_demo/tests/test_case_transactions.py iolta_backend_alpine:/tmp/
docker exec iolta_backend_alpine python /tmp/test_case_transactions.py
```

**Tests:**
- Raw transaction amounts
- API response formatting
- Running balance calculation

---

### **5. test_case_transactions_fix.py** (1.8 KB)
Tests case transactions fix ($ sign).

**Purpose:** Verify $ sign in transaction amounts and balances

**Run:**
```bash
docker cp /home/amin/Projects/ve_demo/tests/test_case_transactions_fix.py iolta_backend_alpine:/tmp/
docker exec iolta_backend_alpine python /tmp/test_case_transactions_fix.py
```

**Tests:**
- All amounts have $ sign
- All balances have $ sign
- Proper formatting of withdrawals (parentheses)

**Result:** ✅ All amounts and balances have $ sign

---

### **6. test_critical_validations.py** (16.9 KB)
Comprehensive backend validation testing.

**Purpose:** Test all 3 critical backend security fixes

**Run:**
```bash
docker cp /home/amin/Projects/ve_demo/tests/test_critical_validations.py iolta_backend_alpine:/tmp/
docker exec iolta_backend_alpine python /tmp/test_critical_validations.py
```

**Tests:**
- Client-Case relationship validation
- Insufficient funds validation (new transactions)
- Insufficient funds validation (edit bypass prevention)

**Result:** ✅ All 3 security validations working

---

### **7. test_field_replacements.py** (6.8 KB)
Tests field name replacements.

**Purpose:** Verify transaction_number → RefNo and case_number → case_title

**Run:**
```bash
docker cp /home/amin/Projects/ve_demo/tests/test_field_replacements.py iolta_backend_alpine:/tmp/
docker exec iolta_backend_alpine python /tmp/test_field_replacements.py
```

**Tests:**
- BankTransactionSerializer has RefNo (not transaction_number)
- BankTransactionSerializer has case_title (not case_number)
- CaseSerializer has case_title only
- CaseListSerializer has case_title only

**Result:** ✅ 4/4 components passing

---

### **8. test_ordering_direct.py** (7.2 KB)
Tests transaction ordering (database level).

**Purpose:** Verify all APIs return transactions oldest-first

**Run:**
```bash
docker cp /home/amin/Projects/ve_demo/tests/test_ordering_direct.py iolta_backend_alpine:/tmp/
docker exec iolta_backend_alpine python /tmp/test_ordering_direct.py
```

**Tests:**
- API 1: BankTransactionViewSet (Main List)
- API 2: BankAccountViewSet.transactions()
- API 3: BankAccountViewSet.balance_history()
- API 4: BankTransactionViewSet.missing()
- API 5: CaseViewSet.transactions()
- API 6: ClientViewSet.balance_history()

**Result:** ✅ 6/6 APIs passing (oldest first)

---

### **9. test_transaction_ordering.py** (9.2 KB)
Tests transaction ordering (API level with HTTP).

**Purpose:** Verify transaction ordering through API request/response

**Run:**
```bash
docker cp /home/amin/Projects/ve_demo/tests/test_transaction_ordering.py iolta_backend_alpine:/tmp/
docker exec iolta_backend_alpine python /tmp/test_transaction_ordering.py
```

**Tests:** Same as test_ordering_direct.py but using APIRequestFactory

**Note:** May fail due to ALLOWED_HOSTS, use test_ordering_direct.py instead

---

### **10. test_us_formatting.py** (11.7 KB)
Comprehensive US format testing.

**Purpose:** Verify US date (MM/DD/YY) and money ($XX,XXX.00) formatting

**Run:**
```bash
docker cp /home/amin/Projects/ve_demo/tests/test_us_formatting.py iolta_backend_alpine:/tmp/
docker exec iolta_backend_alpine python /tmp/test_us_formatting.py
```

**Tests:**
- API 1: BankTransactionSerializer
- API 2: BankAccountSerializer
- API 3: Bank Account Transactions
- API 4: Balance History
- API 5: Bank Account Summary
- API 6: Transaction Summary
- API 7: Missing Transactions
- API 8: Audit History
- API 9: Case Transactions

**Result:** ✅ 9/9 API groups passing

---

### **11. test_validations_live.py** (4.4 KB)
Live backend validation testing.

**Purpose:** Test backend validations with actual API requests

**Run:**
```bash
docker cp /home/amin/Projects/ve_demo/tests/test_validations_live.py iolta_backend_alpine:/tmp/
docker exec iolta_backend_alpine python /tmp/test_validations_live.py
```

**Tests:**
- Backend validation responses
- Error message formatting
- Security validation logic

---

### **12. test_case_api.py** (1.8 KB)
Tests case transactions DRF API endpoint.

**Purpose:** Verify `/api/v1/cases/{id}/transactions/` returns numeric amounts

**Run:**
```bash
docker cp /home/amin/Projects/ve_demo/tests/test_case_api.py iolta_backend_alpine:/tmp/
docker exec iolta_backend_alpine python /tmp/test_case_api.py
```

**Tests:**
- API returns numeric amounts (not formatted strings)
- Transaction count and data structure
- Case balance formatting
- All transaction amounts are parseable

**Result:** ✅ All amounts are numeric (45000.0, 14850.0, etc.)

---

### **13. test_case_ledger.py** (2.2 KB)
Tests case ledger endpoint (Django view).

**Purpose:** Verify `/clients/case-transactions/{case_id}/` endpoint

**Run:**
```bash
docker cp /home/amin/Projects/ve_demo/tests/test_case_ledger.py iolta_backend_alpine:/tmp/
docker exec iolta_backend_alpine python /tmp/test_case_ledger.py
```

**Tests:**
- Django view case_transactions() function
- Amount and balance formatting with $ signs
- Transaction data structure
- Running balance calculations

**Result:** ✅ All amounts and balances formatted with $ sign

---

### **14. test_bank_serializer.py** (2.3 KB)
Tests BankTransactionSerializer amount format.

**Purpose:** Verify amounts are returned without $ signs or commas (parseable by JavaScript)

**Run:**
```bash
docker cp /home/amin/Projects/ve_demo/tests/test_bank_serializer.py iolta_backend_alpine:/tmp/
docker exec iolta_backend_alpine python /tmp/test_bank_serializer.py
```

**Tests:**
- Amount field returns parseable strings
- No $ signs in amount values
- No commas in amount values
- Frontend parseFloat() will work correctly

**Result:** ✅ Amount returns as "34.78" (parseable)

---

### **15. test_bank_transactions_api.py** (2.1 KB)
Tests bank transactions API endpoint (full request/response).

**Purpose:** Verify `/api/v1/bank-accounts/bank-transactions/` returns parseable amounts

**Run:**
```bash
docker cp /home/amin/Projects/ve_demo/tests/test_bank_transactions_api.py iolta_backend_alpine:/tmp/
docker exec iolta_backend_alpine python /tmp/test_bank_transactions_api.py
```

**Tests:**
- API endpoint responds correctly
- Amount data structure
- Amount parsing compatibility

**Note:** May have pagination issues, use test_bank_serializer.py instead

---

## 🚀 How to Run Tests

### **Option 1: Copy to Container and Run**
```bash
# Copy test to container
docker cp /home/amin/Projects/ve_demo/tests/test_name.py iolta_backend_alpine:/tmp/

# Run test
docker exec iolta_backend_alpine python /tmp/test_name.py
```

### **Option 2: Run Most Recent Tests (already in container)**
```bash
# US Formatting test
docker exec iolta_backend_alpine python /tmp/test_us_formatting.py

# Transaction ordering test
docker exec iolta_backend_alpine python /tmp/test_ordering_direct.py

# Field replacement test
docker exec iolta_backend_alpine python /tmp/test_field_replacements.py

# Balance test
docker exec iolta_backend_alpine python /tmp/check_balance_api.py

# Case transactions test
docker exec iolta_backend_alpine python /tmp/test_case_transactions_fix.py
```

**Note:** Some tests are already copied to `/tmp/` in the container from recent runs.

---

## 📊 Test Results Summary

| Test | Status | Result |
|------|--------|--------|
| **US Formatting** | ✅ Pass | 9/9 API groups |
| **Transaction Ordering** | ✅ Pass | 6/6 APIs |
| **Field Replacements** | ✅ Pass | 4/4 components |
| **Balance Calculations** | ✅ Pass | Correct $ sign |
| **Case Transactions** | ✅ Pass | All amounts correct |
| **Critical Validations** | ✅ Pass | 3/3 security checks |
| **Case API Numeric Amounts** | ✅ Pass | Returns numeric values |
| **Case Ledger Formatting** | ✅ Pass | $ signs present |
| **Bank Serializer Amount Format** | ✅ Pass | Parseable strings |

---

## 📝 Notes

### **Test Environment**
- **Container:** iolta_backend_alpine
- **Django:** 5.1.3
- **Database:** PostgreSQL 16 Alpine
- **Python:** 3.12

### **Running Tests**
Most tests require Django setup, so they must run inside the container with proper Django environment.

### **Test Data**
Tests use the demo data loaded into the database:
- Case ID 4: Slip and Fall - Commercial Property
- Client ID 1: Sarah Johnson
- Various transactions across multiple cases

---

## 🔗 Related Documentation

See `/home/amin/Projects/ve_demo/docs/` for:
- Implementation summaries
- Bug fix reports
- API analysis documents

---

**Last Updated:** November 7, 2025

---

## 🐚 Shell Scripts

### **16. test_api_validations.sh** (4.5 KB)
Tests API validations using curl commands.

**Purpose:** Test critical security validations through HTTP API

**Run:**
```bash
cd /home/amin/Projects/ve_demo/tests
./test_api_validations.sh
```

**Tests:**
- Client-Case relationship validation
- Insufficient funds validation (new transactions)
- Insufficient funds validation (edit bypass)

**Requirements:**
- Must be logged in (has session cookie)
- Uses curl to make HTTP requests
- Tests actual API endpoints

**Note:** This is a bash script alternative to Python tests, useful for HTTP-level testing.

---
