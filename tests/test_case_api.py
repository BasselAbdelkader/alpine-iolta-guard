#!/usr/bin/env python
import os, sys, django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from apps.clients.api.views import CaseViewSet

print("\n=== TESTING DRF API ENDPOINT ===")
print("Endpoint: GET /api/v1/cases/4/transactions/\n")

# Create a request
factory = APIRequestFactory()
request = factory.get('/api/v1/cases/4/transactions/')

# Authenticate
User = get_user_model()
user = User.objects.first()
force_authenticate(request, user=user)

# Get the viewset
viewset = CaseViewSet.as_view({'get': 'transactions'})

# Call the view
response = viewset(request, pk=4)

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    data = response.data
    print(f"Case Balance: {data.get('current_balance', 'N/A')}")
    print(f"Transaction Count: {len(data.get('transactions', []))}")

    if 'transactions' in data and len(data['transactions']) > 0:
        print("\n--- First 3 Transactions ---")
        for i, txn in enumerate(data['transactions'][:3], 1):
            print(f"\n{i}. Date: {txn.get('date')}")
            print(f"   Type: {txn.get('type')}")
            print(f"   Amount: {txn.get('amount')}")
            print(f"   Balance: {txn.get('balance', 'N/A')}")
            print(f"   Payee: {txn.get('payee', 'N/A')}")

        print("\n--- All Transaction Amounts ---")
        for i, txn in enumerate(data['transactions'], 1):
            print(f"{i}. {txn.get('date')} | Amount: {txn.get('amount')} | Balance: {txn.get('balance', 'N/A')}")
    else:
        print("\nNo transactions found!")
else:
    print(f"Error: {response.data}")

print("\n=== TEST COMPLETE ===\n")
