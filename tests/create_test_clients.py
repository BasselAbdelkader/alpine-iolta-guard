#!/usr/bin/env python3
"""
Create 65 test clients with cases and balances to test MFLP-22 pagination fix
- 65 total clients (exceeds the 50 pagination limit)
- 1 case per client
- 40 clients with non-zero initial balance (deposits)
- 25 clients with zero balance
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta
import random

# Django setup
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trust_account_project.settings')
django.setup()

from apps.clients.models import Client, Case
from apps.bank_accounts.models import BankAccount, BankTransaction
from django.contrib.auth import get_user_model

User = get_user_model()

# Sample data
first_names = [
    'James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda',
    'William', 'Barbara', 'David', 'Elizabeth', 'Richard', 'Susan', 'Joseph', 'Jessica',
    'Thomas', 'Sarah', 'Charles', 'Karen', 'Christopher', 'Nancy', 'Daniel', 'Lisa',
    'Matthew', 'Betty', 'Anthony', 'Margaret', 'Mark', 'Sandra', 'Donald', 'Ashley',
    'Steven', 'Kimberly', 'Paul', 'Emily', 'Andrew', 'Donna', 'Joshua', 'Michelle',
    'Kenneth', 'Dorothy', 'Kevin', 'Carol', 'Brian', 'Amanda', 'George', 'Melissa',
    'Timothy', 'Deborah', 'Ronald', 'Stephanie', 'Edward', 'Rebecca', 'Jason', 'Sharon',
    'Jeffrey', 'Laura', 'Ryan', 'Cynthia', 'Jacob', 'Kathleen', 'Gary', 'Amy',
    'Nicholas', 'Shirley'
]

last_names = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
    'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas',
    'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White',
    'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young',
    'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
    'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell',
    'Carter', 'Roberts', 'Gomez', 'Phillips', 'Evans', 'Turner', 'Diaz', 'Parker',
    'Cruz', 'Edwards', 'Collins', 'Reyes', 'Stewart', 'Morris', 'Morales', 'Murphy',
    'Cook', 'Rogers'
]

case_types = [
    'Personal Injury - Auto Accident',
    'Medical Malpractice',
    'Workers Compensation',
    'Slip and Fall',
    'Product Liability',
    'Wrongful Death',
    'Dog Bite',
    'Construction Accident',
    'Nursing Home Negligence',
    'Premises Liability'
]

def create_test_data():
    """Create 65 test clients with cases and transactions"""

    print("="*80)
    print("CREATING TEST DATA FOR MFLP-22 PAGINATION TEST")
    print("="*80)

    # Get or create admin user
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.first()

    if not admin_user:
        print("❌ ERROR: No users found in database!")
        return

    # Get first bank account
    bank_account = BankAccount.objects.first()
    if not bank_account:
        print("❌ ERROR: No bank accounts found in database!")
        return

    print(f"\n✅ Using admin user: {admin_user.username}")
    print(f"✅ Using bank account: {bank_account.account_name}")

    # Get current client count
    existing_count = Client.objects.count()
    print(f"\n📊 Existing clients: {existing_count}")

    # Create 65 clients
    clients_to_create = 65
    print(f"\n🔨 Creating {clients_to_create} test clients...")

    created_clients = []
    start_number = existing_count + 1

    for i in range(clients_to_create):
        # Generate unique name
        first_name = first_names[i % len(first_names)]
        last_name = last_names[i % len(last_names)]
        client_number = f"TEST-{start_number + i:04d}"

        # Create client
        client = Client.objects.create(
            client_number=client_number,
            first_name=first_name,
            last_name=last_name,
            email=f"{first_name.lower()}.{last_name.lower()}{i}@testclient.com",
            phone=f"(555) {100 + i:03d}-{1000 + i:04d}",
            address=f"{100 + i} Test Street",
            city="Test City",
            state="NY",
            zip_code="10001",
            is_active=True,
            trust_account_status='ACTIVE_ZERO_BALANCE'
        )

        created_clients.append(client)

        # Create one case per client
        case_type = case_types[i % len(case_types)]
        case = Case.objects.create(
            case_number=f"CASE-TEST-{start_number + i:04d}",
            client=client,
            case_title=f"{case_type} - {last_name}",
            case_description=f"Test case for pagination testing",
            case_status='Open',
            opened_date=datetime.now().date() - timedelta(days=random.randint(30, 365)),
            is_active=True
        )

        if (i + 1) % 10 == 0:
            print(f"  Created {i + 1}/{clients_to_create} clients...")

    print(f"\n✅ Created {len(created_clients)} clients with cases")

    # Add initial balance to first 40 clients
    print(f"\n💰 Adding initial deposits to 40 clients...")

    transaction_date = datetime.now().date() - timedelta(days=30)

    for i, client in enumerate(created_clients[:40]):
        # Random deposit between $5,000 and $150,000
        amount = Decimal(random.randint(5000, 150000))

        # Get client's case
        case = Case.objects.filter(client=client).first()

        # Create deposit transaction
        txn = BankTransaction.objects.create(
            bank_account=bank_account,
            client=client,
            case=case,
            transaction_date=transaction_date,
            transaction_type='DEPOSIT',
            amount=amount,
            description=f'Initial deposit for {client.full_name}',
            reference_number=f'DEP-TEST-{i+1:04d}',
            transaction_number=f'DEPO-TEST-{i+1:04d}',
            status='pending',
            payee=f'{client.full_name}',
            item_type='deposit'
        )

        if (i + 1) % 10 == 0:
            print(f"  Created {i + 1}/40 deposits...")

    print(f"\n✅ Created 40 deposit transactions")

    # Summary
    print(f"\n{'='*80}")
    print(f"SUMMARY:")
    print(f"{'='*80}")
    print(f"Total clients in database: {Client.objects.count()}")
    print(f"Newly created clients: {len(created_clients)}")
    print(f"Clients with non-zero balance: 40")
    print(f"Clients with zero balance: 25")
    print(f"Total cases created: {len(created_clients)}")
    print(f"Total deposits created: 40")

    # Test query with filters
    print(f"\n📊 FILTER TESTING:")
    active_clients = Client.objects.filter(is_active=True).count()
    print(f"  Active clients: {active_clients}")

    # Count clients with non-zero balance
    non_zero = 0
    for client in Client.objects.all():
        if client.get_current_balance() != 0:
            non_zero += 1
    print(f"  Clients with non-zero balance: {non_zero}")

    print(f"\n✅ Test data creation complete!")
    print(f"{'='*80}")

if __name__ == '__main__':
    try:
        create_test_data()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
