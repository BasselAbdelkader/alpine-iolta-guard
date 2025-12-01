from django.core.management.base import BaseCommand
from django.db import transaction
from apps.bank_accounts.models import BankTransaction


class Command(BaseCommand):
    help = 'Match bank transactions to internal transactions (except for the 2 missing checks)'

    def handle(self, *args, **options):
        with transaction.atomic():
            matched_count = 0
            unmatched_count = 0
            
            # Get all bank transactions
            bank_transactions = BankTransaction.objects.all()
            
            for bank_txn in bank_transactions:
                # Skip bank-only transactions (fees, interest)
                if bank_txn.transaction_type in ['FEE', 'INTEREST']:
                    self.stdout.write(f"Skipping bank-only transaction: {bank_txn.description}")
                    unmatched_count += 1
                    continue
                
                # Try to match by reference number first
                internal_txn = None
                if bank_txn.reference_number:
                    internal_txn = BankTransaction.objects.filter(
                        reference_number=bank_txn.reference_number,
                        transaction_date=bank_txn.transaction_date,
                        amount=bank_txn.amount
                    ).first()
                
                # If no match by reference, try matching by date, amount, and type
                if not internal_txn:
                    # Convert bank transaction type to internal transaction type
                    internal_type = self.get_internal_type(bank_txn.transaction_type)
                    
                    internal_txn = BankTransaction.objects.filter(
                        transaction_date=bank_txn.transaction_date,
                        amount=bank_txn.amount,
                        transaction_type=internal_type
                    ).first()
                
                if internal_txn:
                    # Match found - update bank transaction
                    bank_txn.matched_transaction = internal_txn
                    bank_txn.status = 'MATCHED'
                    bank_txn.save()
                    
                    matched_count += 1
                    self.stdout.write(f"✅ Matched: {bank_txn.description} -> {internal_txn.description}")
                else:
                    # No match found - keep as unmatched
                    self.stdout.write(f"❌ Unmatched: {bank_txn.description} ({bank_txn.reference_number})")
                    unmatched_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nMatching completed:\n"
                    f"✅ Matched: {matched_count} transactions\n"
                    f"❌ Unmatched: {unmatched_count} transactions\n"
                    f"\nUnmatched should include:\n"
                    f"- 2 missing checks (CHECK-1005, CHECK-1007)\n"
                    f"- Bank fees and interest transactions"
                )
            )
    
    def get_internal_type(self, bank_type):
        """Convert bank transaction type to internal transaction type"""
        mapping = {
            'DEPOSIT': 'DEPOSIT',
            'WITHDRAWAL': 'WITHDRAWAL',
            'TRANSFER_IN': 'DEPOSIT',
            'TRANSFER_OUT': 'WITHDRAWAL',
            'FEE': 'WITHDRAWAL',
            'INTEREST': 'DEPOSIT',
            'OTHER': 'DEPOSIT'
        }
        return mapping.get(bank_type, 'DEPOSIT')