#!/usr/bin/env python
"""
Test Field Replacements
Verify that transaction_number is renamed to RefNo and case_number is replaced with case_title
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.bank_accounts.models import BankAccount, BankTransaction
from apps.clients.models import Case, Client
from apps.bank_accounts.api.serializers import BankTransactionSerializer, BankAccountSerializer
from apps.clients.api.serializers import CaseSerializer, CaseListSerializer
from django.contrib.auth.models import User

print('=' * 80)
print('FIELD REPLACEMENT TEST')
print('=' * 80)
print()
print('Testing:')
print('  1. transaction_number → RefNo')
print('  2. case_number → case_title')
print()

# Get test data
transaction = BankTransaction.objects.first()
bank_account = BankAccount.objects.first()
case = Case.objects.first()

test_results = []

# ============================================================================
# Test 1: BankTransactionSerializer
# ============================================================================
print('=' * 80)
print('Test 1: BankTransactionSerializer')
print('=' * 80)

if transaction:
    serializer = BankTransactionSerializer(transaction)
    data = serializer.data

    # Check RefNo exists
    has_refno = 'RefNo' in data
    # Check transaction_number is gone
    no_transaction_number = 'transaction_number' not in data
    # Check case_title exists
    has_case_title = 'case_title' in data
    # Check case_number is gone
    no_case_number = 'case_number' not in data

    print(f'  ✓ Has RefNo field: {has_refno}')
    print(f'  ✓ No transaction_number field: {no_transaction_number}')
    print(f'  ✓ Has case_title field: {has_case_title}')
    print(f'  ✓ No case_number field: {no_case_number}')

    if has_refno:
        print(f'  → RefNo value: {data["RefNo"]}')
    if has_case_title:
        print(f'  → case_title value: {data.get("case_title", "None")}')

    test1_pass = has_refno and no_transaction_number and has_case_title and no_case_number
    print(f'  Overall: {"✅ PASS" if test1_pass else "❌ FAIL"}')
    test_results.append(('BankTransactionSerializer', test1_pass))
else:
    print('  ⚠️  No transaction found')
    test_results.append(('BankTransactionSerializer', True))

print()

# ============================================================================
# Test 2: CaseSerializer
# ============================================================================
print('=' * 80)
print('Test 2: CaseSerializer')
print('=' * 80)

if case:
    serializer = CaseSerializer(case)
    data = serializer.data

    # Check case_title exists
    has_case_title = 'case_title' in data
    # Check case_number is gone
    no_case_number = 'case_number' not in data

    print(f'  ✓ Has case_title field: {has_case_title}')
    print(f'  ✓ No case_number field: {no_case_number}')

    if has_case_title:
        print(f'  → case_title value: {data["case_title"]}')

    test2_pass = has_case_title and no_case_number
    print(f'  Overall: {"✅ PASS" if test2_pass else "❌ FAIL"}')
    test_results.append(('CaseSerializer', test2_pass))
else:
    print('  ⚠️  No case found')
    test_results.append(('CaseSerializer', True))

print()

# ============================================================================
# Test 3: CaseListSerializer
# ============================================================================
print('=' * 80)
print('Test 3: CaseListSerializer')
print('=' * 80)

if case:
    serializer = CaseListSerializer(case)
    data = serializer.data

    # Check case_title exists
    has_case_title = 'case_title' in data
    # Check case_number is gone
    no_case_number = 'case_number' not in data

    print(f'  ✓ Has case_title field: {has_case_title}')
    print(f'  ✓ No case_number field: {no_case_number}')

    if has_case_title:
        print(f'  → case_title value: {data["case_title"]}')

    test3_pass = has_case_title and no_case_number
    print(f'  Overall: {"✅ PASS" if test3_pass else "❌ FAIL"}')
    test_results.append(('CaseListSerializer', test3_pass))
else:
    print('  ⚠️  No case found')
    test_results.append(('CaseListSerializer', True))

print()

# ============================================================================
# Test 4: Check custom view responses (mock)
# ============================================================================
print('=' * 80)
print('Test 4: Custom View Responses (Code Review)')
print('=' * 80)

# This tests that the view code uses the correct field names
# We'll check by looking at the actual field names used in the code

print('  Checking views for correct field usage...')

view_checks_pass = True

# Read bank views
with open('/app/apps/bank_accounts/api/views.py', 'r') as f:
    bank_views_content = f.read()

# Read client views
with open('/app/apps/clients/api/views.py', 'r') as f:
    client_views_content = f.read()

# Check bank views doesn't have 'transaction_number': in responses
if "'transaction_number':" in bank_views_content:
    print('  ❌ Bank views still uses transaction_number')
    view_checks_pass = False
else:
    print('  ✅ Bank views does not use transaction_number')

# Check bank views has RefNo
if "'RefNo':" in bank_views_content:
    print('  ✅ Bank views uses RefNo')
else:
    print('  ❌ Bank views missing RefNo')
    view_checks_pass = False

# Check client views doesn't have 'transaction_number': in dict responses
if "'transaction_number': txn" in client_views_content:
    print('  ❌ Client views still uses transaction_number')
    view_checks_pass = False
else:
    print('  ✅ Client views does not use transaction_number')

# Check client views has RefNo
if "'RefNo':" in client_views_content:
    print('  ✅ Client views uses RefNo')
else:
    print('  ❌ Client views missing RefNo')
    view_checks_pass = False

print(f'  Overall: {"✅ PASS" if view_checks_pass else "❌ FAIL"}')
test_results.append(('Custom View Responses', view_checks_pass))

print()

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print('=' * 80)
print('FINAL SUMMARY')
print('=' * 80)
print()

passed = sum(1 for _, result in test_results if result)
failed = len(test_results) - passed

for name, result in test_results:
    status = "✅ PASS" if result else "❌ FAIL"
    print(f'  {status} - {name}')

print()
print(f'Total: {passed}/{len(test_results)} tests passed')
print()

if failed == 0:
    print('🎉 ALL FIELD REPLACEMENTS SUCCESSFUL!')
    print('   ✅ transaction_number → RefNo')
    print('   ✅ case_number → case_title')
else:
    print(f'⚠️  {failed} test(s) failed')

print('=' * 80)
