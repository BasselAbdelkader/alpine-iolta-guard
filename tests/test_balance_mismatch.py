#!/usr/bin/env python
"""
Test script to check for balance mismatches between client balance and sum of case balances.
MFLP-42: Client Total Balance Does Not Match Sum of Associated Case Balances

This script investigates whether there are discrepancies between:
1. Client.get_current_balance() - Sum of all client transactions
2. Sum of Case.get_current_balance() for all client's cases
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.clients.models import Client
from apps.bank_accounts.models import BankTransaction
from decimal import Decimal

print("=" * 80)
print("MFLP-42: Balance Mismatch Investigation")
print("=" * 80)
print()

# Check all clients for balance mismatches
clients_with_balance = Client.objects.filter(is_active=True)
mismatches_found = 0
total_clients_checked = 0

for client in clients_with_balance:
    client_balance = client.get_current_balance()

    # Calculate sum of case balances
    case_balances_sum = Decimal('0.00')
    for case in client.cases.all():
        case_balances_sum += case.get_current_balance()

    total_clients_checked += 1

    # Check for mismatch
    if abs(client_balance - case_balances_sum) > Decimal('0.01'):  # Allow for tiny rounding errors
        mismatches_found += 1
        print(f"\n{'='*80}")
        print(f"❌ MISMATCH FOUND - Client: {client.full_name} (ID: {client.id})")
        print(f"{'='*80}")
        print(f"  Client Balance:     ${client_balance:,.2f}")
        print(f"  Sum of Case Balances: ${case_balances_sum:,.2f}")
        print(f"  Difference:         ${abs(client_balance - case_balances_sum):,.2f}")
        print()

        # Show individual case balances
        print(f"  Cases for {client.full_name}:")
        for case in client.cases.all():
            case_balance = case.get_current_balance()
            print(f"    - {case.case_number} ({case.case_title}): ${case_balance:,.2f}")

        print()

        # Check for transactions without case
        orphan_txns = BankTransaction.objects.filter(
            client=client,
            case__isnull=True
        ).exclude(status='voided')

        if orphan_txns.exists():
            print(f"  ⚠️ Found {orphan_txns.count()} transactions with NO CASE assigned:")
            for txn in orphan_txns:
                print(f"    - {txn.transaction_number}: {txn.transaction_type} ${txn.amount:,.2f}")
                print(f"      Description: {txn.description}")
                print(f"      Date: {txn.transaction_date}")
        else:
            print(f"  ✓ No orphan transactions (all transactions have cases)")

        # Check transactions by case
        print()
        print(f"  All transactions for client {client.full_name}:")
        all_txns = BankTransaction.objects.filter(client=client).exclude(status='voided').order_by('transaction_date', 'id')
        for txn in all_txns:
            case_info = f"Case {txn.case.case_number}" if txn.case else "NO CASE"
            sign = "+" if txn.transaction_type == 'DEPOSIT' else "-"
            print(f"    {sign} ${txn.amount:,.2f} - {txn.transaction_type} ({case_info})")

    elif client_balance != Decimal('0.00') or case_balances_sum != Decimal('0.00'):
        # Client has balances and they match
        print(f"✓ Client: {client.full_name} - Balance: ${client_balance:,.2f} (matches cases)")

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total Clients Checked: {total_clients_checked}")
print(f"Mismatches Found: {mismatches_found}")

if mismatches_found == 0:
    print()
    print("✓ ✓ ✓ NO BALANCE MISMATCHES FOUND ✓ ✓ ✓")
    print()
    print("All client balances match the sum of their case balances.")
    print("This means MFLP-42 does not occur in the current database.")
    print()
    print("POSSIBLE REASONS:")
    print("1. The bug was reported on a different database state")
    print("2. The bug has already been fixed")
    print("3. The bug occurs only under specific conditions not present in current data")
else:
    print()
    print(f"❌ ❌ ❌ {mismatches_found} MISMATCH(ES) FOUND ❌ ❌ ❌")
    print()
    print("Client balances DO NOT match the sum of case balances.")
    print("This confirms MFLP-42 bug exists.")

print("=" * 80)
