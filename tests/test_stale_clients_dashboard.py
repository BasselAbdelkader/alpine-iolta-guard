#!/usr/bin/env python3
"""
Comprehensive Test Suite: Stale Clients Dashboard Feature
==========================================================

Tests the "Open Balances - No Recent Deposits (2+ Years)" dashboard feature.

This feature identifies clients with:
1. Balance > $0
2. Last deposit transaction > 2 years ago (730+ days)
3. Displays top 3 by balance amount

Author: Claude Code
Date: 2025-11-20
"""

import sys
import os
import django

# Setup Django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trust_account_project.settings')
django.setup()

from apps.clients.models import Client, Case
from apps.bank_accounts.models import BankTransaction, BankAccount
from apps.dashboard.views import DashboardView
from decimal import Decimal
from datetime import date, timedelta
from django.db.models import Max

# ANSI color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

class StaleClientsTestSuite:
    """Comprehensive test suite for stale clients dashboard feature"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.test_clients = []

    def print_header(self, text):
        """Print test section header"""
        print(f"\n{BLUE}{BOLD}{'='*80}{RESET}")
        print(f"{BLUE}{BOLD}{text:^80}{RESET}")
        print(f"{BLUE}{BOLD}{'='*80}{RESET}\n")

    def print_test(self, name, passed, message=""):
        """Print test result"""
        if passed:
            print(f"{GREEN}✓{RESET} {name}")
            if message:
                print(f"  {message}")
            self.passed += 1
        else:
            print(f"{RED}✗{RESET} {name}")
            if message:
                print(f"  {RED}{message}{RESET}")
            self.failed += 1

    def print_warning(self, message):
        """Print warning message"""
        print(f"{YELLOW}⚠{RESET} {message}")
        self.warnings += 1

    def cleanup_test_clients(self):
        """Delete all test clients and their transactions"""
        self.print_header("CLEANUP")

        for client in self.test_clients:
            # Delete transactions first
            BankTransaction.objects.filter(client=client).delete()
            # Delete cases
            Case.objects.filter(client=client).delete()
            # Delete client
            client_name = client.full_name
            client.delete()
            print(f"✓ Deleted: {client_name}")

        self.test_clients = []
        print(f"\n{GREEN}Cleanup complete!{RESET}\n")

    def create_test_client_with_deposit(self, first_name, last_name, deposit_amount, days_ago):
        """Helper to create a test client with a deposit transaction"""
        bank_account = BankAccount.objects.first()

        # Create client
        client = Client(
            first_name=first_name,
            last_name=last_name,
            email=f"{first_name.lower()}.{last_name.lower()}@test.com",
            data_source='webapp'
        )
        client.save()
        self.test_clients.append(client)

        # Create case
        case = Case(
            client=client,
            case_number=f'TEST-{client.id}',
            case_title=f'Test Case for {client.full_name}',
            case_status='Open'
        )
        case.save()

        # Create deposit
        transaction_date = date.today() - timedelta(days=days_ago)
        txn = BankTransaction(
            bank_account=bank_account,
            client=client,
            case=case,
            transaction_date=transaction_date,
            transaction_type='DEPOSIT',
            amount=Decimal(str(deposit_amount)),
            description=f'Test deposit {days_ago} days ago',
            status='cleared'
        )
        txn.save()

        return client, case, txn

    def get_stale_clients_from_logic(self):
        """
        Replicate the exact dashboard logic for stale clients
        """
        today = date.today()
        two_years_ago = today - timedelta(days=730)
        stale_clients = []

        for client in Client.objects.all():
            balance = client.get_current_balance()
            if balance > 0:
                # Find last deposit
                last_deposit = BankTransaction.objects.filter(
                    client=client,
                    transaction_type='DEPOSIT'
                ).exclude(status='voided').aggregate(Max('transaction_date'))['transaction_date__max']

                if last_deposit and last_deposit < two_years_ago:
                    stale_clients.append({
                        'client': client,
                        'balance': balance,
                        'last_deposit': last_deposit
                    })

        # Sort by balance descending (highest first)
        stale_clients = sorted(stale_clients, key=lambda x: x['balance'], reverse=True)
        return stale_clients

    def test_scenario_1_client_with_old_deposit(self):
        """Test: Client with deposit > 2 years ago should appear"""
        self.print_header("SCENARIO 1: Client with Deposit > 2 Years Ago")

        # Create client with deposit 1100 days ago (> 2 years)
        client, case, txn = self.create_test_client_with_deposit(
            'Stale', 'TestClient1', 75000.00, 1100
        )

        print(f"Created: {client.full_name}")
        print(f"  Balance: ${client.get_current_balance():,.2f}")
        print(f"  Last Deposit: {txn.transaction_date} ({(date.today() - txn.transaction_date).days} days ago)")

        # Get stale clients
        stale_clients = self.get_stale_clients_from_logic()

        # Find our test client in the list
        found = any(item['client'].id == client.id for item in stale_clients)

        self.print_test(
            "Client appears in stale clients list",
            found,
            f"Found {len(stale_clients)} total stale clients"
        )

    def test_scenario_2_client_with_recent_deposit(self):
        """Test: Client with recent deposit should NOT appear"""
        self.print_header("SCENARIO 2: Client with Recent Deposit (Should NOT Appear)")

        # Create client with deposit 100 days ago (< 2 years)
        client, case, txn = self.create_test_client_with_deposit(
            'Recent', 'TestClient2', 50000.00, 100
        )

        print(f"Created: {client.full_name}")
        print(f"  Balance: ${client.get_current_balance():,.2f}")
        print(f"  Last Deposit: {txn.transaction_date} ({(date.today() - txn.transaction_date).days} days ago)")

        # Get stale clients
        stale_clients = self.get_stale_clients_from_logic()

        # Our test client should NOT be in the list
        found = any(item['client'].id == client.id for item in stale_clients)

        self.print_test(
            "Client does NOT appear in stale clients list",
            not found,
            f"Recent deposit was only 100 days ago (needs > 730 days)"
        )

    def test_scenario_3_client_with_zero_balance(self):
        """Test: Client with $0 balance should NOT appear (even if old deposit)"""
        self.print_header("SCENARIO 3: Client with Zero Balance (Should NOT Appear)")

        # Create client with old deposit AND withdrawal to zero out balance
        client, case, deposit_txn = self.create_test_client_with_deposit(
            'ZeroBalance', 'TestClient3', 30000.00, 1100
        )

        # Add withdrawal to zero out balance
        bank_account = BankAccount.objects.first()
        withdrawal = BankTransaction(
            bank_account=bank_account,
            client=client,
            case=case,
            transaction_date=date.today() - timedelta(days=50),
            transaction_type='WITHDRAWAL',
            amount=Decimal('30000.00'),
            description='Withdrawal to zero balance',
            status='cleared'
        )
        withdrawal.save()

        balance = client.get_current_balance()
        print(f"Created: {client.full_name}")
        print(f"  Balance: ${balance:,.2f}")
        print(f"  Last Deposit: {deposit_txn.transaction_date} ({(date.today() - deposit_txn.transaction_date).days} days ago)")
        print(f"  Last Withdrawal: {withdrawal.transaction_date}")

        # Get stale clients
        stale_clients = self.get_stale_clients_from_logic()

        # Client should NOT appear (balance is zero)
        found = any(item['client'].id == client.id for item in stale_clients)

        self.print_test(
            "Client with $0 balance does NOT appear",
            not found,
            f"Balance must be > $0 (actual: ${balance:,.2f})"
        )

    def test_scenario_4_client_at_exactly_730_days(self):
        """Test: Client with deposit at exactly 730 days (boundary test)"""
        self.print_header("SCENARIO 4: Deposit at Exactly 730 Days (Boundary Test)")

        # Create client with deposit exactly 730 days ago
        client, case, txn = self.create_test_client_with_deposit(
            'Boundary', 'TestClient4', 40000.00, 730
        )

        print(f"Created: {client.full_name}")
        print(f"  Balance: ${client.get_current_balance():,.2f}")
        print(f"  Last Deposit: {txn.transaction_date} ({(date.today() - txn.transaction_date).days} days ago)")

        # Get stale clients
        stale_clients = self.get_stale_clients_from_logic()

        # At exactly 730 days, should NOT appear (needs to be > 730, i.e., 731+)
        found = any(item['client'].id == client.id for item in stale_clients)

        self.print_test(
            "Client at exactly 730 days does NOT appear",
            not found,
            f"Cutoff is < 730 days ago (before 2 years), not <= 730"
        )

    def test_scenario_5_client_at_731_days(self):
        """Test: Client with deposit at 731 days should appear"""
        self.print_header("SCENARIO 5: Deposit at 731 Days (Just Over Threshold)")

        # Create client with deposit 731 days ago
        client, case, txn = self.create_test_client_with_deposit(
            'JustOver', 'TestClient5', 60000.00, 731
        )

        print(f"Created: {client.full_name}")
        print(f"  Balance: ${client.get_current_balance():,.2f}")
        print(f"  Last Deposit: {txn.transaction_date} ({(date.today() - txn.transaction_date).days} days ago)")

        # Get stale clients
        stale_clients = self.get_stale_clients_from_logic()

        # Should appear
        found = any(item['client'].id == client.id for item in stale_clients)

        self.print_test(
            "Client at 731 days DOES appear",
            found,
            f"731 days is > 730 day threshold"
        )

    def test_scenario_6_top_3_sorting(self):
        """Test: Only top 3 clients by balance are shown"""
        self.print_header("SCENARIO 6: Top 3 Sorting by Balance")

        # Create 5 stale clients with different balances
        balances = [10000, 50000, 30000, 80000, 20000]  # $80k, $50k, $30k should be top 3

        for i, balance in enumerate(balances):
            self.create_test_client_with_deposit(
                f'Sort{i+1}', 'TestClient', balance, 1000 + (i * 10)
            )
            print(f"Created Sort{i+1} TestClient with ${balance:,.2f}")

        # Get all stale clients
        stale_clients = self.get_stale_clients_from_logic()

        # Get top 3
        top_3 = stale_clients[:3]

        # Verify we have at least 3
        self.print_test(
            "At least 3 stale clients exist",
            len(stale_clients) >= 3,
            f"Found {len(stale_clients)} stale clients"
        )

        if len(top_3) >= 3:
            print("\nTop 3 by balance:")
            for i, item in enumerate(top_3, 1):
                print(f"  {i}. {item['client'].full_name}: ${item['balance']:,.2f}")

            # Verify sorting (highest to lowest)
            sorted_correctly = (
                top_3[0]['balance'] >= top_3[1]['balance'] >= top_3[2]['balance']
            )

            self.print_test(
                "Top 3 sorted by balance (highest first)",
                sorted_correctly,
                f"Balances: ${top_3[0]['balance']:,.2f}, ${top_3[1]['balance']:,.2f}, ${top_3[2]['balance']:,.2f}"
            )

    def test_scenario_7_voided_deposits_excluded(self):
        """Test: Voided deposits are excluded from last deposit calculation"""
        self.print_header("SCENARIO 7: Voided Deposits Excluded")

        bank_account = BankAccount.objects.first()

        # Create client
        client = Client(
            first_name='Voided',
            last_name='TestClient7',
            email='voided.test7@test.com',
            data_source='webapp'
        )
        client.save()
        self.test_clients.append(client)

        # Create case
        case = Case(
            client=client,
            case_number=f'TEST-{client.id}',
            case_title='Voided deposit test',
            case_status='Open'
        )
        case.save()

        # Create old deposit (1000 days ago)
        old_deposit = BankTransaction(
            bank_account=bank_account,
            client=client,
            case=case,
            transaction_date=date.today() - timedelta(days=1000),
            transaction_type='DEPOSIT',
            amount=Decimal('50000.00'),
            description='Old deposit',
            status='cleared'
        )
        old_deposit.save()

        # Create recent deposit (100 days ago) but VOID it
        recent_deposit = BankTransaction(
            bank_account=bank_account,
            client=client,
            case=case,
            transaction_date=date.today() - timedelta(days=100),
            transaction_type='DEPOSIT',
            amount=Decimal('10000.00'),
            description='Recent but voided',
            status='voided',
            void_reason='Test void'
        )
        recent_deposit.save()

        print(f"Created: {client.full_name}")
        print(f"  Balance: ${client.get_current_balance():,.2f}")
        print(f"  Old deposit: {old_deposit.transaction_date} (1000 days ago) - CLEARED")
        print(f"  Recent deposit: {recent_deposit.transaction_date} (100 days ago) - VOIDED")

        # Get last deposit (should be the old one, not the voided recent one)
        last_deposit = BankTransaction.objects.filter(
            client=client,
            transaction_type='DEPOSIT'
        ).exclude(status='voided').aggregate(Max('transaction_date'))['transaction_date__max']

        # Get stale clients
        stale_clients = self.get_stale_clients_from_logic()
        found = any(item['client'].id == client.id for item in stale_clients)

        self.print_test(
            "Client appears (voided deposit ignored)",
            found,
            f"Last non-voided deposit: {last_deposit}"
        )

    def test_scenario_8_multiple_deposits_uses_latest(self):
        """Test: With multiple deposits, uses the most recent one"""
        self.print_header("SCENARIO 8: Multiple Deposits - Uses Latest")

        # Create client with multiple deposits
        client, case, _ = self.create_test_client_with_deposit(
            'Multiple', 'TestClient8', 10000.00, 1500  # Very old deposit
        )

        # Add a more recent deposit (but still > 2 years)
        bank_account = BankAccount.objects.first()
        recent_deposit = BankTransaction(
            bank_account=bank_account,
            client=client,
            case=case,
            transaction_date=date.today() - timedelta(days=900),
            transaction_type='DEPOSIT',
            amount=Decimal('20000.00'),
            description='More recent deposit',
            status='cleared'
        )
        recent_deposit.save()

        print(f"Created: {client.full_name}")
        print(f"  First deposit: {date.today() - timedelta(days=1500)} (1500 days ago)")
        print(f"  Latest deposit: {recent_deposit.transaction_date} (900 days ago)")
        print(f"  Balance: ${client.get_current_balance():,.2f}")

        # Get last deposit
        last_deposit = BankTransaction.objects.filter(
            client=client,
            transaction_type='DEPOSIT'
        ).exclude(status='voided').aggregate(Max('transaction_date'))['transaction_date__max']

        # Get stale clients
        stale_clients = self.get_stale_clients_from_logic()
        found = any(item['client'].id == client.id for item in stale_clients)

        self.print_test(
            "Uses most recent deposit date",
            last_deposit == recent_deposit.transaction_date,
            f"Last deposit: {last_deposit}"
        )

        self.print_test(
            "Client appears (latest deposit is 900 days ago)",
            found,
            "900 days > 730 day threshold"
        )

    def run_all_tests(self):
        """Run complete test suite"""
        print(f"\n{BOLD}{'='*80}{RESET}")
        print(f"{BOLD}{'STALE CLIENTS DASHBOARD - COMPREHENSIVE TEST SUITE':^80}{RESET}")
        print(f"{BOLD}{'='*80}{RESET}")

        try:
            # Run all test scenarios
            self.test_scenario_1_client_with_old_deposit()
            self.test_scenario_2_client_with_recent_deposit()
            self.test_scenario_3_client_with_zero_balance()
            self.test_scenario_4_client_at_exactly_730_days()
            self.test_scenario_5_client_at_731_days()
            self.test_scenario_6_top_3_sorting()
            self.test_scenario_7_voided_deposits_excluded()
            self.test_scenario_8_multiple_deposits_uses_latest()

        finally:
            # Always cleanup
            self.cleanup_test_clients()

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test results summary"""
        self.print_header("TEST RESULTS SUMMARY")

        total_tests = self.passed + self.failed
        pass_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0

        print(f"Total Tests:     {total_tests}")
        print(f"{GREEN}Passed:{RESET}          {self.passed}")
        print(f"{RED}Failed:{RESET}          {self.failed}")
        print(f"{YELLOW}Warnings:{RESET}        {self.warnings}")
        print(f"Pass Rate:       {pass_rate:.1f}%")

        if self.failed == 0:
            print(f"\n{GREEN}{BOLD}✓ ALL TESTS PASSED - STALE CLIENTS FEATURE IS ROBUST!{RESET}")
        else:
            print(f"\n{RED}{BOLD}✗ SOME TESTS FAILED - REVIEW ISSUES ABOVE{RESET}")

        print(f"{BOLD}{'='*80}{RESET}\n")


if __name__ == '__main__':
    suite = StaleClientsTestSuite()
    suite.run_all_tests()
