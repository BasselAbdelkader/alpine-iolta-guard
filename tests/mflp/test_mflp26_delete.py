import os, sys, django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.clients.models import Client
from apps.clients.api.views import ClientViewSet
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User

print("=" * 80)
print("MFLP-26 TEST: Client Deletion with Transactions")
print("=" * 80)
print()

# Get Sarah Johnson (has transactions)
client = Client.objects.filter(first_name='Sarah', last_name='Johnson').first()

if not client:
    print("❌ Sarah Johnson not found")
    sys.exit(1)

print(f"Client: {client.full_name} (ID: {client.id})")
print(f"Is Active: {client.is_active}")
print()

# Check transactions and cases
from apps.bank_accounts.models import BankTransaction
from django.db import models

has_transactions = BankTransaction.objects.filter(
    models.Q(client=client) | models.Q(case__client=client)
).exists()

has_cases = client.cases.exists()

txn_count = BankTransaction.objects.filter(
    models.Q(client=client) | models.Q(case__client=client)
).count()

case_count = client.cases.count()

print(f"Has Transactions: {has_transactions} ({txn_count} transactions)")
print(f"Has Cases: {has_cases} ({case_count} cases)")
print()

# Try to delete via API
print("=" * 80)
print("TEST: Attempting to delete via API ViewSet")
print("=" * 80)

factory = APIRequestFactory()
request = factory.delete(f"/api/v1/clients/{client.id}/")

# Create a user for the request
user = User.objects.filter(is_superuser=True).first()
if not user:
    user = User.objects.create_superuser('testadmin', 'test@test.com', 'password')
request.user = user

viewset = ClientViewSet()
viewset.request = request
viewset.format_kwarg = None
viewset.kwargs = {'pk': client.id}

try:
    response = viewset.destroy(request, pk=client.id)
    print(f"✅ Response Status: {response.status_code}")
    print(f"Response Data: {response.data}")

    # Check client status
    client.refresh_from_db()
    print(f"\nClient is_active after delete: {client.is_active}")

    if not client.is_active:
        print("✅ Client successfully set to inactive")

        # Restore for future tests
        client.is_active = True
        client.save()
        print("✅ Client restored to active for future tests")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
