import os
import sys
import django

sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.clients.models import Case
from apps.bank_accounts.models import BankTransaction
from apps.api.utils.formatters import format_us_date, format_us_money

print('=' * 80)
print('TESTING CASE TRANSACTIONS API ENDPOINT')
print('=' * 80)
print()

# Get Case ID 4
case = Case.objects.get(id=4)
print(f"Case: {case.case_title}")
print(f"Case Balance: {case.get_current_balance()}")
print()

# Get transactions for this case (same query as the API)
transactions_data = BankTransaction.objects.filter(case=case).order_by('transaction_date', 'id')

print(f"Total transactions for case: {transactions_data.count()}")
print()

# Show first 5 transactions with their raw data
print('Raw Transaction Data:')
print('-' * 80)
for txn in transactions_data[:5]:
    print(f"ID: {txn.id}")
    print(f"  Date: {txn.transaction_date}")
    print(f"  Type: {txn.transaction_type}")
    print(f"  Raw Amount: {txn.amount}")
    print(f"  Status: {txn.status}")
    print(f"  Description: {txn.description}")
    print()

# Simulate what the API does
print('=' * 80)
print('SIMULATING API RESPONSE')
print('=' * 80)
print()

transactions = []
for txn in transactions_data:
    # When voided, amount should be $0.00
    amount = format_us_money(0) if txn.status == 'voided' else format_us_money(txn.amount)

    # Get payee from multiple sources
    payee = txn.payee
    if not payee and txn.vendor:
        payee = txn.vendor.vendor_name
    elif not payee and txn.client:
        payee = txn.client.full_name

    transaction_dict = {
        'id': txn.id,
        'RefNo': txn.transaction_number,
        'date': format_us_date(txn.transaction_date),
        'type': txn.transaction_type,
        'amount': amount,
        'description': txn.description,
        'status': txn.status,
        'payee': payee or '',
        'reference_number': txn.reference_number,
        'void_reason': txn.void_reason or '',
        'voided_by': txn.voided_by or '',
        'voided_date': format_us_date(txn.voided_date) if txn.voided_date else None,
    }
    transactions.append(transaction_dict)

# Show first 5 transactions from API response
print('API Response - First 5 Transactions:')
print('-' * 80)
for i, txn in enumerate(transactions[:5], 1):
    print(f"Transaction {i}:")
    print(f"  Date: {txn['date']}")
    print(f"  Type: {txn['type']}")
    print(f"  Amount: {txn['amount']}")
    print(f"  Status: {txn['status']}")
    print(f"  Payee: {txn['payee']}")
    print()

print('=' * 80)
print('CHECKING FOR RUNNING BALANCE CALCULATION')
print('=' * 80)
print()

# The template needs a running balance - let's check if the API provides it
print("NOTE: The API response above does NOT include a 'balance' field!")
print("The frontend template expects both 'amount' and 'balance' fields.")
print()
print("The balance column in the HTML shows $0.00 because there's no 'balance' field in the API response.")
