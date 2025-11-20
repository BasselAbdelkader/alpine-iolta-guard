#!/usr/bin/env python
"""
Create sample test data for Outstanding Checks Over 90 Days dashboard feature
Creates multiple checks with varying amounts and ages to test:
1. Sorting by amount (highest first)
2. Limit to top 25
3. Display of Client, Description columns
4. Action buttons (Edit, Reissue, Void)
"""
import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.bank_accounts.models import BankAccount, BankTransaction
from apps.clients.models import Client, Case

def create_outstanding_checks_test_data():
    """Create test data for outstanding checks over 90 days"""

    print("\n" + "="*80)
    print("CREATING OUTSTANDING CHECKS TEST DATA")
    print("="*80)

    # Get or create bank account
    bank_account = BankAccount.objects.first()
    if not bank_account:
        print("❌ No bank account found!")
        return

    print(f"\n✅ Using Bank Account: {bank_account.account_name}")

    # Get any available client
    client = Client.objects.first()
    if not client:
        print("❌ No clients found in database!")
        return

    print(f"✅ Using Client: {client.full_name} (ID: {client.id})")

    # Get test case
    case = Case.objects.filter(client=client).first()
    if not case:
        print("❌ No case found for test client!")
        return

    print(f"✅ Using Case: {case.case_number}")

    # Define test checks with varying amounts and ages
    test_checks = [
        {
            'amount': Decimal('5000.00'),
            'days_ago': 120,
            'payee': 'Medical Records Plus',
            'description': 'Medical records request - Case settlement',
            'check_number': '1001'
        },
        {
            'amount': Decimal('3500.00'),
            'days_ago': 95,
            'payee': 'Expert Witness Services Inc',
            'description': 'Expert testimony fees',
            'check_number': '1002'
        },
        {
            'amount': Decimal('8200.00'),
            'days_ago': 150,
            'payee': 'Law Office of Johnson & Associates',
            'description': 'Co-counsel fees for trial',
            'check_number': '1003'
        },
        {
            'amount': Decimal('1200.00'),
            'days_ago': 100,
            'payee': 'ABC Court Reporting',
            'description': 'Deposition transcripts',
            'check_number': '1004'
        },
        {
            'amount': Decimal('6500.00'),
            'days_ago': 180,
            'payee': 'Metropolitan Hospital',
            'description': 'Hospital lien payment',
            'check_number': '1005'
        },
        {
            'amount': Decimal('2800.00'),
            'days_ago': 110,
            'payee': 'Private Investigator LLC',
            'description': 'Investigation services',
            'check_number': '1006'
        },
        {
            'amount': Decimal('4100.00'),
            'days_ago': 130,
            'payee': 'Medical Imaging Center',
            'description': 'MRI and X-ray records',
            'check_number': '1007'
        },
    ]

    print(f"\n📝 Creating {len(test_checks)} outstanding checks...")
    print("-" * 80)

    created_checks = []

    for check_data in test_checks:
        # Calculate transaction date
        transaction_date = date.today() - timedelta(days=check_data['days_ago'])

        # Check if this check already exists
        existing = BankTransaction.objects.filter(
            check_number=check_data['check_number'],
            bank_account=bank_account
        ).first()

        if existing:
            print(f"⏭️  Check #{check_data['check_number']} already exists - skipping")
            created_checks.append(existing)
            continue

        # Create the check transaction
        txn = BankTransaction(
            bank_account=bank_account,
            transaction_type='WITHDRAWAL',
            amount=check_data['amount'],
            transaction_date=transaction_date,
            client=client,
            case=case,
            payee=check_data['payee'],
            description=check_data['description'],
            check_number=check_data['check_number'],
            status='pending',  # Not cleared - this makes it "outstanding"
            data_source='webapp'
        )

        # Save with audit info
        txn.save(
            audit_user='test_script',
            audit_reason='Creating test data for outstanding checks over 90 days',
            audit_ip='127.0.0.1'
        )

        created_checks.append(txn)

        print(f"✅ Check #{txn.check_number}: ${txn.amount} to {txn.payee} ({check_data['days_ago']} days ago)")

    print("-" * 80)
    print(f"\n✅ Created/Found {len(created_checks)} outstanding checks")

    # Verify they appear in outstanding checks query
    print("\n" + "="*80)
    print("VERIFICATION: CHECKS OVER 90 DAYS")
    print("="*80)

    today = date.today()
    ninety_days_ago = today - timedelta(days=90)

    outstanding = BankTransaction.objects.filter(
        transaction_type='WITHDRAWAL',
        check_number__isnull=False,
        status='pending',
        transaction_date__lte=ninety_days_ago
    ).exclude(
        check_number=''
    ).order_by('-amount')[:25]  # Top 25 by amount

    print(f"\n📊 Found {outstanding.count()} checks over 90 days old")
    print(f"📋 Displaying top 25 sorted by amount (highest first):\n")
    print(f"{'#':<6} {'Amount':>12} {'Days':<6} {'Payee':<35} {'Client':<20}")
    print("-" * 80)

    for check in outstanding:
        days_outstanding = (today - check.transaction_date).days
        client_name = check.client.full_name if check.client else 'N/A'
        print(f"{check.check_number:<6} ${check.amount:>10} {days_outstanding:<6} {check.payee[:35]:<35} {client_name[:20]:<20}")

    print("\n" + "="*80)
    print("TEST DATA CREATION COMPLETE")
    print("="*80)
    print("\n✅ Outstanding checks test data created successfully!")
    print("📊 Navigate to dashboard to see 'Open Checks Over 90 Days' section")
    print("🔍 Checks should be sorted by amount (highest first)")
    print("🎯 Test the Edit, Reissue, and Void buttons")
    print("\n")

if __name__ == '__main__':
    create_outstanding_checks_test_data()
