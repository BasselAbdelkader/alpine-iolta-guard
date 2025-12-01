from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import date, timedelta
from apps.bank_accounts.models import BankAccount, BankTransaction
from apps.vendors.models import Vendor, VendorType
from apps.clients.models import Client, Case
from apps.settlements.models import Settlement
import random
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create comprehensive IOLTA insurance program data with positive balances'

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write("🏦 Creating IOLTA Insurance Program Data...")

            # Get or create bank account
            bank_account, created = BankAccount.objects.get_or_create(
                account_number='TRUST-2025-001',
                defaults={
                    'bank_name': 'First National Trust Bank',
                    'bank_address': '123 Financial District, New York, NY 10004',
                    'account_name': 'IOLTA Trust Account - Insurance Division',
                    'routing_number': '021000021',
                    'account_type': 'Trust Account',
                    'opening_balance': Decimal('2500000.00'),  # $2.5M opening balance
                    'is_active': True
                }
            )
            self.stdout.write(f"✅ Bank Account: {bank_account.account_name}")

            # Create vendor types
            vendor_types_data = [
                'Medical Provider', 'Insurance Company', 'Legal Services',
                'Expert Witness', 'Investigation Services', 'Court Services',
                'Physical Therapy', 'Imaging Services', 'Laboratory Services'
            ]

            vendor_types = {}
            for vt_name in vendor_types_data:
                vt, created = VendorType.objects.get_or_create(
                    name=vt_name,
                    defaults={'description': f'{vt_name} for insurance cases', 'is_active': True}
                )
                vendor_types[vt_name] = vt

            # Create insurance-related vendors
            vendors_data = [
                # Medical Providers
                ('Metropolitan General Hospital', 'Medical Provider', 'Dr. Sarah Johnson', 'sarah.johnson@metrohealth.com', '(555) 123-4567'),
                ('Advanced Orthopedic Center', 'Medical Provider', 'Dr. Michael Chen', 'mchen@orthoadvanced.com', '(555) 234-5678'),
                ('City Physical Therapy', 'Physical Therapy', 'Lisa Rodriguez PT', 'lrodriguez@citypt.com', '(555) 345-6789'),
                ('Premier Imaging Solutions', 'Imaging Services', 'Robert Davis', 'rdavis@premierimaging.com', '(555) 456-7890'),
                ('Comprehensive Medical Labs', 'Laboratory Services', 'Jennifer Wong', 'jwong@compmedlabs.com', '(555) 567-8901'),

                # Insurance Companies
                ('State Farm Insurance', 'Insurance Company', 'Mark Thompson', 'mthompson@statefarm.com', '(555) 678-9012'),
                ('Liberty Mutual Group', 'Insurance Company', 'Amanda Garcia', 'agarcia@libertymutual.com', '(555) 789-0123'),
                ('Progressive Insurance', 'Insurance Company', 'David Wilson', 'dwilson@progressive.com', '(555) 890-1234'),
                ('Allstate Corporation', 'Insurance Company', 'Michelle Lee', 'mlee@allstate.com', '(555) 901-2345'),

                # Legal & Professional Services
                ('Expert Witness Associates', 'Expert Witness', 'Dr. James Parker', 'jparker@expertwitness.com', '(555) 012-3456'),
                ('Metropolitan Investigation Services', 'Investigation Services', 'Carol Stevens', 'cstevens@metroinvestigation.com', '(555) 123-4567'),
                ('Superior Court Services', 'Court Services', 'Brian Martinez', 'bmartinez@courtservices.com', '(555) 234-5678'),
                ('Legal Document Services Inc', 'Legal Services', 'Patricia Brown', 'pbrown@legaldocs.com', '(555) 345-6789'),

                # Additional Medical
                ('Neurological Associates', 'Medical Provider', 'Dr. Susan Taylor', 'staylor@neuroassoc.com', '(555) 456-7890'),
                ('Pain Management Clinic', 'Medical Provider', 'Dr. Kevin Moore', 'kmoore@painmanagement.com', '(555) 567-8901'),
            ]

            vendors = {}
            for vendor_name, vt_name, contact, email, phone in vendors_data:
                vendor = Vendor.objects.create(
                    vendor_name=vendor_name,
                    vendor_type=vendor_types[vt_name],
                    contact_person=contact,
                    email=email,
                    phone=phone,
                    address=f'{random.randint(100, 9999)} {random.choice(["Main St", "Oak Ave", "Elm Dr", "Pine Rd", "Maple Blvd"])}',
                    city=random.choice(['New York', 'Chicago', 'Los Angeles', 'Houston', 'Phoenix']),
                    state=random.choice(['NY', 'IL', 'CA', 'TX', 'AZ']),
                    zip_code=f'{random.randint(10000, 99999)}',
                    tax_id=f'{random.randint(10, 99)}-{random.randint(1000000, 9999999)}',
                    is_active=True
                )
                vendors[vendor_name] = vendor

            self.stdout.write(f"✅ Created {len(vendors)} insurance vendors")

            # Create insurance clients with realistic names
            clients_data = [
                ('John', 'Anderson', 'john.anderson@email.com', '(555) 111-2222'),
                ('Maria', 'Rodriguez', 'maria.rodriguez@email.com', '(555) 222-3333'),
                ('William', 'Johnson', 'william.johnson@email.com', '(555) 333-4444'),
                ('Jennifer', 'Davis', 'jennifer.davis@email.com', '(555) 444-5555'),
                ('Michael', 'Wilson', 'michael.wilson@email.com', '(555) 555-6666'),
                ('Lisa', 'Martinez', 'lisa.martinez@email.com', '(555) 666-7777'),
                ('David', 'Garcia', 'david.garcia@email.com', '(555) 777-8888'),
                ('Sarah', 'Brown', 'sarah.brown@email.com', '(555) 888-9999'),
                ('Robert', 'Jones', 'robert.jones@email.com', '(555) 999-0000'),
                ('Emily', 'Miller', 'emily.miller@email.com', '(555) 000-1111'),
                ('Christopher', 'Taylor', 'christopher.taylor@email.com', '(555) 111-0000'),
                ('Ashley', 'Thomas', 'ashley.thomas@email.com', '(555) 222-0000'),
                ('Matthew', 'Moore', 'matthew.moore@email.com', '(555) 333-0000'),
                ('Jessica', 'Lee', 'jessica.lee@email.com', '(555) 444-0000'),
                ('Daniel', 'Clark', 'daniel.clark@email.com', '(555) 555-0000'),
                ('Amanda', 'Lewis', 'amanda.lewis@email.com', '(555) 666-0000'),
                ('James', 'Walker', 'james.walker@email.com', '(555) 777-0000'),
                ('Stephanie', 'Hall', 'stephanie.hall@email.com', '(555) 888-0000'),
                ('Andrew', 'Allen', 'andrew.allen@email.com', '(555) 999-0000'),
                ('Nicole', 'Young', 'nicole.young@email.com', '(555) 000-2222'),
            ]

            clients = []
            for first_name, last_name, email, phone in clients_data:
                client = Client.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=phone,
                    address=f'{random.randint(100, 9999)} {random.choice(["Oak Street", "Elm Avenue", "Pine Drive", "Maple Road", "Cedar Lane"])}',
                    city=random.choice(['Brooklyn', 'Manhattan', 'Queens', 'Bronx', 'Staten Island']),
                    state='NY',
                    zip_code=f'1{random.randint(1000, 9999)}',
                    trust_account_status='ACTIVE_WITH_FUNDS',
                    is_active=True
                )
                clients.append(client)

            self.stdout.write(f"✅ Created {len(clients)} insurance clients")

            # Create active insurance cases
            case_types = [
                'Auto Accident - Rear End Collision',
                'Auto Accident - Side Impact',
                'Auto Accident - Head-On Collision',
                'Slip and Fall - Commercial Property',
                'Slip and Fall - Residential Property',
                'Medical Malpractice - Surgical Error',
                'Medical Malpractice - Misdiagnosis',
                'Product Liability - Defective Equipment',
                'Product Liability - Pharmaceutical',
                'Premises Liability - Inadequate Security',
                'Workers Compensation - Construction Accident',
                'Workers Compensation - Repetitive Injury',
                'Professional Liability - Legal Malpractice',
                'Professional Liability - Accounting Error',
                'Personal Injury - Dog Bite',
                'Personal Injury - Assault',
                'Property Damage - Fire Loss',
                'Property Damage - Water Damage',
                'Wrongful Death - Motor Vehicle',
                'Wrongful Death - Medical Negligence',
            ]

            cases = []
            for i, client in enumerate(clients):
                case_title = random.choice(case_types)
                case_amount = Decimal(str(random.uniform(25000, 500000))).quantize(Decimal('0.01'))

                case = Case.objects.create(
                    case_title=f"{case_title} - {client.last_name}",
                    client=client,
                    case_description=f"Insurance claim case involving {case_title.lower()} resulting in injuries and damages.",
                    case_amount=case_amount,
                    case_status='Open',
                    opened_date=date.today() - timedelta(days=random.randint(30, 365)),
                    is_active=True
                )
                cases.append(case)

            self.stdout.write(f"✅ Created {len(cases)} active insurance cases")

            # Create trust account transactions ensuring positive balances
            self.stdout.write("💰 Creating trust account transactions...")

            total_deposits = Decimal('0')
            total_withdrawals = Decimal('0')

            # Create initial deposits for each case (80% of case amount)
            for case in cases:
                deposit_amount = (case.case_amount * Decimal('0.8')).quantize(Decimal('0.01'))
                deposit_date = case.opened_date + timedelta(days=random.randint(1, 15))

                deposit = BankTransaction.objects.create(
                    bank_account=bank_account,
                    transaction_type='DEPOSIT',
                    transaction_date=deposit_date,
                    amount=deposit_amount,
                    description=f'Insurance settlement deposit - {case.case_title}',
                    client=case.client,
                    case=case,
                    payee='Insurance Settlement Fund',
                    item_type='CLIENT_DEPOSIT',
                    status='cleared',
                    cleared_date=deposit_date,
                    memo=f'Initial settlement deposit for case {case.case_number}'
                )
                total_deposits += deposit_amount

            # Create vendor payments (controlled to maintain positive balances)
            payment_count = 0
            for case in cases:
                case_balance = case.get_current_balance()

                # Create 2-5 vendor payments per case, but limit to 60% of case balance
                num_payments = random.randint(2, 5)
                max_total_payments = case_balance * Decimal('0.6')
                payment_per_vendor = max_total_payments / num_payments

                case_vendors = random.sample(list(vendors.values()), min(num_payments, len(vendors)))

                for vendor in case_vendors:
                    payment_amount = (payment_per_vendor * Decimal(str(random.uniform(0.5, 1.5)))).quantize(Decimal('0.01'))

                    # Ensure we don't exceed case balance
                    if payment_amount > case.get_current_balance():
                        payment_amount = case.get_current_balance() * Decimal('0.3')

                    if payment_amount > 100:  # Only create meaningful payments
                        payment_date = case.opened_date + timedelta(days=random.randint(20, 200))

                        payment = BankTransaction.objects.create(
                            bank_account=bank_account,
                            transaction_type='WITHDRAWAL',
                            transaction_date=payment_date,
                            amount=payment_amount,
                            description=f'Payment to {vendor.vendor_name} for {case.case_title}',
                            client=case.client,
                            case=case,
                            vendor=vendor,
                            payee=vendor.vendor_name,
                            item_type='VENDOR_PAYMENT',
                            status='cleared',
                            cleared_date=payment_date,
                            memo=f'Medical/professional services for case {case.case_number}'
                        )
                        total_withdrawals += payment_amount
                        payment_count += 1

            self.stdout.write(f"✅ Created {payment_count} vendor payments")

            # Create additional deposits to ensure all accounts remain positive
            additional_deposits = 0
            for client in clients:
                current_balance = client.get_current_balance()
                if current_balance < 5000:  # Ensure minimum $5k balance
                    additional_amount = Decimal(str(random.uniform(10000, 50000))).quantize(Decimal('0.01'))
                    additional_date = date.today() - timedelta(days=random.randint(1, 30))

                    # Find a case for this client
                    client_case = cases[clients.index(client)]

                    additional_deposit = BankTransaction.objects.create(
                        bank_account=bank_account,
                        transaction_type='DEPOSIT',
                        transaction_date=additional_date,
                        amount=additional_amount,
                        description=f'Additional insurance payment - {client_case.case_title}',
                        client=client,
                        case=client_case,
                        payee='Insurance Additional Payment',
                        item_type='CLIENT_DEPOSIT',
                        status='cleared',
                        cleared_date=additional_date,
                        memo=f'Supplemental payment for case {client_case.case_number}'
                    )
                    total_deposits += additional_amount
                    additional_deposits += 1

            if additional_deposits > 0:
                self.stdout.write(f"✅ Created {additional_deposits} additional deposits to ensure positive balances")

            # Final verification
            self.stdout.write("\n📊 Final Balance Verification:")
            all_positive = True
            for client in clients:
                balance = client.get_current_balance()
                if balance <= 0:
                    all_positive = False
                    self.stdout.write(f"❌ {client.full_name}: ${balance:,.2f}")
                else:
                    self.stdout.write(f"✅ {client.full_name}: ${balance:,.2f}")

            bank_balance = bank_account.get_current_balance()

            self.stdout.write(f"\n🏦 Bank Account Balance: ${bank_balance:,.2f}")
            self.stdout.write(f"💰 Total Deposits: ${total_deposits:,.2f}")
            self.stdout.write(f"💸 Total Withdrawals: ${total_withdrawals:,.2f}")
            self.stdout.write(f"📈 Net Balance: ${total_deposits - total_withdrawals:,.2f}")

            if all_positive:
                self.stdout.write(self.style.SUCCESS("\n🎉 SUCCESS: All client accounts have positive balances!"))
                self.stdout.write(self.style.SUCCESS("🏆 IOLTA Insurance Program data created successfully!"))
                self.stdout.write(self.style.SUCCESS(f"📋 Summary: {len(clients)} clients, {len(cases)} active cases, {len(vendors)} vendors"))
            else:
                self.stdout.write(self.style.WARNING("\n⚠️  Some accounts have negative balances - additional deposits may be needed"))