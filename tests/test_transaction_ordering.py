#!/usr/bin/env python
"""
Test Transaction Ordering - Verify Oldest First

Tests all 6 APIs that return multiple transactions to ensure they return
oldest transactions first (ascending date order).
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
from apps.bank_accounts.api.serializers import BankTransactionSerializer
from rest_framework.test import APIRequestFactory
from apps.bank_accounts.api.views import BankAccountViewSet, BankTransactionViewSet
from apps.clients.api.views import CaseViewSet, ClientViewSet
from django.contrib.auth.models import User
from datetime import datetime

print('=' * 80)
print('TRANSACTION ORDERING TEST - OLDEST FIRST')
print('=' * 80)
print()

# Get test data
bank_account = BankAccount.objects.first()
case = Case.objects.filter(bank_transactions__isnull=False).first()
client = Client.objects.filter(bank_transactions__isnull=False).first()

# Create request user
factory = APIRequestFactory()
user = User.objects.first()

def check_ordering(dates, api_name):
    """
    Check if dates are in ascending order (oldest first)
    Returns: (is_correct, message)
    """
    if not dates or len(dates) < 2:
        return True, "✓ Only 1 or no transactions (N/A)"

    # Parse dates (handle MM/DD/YY format)
    parsed_dates = []
    for date_str in dates:
        if date_str:
            try:
                # Try MM/DD/YY format
                if '/' in str(date_str):
                    parsed = datetime.strptime(str(date_str), '%m/%d/%y')
                # Try ISO format
                else:
                    parsed = datetime.strptime(str(date_str), '%Y-%m-%d')
                parsed_dates.append(parsed)
            except:
                return False, f"✗ Could not parse date: {date_str}"

    # Check if sorted (oldest first)
    is_sorted = all(parsed_dates[i] <= parsed_dates[i+1] for i in range(len(parsed_dates)-1))

    if is_sorted:
        first = parsed_dates[0].strftime('%m/%d/%y')
        last = parsed_dates[-1].strftime('%m/%d/%y')
        return True, f"✓ Correct order: {first} → {last} ({len(dates)} transactions)"
    else:
        first = parsed_dates[0].strftime('%m/%d/%y')
        last = parsed_dates[-1].strftime('%m/%d/%y')
        return False, f"✗ Wrong order: {first} → {last} (should be ascending)"

# ============================================================================
# API 1: BankTransactionViewSet (Main List)
# ============================================================================
print('=' * 80)
print('API 1: /api/v1/bank-accounts/bank-transactions/ (Main List)')
print('=' * 80)

request1 = factory.get('/api/v1/bank-accounts/bank-transactions/')
request1.user = user
view1 = BankTransactionViewSet.as_view({'get': 'list'})
response1 = view1(request1)

if response1.data.get('results'):
    dates1 = [t['transaction_date'] for t in response1.data['results'][:10]]
    is_correct1, msg1 = check_ordering(dates1, 'API 1')
    print(f'  {msg1}')
    print(f'  Sample dates: {dates1[:3] if len(dates1) >= 3 else dates1}...')
else:
    is_correct1 = True
    print('  ✓ No transactions returned')

print(f'  Overall: {"✅ PASS" if is_correct1 else "❌ FAIL"}')
print()

# ============================================================================
# API 2: BankAccountViewSet.transactions()
# ============================================================================
print('=' * 80)
print('API 2: /api/v1/bank-accounts/accounts/{id}/transactions/')
print('=' * 80)

request2 = factory.get(f'/api/v1/bank-accounts/accounts/{bank_account.id}/transactions/')
request2.user = user
view2 = BankAccountViewSet.as_view({'get': 'transactions'})
response2 = view2(request2, pk=bank_account.id)

if response2.data.get('transactions'):
    dates2 = [t['transaction_date'] for t in response2.data['transactions'][:10]]
    is_correct2, msg2 = check_ordering(dates2, 'API 2')
    print(f'  {msg2}')
    print(f'  Sample dates: {dates2[:3] if len(dates2) >= 3 else dates2}...')
else:
    is_correct2 = True
    print('  ✓ No transactions returned')

print(f'  Overall: {"✅ PASS" if is_correct2 else "❌ FAIL"}')
print()

# ============================================================================
# API 3: BankAccountViewSet.balance_history()
# ============================================================================
print('=' * 80)
print('API 3: /api/v1/bank-accounts/accounts/{id}/balance_history/')
print('=' * 80)

request3 = factory.get(f'/api/v1/bank-accounts/accounts/{bank_account.id}/balance_history/')
request3.user = user
view3 = BankAccountViewSet.as_view({'get': 'balance_history'})
response3 = view3(request3, pk=bank_account.id)

if response3.data.get('balance_history'):
    dates3 = [item['date'] for item in response3.data['balance_history'][:10]]
    is_correct3, msg3 = check_ordering(dates3, 'API 3')
    print(f'  {msg3}')
    print(f'  Sample dates: {dates3[:3] if len(dates3) >= 3 else dates3}...')
else:
    is_correct3 = True
    print('  ✓ No history returned')

print(f'  Overall: {"✅ PASS" if is_correct3 else "❌ FAIL"}')
print()

# ============================================================================
# API 4: BankTransactionViewSet.missing()
# ============================================================================
print('=' * 80)
print('API 4: /api/v1/bank-accounts/bank-transactions/missing/')
print('=' * 80)

request4 = factory.get('/api/v1/bank-accounts/bank-transactions/missing/')
request4.user = user
view4 = BankTransactionViewSet.as_view({'get': 'missing'})
response4 = view4(request4)

if response4.data.get('missing_checks'):
    dates4 = [t['transaction_date'] for t in response4.data['missing_checks'][:10]]
    is_correct4, msg4 = check_ordering(dates4, 'API 4')
    print(f'  {msg4}')
    print(f'  Sample dates: {dates4[:3] if len(dates4) >= 3 else dates4}...')
else:
    is_correct4 = True
    print('  ✓ No missing checks')

print(f'  Overall: {"✅ PASS" if is_correct4 else "❌ FAIL"}')
print()

# ============================================================================
# API 5: CaseViewSet.transactions()
# ============================================================================
print('=' * 80)
print('API 5: /api/v1/cases/{id}/transactions/')
print('=' * 80)

if case:
    request5 = factory.get(f'/api/v1/cases/{case.id}/transactions/')
    request5.user = user
    view5 = CaseViewSet.as_view({'get': 'transactions'})
    response5 = view5(request5, pk=case.id)

    if response5.data.get('transactions'):
        dates5 = [t['date'] for t in response5.data['transactions'][:10]]
        is_correct5, msg5 = check_ordering(dates5, 'API 5')
        print(f'  {msg5}')
        print(f'  Sample dates: {dates5[:3] if len(dates5) >= 3 else dates5}...')
    else:
        is_correct5 = True
        print('  ✓ No transactions')
else:
    is_correct5 = True
    print('  ✓ No case with transactions found')

print(f'  Overall: {"✅ PASS" if is_correct5 else "❌ FAIL"}')
print()

# ============================================================================
# API 6: ClientViewSet.balance_history()
# ============================================================================
print('=' * 80)
print('API 6: /api/v1/clients/{id}/balance_history/')
print('=' * 80)

if client:
    request6 = factory.get(f'/api/v1/clients/{client.id}/balance_history/')
    request6.user = user
    view6 = ClientViewSet.as_view({'get': 'balance_history'})
    response6 = view6(request6, pk=client.id)

    if response6.data.get('balance_history'):
        dates6 = [item['date'] for item in response6.data['balance_history'][:10]]
        is_correct6, msg6 = check_ordering(dates6, 'API 6')
        print(f'  {msg6}')
        print(f'  Sample dates: {dates6[:3] if len(dates6) >= 3 else dates6}...')
    else:
        is_correct6 = True
        print('  ✓ No balance history')
else:
    is_correct6 = True
    print('  ✓ No client with transactions found')

print(f'  Overall: {"✅ PASS" if is_correct6 else "❌ FAIL"}')
print()

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print('=' * 80)
print('FINAL SUMMARY')
print('=' * 80)
print()

all_results = [
    ('API 1: BankTransactionViewSet (Main List)', is_correct1),
    ('API 2: BankAccountViewSet.transactions()', is_correct2),
    ('API 3: BankAccountViewSet.balance_history()', is_correct3),
    ('API 4: BankTransactionViewSet.missing()', is_correct4),
    ('API 5: CaseViewSet.transactions()', is_correct5),
    ('API 6: ClientViewSet.balance_history()', is_correct6),
]

passed = sum(1 for _, result in all_results if result)
failed = len(all_results) - passed

for name, result in all_results:
    status = "✅ PASS" if result else "❌ FAIL"
    print(f'  {status} - {name}')

print()
print(f'Total: {passed}/{len(all_results)} APIs passed')
print()

if failed == 0:
    print('🎉 ALL APIs NOW RETURN OLDEST FIRST!')
    print('   Transactions are ordered chronologically ✓')
else:
    print(f'⚠️  {failed} API(s) failed ordering check')

print('=' * 80)
