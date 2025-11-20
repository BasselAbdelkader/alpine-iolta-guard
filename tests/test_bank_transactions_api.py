#!/usr/bin/env python
"""
Test bank transactions API endpoint to check amount format
Frontend expects numeric values but API might be returning formatted strings
"""
import os, sys, django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from apps.bank_accounts.api.views import BankTransactionViewSet
from apps.bank_accounts.models import BankTransaction

print("\n=== TESTING BANK TRANSACTIONS API ===")
print("Endpoint: GET /api/v1/bank-accounts/bank-transactions/?bank_account=1\n")

# Get a bank account and its transactions
from apps.bank_accounts.models import BankAccount
bank_account = BankAccount.objects.first()

if not bank_account:
    print("❌ No bank accounts found in database")
    sys.exit(1)

print(f"Testing with Bank Account ID: {bank_account.id}")
print(f"Bank Account Name: {bank_account.account_name}\n")

# Create a request
factory = APIRequestFactory()
request = factory.get(f'/api/v1/bank-accounts/bank-transactions/?bank_account={bank_account.id}')

# Authenticate
User = get_user_model()
user = User.objects.first()
force_authenticate(request, user=user)

# Get the viewset
viewset = BankTransactionViewSet.as_view({'get': 'list'})

# Call the view
response = viewset(request)

print(f"Status Code: {response.status_code}\n")

if response.status_code == 200:
    # Handle pagination
    if hasattr(response.data, 'get'):
        transactions = response.data.get('results', response.data)
    else:
        transactions = response.data

    if not transactions:
        print("No transactions found for this account")
    else:
        print(f"Total Transactions: {len(transactions)}\n")

        print("--- First 3 Transactions ---")
        for i, txn in enumerate(transactions[:3], 1):
            print(f"\n{i}. Transaction ID: {txn.get('id')}")
            print(f"   Date: {txn.get('transaction_date')}")
            print(f"   Type: {txn.get('transaction_type')}")
            print(f"   Amount: {txn.get('amount')}")
            print(f"   Amount Type: {type(txn.get('amount'))}")

            # Check if it's numeric or string
            amount_value = txn.get('amount')
            if isinstance(amount_value, str):
                print(f"   ⚠️  PROBLEM: Amount is a STRING: '{amount_value}'")
                print(f"   parseFloat('{amount_value}') would fail!")
            elif isinstance(amount_value, (int, float)):
                print(f"   ✅ GOOD: Amount is numeric: {amount_value}")
            else:
                print(f"   ❓ Unknown type: {type(amount_value)}")

        # Test all transactions
        print("\n--- Testing All Transactions ---")
        string_amounts = []
        numeric_amounts = []

        for txn in transactions:
            amount = txn.get('amount')
            if isinstance(amount, str):
                string_amounts.append((txn.get('id'), amount))
            elif isinstance(amount, (int, float)):
                numeric_amounts.append((txn.get('id'), amount))

        print(f"\nString amounts: {len(string_amounts)}")
        print(f"Numeric amounts: {len(numeric_amounts)}")

        if string_amounts:
            print("\n❌ PROBLEM: API is returning formatted strings")
            print("   Frontend parseFloat() will fail and show NaN")
            print(f"   Example: parseFloat('{string_amounts[0][1]}') = NaN")
        else:
            print("\n✅ All amounts are numeric - frontend can parse them")

else:
    print(f"Error: {response.data}")

print("\n=== TEST COMPLETE ===\n")
