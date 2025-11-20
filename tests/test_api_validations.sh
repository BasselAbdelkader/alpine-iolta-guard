#!/bin/bash

# Test API Validations for 3 Critical Security Fixes
# Must be run after logging in

BASE_URL="http://localhost/api/v1/bank-accounts/bank-transactions/"

echo "=========================================================================="
echo "TESTING CRITICAL SECURITY VALIDATIONS"
echo "=========================================================================="
echo ""

# Get bank account ID
BANK_ACCOUNT_ID=$(docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -t -c "SELECT id FROM bank_accounts LIMIT 1;" | tr -d ' ')

echo "Using Bank Account ID: $BANK_ACCOUNT_ID"
echo "Case 1 Balance: \$4,953.00"
echo ""

# ========================================================================
# TEST 1: Client-Case Relationship Validation
# ========================================================================
echo "=========================================================================="
echo "TEST 1: Client-Case Relationship Validation"
echo "=========================================================================="
echo "Attempting to assign Case 1 (belongs to Client 1) to Client 3..."
echo ""

curl -s -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "bank_account": '$BANK_ACCOUNT_ID',
    "client": 3,
    "case": 1,
    "transaction_date": "2025-01-10",
    "transaction_type": "WITHDRAWAL",
    "amount": 100.00,
    "description": "Test client-case mismatch",
    "payee": "Test Vendor",
    "reference_number": "TEST-REF-001"
  }' | python3 -m json.tool

echo ""
echo "Expected: ERROR - 'Invalid case assignment'"
echo ""

# ========================================================================
# TEST 2: Insufficient Funds Validation
# ========================================================================
echo "=========================================================================="
echo "TEST 2: Insufficient Funds Validation"
echo "=========================================================================="
echo "Attempting to withdraw \$10,000.00 from Case 1 (only has \$4,953.00)..."
echo ""

curl -s -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "bank_account": '$BANK_ACCOUNT_ID',
    "client": 1,
    "case": 1,
    "transaction_date": "2025-01-10",
    "transaction_type": "WITHDRAWAL",
    "amount": 10000.00,
    "description": "Test insufficient funds",
    "payee": "Test Vendor",
    "reference_number": "TEST-REF-002"
  }' | python3 -m json.tool

echo ""
echo "Expected: ERROR - 'Insufficient funds'"
echo ""

# ========================================================================
# TEST 3: Edit Amount Bypass Protection
# ========================================================================
echo "=========================================================================="
echo "TEST 3: Edit Amount Bypass Protection"
echo "=========================================================================="
echo "Step 1: Creating small withdrawal (\$100)..."
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "bank_account": '$BANK_ACCOUNT_ID',
    "client": 1,
    "case": 1,
    "transaction_date": "2025-01-10",
    "transaction_type": "WITHDRAWAL",
    "amount": 100.00,
    "description": "Small withdrawal for edit test",
    "payee": "Test Vendor",
    "reference_number": "TEST-REF-003"
  }')

echo "$RESPONSE" | python3 -m json.tool

# Extract transaction ID
TRANSACTION_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', 0))" 2>/dev/null)

if [ "$TRANSACTION_ID" != "0" ] && [ -n "$TRANSACTION_ID" ]; then
    echo ""
    echo "Created transaction ID: $TRANSACTION_ID"
    echo "Step 2: Attempting to edit \$100 to \$10,000 (requires \$9,900 more, only \$4,853 available)..."
    echo ""
    
    curl -s -X PUT "${BASE_URL}${TRANSACTION_ID}/" \
      -H "Content-Type: application/json" \
      -d '{
        "bank_account": '$BANK_ACCOUNT_ID',
        "client": 1,
        "case": 1,
        "transaction_date": "2025-01-10",
        "transaction_type": "WITHDRAWAL",
        "amount": 10000.00,
        "description": "Edit bypass attack attempt",
        "payee": "Test Vendor",
        "reference_number": "TEST-REF-003"
      }' | python3 -m json.tool
    
    echo ""
    echo "Expected: ERROR - 'Insufficient funds for this edit'"
else
    echo "Failed to create test transaction"
fi

echo ""
echo "=========================================================================="
echo "VALIDATION TESTS COMPLETE"
echo "=========================================================================="
