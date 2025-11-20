#!/usr/bin/env python
"""
Live API validation tests for 3 CRITICAL security fixes
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.bank_accounts.api.serializers import BankTransactionSerializer
from apps.bank_accounts.models import BankAccount, BankTransaction
from apps.clients.models import Client, Case
from decimal import Decimal

print('=' * 80)
print('CRITICAL SECURITY VALIDATIONS - LIVE API TEST')
print('=' * 80)
print()

# Get test data
bank_account = BankAccount.objects.first()
client1 = Client.objects.get(id=1)
client3 = Client.objects.get(id=3)
case1 = Case.objects.get(id=1)

balance = case1.get_current_balance()
print(f'Case 1 Balance: ${balance:,.2f}')
print(f'Case 1 ({case1.case_number}) belongs to: {case1.client.full_name}')
print(f'Client 1: {client1.full_name}')
print(f'Client 3: {client3.full_name}')
print()

# ============================================================================
# TEST 1: Client-Case Relationship Validation
# ============================================================================
print('=' * 80)
print('TEST 1: Client-Case Relationship Validation')
print('=' * 80)
print(f'Attempting to assign Case 1 to Client 3 (should REJECT)...')
print()

data1 = {
    'bank_account': bank_account.id,
    'client': client3.id,  # Client 3
    'case': case1.id,      # Case 1 belongs to Client 1
    'transaction_date': '2025-01-10',
    'transaction_type': 'WITHDRAWAL',
    'amount': '100.00',
    'description': 'Test client-case mismatch',
    'payee': 'Test Vendor',
    'reference_number': 'TEST-001'
}

s1 = BankTransactionSerializer(data=data1)
if s1.is_valid():
    print('❌ FAIL: Should have rejected!')
    print(f'Result: {s1.validated_data}')
else:
    print('✅ PASS: Correctly rejected')
    if 'case' in s1.errors:
        print(f'Error: {s1.errors["case"][0]}')
print()

# ============================================================================
# TEST 2: Insufficient Funds Validation
# ============================================================================
print('=' * 80)
print('TEST 2: Insufficient Funds Validation')
print('=' * 80)
print(f'Attempting to withdraw $10,000 from Case 1 (balance: ${balance:,.2f})...')
print()

data2 = {
    'bank_account': bank_account.id,
    'client': client1.id,
    'case': case1.id,
    'transaction_date': '2025-01-10',
    'transaction_type': 'WITHDRAWAL',
    'amount': '10000.00',
    'description': 'Test insufficient funds',
    'payee': 'Test Vendor',
    'reference_number': 'TEST-002'
}

s2 = BankTransactionSerializer(data=data2)
if s2.is_valid():
    print('❌ FAIL: Should have rejected!')
    print(f'Result: {s2.validated_data}')
else:
    print('✅ PASS: Correctly rejected')
    if 'amount' in s2.errors:
        print(f'Error: {s2.errors["amount"][0]}')
print()

# ============================================================================
# TEST 3: Edit Amount Bypass Protection
# ============================================================================
print('=' * 80)
print('TEST 3: Edit Amount Bypass Protection')
print('=' * 80)
print('Creating small withdrawal ($100)...')

small_tx = BankTransaction.objects.create(
    bank_account=bank_account,
    client=client1,
    case=case1,
    transaction_date='2025-01-10',
    transaction_type='WITHDRAWAL',
    amount=Decimal('100.00'),
    description='Small withdrawal',
    payee='Test Vendor',
    reference_number='TEST-003',
    status='pending',
    created_by='system'
)

print(f'Created transaction ID: {small_tx.id}')
new_bal = case1.get_current_balance()
print(f'New balance: ${new_bal:,.2f}')
print(f'Attempting to edit $100 to $10,000 (needs $9,900 more)...')
print()

data3 = {
    'bank_account': bank_account.id,
    'client': client1.id,
    'case': case1.id,
    'transaction_date': '2025-01-10',
    'transaction_type': 'WITHDRAWAL',
    'amount': '10000.00',
    'description': 'Edit bypass attempt',
    'payee': 'Test Vendor',
    'reference_number': 'TEST-003'
}

s3 = BankTransactionSerializer(small_tx, data=data3)
if s3.is_valid():
    print('❌ FAIL: Should have rejected the edit!')
    print(f'Result: {s3.validated_data}')
else:
    print('✅ PASS: Correctly rejected the edit')
    if 'amount' in s3.errors:
        print(f'Error: {s3.errors["amount"][0]}')

# Cleanup
small_tx.delete()
print()
print('=' * 80)
print('VALIDATION TEST COMPLETE')
print('=' * 80)
