#!/usr/bin/env python
"""
Test clients API endpoint to check what's being returned
"""
import os, sys, django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from apps.clients.api.views import ClientViewSet

print("\n=== TESTING CLIENTS API ===")
print("Endpoint: GET /api/v1/clients/?page_size=1000\n")

# Create a request
factory = APIRequestFactory()
request = factory.get('/api/v1/clients/?page_size=1000')

# Authenticate
User = get_user_model()
user = User.objects.first()
if not user:
    print("❌ No users found in database")
    sys.exit(1)

force_authenticate(request, user=user)

# Get the viewset
viewset = ClientViewSet.as_view({'get': 'list'})

# Call the view
try:
    response = viewset(request)

    print(f"Status Code: {response.status_code}\n")

    if response.status_code == 200:
        data = response.data

        # Check if it's paginated
        if isinstance(data, dict) and 'results' in data:
            clients = data['results']
            print(f"✓ Paginated response")
            print(f"  Total clients: {len(clients)}")
            print(f"  Count: {data.get('count', 'N/A')}")
        elif isinstance(data, list):
            clients = data
            print(f"✓ Array response")
            print(f"  Total clients: {len(clients)}")
        else:
            print(f"❌ Unexpected response format: {type(data)}")
            clients = []

        if not clients:
            print("\n❌ No clients returned!")
            print("   Frontend dropdown will be empty")
        else:
            print(f"\n✅ API returns {len(clients)} clients")

            # Show first client
            first_client = clients[0]
            print("\n--- First Client ---")
            print(f"  ID: {first_client.get('id')}")
            print(f"  Full Name: {first_client.get('full_name')}")
            print(f"  formatted_balance: {first_client.get('formatted_balance')}")
            print(f"  current_balance: {first_client.get('current_balance')}")

            # Check if formatted_balance has $ sign
            fb = first_client.get('formatted_balance', '')
            if fb:
                if fb.startswith('$'):
                    print(f"\n  ✓ formatted_balance has $ sign: '{fb}'")
                else:
                    print(f"\n  ⚠️ formatted_balance missing $ sign: '{fb}'")
            else:
                print(f"\n  ❌ formatted_balance is empty!")

            # Test dropdown text generation
            dropdown_text = f"{first_client.get('full_name')} (Balance: ${first_client.get('formatted_balance')})"
            print(f"\n--- Dropdown Display ---")
            print(f"  Text: {dropdown_text}")

            if '$$' in dropdown_text:
                print(f"  ⚠️ Double $$ detected - formatted_balance already has $ sign")
    else:
        print(f"❌ Error: {response.data}")

except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback
    traceback.print_exc()

print("\n=== TEST COMPLETE ===\n")
