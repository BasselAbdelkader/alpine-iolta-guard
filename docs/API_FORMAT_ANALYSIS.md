# Bank/Transaction API Data Format Analysis

**Analysis Date:** November 7, 2025
**Requirement:** US Format
- **Dates:** MM/DD/YY
- **Money:** $XX,XXX.00 ($ sign, comma separation for thousands, 2 decimal places)

---

## Executive Summary

**Current State:**
- ✅ **1 API** already has US money format (with comma, but missing $ sign)
- ❌ **ALL APIs** return dates in ISO format (YYYY-MM-DD) instead of MM/DD/YY
- ❌ **Most APIs** return money as plain decimal strings (no $ sign, no commas)

**APIs Requiring Format Changes:** **7 APIs** need date/money formatting

---

## API Inventory & Format Analysis

### 1️⃣ `/api/v1/bank-accounts/bank-transactions/` (List/Detail)
**Purpose:** List all bank transactions, get transaction details
**Method:** GET, POST, PUT, PATCH, DELETE
**Serializer:** `BankTransactionSerializer`

**Current Format:**
```json
{
  "transaction_date": "2025-10-14",          ← ISO format (YYYY-MM-DD)
  "amount": "34.78",                          ← Plain decimal, no $ or comma
  "post_date": null,
  "created_at": "2025-10-14T06:47:32.229724Z"
}
```

**Required Format:**
```json
{
  "transaction_date": "10/14/25",             ← US format (MM/DD/YY)
  "amount": "$34.78",                         ← $ sign + comma + 2 decimals
  "post_date": null,
  "created_at": "10/14/25"                    ← US format
}
```

**Fields Needing Format:**
- ❌ `transaction_date` → needs MM/DD/YY
- ❌ `post_date` → needs MM/DD/YY
- ❌ `amount` → needs $XX,XXX.00
- ❌ `created_at` → needs MM/DD/YY (or MM/DD/YY HH:MM AM/PM)
- ❌ `updated_at` → needs MM/DD/YY
- ❌ `voided_date` → needs MM/DD/YY

**File:** `/app/apps/bank_accounts/api/serializers.py:101-291`

---

### 2️⃣ `/api/v1/bank-accounts/accounts/` (List/Detail)
**Purpose:** List all bank accounts, get account details
**Method:** GET, POST, PUT, PATCH, DELETE
**Serializer:** `BankAccountSerializer` (detail), `BankAccountListSerializer` (list)

**Current Format:**
```json
{
  "opening_balance": "0.00",                  ← Plain decimal
  "trust_balance": 398939.22,                 ← Decimal object (no quotes)
  "formatted_trust_balance": "398,939.22",    ← Has comma, but NO $ sign ⚠️
  "created_at": "2025-10-03T09:40:14.766563Z",
  "updated_at": "2025-10-14T06:47:32.229735Z"
}
```

**Required Format:**
```json
{
  "opening_balance": "$0.00",                 ← $ sign
  "trust_balance": "$398,939.22",             ← $ sign + comma
  "formatted_trust_balance": "$398,939.22",   ← Add $ sign
  "created_at": "10/03/25",
  "updated_at": "10/14/25"
}
```

**Fields Needing Format:**
- ⚠️ `formatted_trust_balance` → HAS comma, needs $ sign
- ❌ `opening_balance` → needs $XX,XXX.00
- ❌ `trust_balance` → needs $XX,XXX.00
- ❌ `register_balance` → needs $XX,XXX.00
- ❌ `created_at` → needs MM/DD/YY
- ❌ `updated_at` → needs MM/DD/YY
- ❌ `last_transaction_date` → needs MM/DD/YY

**File:** `/app/apps/bank_accounts/api/serializers.py:5-99`

---

### 3️⃣ `/api/v1/bank-accounts/accounts/{id}/transactions/`
**Purpose:** Get all transactions for a specific bank account
**Method:** GET
**View:** `BankAccountViewSet.transactions()` (custom action)

**Current Format:**
```json
{
  "account_id": 1,
  "account_name": "IOLTA Trust Account - Main",
  "current_balance": "398939.22",             ← Plain decimal string
  "transactions": [
    {
      "transaction_date": "2025-10-14",       ← ISO format
      "amount": "34.78"                       ← Plain decimal
    }
  ],
  "summary": {
    "total_amount": "12345.67",               ← Plain decimal
    "deposits": "5000.00",                    ← Plain decimal
    "withdrawals": "2000.00",                 ← Plain decimal
    "cleared_amount": "3000.00"               ← Plain decimal
  }
}
```

