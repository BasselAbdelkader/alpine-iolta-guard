import os, sys, django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.clients.models import Client, Case
from apps.bank_accounts.models import BankTransaction
from decimal import Decimal
from datetime import date

print("=" * 80)
print("MFLP-29 TEST: Automatic Deposit Payee Field")
print("=" * 80)
print()

# Get a client (Sarah Johnson)
client = Client.objects.filter(first_name='Sarah', last_name='Johnson').first()

if not client:
    print("❌ Sarah Johnson not found")
    sys.exit(1)

print(f"Client: {client.full_name} (ID: {client.id})")
print()

# Create a test case with amount
print("Creating new case with $5000 amount...")
test_case = Case.objects.create(
    client=client,
    case_title="Test Case for MFLP-29",
    case_description="Testing automatic deposit payee field",
    case_amount=Decimal('5000.00'),
    case_status='Open',
    opened_date=date.today()
)

print(f"✅ Case created: {test_case.case_number} - {test_case.case_title}")
print(f"   Case Amount: ${test_case.case_amount}")
print()

# Find the automatic deposit transaction
print("Searching for automatic deposit transaction...")
deposit = BankTransaction.objects.filter(
    case=test_case,
    transaction_type='DEPOSIT',
    item_type='CLIENT_DEPOSIT'
).first()

if deposit:
    print("✅ Automatic deposit found:")
    print(f"   Transaction Number: {deposit.transaction_number}")
    print(f"   Amount: ${deposit.amount}")
    print(f"   Description: {deposit.description}")
    print(f"   Payee: '{deposit.payee}'")
    print(f"   Client: {deposit.client.full_name if deposit.client else 'None'}")
    print()

    if deposit.payee:
        print(f"✅ PASS: Payee is set to '{deposit.payee}'")
    else:
        print(f"❌ FAIL: Payee is NULL/empty")

    if deposit.payee == client.full_name:
        print(f"✅ PASS: Payee matches client name ({client.full_name})")
    else:
        print(f"❌ FAIL: Payee '{deposit.payee}' does not match client name '{client.full_name}'")
else:
    print("❌ No automatic deposit transaction found")

print()

# Clean up - delete test case
print("Cleaning up test case...")
test_case.delete()
print("✅ Test case deleted")

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
