#!/usr/bin/env python3
"""
IOLTA Guard - Database Reset & Comprehensive Test Data Setup
=============================================================

This script:
1. Drops all existing data from localhost database
2. Resets primary sequences to start at 1001
3. Creates IOLTA-compliant bank account
4. Creates initial $100 unassigned transaction (differential)
5. Generates extensive test data with VOIDED/CLEARED/PENDING transactions
6. Ensures complete audit trail for all changes

Usage:
    python reset_database_with_test_data.py
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Setup Django environment
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trust_account_project.settings')
django.setup()

from django.db import connection, transaction
from django.contrib.contenttypes.models import ContentType
from apps.clients.models import Client, Case
from apps.bank_accounts.models import BankAccount, BankTransaction
from apps.vendors.models import Vendor
from auditlog.models import LogEntry

# ============================================================================
# Configuration
# ============================================================================

SEQUENCE_START = 1001
INITIAL_DIFFERENTIAL = Decimal('100.00')

# Realistic test data
BANK_ACCOUNT_DATA = {
    'account_number': '1234567890',
    'bank_name': 'First National Bank',
    'routing_number': '021000021',
    'account_type': 'IOLTA Trust Account',
    'is_active': True
}

CLIENT_NAMES = [
    ('John', 'Anderson'), ('Sarah', 'Mitchell'), ('Michael', 'Thompson'),
    ('Emily', 'Rodriguez'), ('David', 'Chen'), ('Jessica', 'Williams'),
    ('Robert', 'Taylor'), ('Maria', 'Garcia'), ('James', 'Brown'),
    ('Jennifer', 'Davis'), ('William', 'Martinez'), ('Linda', 'Miller'),
    ('Richard', 'Wilson'), ('Patricia', 'Moore'), ('Charles', 'Jackson'),
    ('Barbara', 'White'), ('Joseph', 'Harris'), ('Susan', 'Martin'),
    ('Thomas', 'Lee'), ('Karen', 'Walker')
]

CASE_TYPES = [
    'Personal Injury', 'Real Estate Transaction', 'Estate Planning',
    'Family Law Settlement', 'Business Litigation', 'Employment Dispute',
    'Insurance Claim', 'Contract Dispute', 'Probate Matter'
]

VENDOR_NAMES = [
    'Medical Records Inc.', 'Court Reporter Services LLC',
    'Expert Witness Consultants', 'Process Server Associates',
    'Legal Research Services', 'Translation Services Inc.',
    'Private Investigation Firm', 'Document Review Company',
    'Mediation Services Group', 'Appraisal Services LLC',
    'Title Company', 'Notary Services Inc.'
]

TRANSACTION_DESCRIPTIONS = [
    'Settlement proceeds received',
    'Retainer payment',
    'Court filing fees',
    'Expert witness fees',
    'Medical records request',
    'Court reporter fees',
    'Settlement distribution',
    'Mediation fees',
    'Client reimbursement',
    'Case costs payment'
]

# ============================================================================
# Helper Functions
# ============================================================================

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_success(text):
    """Print success message"""
    print(f"✓ {text}")

def print_info(text):
    """Print info message"""
    print(f"  → {text}")

def reset_sequences():
    """Reset all primary key sequences to start at 1001"""
    print_header("Resetting Database Sequences")

    with connection.cursor() as cursor:
        # Get all sequences
        cursor.execute("""
            SELECT sequence_name
            FROM information_schema.sequences
            WHERE sequence_schema = 'public'
            AND sequence_name LIKE '%_id_seq'
        """)

        sequences = cursor.fetchall()

        for seq in sequences:
            seq_name = seq[0]
            cursor.execute(f"ALTER SEQUENCE {seq_name} RESTART WITH {SEQUENCE_START}")
            print_success(f"Reset {seq_name} to {SEQUENCE_START}")

def clear_all_data():
    """Drop all existing data from database"""
    print_header("Clearing All Existing Data")

    with connection.cursor() as cursor:
        # Disable triggers
        cursor.execute("SET session_replication_role = 'replica';")

        # Clear audit logs first
        cursor.execute("TRUNCATE TABLE auditlog_logentry CASCADE;")
        print_success("Cleared audit logs")

        # Clear transactions
        cursor.execute("TRUNCATE TABLE bank_accounts_transaction CASCADE;")
        print_success("Cleared transactions")

        # Clear cases
        cursor.execute("TRUNCATE TABLE clients_case CASCADE;")
        print_success("Cleared cases")

        # Clear clients
        cursor.execute("TRUNCATE TABLE clients_client CASCADE;")
        print_success("Cleared clients")

        # Clear vendors
        cursor.execute("TRUNCATE TABLE vendors_vendor CASCADE;")
        print_success("Cleared vendors")

        # Clear bank accounts
        cursor.execute("TRUNCATE TABLE bank_accounts_bankaccount CASCADE;")
        print_success("Cleared bank accounts")

        # Re-enable triggers
        cursor.execute("SET session_replication_role = 'origin';")

def create_bank_account():
    """Create IOLTA-compliant bank account"""
    print_header("Creating IOLTA Bank Account")

    bank_account = BankAccount.objects.create(**BANK_ACCOUNT_DATA)

    print_success(f"Created bank account: {bank_account.bank_name}")
    print_info(f"Account Number: {bank_account.account_number}")
    print_info(f"Account Type: {bank_account.account_type}")
    print_info(f"Initial Balance: ${bank_account.balance}")

    return bank_account

def create_clients_and_cases():
    """Create multiple clients with cases"""
    print_header("Creating Clients and Cases")

    clients_with_cases = []

    for i, (first_name, last_name) in enumerate(CLIENT_NAMES[:15], 1):
        # Create client
        client = Client.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=f"{first_name.lower()}.{last_name.lower()}@example.com",
            phone=f"(555) {random.randint(100, 999)}-{random.randint(1000, 9999)}",
            address=f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Elm', 'Maple'])} St",
            city=random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']),
            state=random.choice(['NY', 'CA', 'IL', 'TX', 'AZ']),
            zip_code=f"{random.randint(10000, 99999)}",
            is_active=True
        )

        # Create 1-3 cases per client
        num_cases = random.randint(1, 3)
        cases = []

        for j in range(num_cases):
            case_type = random.choice(CASE_TYPES)
            case = Case.objects.create(
                client=client,
                case_title=f"{case_type} - {last_name}",
                case_description=f"{case_type} matter for {first_name} {last_name}",
                case_status=random.choice(['Open', 'Open', 'Open', 'Pending Settlement']),
                opened_date=datetime.now().date() - timedelta(days=random.randint(30, 365))
            )
            cases.append(case)

        clients_with_cases.append({'client': client, 'cases': cases})
        print_success(f"Created client: {client.full_name} with {len(cases)} case(s)")

    return clients_with_cases

def create_vendors():
    """Create vendor/payee records"""
    print_header("Creating Vendors")

    vendors = []

    for vendor_name in VENDOR_NAMES:
        vendor = Vendor.objects.create(
            vendor_name=vendor_name,
            contact_person=f"{random.choice(['John', 'Sarah', 'Michael', 'Emily'])} {random.choice(['Smith', 'Jones', 'Brown'])}",
            email=f"billing@{vendor_name.lower().replace(' ', '').replace('.', '')}",
            phone=f"(555) {random.randint(100, 999)}-{random.randint(1000, 9999)}",
            address=f"{random.randint(100, 9999)} Business Blvd",
            city=random.choice(['New York', 'Los Angeles', 'Chicago']),
            state=random.choice(['NY', 'CA', 'IL']),
            is_active=True
        )
        vendors.append(vendor)
        print_success(f"Created vendor: {vendor.vendor_name}")

    return vendors

def create_initial_unassigned_transaction(bank_account):
    """Create initial $100 unassigned transaction (creates differential)"""
    print_header("Creating Initial Unassigned Transaction")
    print_info("This creates the $100 differential between trust and bank register")

    txn = BankTransaction.objects.create(
        bank_account=bank_account,
        client=None,  # NO CLIENT - creates differential
        case=None,
        transaction_date=datetime.now().date() - timedelta(days=90),
        transaction_type='DEPOSIT',
        amount=INITIAL_DIFFERENTIAL,
        reference_number='INIT-1000',
        payee='Initial Bank Deposit',
        description='Initial IOLTA account funding - unassigned to client',
        status='CLEARED',
        cleared_date=datetime.now().date() - timedelta(days=89)
    )

    print_success(f"Created unassigned transaction: ${txn.amount}")
    print_info(f"Transaction ID: {txn.id}")
    print_info(f"Status: {txn.status}")
    print_info(f"This creates $100 differential (in bank but not in client trust)")

    return txn

def create_comprehensive_transactions(bank_account, clients_with_cases, vendors):
    """Create extensive test data with all transaction types and states"""
    print_header("Creating Comprehensive Transaction Test Data")

    transactions = []
    transaction_num = 1001

    # Track balances per case to ensure positivity
    case_balances = {}

    # Get date range for transactions
    start_date = datetime.now().date() - timedelta(days=180)

    print_info("Creating DEPOSITS...")

    # Create multiple deposits for each case (30-40 deposits)
    deposit_count = 0
    for client_data in clients_with_cases:
        for case in client_data['cases']:
            # Initialize case balance
            case_balances[case.id] = Decimal('0.00')

            # Create 2-4 deposits per case
            num_deposits = random.randint(2, 4)

            for i in range(num_deposits):
                amount = Decimal(str(random.randint(1000, 50000)))
                days_ago = random.randint(1, 180)

                txn = BankTransaction.objects.create(
                    bank_account=bank_account,
                    client=client_data['client'],
                    case=case,
                    transaction_date=start_date + timedelta(days=days_ago),
                    transaction_type='DEPOSIT',
                    amount=amount,
                    reference_number=f'DEP-{transaction_num}',
                    payee=f'{client_data["client"].full_name}',
                    description=random.choice(TRANSACTION_DESCRIPTIONS),
                    status=random.choice(['CLEARED', 'CLEARED', 'CLEARED', 'PENDING']),  # Mostly cleared
                    cleared_date=(start_date + timedelta(days=days_ago + 1)) if random.random() > 0.2 else None
                )

                # Update case balance
                case_balances[case.id] += amount

                transactions.append(txn)
                transaction_num += 1
                deposit_count += 1

    print_success(f"Created {deposit_count} deposit transactions")

    print_info("Creating WITHDRAWALS...")

    # Create withdrawals (ensuring positive balances)
    withdrawal_count = 0
    for client_data in clients_with_cases:
        for case in client_data['cases']:
            available_balance = case_balances[case.id]

            if available_balance > Decimal('500'):
                # Create 1-3 withdrawals per case
                num_withdrawals = random.randint(1, 3)

                for i in range(num_withdrawals):
                    # Ensure withdrawal doesn't exceed 80% of available balance
                    max_withdrawal = available_balance * Decimal('0.8')
                    amount = Decimal(str(random.randint(100, int(max_withdrawal))))

                    if amount > available_balance:
                        continue

                    days_ago = random.randint(1, 175)
                    vendor = random.choice(vendors)

                    # Mix of statuses
                    status = random.choice([
                        'CLEARED', 'CLEARED', 'CLEARED',  # 60% cleared
                        'PENDING', 'PENDING',  # 40% pending
                    ])

                    txn = BankTransaction.objects.create(
                        bank_account=bank_account,
                        client=client_data['client'],
                        case=case,
                        transaction_date=start_date + timedelta(days=days_ago),
                        transaction_type='WITHDRAWAL',
                        amount=amount,
                        reference_number=f'CHK-{transaction_num}',
                        payee=vendor.vendor_name,
                        description=random.choice(TRANSACTION_DESCRIPTIONS),
                        status=status,
                        cleared_date=(start_date + timedelta(days=days_ago + 2)) if status == 'CLEARED' else None,
                        to_print=random.choice([True, False])
                    )

                    # Update case balance
                    case_balances[case.id] -= amount
                    available_balance -= amount

                    transactions.append(txn)
                    transaction_num += 1
                    withdrawal_count += 1

    print_success(f"Created {withdrawal_count} withdrawal transactions")

    print_info("Creating VOIDED transactions...")

    # Create voided transactions (10-15 voided)
    voided_count = 0
    for i in range(15):
        # Pick random client and case
        client_data = random.choice(clients_with_cases)
        case = random.choice(client_data['cases'])

        # Create a transaction that will be voided
        amount = Decimal(str(random.randint(500, 5000)))
        days_ago = random.randint(5, 170)

        txn_type = random.choice(['DEPOSIT', 'WITHDRAWAL'])

        # For withdrawals, ensure we have balance
        if txn_type == 'WITHDRAWAL':
            if case_balances[case.id] < amount:
                txn_type = 'DEPOSIT'  # Switch to deposit if insufficient balance

        vendor = random.choice(vendors) if txn_type == 'WITHDRAWAL' else None

        txn = BankTransaction.objects.create(
            bank_account=bank_account,
            client=client_data['client'],
            case=case,
            transaction_date=start_date + timedelta(days=days_ago),
            transaction_type=txn_type,
            amount=amount,
            reference_number=f'VOID-{transaction_num}',
            payee=vendor.vendor_name if vendor else client_data['client'].full_name,
            description=f'VOIDED: {random.choice(TRANSACTION_DESCRIPTIONS)}',
            status='VOIDED',
            void_reason=random.choice([
                'Duplicate entry',
                'Incorrect amount',
                'Client request',
                'Administrative correction',
                'Bank error correction'
            ]),
            voided_date=start_date + timedelta(days=days_ago + random.randint(1, 5))
        )

        transactions.append(txn)
        transaction_num += 1
        voided_count += 1

    print_success(f"Created {voided_count} voided transactions")

    # Print transaction summary
    print_header("Transaction Summary")
    total_deposits = sum(1 for t in transactions if t.transaction_type == 'DEPOSIT' and t.status != 'VOIDED')
    total_withdrawals = sum(1 for t in transactions if t.transaction_type == 'WITHDRAWAL' and t.status != 'VOIDED')
    total_voided = sum(1 for t in transactions if t.status == 'VOIDED')
    total_cleared = sum(1 for t in transactions if t.status == 'CLEARED')
    total_pending = sum(1 for t in transactions if t.status == 'PENDING')

    print_info(f"Total Transactions: {len(transactions)}")
    print_info(f"  - Deposits: {total_deposits}")
    print_info(f"  - Withdrawals: {total_withdrawals}")
    print_info(f"  - Voided: {total_voided}")
    print_info(f"  - Cleared: {total_cleared}")
    print_info(f"  - Pending: {total_pending}")

    return transactions

def create_audit_trails(transactions):
    """Ensure complete audit trail for all transactions"""
    print_header("Creating Comprehensive Audit Trails")

    # Get ContentType for Transaction model
    transaction_ct = ContentType.objects.get_for_model(Transaction)

    audit_count = 0

    for txn in transactions:
        # Create initial creation audit
        LogEntry.objects.create(
            content_type=transaction_ct,
            object_pk=txn.pk,
            object_id=txn.id,
            object_repr=str(txn),
            action=0,  # CREATE
            changes='{"status": ["", "' + txn.status + '"]}',
            actor=None
        )
        audit_count += 1

        # If cleared, create clearance audit
        if txn.status == 'CLEARED' and txn.cleared_date:
            LogEntry.objects.create(
                content_type=transaction_ct,
                object_pk=txn.pk,
                object_id=txn.id,
                object_repr=str(txn),
                action=1,  # UPDATE
                changes='{"status": ["PENDING", "CLEARED"], "cleared_date": ["null", "' + str(txn.cleared_date) + '"]}',
                actor=None
            )
            audit_count += 1

        # If voided, create void audit
        if txn.status == 'VOIDED':
            original_status = random.choice(['PENDING', 'CLEARED'])
            LogEntry.objects.create(
                content_type=transaction_ct,
                object_pk=txn.pk,
                object_id=txn.id,
                object_repr=str(txn),
                action=1,  # UPDATE
                changes='{"status": ["' + original_status + '", "VOIDED"], "void_reason": ["", "' + (txn.void_reason or '') + '"]}',
                actor=None
            )
            audit_count += 1

    print_success(f"Created {audit_count} audit log entries")
    print_info("All transactions have complete audit trails")

def validate_data():
    """Validate all data meets requirements"""
    print_header("Data Validation")

    # Check bank account
    bank_accounts = BankAccount.objects.all()
    print_info(f"Bank Accounts: {bank_accounts.count()}")
    assert bank_accounts.count() == 1, "Should have exactly 1 bank account"
    print_success("✓ Exactly 1 bank account created")

    # Check clients
    clients = Client.objects.all()
    print_info(f"Clients: {clients.count()}")
    assert clients.count() >= 10, "Should have at least 10 clients"
    print_success(f"✓ {clients.count()} clients created")

    # Check cases
    cases = Case.objects.all()
    print_info(f"Cases: {cases.count()}")
    assert cases.count() >= 15, "Should have at least 15 cases"
    print_success(f"✓ {cases.count()} cases created")

    # Check vendors
    vendors = Vendor.objects.all()
    print_info(f"Vendors: {vendors.count()}")
    print_success(f"✓ {vendors.count()} vendors created")

    # Check transactions
    all_txns = BankTransaction.objects.all()
    voided_txns = BankTransaction.objects.filter(status='VOIDED')
    cleared_txns = BankTransaction.objects.filter(status='CLEARED')
    pending_txns = BankTransaction.objects.filter(status='PENDING')

    print_info(f"Total Transactions: {all_txns.count()}")
    print_info(f"  - VOIDED: {voided_txns.count()}")
    print_info(f"  - CLEARED: {cleared_txns.count()}")
    print_info(f"  - PENDING: {pending_txns.count()}")

    assert voided_txns.count() >= 10, "Should have at least 10 voided transactions"
    assert cleared_txns.count() >= 20, "Should have at least 20 cleared transactions"
    assert pending_txns.count() >= 5, "Should have at least 5 pending transactions"

    print_success(f"✓ {all_txns.count()} transactions created with all states")

    # Check for unassigned transaction
    unassigned = BankTransaction.objects.filter(client__isnull=True, case__isnull=True)
    print_info(f"Unassigned Transactions: {unassigned.count()}")
    assert unassigned.count() == 1, "Should have exactly 1 unassigned transaction"
    assert unassigned.first().amount == INITIAL_DIFFERENTIAL, f"Unassigned transaction should be ${INITIAL_DIFFERENTIAL}"
    print_success(f"✓ $100 differential transaction created (unassigned to client)")

    # Check audit trails
    audit_logs = LogEntry.objects.all()
    print_info(f"Audit Log Entries: {audit_logs.count()}")
    assert audit_logs.count() >= all_txns.count(), "Should have audit logs for all transactions"
    print_success(f"✓ Complete audit trails created ({audit_logs.count()} entries)")

    # Validate positive balances
    for case in cases:
        deposits = BankTransaction.objects.filter(
            case=case,
            transaction_type='DEPOSIT',
            status__in=['CLEARED', 'PENDING']
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')

        withdrawals = BankTransaction.objects.filter(
            case=case,
            transaction_type='WITHDRAWAL',
            status__in=['CLEARED', 'PENDING']
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')

        balance = deposits - withdrawals

        assert balance >= Decimal('0'), f"Case {case.id} has negative balance: ${balance}"

    print_success("✓ All case balances are positive")

    print_header("✅ ALL VALIDATIONS PASSED")

# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Main execution function"""
    print("\n" + "=" * 70)
    print("  IOLTA Guard - Database Reset & Test Data Setup")
    print("  Environment: localhost")
    print("=" * 70)

    try:
        with transaction.atomic():
            # Step 1: Clear all data
            clear_all_data()

            # Step 2: Reset sequences
            reset_sequences()

            # Step 3: Create bank account
            bank_account = create_bank_account()

            # Step 4: Create clients and cases
            clients_with_cases = create_clients_and_cases()

            # Step 5: Create vendors
            vendors = create_vendors()

            # Step 6: Create initial unassigned transaction ($100 differential)
            initial_txn = create_initial_unassigned_transaction(bank_account)

            # Step 7: Create comprehensive transactions
            transactions = create_comprehensive_transactions(
                bank_account,
                clients_with_cases,
                vendors
            )

            # Add initial transaction to list
            all_transactions = [initial_txn] + transactions

            # Step 8: Create audit trails
            create_audit_trails(all_transactions)

            # Step 9: Validate data
            validate_data()

            print_header("🎉 DATABASE RESET COMPLETE!")
            print_success("Database reset successfully with comprehensive test data")
            print_success("Ready for testing with realistic IOLTA-compliant data")
            print("\n")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    # Import models after Django setup
    from django.db import models
    main()