**Required Format:**
```json
{
  "current_balance": "$398,939.22",           ← $ + comma
  "transactions": [
    {
      "transaction_date": "10/14/25",         ← MM/DD/YY
      "amount": "$34.78"
    }
  ],
  "summary": {
    "total_amount": "$12,345.67",
    "deposits": "$5,000.00",
    "withdrawals": "$2,000.00",
    "cleared_amount": "$3,000.00"
  }
}
```

**Fields Needing Format:**
- ❌ `current_balance` → needs $XX,XXX.00
- ❌ `transactions[].transaction_date` → needs MM/DD/YY (uses BankTransactionSerializer)
- ❌ `transactions[].amount` → needs $XX,XXX.00
- ❌ `summary.total_amount` → needs $XX,XXX.00
- ❌ `summary.deposits` → needs $XX,XXX.00
- ❌ `summary.withdrawals` → needs $XX,XXX.00
- ❌ `summary.cleared_amount` → needs $XX,XXX.00

**File:** `/app/apps/bank_accounts/api/views.py:107-154`

---

### 4️⃣ `/api/v1/bank-accounts/accounts/{id}/balance_history/`
**Purpose:** Get balance history for a bank account
**Method:** GET
**View:** `BankAccountViewSet.balance_history()` (custom action)

**Current Format:**
```json
{
  "opening_balance": "0.00",                  ← Plain decimal
  "current_balance": "398939.22",             ← Plain decimal
  "balance_history": [
    {
      "date": "2025-10-03",                   ← ISO format (date object)
      "amount": "1000.00",                    ← Plain decimal
      "running_balance": "1000.00"            ← Plain decimal
    }
  ]
}
```

**Required Format:**
```json
{
  "opening_balance": "$0.00",
  "current_balance": "$398,939.22",
  "balance_history": [
    {
      "date": "10/03/25",                     ← MM/DD/YY
      "amount": "$1,000.00",
      "running_balance": "$1,000.00"
    }
  ]
}
```

**Fields Needing Format:**
- ❌ `opening_balance` → needs $XX,XXX.00
- ❌ `current_balance` → needs $XX,XXX.00
- ❌ `balance_history[].date` → needs MM/DD/YY
- ❌ `balance_history[].amount` → needs $XX,XXX.00
- ❌ `balance_history[].running_balance` → needs $XX,XXX.00

**File:** `/app/apps/bank_accounts/api/views.py:156-200`

---

### 5️⃣ `/api/v1/bank-accounts/accounts/summary/`
**Purpose:** Get comprehensive summary of all bank accounts
**Method:** GET
**View:** `BankAccountViewSet.summary()` (custom action)

**Current Format:**
```json
{
  "total_system_balance": "500000.00",        ← Plain decimal
  "account_details": [
    {
      "opening_balance": "0.00",              ← Plain decimal
      "current_balance": "398939.22",         ← Plain decimal
      "balance_difference": "398939.22"       ← Plain decimal
    }
  ]
}
```

**Required Format:**
```json
{
  "total_system_balance": "$500,000.00",
  "account_details": [
    {
      "opening_balance": "$0.00",
      "current_balance": "$398,939.22",
      "balance_difference": "$398,939.22"
    }
  ]
}
```

**Fields Needing Format:**
- ❌ `total_system_balance` → needs $XX,XXX.00
- ❌ `account_details[].opening_balance` → needs $XX,XXX.00
- ❌ `account_details[].current_balance` → needs $XX,XXX.00
- ❌ `account_details[].balance_difference` → needs $XX,XXX.00

**File:** `/app/apps/bank_accounts/api/views.py:202-232`

---

### 6️⃣ `/api/v1/bank-accounts/bank-transactions/summary/`
**Purpose:** Get summary statistics for all transactions
**Method:** GET
**View:** `BankTransactionViewSet.summary()` (custom action)

**Current Format:**
```json
{
  "deposits": {
    "total": "50000.00"                       ← Plain decimal
  },
  "withdrawals": {
    "total": "20000.00"                       ← Plain decimal
  },
  "matched": {
    "amount": "30000.00"                      ← Plain decimal
  },
  "unmatched": {
    "amount": "10000.00"                      ← Plain decimal
  }
}
```

**Required Format:**
```json
{
  "deposits": {
    "total": "$50,000.00"
  },
  "withdrawals": {
    "total": "$20,000.00"
  },
  "matched": {
    "amount": "$30,000.00"
  },
  "unmatched": {
    "amount": "$10,000.00"
  }
}
```

**Fields Needing Format:**
- ❌ `deposits.total` → needs $XX,XXX.00
- ❌ `withdrawals.total` → needs $XX,XXX.00
- ❌ `matched.amount` → needs $XX,XXX.00
- ❌ `unmatched.amount` → needs $XX,XXX.00

