import os
import sys
import django

sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.clients.models import Case, Client
from apps.clients.api.serializers import CaseSerializer, ClientSerializer
import json

print('=' * 80)
print('CHECKING CASE AND CLIENT API RESPONSES')
print('=' * 80)
print()

# Test Case ID 4
print('Case ID 4:')
print('-' * 80)
try:
    case = Case.objects.get(id=4)
    print(f"Case found: {case.case_title}")
    print(f"Raw case_amount: {case.case_amount}")
    print(f"Calculated balance: {case.get_current_balance()}")
    print()

    serializer = CaseSerializer(case)
    data = serializer.data

    print(f"API Response - Case Title: {data.get('case_title', 'N/A')}")
    print(f"API Response - Current Balance: {data.get('current_balance', 'MISSING')}")
    print(f"API Response - Formatted Balance: {data.get('formatted_balance', 'MISSING')}")
    print(f"API Response - Case Amount: {data.get('case_amount', 'MISSING')}")
    print()
    print("All fields in API response:")
    for key, value in sorted(data.items()):
        print(f"  {key}: {value}")
except Case.DoesNotExist:
    print("Case ID 4 not found")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print()
print('=' * 80)

# Test Client ID 1
print('Client ID 1:')
print('-' * 80)
try:
    client = Client.objects.get(id=1)
    print(f"Client found: {client.full_name}")
    print(f"Calculated balance: {client.get_current_balance()}")
    print()

    serializer = ClientSerializer(client)
    data = serializer.data

    print(f"API Response - Client Name: {data.get('first_name', '')} {data.get('last_name', '')}")
    print(f"API Response - Current Balance: {data.get('current_balance', 'MISSING')}")
    print(f"API Response - Formatted Balance: {data.get('formatted_balance', 'MISSING')}")
    print()
    print("All fields in API response:")
    for key, value in sorted(data.items()):
        print(f"  {key}: {value}")
except Client.DoesNotExist:
    print("Client ID 1 not found")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print()
print('=' * 80)
print('CHECKING SERIALIZER DEFINITIONS')
print('=' * 80)

# Check what fields are defined in serializers
from apps.clients.api.serializers import CaseSerializer, ClientSerializer

print()
print("CaseSerializer Meta fields:")
print(CaseSerializer.Meta.fields)

print()
print("ClientSerializer Meta fields:")
print(ClientSerializer.Meta.fields)
