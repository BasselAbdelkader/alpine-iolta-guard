from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import date, timedelta
from apps.bank_accounts.models import BankAccount, BankTransaction


class Command(BaseCommand):
    help = 'Create demo bank transaction data matching existing transactions (with 2 missing checks)'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Clear existing bank transactions
            BankTransaction.objects.all().delete()
            self.stdout.write("Cleared existing bank transactions")
            
            # Get the bank account
            bank_account = BankAccount.objects.first()
            if not bank_account:
                self.stdout.write(self.style.ERROR("No bank account found. Please create a bank account first."))
                return
            
            # Get all existing transactions
            transactions = BankTransaction.objects.all().order_by('transaction_date')
            
            # List of transactions to SKIP (these will be the unmatched ones)
            unmatched_checks = ['CHECK-1005', 'CHECK-1007']  # These checks won't appear in bank data
            
            # Create bank transactions for each internal transaction (except the unmatched ones)
            bank_transactions_created = 0
            
            for txn in transactions:
                # Skip the unmatched checks
                if txn.reference_number in unmatched_checks:
                    self.stdout.write(f"Skipping {txn.reference_number} - will remain unmatched")
                    continue
                
                # Determine bank transaction type
                if txn.transaction_type == 'DEPOSIT':
                    bank_type = 'DEPOSIT'
                elif txn.transaction_type == 'WITHDRAWAL':
                    bank_type = 'WITHDRAWAL'
                elif txn.transaction_type == 'TRANSFER':
                    bank_type = 'TRANSFER_OUT'
                else:
                    bank_type = 'OTHER'
                
                # Create bank transaction
                post_date = txn.transaction_date + timedelta(days=1)  # Bank usually posts next day
                
                # Generate bank reference
                bank_ref = f"BANK{txn.transaction_date.strftime('%Y%m%d')}{txn.id:03d}"
                
                # Bank description (slightly different from internal description)
                bank_description = self.get_bank_description(txn.description, txn.reference_number)
                
                # Determine check number
                check_num = None
                if txn.reference_number and txn.reference_number.startswith('CHECK-'):
                    check_num = txn.reference_number.replace('CHECK-', '')
                
                bank_transaction = BankTransaction.objects.create(
                    bank_account=bank_account,
                    transaction_date=txn.transaction_date,
                    post_date=post_date,
                    transaction_type=bank_type,
                    amount=txn.amount,
                    description=bank_description,
                    reference_number=txn.reference_number,
                    reference_number=check_num,
                    bank_reference=bank_ref,
                    bank_category=self.get_bank_category(bank_type),
                    status='UNMATCHED',  # Start as unmatched
                    created_by='Demo Data Generator'
                )
                
                bank_transactions_created += 1
                self.stdout.write(f"Created: {bank_transaction}")
            
            # Add some additional bank transactions (fees, interest) that don't match internal transactions
            additional_transactions = [
                {
                    'date': date(2024, 1, 31),
                    'type': 'FEE',
                    'amount': 25.00,
                    'description': 'Monthly Maintenance Fee',
                    'category': 'Service Charges'
                },
                {
                    'date': date(2024, 2, 28),
                    'type': 'FEE',
                    'amount': 25.00,
                    'description': 'Monthly Maintenance Fee',
                    'category': 'Service Charges'
                },
                {
                    'date': date(2024, 3, 31),
                    'type': 'INTEREST',
                    'amount': 150.75,
                    'description': 'Interest Credit',
                    'category': 'Interest Income'
                },
                {
                    'date': date(2024, 4, 30),
                    'type': 'FEE',
                    'amount': 25.00,
                    'description': 'Monthly Maintenance Fee',
                    'category': 'Service Charges'
                },
                {
                    'date': date(2024, 5, 31),
                    'type': 'FEE',
                    'amount': 25.00,
                    'description': 'Monthly Maintenance Fee',
                    'category': 'Service Charges'
                },
                {
                    'date': date(2024, 6, 30),
                    'type': 'INTEREST',
                    'amount': 275.50,
                    'description': 'Interest Credit',
                    'category': 'Interest Income'
                },
                {
                    'date': date(2024, 7, 15),
                    'type': 'FEE',
                    'amount': 15.00,
                    'description': 'Wire Transfer Fee',
                    'category': 'Wire Fees'
                }
            ]
            
            for add_txn in additional_transactions:
                bank_ref = f"BANK{add_txn['date'].strftime('%Y%m%d')}FEE"
                post_date = add_txn['date'] + timedelta(days=1)
                
                BankTransaction.objects.create(
                    bank_account=bank_account,
                    transaction_date=add_txn['date'],
                    post_date=post_date,
                    transaction_type=add_txn['type'],
                    amount=add_txn['amount'],
                    description=add_txn['description'],
                    bank_reference=bank_ref,
                    bank_category=add_txn['category'],
                    status='UNMATCHED',
                    created_by='Demo Data Generator'
                )
                bank_transactions_created += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created {bank_transactions_created} bank transactions\n"
                    f"Unmatched checks: {', '.join(unmatched_checks)}\n"
                    f"Additional bank fees and interest added for reconciliation testing"
                )
            )
    
    def get_bank_description(self, internal_desc, ref_num):
        """Convert internal description to bank-style description"""
        bank_descriptions = {
            'Opening Balance': 'OPENING BALANCE',
            'Initial settlement - Workers Comp Case': 'WIRE TRANSFER IN - SETTLEMENT',
            'Medical bills payment': 'CHECK PAYMENT',
            'Insurance settlement - Auto Accident': 'CHECK DEPOSIT',
            'Client settlement payment': 'CHECK PAYMENT',
            'Medical malpractice settlement': 'WIRE TRANSFER IN',
            'Attorney fees': 'CHECK PAYMENT',
            'Premises liability settlement': 'CHECK DEPOSIT',
            'Expert witness fees': 'CHECK PAYMENT',
            'Dog bite settlement': 'CHECK DEPOSIT',
            'Multi-vehicle accident settlement': 'WIRE TRANSFER IN',
            'Medical treatment costs': 'CHECK PAYMENT',
            'Client final settlement': 'CHECK PAYMENT',
            'Product liability settlement': 'CHECK DEPOSIT',
            'Court filing fees': 'CHECK PAYMENT'
        }
        
        # Try exact match first
        if internal_desc in bank_descriptions:
            return bank_descriptions[internal_desc]
        
        # Generate generic bank description based on reference
        if ref_num:
            if ref_num.startswith('CHECK-'):
                return 'CHECK PAYMENT' if internal_desc and 'payment' in internal_desc.lower() else 'CHECK DEPOSIT'
            elif ref_num.startswith('WIRE-'):
                return 'WIRE TRANSFER IN' if internal_desc and 'settlement' in internal_desc.lower() else 'WIRE TRANSFER'
        
        return 'MISC TRANSACTION'
    
    def get_bank_category(self, transaction_type):
        """Get bank category based on transaction type"""
        categories = {
            'DEPOSIT': 'Deposits',
            'WITHDRAWAL': 'Payments',
            'TRANSFER_IN': 'Transfers',
            'TRANSFER_OUT': 'Transfers',
            'FEE': 'Service Charges',
            'INTEREST': 'Interest Income',
            'OTHER': 'Miscellaneous'
        }
        return categories.get(transaction_type, 'Miscellaneous')