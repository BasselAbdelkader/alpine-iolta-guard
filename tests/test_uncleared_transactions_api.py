#!/usr/bin/env python
"""
Test uncleared transactions API to check available fields
"""
import os, sys, django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.dashboard.api.views import DashboardViewSet
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model

print("\n=== TESTING UNCLEARED TRANSACTIONS API ===")
print("Endpoint: GET /api/v1/dashboard/uncleared-transactions/\n")

# Create a request
factory = APIRequestFactory()
request = factory.get('/api/v1/dashboard/uncleared-transactions/')

# Authenticate
User = get_user_model()
user = User.objects.first()
if not user:
    print("❌ No users found in database")
    sys.exit(1)

force_authenticate(request, user=user)

# Get the viewset
viewset = DashboardViewSet.as_view({'get': 'uncleared_transactions'})

# Call the view
try:
    response = viewset(request)

    print(f"Status Code: {response.status_code}\n")

    if response.status_code == 200:
        transactions = response.data.get('transactions', [])

        if not transactions:
            print("No uncleared transactions found")
        else:
            print(f"Total Uncleared Transactions: {len(transactions)}\n")

            # Show first transaction fields
            first_txn = transactions[0]
            print("--- First Transaction Fields ---")
            for key, value in first_txn.items():
                print(f"  {key}: {value}")

            # Check specifically for case fields
            print("\n--- Case-Related Fields ---")
            case_fields = [k for k in first_txn.keys() if 'case' in k.lower()]
            if case_fields:
                for field in case_fields:
                    print(f"  ✓ {field}: {first_txn.get(field)}")
            else:
                print("  ❌ No case-related fields found")

            # Check if case_title exists
            print("\n--- Checking for case_title ---")
            if 'case_title' in first_txn:
                print(f"  ✅ case_title exists: '{first_txn['case_title']}'")
            elif 'case' in first_txn:
                print(f"  ⚠️  Only 'case' field exists: '{first_txn['case']}'")
                print(f"  Need to add case_title to API response")
            else:
                print(f"  ❌ No case field found")
    else:
        print(f"Error: {response.data}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== TEST COMPLETE ===\n")