**File:** `/app/apps/bank_accounts/api/views.py:611-644`

---

### 7️⃣ `/api/v1/bank-accounts/bank-transactions/missing/`
**Purpose:** Get missing/outstanding transactions
**Method:** GET
**View:** `BankTransactionViewSet.missing()` (custom action)

**Current Format:**
```json
{
  "missing_checks": [
    {
      "transaction_date": "2025-10-14",       ← ISO format
      "amount": "34.78"                       ← Plain decimal
    }
  ],
  "missing_checks_amount": "1234.56"          ← Plain decimal
}
```

**Required Format:**
```json
{
  "missing_checks": [
    {
      "transaction_date": "10/14/25",
      "amount": "$34.78"
    }
  ],
  "missing_checks_amount": "$1,234.56"
}
```

**Fields Needing Format:**
- ❌ `missing_checks[]` → uses BankTransactionSerializer (dates + amounts)
- ❌ `missing_checks_amount` → needs $XX,XXX.00

**File:** `/app/apps/bank_accounts/api/views.py:646-661`

---

### 8️⃣ `/api/v1/bank-accounts/bank-transactions/{id}/audit_history/`
**Purpose:** Get audit history for a transaction
**Method:** GET
**View:** `BankTransactionViewSet.audit_history()` (custom action)

**Current Format:**
```json
{
  "transaction": {
    "transaction_date": "10/14/2025",         ← Already MM/DD/YYYY ✓ (but needs YY)
    "amount": "34.78"                         ← Plain decimal
  },
  "audit_logs": [
    {
      "action_date": "10/14/2025 06:47 PM",   ← Already MM/DD/YYYY HH:MM AM/PM ✓
      "old_amount": "100.00",                 ← Plain decimal
      "new_amount": "200.00"                  ← Plain decimal
    }
  ]
}
```

**Required Format:**
```json
{
  "transaction": {
    "transaction_date": "10/14/25",           ← Change to YY instead of YYYY
    "amount": "$34.78"
  },
  "audit_logs": [
    {
      "action_date": "10/14/25 06:47 PM",     ← Change to YY instead of YYYY
      "old_amount": "$100.00",
      "new_amount": "$200.00"
    }
  ]
}
```

**Fields Needing Format:**
- ⚠️ `transaction.transaction_date` → has MM/DD/YYYY, needs MM/DD/YY
- ❌ `transaction.amount` → needs $XX,XXX.00
- ⚠️ `audit_logs[].action_date` → has MM/DD/YYYY, needs MM/DD/YY
- ❌ `audit_logs[].old_amount` → needs $XX,XXX.00
- ❌ `audit_logs[].new_amount` → needs $XX,XXX.00

**File:** `/app/apps/bank_accounts/api/views.py:520-569`

---

### 9️⃣ `/api/v1/cases/{id}/transactions/`
**Purpose:** Get all transactions for a specific case
**Method:** GET
**View:** `CaseViewSet.transactions()` (custom action)

**Current Format:**
```json
{
  "current_balance": "4953.00",               ← Plain decimal
  "transactions": [
    {
      "date": "2025-10-14",                   ← ISO format (date object)
      "amount": "34.78",                      ← Plain decimal
      "voided_date": "2025-10-15"             ← ISO format
    }
  ]
}
```

**Required Format:**
```json
{
  "current_balance": "$4,953.00",
  "transactions": [
    {
      "date": "10/14/25",
      "amount": "$34.78",
      "voided_date": "10/15/25"
    }
  ]
}
```

**Fields Needing Format:**
- ❌ `current_balance` → needs $XX,XXX.00
- ❌ `transactions[].date` → needs MM/DD/YY
- ❌ `transactions[].amount` → needs $XX,XXX.00
- ❌ `transactions[].voided_date` → needs MM/DD/YY

**File:** `/app/apps/clients/api/views.py:354-394`

---

### 🔟 `/api/v1/bank-accounts/reconciliations/`
**Purpose:** List/create/update bank reconciliations
**Method:** GET, POST, PUT, PATCH, DELETE
**Serializer:** `BankReconciliationSerializer`

**Current Format:**
```json
{
  "reconciliation_date": "2025-10-14",        ← ISO format
  "statement_balance": "100000.00",           ← Plain decimal
  "book_balance": "100000.00",                ← Plain decimal
  "difference": "0.00",                       ← Plain decimal
  "reconciled_at": "2025-10-14T10:00:00Z"
}
```

**Required Format:**
```json
{
  "reconciliation_date": "10/14/25",
  "statement_balance": "$100,000.00",
  "book_balance": "$100,000.00",
  "difference": "$0.00",
  "reconciled_at": "10/14/25"
}
```

