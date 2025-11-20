#!/usr/bin/env python
import os, sys, django, json
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.clients.models import Case
from apps.bank_accounts.models import BankTransaction
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from apps.clients.views import case_transactions

print("\n=== TESTING CASE LEDGER API ===\n")

# Check database data first
case = Case.objects.get(id=4)
print(f"Case ID: {case.id}")
print(f"Case Title: {case.case_title}")
print(f"Current Balance: ${case.get_current_balance():,.2f}")

txns = BankTransaction.objects.filter(case=case).order_by('transaction_date', 'id')
print(f"Total Transactions: {txns.count()}")

if txns.count() > 0:
    print("\n--- First Transaction Raw Data ---")
    first = txns.first()
    print(f"Date: {first.transaction_date}")
    print(f"Type: {first.transaction_type}")
    print(f"Amount: {first.amount}")
    print(f"Status: {first.status}")

# Now test the API endpoint
print("\n=== TESTING API ENDPOINT ===\n")
factory = RequestFactory()
request = factory.get('/clients/case-transactions/4/')
User = get_user_model()
user = User.objects.first()
request.user = user

response = case_transactions(request, case_id=4)
data = json.loads(response.content)

print(f"API Status Code: {response.status_code}")
print(f"Case Balance from API: {data.get('case_balance', 'N/A')}")
print(f"Transaction Count from API: {data.get('count', 0)}")

if 'transactions' in data and len(data['transactions']) > 0:
    print("\n--- First Transaction from API ---")
    first_txn = data['transactions'][0]
    print(f"Date: {first_txn.get('date')}")
    print(f"Type: {first_txn.get('type')}")
    print(f"Amount Display: {first_txn.get('amount_display')}")
    print(f"Balance Display: {first_txn.get('balance_display')}")
    print(f"Payee: {first_txn.get('payee')}")
    print(f"Status: {first_txn.get('status')}")

    print("\n--- All Transactions ---")
    for i, txn in enumerate(data['transactions'], 1):
        print(f"{i}. {txn.get('date')} | {txn.get('type')} | Amount: {txn.get('amount_display')} | Balance: {txn.get('balance_display')}")
else:
    print("No transactions returned from API!")

print("\n=== TEST COMPLETE ===\n")
