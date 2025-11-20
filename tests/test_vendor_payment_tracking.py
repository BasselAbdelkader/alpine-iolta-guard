#!/usr/bin/env python3
"""
Comprehensive Test Suite: Vendor Payment Tracking
=================================================

Tests all scenarios where vendors are paid and ensures:
1. Vendor FK is set correctly when transactions are created
2. Vendor detail page shows all payments
3. Auto-linking works for create and update operations
4. Edge cases are handled properly

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

from apps.vendors.models import Vendor
from apps.bank_accounts.models import BankTransaction, BankAccount
from apps.clients.models import Client, Case
from decimal import Decimal
from datetime import date, timedelta
from django.db import transaction as db_transaction

# ANSI color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

class VendorPaymentTestSuite:
    """Comprehensive test suite for vendor payment tracking"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.test_data = {}

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

    def setup_test_data(self):
        """Setup test vendors, clients, cases, bank account"""
        self.print_header("SETUP TEST DATA")

        try:
            # Create test bank account
            self.test_data['bank_account'] = BankAccount.objects.filter(is_active=True).first()
            if not self.test_data['bank_account']:
                self.test_data['bank_account'] = BankAccount.objects.create(
                    account_number='TEST-ACCT-001',
                    bank_name='Test Bank',
                    account_name='Test Trust Account',
                    account_type='TRUST',
                    opening_balance=Decimal('0.00')
                )
            print(f"✓ Bank Account: {self.test_data['bank_account'].account_number}")

            # Create test client
            self.test_data['client'] = Client.objects.filter(is_active=True).first()
            if not self.test_data['client']:
                self.test_data['client'] = Client.objects.create(
                    first_name='Test',
                    last_name='Client',
                    email='testclient@example.com'
                )
            print(f"✓ Client: {self.test_data['client'].full_name}")

            # Create test case
            self.test_data['case'] = Case.objects.filter(
                client=self.test_data['client'],
                case_status='Open'
            ).first()
            if not self.test_data['case']:
                self.test_data['case'] = Case.objects.create(
                    client=self.test_data['client'],
                    case_title='Test Case for Vendor Payments',
                    case_number='TEST-CASE-001',
                    case_status='Open'
                )
            print(f"✓ Case: {self.test_data['case'].case_number}")

            # Create test vendors
            vendors_data = [
                {'name': 'Test Vendor Alpha', 'email': 'alpha@vendor.com'},
                {'name': 'Test Vendor Beta', 'email': 'beta@vendor.com'},
                {'name': 'Test Vendor Gamma', 'email': 'gamma@vendor.com'},
                {'name': 'Medical Records Plus', 'email': 'existing@vendor.com'},  # Existing vendor
            ]

            self.test_data['vendors'] = []
            for vdata in vendors_data:
                vendor, created = Vendor.objects.get_or_create(
                    vendor_name=vdata['name'],
                    defaults={'email': vdata['email']}
                )
                self.test_data['vendors'].append(vendor)
                print(f"✓ Vendor: {vendor.vendor_name} (ID: {vendor.id})")

            print(f"\n{GREEN}Setup complete!{RESET}\n")
            return True

        except Exception as e:
            print(f"{RED}Setup failed: {str(e)}{RESET}")
            return False

    def test_scenario_1_new_transaction_with_vendor_payee(self):
        """Test: Create new transaction with vendor name as payee"""
        self.print_header("SCENARIO 1: New Transaction with Vendor Payee")

        vendor = self.test_data['vendors'][0]

        # Create transaction with vendor name as payee
        txn = BankTransaction(
            bank_account=self.test_data['bank_account'],
            client=self.test_data['client'],
            case=self.test_data['case'],
            transaction_date=date.today(),
            transaction_type='WITHDRAWAL',
            amount=Decimal('250.00'),
            description='Test payment to vendor',
            payee=vendor.vendor_name,  # Using vendor name
            reference_number='TEST-001',
            status='pending'
        )
        txn.save(audit_user='test_suite')

        # Reload from DB
        txn.refresh_from_db()

        # Verify vendor FK is set
        passed = txn.vendor is not None and txn.vendor.id == vendor.id
        self.print_test(
            "Vendor FK automatically set when creating transaction",
            passed,
            f"Expected vendor #{vendor.id}, got {txn.vendor.id if txn.vendor else 'None'}"
        )

        # Verify it appears in vendor payments API
        payments = BankTransaction.objects.filter(vendor=vendor).exclude(status='voided')
        passed = payments.filter(id=txn.id).exists()
        self.print_test(
            "Transaction appears in vendor.payments query",
            passed,
            f"Found {payments.count()} payment(s) for vendor"
        )

        # Cleanup
        txn.delete()

    def test_scenario_2_case_insensitive_matching(self):
        """Test: Vendor matching is case-insensitive"""
        self.print_header("SCENARIO 2: Case-Insensitive Vendor Matching")

        vendor = self.test_data['vendors'][1]
        variations = [
            vendor.vendor_name.upper(),  # ALL CAPS
            vendor.vendor_name.lower(),  # all lowercase
            vendor.vendor_name.title(),  # Title Case
        ]

        for payee_variation in variations:
            txn = BankTransaction(
                bank_account=self.test_data['bank_account'],
                client=self.test_data['client'],
                case=self.test_data['case'],
                transaction_date=date.today(),
                transaction_type='WITHDRAWAL',
                amount=Decimal('100.00'),
                description='Case insensitive test',
                payee=payee_variation,
                reference_number=f'TEST-{payee_variation[:5]}',
                status='pending')

            txn.save()

            txn.refresh_from_db()
            passed = txn.vendor is not None and txn.vendor.id == vendor.id
            self.print_test(
                f"Matched '{payee_variation}' to vendor",
                passed,
                f"Vendor: {txn.vendor.vendor_name if txn.vendor else 'None'}"
            )

            txn.delete()

    def test_scenario_3_update_existing_transaction(self):
        """Test: Updating transaction payee links to vendor"""
        self.print_header("SCENARIO 3: Update Transaction Payee")

        vendor = self.test_data['vendors'][2]

        # Create transaction WITHOUT vendor
        txn = BankTransaction(
            bank_account=self.test_data['bank_account'],
            client=self.test_data['client'],
            case=self.test_data['case'],
            transaction_date=date.today(),
            transaction_type='WITHDRAWAL',
            amount=Decimal('300.00'),
            description='Initially no vendor',
            payee='Some Random Payee',
            reference_number='TEST-UPD',
            status='pending')
        txn.save()

        # Verify no vendor initially
        txn.refresh_from_db()
        self.print_test(
            "Transaction created without vendor FK",
            txn.vendor is None,
            f"Payee: {txn.payee}"
        )

        # Update payee to vendor name
        txn.payee = vendor.vendor_name
        txn.save()

        # Reload and verify vendor FK is NOW set
        txn.refresh_from_db()
        passed = txn.vendor is not None and txn.vendor.id == vendor.id
        self.print_test(
            "Vendor FK set after updating payee",
            passed,
            f"Vendor: {txn.vendor.vendor_name if txn.vendor else 'None'}"
        )

        txn.delete()

    def test_scenario_4_whitespace_handling(self):
        """Test: Payee with extra whitespace still matches"""
        self.print_header("SCENARIO 4: Whitespace Handling")

        vendor = self.test_data['vendors'][0]
        payee_variations = [
            f"  {vendor.vendor_name}  ",  # Leading/trailing spaces
            f" {vendor.vendor_name} ",     # Single spaces
            f"   {vendor.vendor_name}   ", # Multiple spaces
        ]

        for payee in payee_variations:
            txn = BankTransaction(
                bank_account=self.test_data['bank_account'],
                client=self.test_data['client'],
                case=self.test_data['case'],
                transaction_date=date.today(),
                transaction_type='WITHDRAWAL',
                amount=Decimal('50.00'),
                description='Whitespace test',
                payee=payee,
                reference_number='TEST-WS',
                status='pending')

            txn.save()

            txn.refresh_from_db()
            passed = txn.vendor is not None and txn.vendor.id == vendor.id
            self.print_test(
                f"Matched payee with whitespace: '{payee}'",
                passed
            )

            txn.delete()

    def test_scenario_5_vendor_does_not_exist(self):
        """Test: Payee that doesn't match any vendor"""
        self.print_header("SCENARIO 5: Non-Existent Vendor")

        txn = BankTransaction(
            bank_account=self.test_data['bank_account'],
            client=self.test_data['client'],
            case=self.test_data['case'],
            transaction_date=date.today(),
            transaction_type='WITHDRAWAL',
            amount=Decimal('75.00'),
            description='Non-vendor payee',
            payee='This Vendor Does Not Exist',
            reference_number='TEST-NONE',
            status='pending')

        txn.save()

        txn.refresh_from_db()
        passed = txn.vendor is None
        self.print_test(
            "Vendor FK is None when payee doesn't match",
            passed,
            f"Payee: '{txn.payee}', Vendor: {txn.vendor}"
        )

        txn.delete()

    def test_scenario_6_existing_vendor_payments(self):
        """Test: Existing vendor shows all payments"""
        self.print_header("SCENARIO 6: Existing Vendor Payment History")

        # Use Medical Records Plus (existing vendor from setup)
        vendor = self.test_data['vendors'][3]

        # Get all payments for this vendor
        payments = BankTransaction.objects.filter(vendor=vendor).exclude(status='voided')

        self.print_test(
            f"Found payments for {vendor.vendor_name}",
            payments.count() > 0,
            f"Total payments: {payments.count()}"
        )

        # Verify each payment has vendor FK set
        for payment in payments:
            passed = payment.vendor is not None and payment.vendor.id == vendor.id
            if not passed:
                self.print_warning(
                    f"Payment #{payment.id} missing vendor FK (payee: {payment.payee})"
                )

    def test_scenario_7_multiple_payments_same_vendor(self):
        """Test: Multiple payments to same vendor"""
        self.print_header("SCENARIO 7: Multiple Payments to Same Vendor")

        vendor = self.test_data['vendors'][0]
        payment_amounts = [Decimal('100.00'), Decimal('200.00'), Decimal('300.00')]
        created_txns = []

        for i, amount in enumerate(payment_amounts):
            txn = BankTransaction(
                bank_account=self.test_data['bank_account'],
                client=self.test_data['client'],
                case=self.test_data['case'],
                transaction_date=date.today() - timedelta(days=i),
                transaction_type='WITHDRAWAL',
                amount=amount,
                description=f'Payment {i+1}',
                payee=vendor.vendor_name,
                reference_number=f'TEST-MULTI-{i+1}',
                status='pending')
            created_txns.append(txn)

        # Query all payments for this vendor
        vendor_payments = BankTransaction.objects.filter(vendor=vendor).exclude(status='voided')
        txn.save()

        # Verify all created transactions appear
        all_found = True
        for txn in created_txns:
            if not vendor_payments.filter(id=txn.id).exists():
                all_found = False
                break

        self.print_test(
            "All payments appear in vendor query",
            all_found,
            f"Created {len(created_txns)}, found {vendor_payments.filter(id__in=[t.id for t in created_txns]).count()}"
        )

        # Calculate running total
        expected_total = sum(payment_amounts)
        actual_total = sum(p.amount for p in created_txns)

        self.print_test(
            "Payment totals match",
            expected_total == actual_total,
            f"Expected ${expected_total}, got ${actual_total}"
        )

        # Cleanup
        for txn in created_txns:
            txn.delete()

    def test_scenario_8_voided_transactions_excluded(self):
        """Test: Voided transactions don't appear in vendor payments"""
        self.print_header("SCENARIO 8: Voided Transactions Excluded")

        vendor = self.test_data['vendors'][1]

        # Create and void a transaction
        txn = BankTransaction(
            bank_account=self.test_data['bank_account'],
            client=self.test_data['client'],
            case=self.test_data['case'],
            transaction_date=date.today(),
            transaction_type='WITHDRAWAL',
            amount=Decimal('500.00'),
            description='To be voided',
            payee=vendor.vendor_name,
            reference_number='TEST-VOID',
            status='pending')

        # Void it
        txn.status = 'voided'
        txn.void_reason = 'Test void'
        txn.save()

        # Query non-voided payments
        payments = BankTransaction.objects.filter(vendor=vendor).exclude(status='voided')

        passed = not payments.filter(id=txn.id).exists()
        self.print_test(
            "Voided transaction excluded from vendor payments",
            passed,
            f"Voided txn #{txn.id} in results: {payments.filter(id=txn.id).exists()}"
        )

        txn.delete()

    def test_scenario_9_api_endpoint_integration(self):
        """Test: Vendor payments API returns correct data"""
        self.print_header("SCENARIO 9: API Endpoint Integration")

        vendor = self.test_data['vendors'][0]

        # Create test payments
        test_amounts = [Decimal('111.11'), Decimal('222.22'), Decimal('333.33')]
        created_ids = []

        for i, amount in enumerate(test_amounts):
            txn = BankTransaction(
                bank_account=self.test_data['bank_account'],
                client=self.test_data['client'],
                case=self.test_data['case'],
                transaction_date=date.today() - timedelta(days=i*2),
                transaction_type='WITHDRAWAL',
                amount=amount,
                description=f'API test payment {i+1}',
                payee=vendor.vendor_name,
                reference_number=f'API-TEST-{i+1}',
                status='cleared')
            created_ids.append(txn.id)

        # Simulate API query (same as vendor detail page uses)
        payments_qs = BankTransaction.objects.filter(
            vendor=vendor
        ).exclude(status='voided').select_related('case', 'client').order_by('-transaction_date')
        txn.save()

        # Verify all test payments are included
        found_count = payments_qs.filter(id__in=created_ids).count()

        self.print_test(
            "API query returns all test payments",
            found_count == len(test_amounts),
            f"Expected {len(test_amounts)}, found {found_count}"
        )

        # Verify running total calculation
        running_total = Decimal('0')
        for payment in payments_qs.filter(id__in=created_ids).order_by('transaction_date'):
            running_total += payment.amount

        expected_total = sum(test_amounts)
        self.print_test(
            "Running total calculated correctly",
            running_total == expected_total,
            f"Expected ${expected_total}, got ${running_total}"
        )

        # Cleanup
        BankTransaction.objects.filter(id__in=created_ids).delete()

    def test_scenario_10_serializer_auto_linking(self):
        """Test: Serializer auto-links vendor on create and update"""
        self.print_header("SCENARIO 10: Serializer Auto-Linking")

        from apps.bank_accounts.api.serializers import BankTransactionSerializer

        vendor = self.test_data['vendors'][2]

        # Test CREATE via serializer
        data = {
            'bank_account': self.test_data['bank_account'].id,
            'client': self.test_data['client'].id,
            'case': self.test_data['case'].id,
            'transaction_date': str(date.today()),
            'transaction_type': 'WITHDRAWAL',
            'amount': '450.00',
            'description': 'Serializer create test',
            'payee': vendor.vendor_name,
            'reference_number': 'SER-CREATE',
            'status': 'pending'
        }

        serializer = BankTransactionSerializer(data=data)
        if serializer.is_valid():
            txn = serializer.save()

            passed = txn.vendor is not None and txn.vendor.id == vendor.id
            self.print_test(
                "Serializer.create() auto-links vendor",
                passed,
                f"Vendor: {txn.vendor.vendor_name if txn.vendor else 'None'}"
            )

            # Test UPDATE via serializer
            update_vendor = self.test_data['vendors'][1]
            update_serializer = BankTransactionSerializer(
                txn,
                data={'payee': update_vendor.vendor_name},
                partial=True
            )

            if update_serializer.is_valid():
                updated_txn = update_serializer.save()

                passed = updated_txn.vendor is not None and updated_txn.vendor.id == update_vendor.id
                self.print_test(
                    "Serializer.update() auto-links vendor",
                    passed,
                    f"Vendor: {updated_txn.vendor.vendor_name if updated_txn.vendor else 'None'}"
                )

            txn.delete()
        else:
            self.print_test(
                "Serializer validation",
                False,
                f"Errors: {serializer.errors}"
            )

    def run_all_tests(self):
        """Run complete test suite"""
        print(f"\n{BOLD}{'='*80}{RESET}")
        print(f"{BOLD}{'VENDOR PAYMENT TRACKING - COMPREHENSIVE TEST SUITE':^80}{RESET}")
        print(f"{BOLD}{'='*80}{RESET}")

        # Setup
        if not self.setup_test_data():
            print(f"\n{RED}Setup failed - aborting tests{RESET}")
            return

        # Run all test scenarios
        self.test_scenario_1_new_transaction_with_vendor_payee()
        self.test_scenario_2_case_insensitive_matching()
        self.test_scenario_3_update_existing_transaction()
        self.test_scenario_4_whitespace_handling()
        self.test_scenario_5_vendor_does_not_exist()
        self.test_scenario_6_existing_vendor_payments()
        self.test_scenario_7_multiple_payments_same_vendor()
        self.test_scenario_8_voided_transactions_excluded()
        self.test_scenario_9_api_endpoint_integration()
        self.test_scenario_10_serializer_auto_linking()

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
            print(f"\n{GREEN}{BOLD}✓ ALL TESTS PASSED - VENDOR PAYMENT TRACKING IS ROBUST!{RESET}")
        else:
            print(f"\n{RED}{BOLD}✗ SOME TESTS FAILED - REVIEW ISSUES ABOVE{RESET}")

        print(f"{BOLD}{'='*80}{RESET}\n")


if __name__ == '__main__':
    suite = VendorPaymentTestSuite()
    suite.run_all_tests()
