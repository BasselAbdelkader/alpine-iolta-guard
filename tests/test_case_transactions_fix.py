import os
import sys
import django

sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from apps.clients.views import case_transactions
import json

print('=' * 80)
print('TESTING CASE TRANSACTIONS VIEW AFTER FIX')
print('=' * 80)
print()

# Create a request
factory = RequestFactory()
request = factory.get('/clients/case-transactions/4/')
request.user = User.objects.first()

# Call the view
response = case_transactions(request, case_id=4)

# Parse the JSON response
data = json.loads(response.content)

print(f"Case Balance: {data.get('case_balance')}")
print(f"Transaction Count: {data.get('count')}")
print()

# Show first 5 transactions
print('First 5 Transactions:')
print('-' * 80)
for i, txn in enumerate(data.get('transactions', [])[:5], 1):
    print(f"Transaction {i}:")
    print(f"  Date: {txn.get('date')}")
    print(f"  Type: {txn.get('type')}")
    print(f"  Payee: {txn.get('payee')}")
    print(f"  Amount: {txn.get('amount_display')}")
    print(f"  Balance: {txn.get('balance_display')}")
    print(f"  Status: {txn.get('status')}")
    print()

print('=' * 80)
print('VERIFICATION')
print('=' * 80)
print()

# Check if all amounts have $ sign
all_have_dollar = True
for txn in data.get('transactions', []):
    amount = txn.get('amount_display', '')
    balance = txn.get('balance_display', '')

    if '$' not in amount and txn.get('status') != 'Voided':
        print(f"❌ Missing $ in amount: {amount}")
        all_have_dollar = False

    if '$' not in balance:
        print(f"❌ Missing $ in balance: {balance}")
        all_have_dollar = False

if all_have_dollar:
    print('✅ All amounts and balances have $ sign!')
else:
    print('❌ Some amounts/balances missing $ sign')

print()
print('=' * 80)
