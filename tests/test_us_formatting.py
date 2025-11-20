#!/usr/bin/env python
"""
Test US Formatting for all 10 Bank/Transaction APIs

Verifies:
- Dates: MM/DD/YY
- Money: $XX,XXX.00
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
from rest_framework.test import APIRequestFactory
from apps.bank_accounts.api.views import BankAccountViewSet, BankTransactionViewSet
from apps.clients.api.views import CaseViewSet
from django.contrib.auth.models import User
import re

print('=' * 80)
print('US FORMATTING TEST - ALL 10 APIs')
print('=' * 80)
print()

# Get test data
bank_account = BankAccount.objects.first()
case = Case.objects.first()
transaction = BankTransaction.objects.filter(case__isnull=False).first()

# Create request user
factory = APIRequestFactory()
user = User.objects.first()

def check_date_format(date_str, field_name):
    """Check if date is in MM/DD/YY format"""
    if date_str is None:
        return True, "N/A"

    # MM/DD/YY format
    if re.match(r'^\d{2}/\d{2}/\d{2}$', str(date_str)):
        return True, f"✓ {date_str} (MM/DD/YY)"
    # MM/DD/YY HH:MM AM/PM format
    elif re.match(r'^\d{2}/\d{2}/\d{2} \d{2}:\d{2} [AP]M$', str(date_str)):
        return True, f"✓ {date_str} (MM/DD/YY HH:MM AM/PM)"
    else:
        return False, f"✗ {date_str} (NOT US FORMAT)"

def check_money_format(money_str, field_name):
    """Check if money is in $XX,XXX.00 format"""
    if money_str is None:
        return True, "N/A"

    # $XX,XXX.00 format (with optional negative parentheses)
    if re.match(r'^\$[\d,]+\.\d{2}$', str(money_str)):
        return True, f"✓ {money_str} ($XX,XXX.00)"
    # Negative: ($XX,XXX.00)
    elif re.match(r'^\(\$[\d,]+\.\d{2}\)$', str(money_str)):
        return True, f"✓ {money_str} (negative format)"
    else:
        return False, f"✗ {money_str} (NOT US FORMAT)"

# ============================================================================
# API 1: BankTransactionSerializer
# ============================================================================
print('=' * 80)
print('API 1: /api/v1/bank-accounts/bank-transactions/ (BankTransactionSerializer)')
print('=' * 80)

serializer = BankTransactionSerializer(transaction)
data = serializer.data

print(f'Sample Transaction ID: {transaction.id}')
print()

# Check date fields
date_ok, date_msg = check_date_format(data.get('transaction_date'), 'transaction_date')
print(f'  transaction_date: {date_msg}')

created_ok, created_msg = check_date_format(data.get('created_at'), 'created_at')
print(f'  created_at: {created_msg}')

# Check money field
amount_ok, amount_msg = check_money_format(data.get('amount'), 'amount')
print(f'  amount: {amount_msg}')

api1_pass = date_ok and created_ok and amount_ok
print(f'\n  Overall: {"✅ PASS" if api1_pass else "❌ FAIL"}')
print()

# ============================================================================
# API 2: BankAccountSerializer
# ============================================================================
print('=' * 80)
print('API 2: /api/v1/bank-accounts/accounts/ (BankAccountSerializer)')
print('=' * 80)

ba_serializer = BankAccountSerializer(bank_account)
ba_data = ba_serializer.data

print(f'Sample Bank Account ID: {bank_account.id}')
print()

# Check date fields
created_ok2, created_msg2 = check_date_format(ba_data.get('created_at'), 'created_at')
print(f'  created_at: {created_msg2}')

# Check money fields
tb_ok, tb_msg = check_money_format(ba_data.get('trust_balance'), 'trust_balance')
print(f'  trust_balance: {tb_msg}')

ftb_ok, ftb_msg = check_money_format(ba_data.get('formatted_trust_balance'), 'formatted_trust_balance')
print(f'  formatted_trust_balance: {ftb_msg}')

api2_pass = created_ok2 and tb_ok and ftb_ok
print(f'\n  Overall: {"✅ PASS" if api2_pass else "❌ FAIL"}')
print()

# ============================================================================
# API 3: Bank Account Transactions
# ============================================================================
print('=' * 80)
print('API 3: /api/v1/bank-accounts/accounts/{id}/transactions/')
print('=' * 80)

request3 = factory.get(f'/api/v1/bank-accounts/accounts/{bank_account.id}/transactions/')
request3.user = user
view3 = BankAccountViewSet.as_view({'get': 'transactions'})
response3 = view3(request3, pk=bank_account.id)

cb_ok3, cb_msg3 = check_money_format(response3.data.get('current_balance'), 'current_balance')
print(f'  current_balance: {cb_msg3}')

if response3.data.get('summary'):
    ta_ok3, ta_msg3 = check_money_format(response3.data['summary'].get('total_amount'), 'summary.total_amount')
    print(f'  summary.total_amount: {ta_msg3}')
else:
    ta_ok3 = True

api3_pass = cb_ok3 and ta_ok3
print(f'\n  Overall: {"✅ PASS" if api3_pass else "❌ FAIL"}')
print()

# ============================================================================
# API 4: Balance History
# ============================================================================
print('=' * 80)
print('API 4: /api/v1/bank-accounts/accounts/{id}/balance_history/')
print('=' * 80)

request4 = factory.get(f'/api/v1/bank-accounts/accounts/{bank_account.id}/balance_history/')
request4.user = user
view4 = BankAccountViewSet.as_view({'get': 'balance_history'})
response4 = view4(request4, pk=bank_account.id)

cb_ok4, cb_msg4 = check_money_format(response4.data.get('current_balance'), 'current_balance')
print(f'  current_balance: {cb_msg4}')

if response4.data.get('balance_history'):
    first_item = response4.data['balance_history'][0]
    date_ok4, date_msg4 = check_date_format(first_item.get('date'), 'balance_history[0].date')
    print(f'  balance_history[0].date: {date_msg4}')

    amt_ok4, amt_msg4 = check_money_format(first_item.get('amount'), 'balance_history[0].amount')
    print(f'  balance_history[0].amount: {amt_msg4}')
else:
    date_ok4 = amt_ok4 = True

api4_pass = cb_ok4 and date_ok4 and amt_ok4
print(f'\n  Overall: {"✅ PASS" if api4_pass else "❌ FAIL"}')
print()

# ============================================================================
# API 5: Bank Account Summary
# ============================================================================
print('=' * 80)
print('API 5: /api/v1/bank-accounts/accounts/summary/')
print('=' * 80)

request5 = factory.get('/api/v1/bank-accounts/accounts/summary/')
request5.user = user
view5 = BankAccountViewSet.as_view({'get': 'summary'})
response5 = view5(request5)

tsb_ok5, tsb_msg5 = check_money_format(response5.data.get('total_system_balance'), 'total_system_balance')
print(f'  total_system_balance: {tsb_msg5}')

api5_pass = tsb_ok5
print(f'\n  Overall: {"✅ PASS" if api5_pass else "❌ FAIL"}')
print()

# ============================================================================
# API 6: Transaction Summary
# ============================================================================
print('=' * 80)
print('API 6: /api/v1/bank-accounts/bank-transactions/summary/')
print('=' * 80)

request6 = factory.get('/api/v1/bank-accounts/bank-transactions/summary/')
request6.user = user
view6 = BankTransactionViewSet.as_view({'get': 'summary'})
response6 = view6(request6)

dt_ok6, dt_msg6 = check_money_format(response6.data['deposits'].get('total'), 'deposits.total')
print(f'  deposits.total: {dt_msg6}')

wt_ok6, wt_msg6 = check_money_format(response6.data['withdrawals'].get('total'), 'withdrawals.total')
print(f'  withdrawals.total: {wt_msg6}')

api6_pass = dt_ok6 and wt_ok6
print(f'\n  Overall: {"✅ PASS" if api6_pass else "❌ FAIL"}')
print()

# ============================================================================
# API 7: Missing Transactions
# ============================================================================
print('=' * 80)
print('API 7: /api/v1/bank-accounts/bank-transactions/missing/')
print('=' * 80)

request7 = factory.get('/api/v1/bank-accounts/bank-transactions/missing/')
request7.user = user
view7 = BankTransactionViewSet.as_view({'get': 'missing'})
response7 = view7(request7)

mca_ok7, mca_msg7 = check_money_format(response7.data.get('missing_checks_amount'), 'missing_checks_amount')
print(f'  missing_checks_amount: {mca_msg7}')

api7_pass = mca_ok7
print(f'\n  Overall: {"✅ PASS" if api7_pass else "❌ FAIL"}')
print()

# ============================================================================
# API 8: Audit History
# ============================================================================
print('=' * 80)
print('API 8: /api/v1/bank-accounts/bank-transactions/{id}/audit_history/')
print('=' * 80)

request8 = factory.get(f'/api/v1/bank-accounts/bank-transactions/{transaction.id}/audit_history/')
request8.user = user
view8 = BankTransactionViewSet.as_view({'get': 'audit_history'})
response8 = view8(request8, pk=transaction.id)

if response8.data.get('transaction'):
    txn_date_ok8, txn_date_msg8 = check_date_format(
        response8.data['transaction'].get('transaction_date'),
        'transaction.transaction_date'
    )
    print(f'  transaction.transaction_date: {txn_date_msg8}')

    txn_amt_ok8, txn_amt_msg8 = check_money_format(
        response8.data['transaction'].get('amount'),
        'transaction.amount'
    )
    print(f'  transaction.amount: {txn_amt_msg8}')
else:
    txn_date_ok8 = txn_amt_ok8 = True

api8_pass = txn_date_ok8 and txn_amt_ok8
print(f'\n  Overall: {"✅ PASS" if api8_pass else "❌ FAIL"}')
print()

# ============================================================================
# API 9: Case Transactions
# ============================================================================
print('=' * 80)
print('API 9: /api/v1/cases/{id}/transactions/')
print('=' * 80)

request9 = factory.get(f'/api/v1/cases/{case.id}/transactions/')
request9.user = user
view9 = CaseViewSet.as_view({'get': 'transactions'})
response9 = view9(request9, pk=case.id)

cb_ok9, cb_msg9 = check_money_format(response9.data.get('current_balance'), 'current_balance')
print(f'  current_balance: {cb_msg9}')

if response9.data.get('transactions'):
    first_txn = response9.data['transactions'][0]
    date_ok9, date_msg9 = check_date_format(first_txn.get('date'), 'transactions[0].date')
    print(f'  transactions[0].date: {date_msg9}')

    amt_ok9, amt_msg9 = check_money_format(first_txn.get('amount'), 'transactions[0].amount')
    print(f'  transactions[0].amount: {amt_msg9}')
else:
    date_ok9 = amt_ok9 = True

api9_pass = cb_ok9 and date_ok9 and amt_ok9
print(f'\n  Overall: {"✅ PASS" if api9_pass else "❌ FAIL"}')
print()

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print('=' * 80)
print('FINAL SUMMARY')
print('=' * 80)

all_results = [
    ('API 1: BankTransactionSerializer', api1_pass),
    ('API 2: BankAccountSerializer', api2_pass),
    ('API 3: Bank Account Transactions', api3_pass),
    ('API 4: Balance History', api4_pass),
    ('API 5: Bank Account Summary', api5_pass),
    ('API 6: Transaction Summary', api6_pass),
    ('API 7: Missing Transactions', api7_pass),
    ('API 8: Audit History', api8_pass),
    ('API 9: Case Transactions', api9_pass),
]

passed = sum(1 for _, result in all_results if result)
failed = len(all_results) - passed

print()
for name, result in all_results:
    status = "✅ PASS" if result else "❌ FAIL"
    print(f'  {status} - {name}')

print()
print(f'Total: {passed}/{len(all_results)} APIs passed')
print()

if failed == 0:
    print('🎉 ALL APIs NOW RETURN US FORMAT!')
    print('   - Dates: MM/DD/YY ✓')
    print('   - Money: $XX,XXX.00 ✓')
else:
    print(f'⚠️  {failed} API(s) failed formatting check')

print('=' * 80)
