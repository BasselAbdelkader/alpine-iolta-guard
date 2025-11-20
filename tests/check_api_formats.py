#!/usr/bin/env python
"""
Check current date and money formats returned by all transaction APIs
"""
import os
import sys
import django
import json

# Setup Django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.bank_accounts.models import BankAccount, BankTransaction
from apps.clients.models import Case
from apps.bank_accounts.api.serializers import BankTransactionSerializer, BankAccountSerializer
from rest_framework.test import APIRequestFactory
from apps.bank_accounts.api.views import BankAccountViewSet, BankTransactionViewSet
from apps.clients.api.views import CaseViewSet

print('=' * 80)
print('API DATA FORMAT ANALYSIS')
print('=' * 80)
print()

# Get sample data
bank_account = BankAccount.objects.first()
case = Case.objects.first()
transaction = BankTransaction.objects.filter(case__isnull=False).first()

print('Sample Transaction from Database:')
print(f'  ID: {transaction.id}')
print(f'  Date (raw): {transaction.transaction_date}')
print(f'  Amount (raw): {transaction.amount}')
print(f'  Type: {type(transaction.amount)}')
print()

# ============================================================================
# API 1: Bank Transaction List - /api/v1/bank-accounts/bank-transactions/
# ============================================================================
print('=' * 80)
print('API 1: /api/v1/bank-accounts/bank-transactions/ (BankTransactionSerializer)')
print('=' * 80)

serializer = BankTransactionSerializer(transaction)
print('Serializer Output:')
print(json.dumps(serializer.data, indent=2, default=str))
print()
print('Format Check:')
print(f'  transaction_date: {serializer.data.get("transaction_date")} (Type: {type(serializer.data.get("transaction_date"))})')
print(f'  amount: {serializer.data.get("amount")} (Type: {type(serializer.data.get("amount"))})')
print()

# ============================================================================
# API 2: Case Transactions - /api/v1/cases/{id}/transactions/
# ============================================================================
print('=' * 80)
print('API 2: /api/v1/cases/{id}/transactions/ (Custom Response)')
print('=' * 80)

factory = APIRequestFactory()
request = factory.get(f'/api/v1/cases/{case.id}/transactions/')
view = CaseViewSet.as_view({'get': 'transactions'})

# Mock the request object
from django.contrib.auth.models import AnonymousUser
request.user = AnonymousUser()

# Get the response
response = view(request, pk=case.id)
print('Response Data Sample (first transaction):')
if response.data.get('transactions'):
    first_txn = response.data['transactions'][0]
    print(json.dumps(first_txn, indent=2, default=str))
    print()
    print('Format Check:')
    print(f'  date: {first_txn.get("date")} (Type: {type(first_txn.get("date"))})')
    print(f'  amount: {first_txn.get("amount")} (Type: {type(first_txn.get("amount"))})')
    print(f'  current_balance: {response.data.get("current_balance")}')
print()

# ============================================================================
# API 3: Bank Account Transactions - /api/v1/bank-accounts/accounts/{id}/transactions/
# ============================================================================
print('=' * 80)
print('API 3: /api/v1/bank-accounts/accounts/{id}/transactions/')
print('=' * 80)

request2 = factory.get(f'/api/v1/bank-accounts/accounts/{bank_account.id}/transactions/')
request2.user = AnonymousUser()
view2 = BankAccountViewSet.as_view({'get': 'transactions'})

response2 = view2(request2, pk=bank_account.id)
print('Response Data Sample (first transaction):')
if response2.data.get('transactions'):
    first_txn2 = response2.data['transactions'][0]
    print(json.dumps(first_txn2, indent=2, default=str))
    print()
    print('Format Check:')
    print(f'  transaction_date: {first_txn2.get("transaction_date")}')
    print(f'  amount: {first_txn2.get("amount")}')
    print(f'  current_balance: {response2.data.get("current_balance")}')
    print(f'  summary.total_amount: {response2.data.get("summary", {}).get("total_amount")}')
print()

