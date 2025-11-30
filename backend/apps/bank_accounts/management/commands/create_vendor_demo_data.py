from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import date, timedelta
from apps.bank_accounts.models import BankAccount, BankTransaction
from apps.vendors.models import Vendor
from apps.clients.models import Client, Case
import random


class Command(BaseCommand):
    help = 'Create demo transactions to showcase vendor payment register feature'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Get the bank account
            bank_account = BankAccount.objects.first()
            if not bank_account:
                self.stdout.write(self.style.ERROR("No bank account found. Please create a bank account first."))
                return

            # Get existing vendors and clients
            vendors = list(Vendor.objects.filter(is_active=True))
            clients = list(Client.objects.filter(is_active=True))
            cases = list(Case.objects.filter(is_active=True))

            if not vendors:
                self.stdout.write(self.style.ERROR("No vendors found. Please create vendors first."))
                return

            if not clients or not cases:
                self.stdout.write(self.style.ERROR("No clients or cases found. Please create clients and cases first."))
                return

            # Create lots of vendor payment transactions
            self.stdout.write("Creating vendor payment transactions...")

            # Track transaction count
            created_count = 0

            # Create payments for each vendor (multiple payments per vendor)
            for vendor in vendors:
                # Create 3-8 payments per vendor to showcase the feature
                num_payments = random.randint(3, 8)

                for i in range(num_payments):
                    # Random case and client
                    case = random.choice(cases)
                    client = case.client

                    # Random payment amount between $500 - $15,000
                    amount = random.uniform(500, 15000)
                    amount = round(amount, 2)

                    # Random date in the last 6 months
                    days_back = random.randint(1, 180)
                    txn_date = date.today() - timedelta(days=days_back)

                    # Payment descriptions
                    descriptions = [
                        f"Medical services - {vendor.vendor_name}",
                        f"Expert witness fees - {vendor.vendor_name}",
                        f"Professional services - {vendor.vendor_name}",
                        f"Medical records request - {vendor.vendor_name}",
                        f"Treatment costs - {vendor.vendor_name}",
                        f"Consultation fees - {vendor.vendor_name}",
                        f"Imaging services - {vendor.vendor_name}",
                        f"Physical therapy - {vendor.vendor_name}",
                    ]

                    description = random.choice(descriptions)

                    # Create transaction with PAYEE field (to showcase the feature)
                    # Some transactions will have vendor FK, others will only have payee name
                    use_vendor_fk = random.choice([True, False])

                    transaction_data = {
                        'bank_account': bank_account,
                        'transaction_type': 'WITHDRAWAL',
                        'transaction_date': txn_date,
                        'amount': amount,
                        'description': description,
                        'client': client,
                        'case': case,
                        'payee': vendor.vendor_name,  # ALWAYS set payee name
                        'item_type': 'VENDOR_PAYMENT',
                        'status': random.choice(['pending', 'cleared']),
                        'memo': f"Payment to {vendor.vendor_name} for case {case.case_number}",
                    }

                    # Sometimes set vendor FK, sometimes don't (to test both scenarios)
                    if use_vendor_fk:
                        transaction_data['vendor'] = vendor

                    # Set cleared date if cleared
                    if transaction_data'status':
                        transaction_data['cleared_date'] = txn_date + timedelta(days=random.randint(1, 5))

                    # Create the transaction
                    BankTransaction.objects.create(**transaction_data)
                    created_count += 1

                    self.stdout.write(f"Created payment #{created_count}: ${amount:,.2f} to {vendor.vendor_name}")

            # Create some additional transactions with common vendor names (to test name matching)
            common_vendors = ["Dr. Smith", "ABC Medical", "Legal Services Inc", "Expert Witness LLC"]

            for vendor_name in common_vendors:
                # Create 2-4 payments for each common vendor name
                num_payments = random.randint(2, 4)

                for i in range(num_payments):
                    case = random.choice(cases)
                    client = case.client
                    amount = random.uniform(1000, 8000)
                    amount = round(amount, 2)

                    days_back = random.randint(1, 120)
                    txn_date = date.today() - timedelta(days=days_back)

                    # Create transaction with ONLY payee name (no vendor FK)
                    BankTransaction.objects.create(
                        bank_account=bank_account,
                        transaction_type='WITHDRAWAL',
                        transaction_date=txn_date,
                        amount=amount,
                        description=f"Professional services - {vendor_name}",
                        client=client,
                        case=case,
                        payee=vendor_name,  # Only payee name, no vendor FK
                        item_type='VENDOR_PAYMENT',
                        status=random.choice(['pending', 'cleared']),
                        memo=f"Payment to {vendor_name}",
                    )
                    created_count += 1

                    self.stdout.write(f"Created payment #{created_count}: ${amount:,.2f} to {vendor_name} (payee only)")

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created {created_count} vendor payment transactions!\n"
                    f"This showcases the vendor payment register feature:\n"
                    f"- Some transactions have vendor FK + payee name\n"
                    f"- Some transactions have only payee name\n"
                    f"- All will appear in the respective vendor's payment register\n"
                    f"Visit vendor detail pages to see the payment registers!"
                )
            )