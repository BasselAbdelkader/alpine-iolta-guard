"""
Unit Tests for Critical Security Validations in BankTransactionSerializer

Tests the three CRITICAL security fixes:
1. Insufficient funds validation
2. Edit amount bypass protection
3. Client-case relationship validation

Run with: docker exec iolta_backend_alpine python manage.py test apps.bank_accounts.tests.test_critical_validations
"""

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from apps.bank_accounts.models import BankAccount, BankTransaction
from apps.bank_accounts.api.serializers import BankTransactionSerializer
from apps.clients.models import Client, Case


class CriticalValidationsTestCase(TestCase):
    """Test critical security validations"""

    def setUp(self):
        """Set up test data"""
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create bank account
        self.bank_account = BankAccount.objects.create(
            account_number='TEST123',
            bank_name='Test Bank',
            account_name='Test Trust Account',
            routing_number='111000025',
            account_type='TRUST',
            opening_balance=Decimal('0.00')
        )

        # Create two clients
        self.client_a = Client.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com'
        )

        self.client_b = Client.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com'
        )

        # Create cases for each client
        self.case_a = Case.objects.create(
            case_number='CASE-A-001',
            client=self.client_a,
            case_title='Doe vs Company',
            case_description='Test case for Client A'
        )

        self.case_b = Case.objects.create(
            case_number='CASE-B-001',
            client=self.client_b,
            case_title='Smith vs Corp',
            case_description='Test case for Client B'
        )

        # Create initial deposit for case_a ($1000)
        self.initial_deposit = BankTransaction.objects.create(
            bank_account=self.bank_account,
            client=self.client_a,
            case=self.case_a,
            transaction_date='2025-01-01',
            transaction_type='DEPOSIT',
            item_type='CLIENT_DEPOSIT',
            amount=Decimal('1000.00'),
            description='Initial deposit',
            payee='Client A',
            reference_number='REF001',
            status='pending',
            created_by='system'
        )

    # ========================================================================
    # TEST 1: Client-Case Relationship Validation
    # ========================================================================

    def test_valid_client_case_relationship(self):
        """Should ALLOW transaction when case belongs to client"""
        data = {
            'bank_account': self.bank_account,
            'client': self.client_a,
            'case': self.case_a,  # Case A belongs to Client A ✓
            'transaction_date': '2025-01-02',
            'transaction_type': 'WITHDRAWAL',
            'item_type': 'VENDOR_PAYMENT',
            'amount': Decimal('100.00'),
            'description': 'Valid transaction',
            'payee': 'Test Vendor',
            'reference_number': 'REF002'
        }

        serializer = BankTransactionSerializer(data=data)
        # Should NOT raise validation error
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_client_case_relationship(self):
        """Should REJECT transaction when case doesn't belong to client"""
        data = {
            'bank_account': self.bank_account,
            'client': self.client_a,  # Client A
            'case': self.case_b,      # Case B belongs to Client B ✗
            'transaction_date': '2025-01-02',
            'transaction_type': 'WITHDRAWAL',
            'item_type': 'VENDOR_PAYMENT',
            'amount': Decimal('100.00'),
            'description': 'Invalid transaction',
            'payee': 'Test Vendor',
            'reference_number': 'REF003'
        }

        serializer = BankTransactionSerializer(data=data)
        # Should raise validation error
        self.assertFalse(serializer.is_valid())
        self.assertIn('case', serializer.errors)
        self.assertIn('Invalid case assignment', str(serializer.errors['case']))

    # ========================================================================
    # TEST 2: Insufficient Funds Validation (New Transactions)
    # ========================================================================

    def test_withdrawal_within_available_balance(self):
        """Should ALLOW withdrawal when sufficient funds exist"""
        # Case A has $1000 balance
        data = {
            'bank_account': self.bank_account,
            'client': self.client_a,
            'case': self.case_a,
            'transaction_date': '2025-01-02',
            'transaction_type': 'WITHDRAWAL',
            'item_type': 'VENDOR_PAYMENT',
            'amount': Decimal('500.00'),  # $500 < $1000 ✓
            'description': 'Valid withdrawal',
            'payee': 'Test Vendor',
            'reference_number': 'REF004'
        }

        serializer = BankTransactionSerializer(data=data)
        # Should NOT raise validation error
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_withdrawal_exceeds_available_balance(self):
        """Should REJECT withdrawal when insufficient funds"""
        # Case A has $1000 balance
        data = {
            'bank_account': self.bank_account,
            'client': self.client_a,
            'case': self.case_a,
            'transaction_date': '2025-01-02',
            'transaction_type': 'WITHDRAWAL',
            'item_type': 'VENDOR_PAYMENT',
            'amount': Decimal('2000.00'),  # $2000 > $1000 ✗
            'description': 'Overdraft attempt',
            'payee': 'Test Vendor',
            'reference_number': 'REF005'
        }

        serializer = BankTransactionSerializer(data=data)
        # Should raise validation error
        self.assertFalse(serializer.is_valid())
        self.assertIn('amount', serializer.errors)
        self.assertIn('Insufficient funds', str(serializer.errors['amount']))

    def test_withdrawal_exact_balance(self):
        """Should ALLOW withdrawal of exact available balance"""
        # Case A has $1000 balance
        data = {
            'bank_account': self.bank_account,
            'client': self.client_a,
            'case': self.case_a,
            'transaction_date': '2025-01-02',
            'transaction_type': 'WITHDRAWAL',
            'item_type': 'VENDOR_PAYMENT',
            'amount': Decimal('1000.00'),  # $1000 = $1000 ✓
            'description': 'Full withdrawal',
            'payee': 'Test Vendor',
            'reference_number': 'REF006'
        }

        serializer = BankTransactionSerializer(data=data)
        # Should NOT raise validation error
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_deposit_does_not_check_balance(self):
        """Should ALLOW deposits regardless of balance (they ADD funds)"""
        # Case A has $1000 balance
        data = {
            'bank_account': self.bank_account,
            'client': self.client_a,
            'case': self.case_a,
            'transaction_date': '2025-01-02',
            'transaction_type': 'DEPOSIT',
            'item_type': 'CLIENT_DEPOSIT',
            'amount': Decimal('5000.00'),  # Any amount is OK for deposits ✓
            'description': 'Additional deposit',
            'payee': 'Client A',
            'reference_number': 'REF007'
        }

        serializer = BankTransactionSerializer(data=data)
        # Should NOT raise validation error
        self.assertTrue(serializer.is_valid(), serializer.errors)

    # ========================================================================
    # TEST 3: Edit Amount Bypass Protection
    # ========================================================================

    def test_edit_withdrawal_increase_within_balance(self):
        """Should ALLOW editing withdrawal amount if sufficient funds"""
        # Create a $100 withdrawal
        small_withdrawal = BankTransaction.objects.create(
            bank_account=self.bank_account,
            client=self.client_a,
            case=self.case_a,
            transaction_date='2025-01-02',
            transaction_type='WITHDRAWAL',
            item_type='VENDOR_PAYMENT',
            amount=Decimal('100.00'),
            description='Small withdrawal',
            payee='Test Vendor',
            reference_number='REF008',
            status='pending',
            created_by='system'
        )

        # After $100 withdrawal, balance is $900
        # Try to edit to $500 (needs additional $400, available $900) ✓
        data = {
            'bank_account': self.bank_account,
            'client': self.client_a,
            'case': self.case_a,
            'transaction_date': '2025-01-02',
            'transaction_type': 'WITHDRAWAL',
            'item_type': 'VENDOR_PAYMENT',
            'amount': Decimal('500.00'),  # Increase by $400, available $900 ✓
            'description': 'Edited withdrawal',
            'payee': 'Test Vendor',
            'reference_number': 'REF008'
        }

        serializer = BankTransactionSerializer(small_withdrawal, data=data)
        # Should NOT raise validation error
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_edit_withdrawal_increase_exceeds_balance(self):
        """Should REJECT editing withdrawal amount if insufficient funds"""
        # Create a $100 withdrawal
        small_withdrawal = BankTransaction.objects.create(
            bank_account=self.bank_account,
            client=self.client_a,
            case=self.case_a,
            transaction_date='2025-01-02',
            transaction_type='WITHDRAWAL',
            item_type='VENDOR_PAYMENT',
            amount=Decimal('100.00'),
            description='Small withdrawal',
            payee='Test Vendor',
            'reference_number': 'REF009',
            status='pending',
            created_by='system'
        )

        # After $100 withdrawal, balance is $900
        # Try to edit to $1500 (needs additional $1400, only $900 available) ✗
        data = {
            'bank_account': self.bank_account,
            'client': self.client_a,
            'case': self.case_a,
            'transaction_date': '2025-01-02',
            'transaction_type': 'WITHDRAWAL',
            'item_type': 'VENDOR_PAYMENT',
            'amount': Decimal('1500.00'),  # Increase by $1400, only $900 available ✗
            'description': 'Overdraft edit attempt',
            'payee': 'Test Vendor',
            'reference_number': 'REF009'
        }

        serializer = BankTransactionSerializer(small_withdrawal, data=data)
        # Should raise validation error
        self.assertFalse(serializer.is_valid())
        self.assertIn('amount', serializer.errors)
        self.assertIn('Insufficient funds', str(serializer.errors['amount']))

    def test_edit_change_deposit_to_withdrawal(self):
        """Should VALIDATE when changing DEPOSIT to WITHDRAWAL (edit bypass attack)"""
        # Create a $500 deposit
        deposit = BankTransaction.objects.create(
            bank_account=self.bank_account,
            client=self.client_a,
            case=self.case_a,
            transaction_date='2025-01-03',
            transaction_type='DEPOSIT',
            item_type='CLIENT_DEPOSIT',
            amount=Decimal('500.00'),
            description='Deposit',
            payee='Client A',
            reference_number='REF010',
            status='pending',
            created_by='system'
        )

        # After $1000 + $500 deposit, balance is $1500
        # Try to change DEPOSIT to WITHDRAWAL of $2000 ✗
        data = {
            'bank_account': self.bank_account,
            'client': self.client_a,
            'case': self.case_a,
            'transaction_date': '2025-01-03',
            'transaction_type': 'WITHDRAWAL',  # Changed from DEPOSIT
            'item_type': 'VENDOR_PAYMENT',
            'amount': Decimal('2000.00'),
            'description': 'Attack attempt',
            'payee': 'Attacker',
            'reference_number': 'REF010'
        }

        serializer = BankTransactionSerializer(deposit, data=data)
        # Should raise validation error (needs $2000, only $1500 available)
        self.assertFalse(serializer.is_valid())
        self.assertIn('amount', serializer.errors)
        self.assertIn('Insufficient funds', str(serializer.errors['amount']))

    def test_edit_decrease_withdrawal_always_allowed(self):
        """Should ALLOW decreasing withdrawal amount (frees up funds)"""
        # Create a $500 withdrawal
        large_withdrawal = BankTransaction.objects.create(
            bank_account=self.bank_account,
            client=self.client_a,
            case=self.case_a,
            'transaction_date': '2025-01-02',
            transaction_type='WITHDRAWAL',
            item_type='VENDOR_PAYMENT',
            amount=Decimal('500.00'),
            description='Large withdrawal',
            payee='Test Vendor',
            reference_number='REF011',
            status='pending',
            created_by='system'
        )

        # Edit to $100 (frees up $400) ✓
        data = {
            'bank_account': self.bank_account,
            'client': self.client_a,
            'case': self.case_a,
            'transaction_date': '2025-01-02',
            'transaction_type': 'WITHDRAWAL',
            'item_type': 'VENDOR_PAYMENT',
            'amount': Decimal('100.00'),  # Decrease by $400 ✓
            'description': 'Reduced withdrawal',
            'payee': 'Test Vendor',
            'reference_number': 'REF011'
        }

        serializer = BankTransactionSerializer(large_withdrawal, data=data)
        # Should NOT raise validation error
        self.assertTrue(serializer.is_valid(), serializer.errors)

    # ========================================================================
    # TEST 4: Edge Cases
    # ========================================================================

    def test_zero_balance_case_reject_withdrawal(self):
        """Should REJECT withdrawal from case with zero balance"""
        # Create a case with no transactions (zero balance)
        case_zero = Case.objects.create(
            case_number='CASE-ZERO',
            client=self.client_a,
            case_title='Zero Balance Case',
            case_description='Test case with no funds'
        )

        data = {
            'bank_account': self.bank_account,
            'client': self.client_a,
            'case': case_zero,
            'transaction_date': '2025-01-02',
            'transaction_type': 'WITHDRAWAL',
            'item_type': 'VENDOR_PAYMENT',
            'amount': Decimal('100.00'),  # $100 > $0 ✗
            'description': 'Overdraft attempt',
            'payee': 'Test Vendor',
            'reference_number': 'REF012'
        }

        serializer = BankTransactionSerializer(data=data)
        # Should raise validation error
        self.assertFalse(serializer.is_valid())
        self.assertIn('amount', serializer.errors)

    def test_multiple_withdrawals_cumulative_validation(self):
        """Should validate against CURRENT balance (after all transactions)"""
        # Starting balance: $1000
        # Withdrawal 1: $600 (leaves $400)
        BankTransaction.objects.create(
            bank_account=self.bank_account,
            client=self.client_a,
            case=self.case_a,
            transaction_date='2025-01-02',
            transaction_type='WITHDRAWAL',
            item_type='VENDOR_PAYMENT',
            amount=Decimal('600.00'),
            description='First withdrawal',
            payee='Vendor 1',
            reference_number='REF013',
            status='pending',
            created_by='system'
        )

        # Try to create another $600 withdrawal (only $400 left) ✗
        data = {
            'bank_account': self.bank_account,
            'client': self.client_a,
            'case': self.case_a,
            'transaction_date': '2025-01-03',
            'transaction_type': 'WITHDRAWAL',
            'item_type': 'VENDOR_PAYMENT',
            'amount': Decimal('600.00'),  # $600 > $400 remaining ✗
            'description': 'Second withdrawal',
            'payee': 'Vendor 2',
            'reference_number': 'REF014'
        }

        serializer = BankTransactionSerializer(data=data)
        # Should raise validation error
        self.assertFalse(serializer.is_valid())
        self.assertIn('amount', serializer.errors)
        self.assertIn('Insufficient funds', str(serializer.errors['amount']))


# Run tests with:
# docker exec iolta_backend_alpine python manage.py test apps.bank_accounts.tests.test_critical_validations -v 2