# ============================================================================
# API 4: Bank Account List - /api/v1/bank-accounts/accounts/
# ============================================================================
print('=' * 80)
print('API 4: /api/v1/bank-accounts/accounts/ (BankAccountSerializer)')
print('=' * 80)

ba_serializer = BankAccountSerializer(bank_account)
print('Serializer Output (relevant fields):')
print(f'  trust_balance: {ba_serializer.data.get("trust_balance")}')
print(f'  opening_balance: {ba_serializer.data.get("opening_balance")}')
print(f'  formatted_trust_balance: {ba_serializer.data.get("formatted_trust_balance")}')
print(f'  created_at: {ba_serializer.data.get("created_at")}')
print()

# ============================================================================
# API 5: Balance History - /api/v1/bank-accounts/accounts/{id}/balance_history/
# ============================================================================
print('=' * 80)
print('API 5: /api/v1/bank-accounts/accounts/{id}/balance_history/')
print('=' * 80)

request3 = factory.get(f'/api/v1/bank-accounts/accounts/{bank_account.id}/balance_history/')
request3.user = AnonymousUser()
view3 = BankAccountViewSet.as_view({'get': 'balance_history'})

response3 = view3(request3, pk=bank_account.id)
print('Response Data Sample (first 2 history items):')
if response3.data.get('balance_history'):
    for i, item in enumerate(response3.data['balance_history'][:2]):
        print(f'\nHistory Item {i+1}:')
        print(json.dumps(item, indent=2, default=str))
    print()
    print('Format Check:')
    first_item = response3.data['balance_history'][0]
    print(f'  date: {first_item.get("date")} (Type: {type(first_item.get("date"))})')
    print(f'  amount: {first_item.get("amount")}')
    print(f'  running_balance: {first_item.get("running_balance")}')
print()

# ============================================================================
# API 6: Transaction Summary - /api/v1/bank-accounts/bank-transactions/summary/
# ============================================================================
print('=' * 80)
print('API 6: /api/v1/bank-accounts/bank-transactions/summary/')
print('=' * 80)

request4 = factory.get('/api/v1/bank-accounts/bank-transactions/summary/')
request4.user = AnonymousUser()
view4 = BankTransactionViewSet.as_view({'get': 'summary'})

response4 = view4(request4)
print('Summary Response:')
print(json.dumps(response4.data, indent=2, default=str))
print()

# ============================================================================
# API 7: Audit History - /api/v1/bank-accounts/bank-transactions/{id}/audit_history/
# ============================================================================
print('=' * 80)
print('API 7: /api/v1/bank-accounts/bank-transactions/{id}/audit_history/')
print('=' * 80)

request5 = factory.get(f'/api/v1/bank-accounts/bank-transactions/{transaction.id}/audit_history/')
request5.user = AnonymousUser()
view5 = BankTransactionViewSet.as_view({'get': 'audit_history'})

response5 = view5(request5, pk=transaction.id)
print('Audit History Response (transaction info):')
txn_info = response5.data.get('transaction', {})
print(f'  transaction_date: {txn_info.get("transaction_date")}')
print(f'  amount: {txn_info.get("amount")}')
print()

print('=' * 80)
print('SUMMARY: CURRENT FORMATS')
print('=' * 80)
print()
print('DATES:')
print('  - BankTransactionSerializer.transaction_date: ISO format (YYYY-MM-DD)')
print('  - Case transactions API date: ISO format (YYYY-MM-DD)')
print('  - Audit history action_date: MM/DD/YYYY HH:MM AM/PM (US format!) ✓')
print('  - Audit history transaction_date: MM/DD/YYYY (US format!) ✓')
print()
print('MONEY:')
print('  - BankTransactionSerializer.amount: Plain decimal string (e.g., "100.00")')
print('  - Case transactions amount: Plain decimal string (e.g., "100.00")')
print('  - BankAccountSerializer.trust_balance: Decimal object')
print('  - BankAccountSerializer.formatted_trust_balance: "X,XXX.XX" (comma, no $)')
print('  - Balance history amounts: Plain decimal string (e.g., "100.00")')
print()
print('=' * 80)