**Fields Needing Format:**
- ❌ `reconciliation_date` → needs MM/DD/YY
- ❌ `statement_balance` → needs $XX,XXX.00
- ❌ `book_balance` → needs $XX,XXX.00
- ❌ `difference` → needs $XX,XXX.00
- ❌ `reconciled_at` → needs MM/DD/YY
- ❌ `created_at` → needs MM/DD/YY

**File:** `/app/apps/bank_accounts/api/serializers.py:293-319`

---

## Summary Table

| API Endpoint | Current Date Format | Current Money Format | Status |
|--------------|---------------------|----------------------|--------|
| `/api/v1/bank-accounts/bank-transactions/` | ISO (YYYY-MM-DD) | Plain decimal | ❌ Needs both |
| `/api/v1/bank-accounts/accounts/` | ISO (YYYY-MM-DD) | Has comma, no $ | ⚠️ Needs both |
| `/api/v1/bank-accounts/accounts/{id}/transactions/` | ISO (YYYY-MM-DD) | Plain decimal | ❌ Needs both |
| `/api/v1/bank-accounts/accounts/{id}/balance_history/` | ISO (YYYY-MM-DD) | Plain decimal | ❌ Needs both |
| `/api/v1/bank-accounts/accounts/summary/` | N/A | Plain decimal | ❌ Needs money |
| `/api/v1/bank-accounts/bank-transactions/summary/` | N/A | Plain decimal | ❌ Needs money |
| `/api/v1/bank-accounts/bank-transactions/missing/` | ISO (YYYY-MM-DD) | Plain decimal | ❌ Needs both |
| `/api/v1/bank-accounts/bank-transactions/{id}/audit_history/` | MM/DD/YYYY | Plain decimal | ⚠️ Needs both (4→2 digit year) |
| `/api/v1/cases/{id}/transactions/` | ISO (YYYY-MM-DD) | Plain decimal | ❌ Needs both |
| `/api/v1/bank-accounts/reconciliations/` | ISO (YYYY-MM-DD) | Plain decimal | ❌ Needs both |

**Total APIs:** 10
**Fully Compliant:** 0
**Partially Compliant:** 2 (audit history has US date format with 4-digit year; accounts has comma)
**Non-Compliant:** 8

---

## Implementation Strategy

### Option 1: **Serializer-Level Formatting** ✅ RECOMMENDED
**Pros:**
- Centralized formatting logic
- DRY (Don't Repeat Yourself)
- Easy to maintain
- Consistent across all endpoints using same serializer

**Implementation:**
- Add custom `SerializerMethodField` for formatted dates/money
- OR override `to_representation()` method in serializers

**Files to Modify:**
1. `/app/apps/bank_accounts/api/serializers.py`
   - `BankTransactionSerializer` (lines 101-291)
   - `BankAccountSerializer` (lines 5-66)
   - `BankAccountListSerializer` (lines 68-99)
   - `BankReconciliationSerializer` (lines 293-319)

2. `/app/apps/clients/api/views.py`
   - `CaseViewSet.transactions()` (lines 354-394)

### Option 2: **View-Level Formatting**
**Pros:**
- More control per endpoint
- Can customize per use case

**Cons:**
- Code duplication
- Harder to maintain
- Inconsistent if not careful

### Option 3: **Utility Functions**
**Pros:**
- Reusable across serializers and views
- Centralized logic

**Implementation:**
```python
# utils/formatters.py
def format_us_date(date_obj):
    """Convert date to MM/DD/YY format"""
    if not date_obj:
        return None
    return date_obj.strftime('%m/%d/%y')

def format_us_money(amount):
    """Convert decimal to $XX,XXX.00 format"""
    if amount is None:
        return None
    return f"${amount:,.2f}"
```

---

## Recommendation

**Use Option 1 (Serializer-Level) + Option 3 (Utility Functions)**

1. Create utility functions in `/app/apps/api/utils/formatters.py`
2. Use utility functions in serializers via `SerializerMethodField` or `to_representation()`
3. For custom view actions (like `transactions()`, `balance_history()`), apply formatting in view

**Benefits:**
- ✅ Centralized formatting logic
- ✅ Consistent across entire API
- ✅ Easy to test
- ✅ Easy to change if requirements change (e.g., switch to MM/DD/YYYY)

---

## Next Steps

1. **Create utility formatters** (`/app/apps/api/utils/formatters.py`)
2. **Update serializers** to use formatters
3. **Update custom view actions** to use formatters
4. **Test all 10 APIs** to verify formatting
5. **Update API documentation** with new response formats

---

**Total Estimated Changes:** ~200 lines of code across 4 files
