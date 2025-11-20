#!/usr/bin/env python
"""
Test BankTransactionSerializer to check amount format
"""
import os, sys, django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.bank_accounts.api.serializers import BankTransactionSerializer
from apps.bank_accounts.models import BankTransaction

print("\n=== TESTING BANK TRANSACTION SERIALIZER ===\n")

# Get first transaction
transaction = BankTransaction.objects.select_related('bank_account', 'client', 'case').first()

if not transaction:
    print("❌ No transactions found in database")
    sys.exit(1)

print(f"Testing Transaction ID: {transaction.id}")
print(f"Raw Amount from DB: {transaction.amount}")
print(f"Amount Type in DB: {type(transaction.amount)}\n")

# Serialize it
serializer = BankTransactionSerializer(transaction)
data = serializer.data

print("--- Serialized Data ---")
print(f"Amount in API Response: {data.get('amount')}")
print(f"Amount Type: {type(data.get('amount'))}\n")

# Check if it's parseable by JavaScript
amount_value = data.get('amount')
if isinstance(amount_value, str):
    print("❌ PROBLEM: Amount is a STRING")
    print(f"   Value: '{amount_value}'")
    print(f"   Frontend parseFloat('{amount_value}') will fail!")

    # Try to parse it
    try:
        parsed = float(amount_value.replace('$', '').replace(',', ''))
        print(f"   (Can be parsed after removing $ and commas: {parsed})")
    except:
        print(f"   Cannot be parsed even after cleanup!")

elif isinstance(amount_value, (int, float)):
    print("✅ GOOD: Amount is NUMERIC")
    print(f"   Value: {amount_value}")
    print(f"   Frontend parseFloat({amount_value}) will work correctly")
else:
    print(f"❓ Unknown type: {type(amount_value)}")

# Test a few more transactions
print("\n--- Testing Multiple Transactions ---")
transactions = BankTransaction.objects.all()[:5]
serializer = BankTransactionSerializer(transactions, many=True)

string_count = 0
numeric_count = 0

for txn_data in serializer.data:
    amount = txn_data.get('amount')
    if isinstance(amount, str):
        string_count += 1
    elif isinstance(amount, (int, float)):
        numeric_count += 1

print(f"String amounts: {string_count}/5")
print(f"Numeric amounts: {numeric_count}/5\n")

if string_count > 0:
    print("❌ CONCLUSION: API is returning formatted STRING amounts")
    print("   This causes NaN in frontend (parseFloat fails)")
    print("   Need to change serializer to return NUMERIC values\n")
else:
    print("✅ CONCLUSION: API is returning NUMERIC amounts")
    print("   Frontend parseFloat() will work correctly\n")

print("=== TEST COMPLETE ===\n")
