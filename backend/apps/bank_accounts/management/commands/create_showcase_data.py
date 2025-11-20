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
    help = 'Create IOLTA Insurance data showcasing Issues and Warnings dashboard features'

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write("🏦 Creating IOLTA Insurance Showcase Data...")
            self.stdout.write("🎯 Targeting: Issues and Warnings Dashboard Features")

            # Create single bank account with proper opening balance
            bank_account = BankAccount.objects.create(
                account_number='IOLTA-TRUST-2025',
                bank_name='Metropolitan Trust Bank',
                bank_address='456 Financial Plaza, New York, NY 10005',
                account_name='IOLTA Trust Account - Insurance Claims Division',
                routing_number='021000322',
                account_type='Trust Account',
                opening_balance=Decimal('5000000.00'),  # $5M opening balance
                is_active=True
            )
            self.stdout.write(f"✅ Single Bank Account Created: {bank_account.account_name}")

            # Create vendor types for insurance program
            vendor_types_data = [
                ('Medical Provider', 'Hospitals, clinics, and medical professionals'),
                ('Insurance Company', 'Auto and liability insurance carriers'),
                ('Legal Services', 'Attorneys and legal support services'),
                ('Expert Witness', 'Professional expert testimony services'),
                ('Investigation Services', 'Private investigation and accident reconstruction'),
                ('Court Services', 'Court reporters, process servers, filing services'),
                ('Physical Therapy', 'Rehabilitation and physical therapy providers'),
                ('Imaging Services', 'MRI, CT, X-ray diagnostic services'),
                ('Laboratory Services', 'Medical testing and laboratory analysis'),
                ('Automotive Services', 'Vehicle repair and towing services')
            ]

            vendor_types = {}
            for vt_name, vt_desc in vendor_types_data:
                vt = VendorType.objects.create(
                    name=vt_name,
                    description=vt_desc,
                    is_active=True
                )
                vendor_types[vt_name] = vt

            # Create comprehensive vendor list
            vendors_data = [
                # Medical Providers
                ('St. Mary\'s General Hospital', 'Medical Provider', 'Dr. Patricia Wilson', 'pwilson@stmarys.org', '(555) 101-1001'),
                ('Advanced Spine & Orthopedic Clinic', 'Medical Provider', 'Dr. Michael Rodriguez', 'mrodriguez@spineclinic.com', '(555) 102-1002'),
                ('Downtown Physical Medicine', 'Medical Provider', 'Dr. Sarah Kim', 'skim@downtownmed.com', '(555) 103-1003'),
                ('Emergency Trauma Associates', 'Medical Provider', 'Dr. James Patterson', 'jpatterson@trauma.org', '(555) 104-1004'),
                ('Neurological Treatment Center', 'Medical Provider', 'Dr. Lisa Chen', 'lchen@neurotreatment.com', '(555) 105-1005'),

                # Insurance Companies
                ('State Farm Mutual Insurance', 'Insurance Company', 'Robert Thompson', 'rthompson@statefarm.com', '(555) 201-2001'),
                ('GEICO Insurance Company', 'Insurance Company', 'Amanda Martinez', 'amartinez@geico.com', '(555) 202-2002'),
                ('Progressive Casualty Insurance', 'Insurance Company', 'David Johnson', 'djohnson@progressive.com', '(555) 203-2003'),
                ('Allstate Insurance Group', 'Insurance Company', 'Jennifer Davis', 'jdavis@allstate.com', '(555) 204-2004'),
                ('Liberty Mutual Insurance', 'Insurance Company', 'Christopher Lee', 'clee@libertymutual.com', '(555) 205-2005'),

                # Physical Therapy & Rehabilitation
                ('Premier Physical Therapy', 'Physical Therapy', 'Maria Gonzalez PT', 'mgonzalez@premierpt.com', '(555) 301-3001'),
                ('Sports Medicine Rehabilitation', 'Physical Therapy', 'Kevin Brown PT', 'kbrown@sportsmed.com', '(555) 302-3002'),
                ('Complete Wellness Physical Therapy', 'Physical Therapy', 'Nicole Taylor PT', 'ntaylor@completewellness.com', '(555) 303-3003'),

                # Imaging Services
                ('Metropolitan Imaging Center', 'Imaging Services', 'Dr. Brian Wilson', 'bwilson@metroimaging.com', '(555) 401-4001'),
                ('Advanced Diagnostic Imaging', 'Imaging Services', 'Dr. Michelle Garcia', 'mgarcia@advancedimaging.com', '(555) 402-4002'),
                ('Precision MRI Services', 'Imaging Services', 'Dr. Thomas Anderson', 'tanderson@precisionmri.com', '(555) 403-4003'),

                # Expert Witnesses & Investigation
                ('Forensic Engineering Associates', 'Expert Witness', 'Dr. William Jackson', 'wjackson@forensiceng.com', '(555) 501-5001'),
                ('Accident Reconstruction Experts', 'Investigation Services', 'Captain Mark Thompson', 'mthompson@accidentreconstruction.com', '(555) 502-5002'),
                ('Professional Investigation Services', 'Investigation Services', 'Detective Sarah Williams', 'swilliams@proinvestigation.com', '(555) 503-5003'),

                # Legal & Court Services
                ('Metro Court Reporting Services', 'Court Services', 'Elizabeth Martinez', 'emartinez@metrocourt.com', '(555) 601-6001'),
                ('Legal Document Processing Inc', 'Legal Services', 'Andrew Clark', 'aclark@legaldocs.com', '(555) 602-6002'),
                ('Professional Process Servers', 'Court Services', 'Jessica Moore', 'jmoore@processservers.com', '(555) 603-6003'),

                # Laboratory & Automotive
                ('Comprehensive Medical Labs', 'Laboratory Services', 'Dr. Daniel Lee', 'dlee@compmedlabs.com', '(555) 701-7001'),
                ('Precision Auto Body & Repair', 'Automotive Services', 'Frank Rodriguez', 'frodriguez@precisionauto.com', '(555) 801-8001'),
                ('24/7 Towing & Recovery Services', 'Automotive Services', 'Mike Johnson', 'mjohnson@247towing.com', '(555) 802-8002'),
            ]

            vendors = {}
            for vendor_name, vt_name, contact, email, phone in vendors_data:
                vendor = Vendor.objects.create(
                    vendor_name=vendor_name,
                    vendor_type=vendor_types[vt_name],
                    contact_person=contact,
                    email=email,
                    phone=phone,
                    address=f'{random.randint(100, 9999)} {random.choice(["Broadway", "Main Street", "Fifth Avenue", "Park Avenue", "Wall Street"])}',
                    city=random.choice(['New York', 'Brooklyn', 'Queens', 'Manhattan', 'Staten Island']),
                    state='NY',
                    zip_code=f'1{random.randint(1000, 9999)}',
                    tax_id=f'{random.randint(10, 99)}-{random.randint(1000000, 9999999)}',
                    is_active=True
                )
                vendors[vendor_name] = vendor

            self.stdout.write(f"✅ Created {len(vendors)} insurance program vendors")

            # Create insurance clients - mix of positive and negative balance scenarios
            clients_data = [
                # Clients who will have POSITIVE balances (most clients)
                ('Michael', 'Thompson', 'mthompson@email.com', '(555) 111-1111'),
                ('Jennifer', 'Anderson', 'janderson@email.com', '(555) 111-2222'),
                ('David', 'Martinez', 'dmartinez@email.com', '(555) 111-3333'),
                ('Sarah', 'Johnson', 'sjohnson@email.com', '(555) 111-4444'),
                ('Robert', 'Williams', 'rwilliams@email.com', '(555) 111-5555'),
                ('Lisa', 'Brown', 'lbrown@email.com', '(555) 111-6666'),
                ('Christopher', 'Davis', 'cdavis@email.com', '(555) 111-7777'),
                ('Amanda', 'Miller', 'amiller@email.com', '(555) 111-8888'),
                ('Matthew', 'Wilson', 'mwilson@email.com', '(555) 111-9999'),
                ('Jessica', 'Moore', 'jmoore@email.com', '(555) 222-0000'),
                ('Daniel', 'Taylor', 'dtaylor@email.com', '(555) 222-1111'),
                ('Ashley', 'Jackson', 'ajackson@email.com', '(555) 222-2222'),
                ('James', 'White', 'jwhite@email.com', '(555) 222-3333'),
                ('Emily', 'Harris', 'eharris@email.com', '(555) 222-4444'),
                ('Andrew', 'Martin', 'amartin@email.com', '(555) 222-5555'),
                ('Michelle', 'Garcia', 'mgarcia@email.com', '(555) 222-6666'),
                ('Joshua', 'Rodriguez', 'jrodriguez@email.com', '(555) 222-7777'),
                ('Stephanie', 'Lewis', 'slewis@email.com', '(555) 222-8888'),

                # Client who will have NEGATIVE balance (for Issues showcase)
                ('Kevin', 'Clark', 'kclark@email.com', '(555) 999-9999'),  # This client will go negative
            ]

            clients = []
            for first_name, last_name, email, phone in clients_data:
                client = Client.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=phone,
                    address=f'{random.randint(100, 9999)} {random.choice(["Oak Street", "Pine Avenue", "Maple Drive", "Cedar Lane", "Elm Boulevard"])}',
                    city=random.choice(['Brooklyn', 'Queens', 'Manhattan', 'Bronx', 'Staten Island']),
                    state='NY',
                    zip_code=f'1{random.randint(1000, 9999)}',
                    trust_account_status='ACTIVE_WITH_FUNDS',
                    is_active=True
                )
                clients.append(client)

            self.stdout.write(f"✅ Created {len(clients)} insurance clients")

            # Create ALL ACTIVE insurance cases
            insurance_case_types = [
                'Auto Accident - Rear End Collision',
                'Auto Accident - T-Bone Impact',
                'Auto Accident - Multi-Vehicle Collision',
                'Slip and Fall - Grocery Store',
                'Slip and Fall - Restaurant',
                'Slip and Fall - Office Building',
                'Medical Malpractice - Surgical Negligence',
                'Medical Malpractice - Delayed Diagnosis',
                'Medical Malpractice - Medication Error',
                'Product Liability - Defective Auto Parts',
                'Product Liability - Faulty Medical Device',
                'Premises Liability - Inadequate Security',
                'Premises Liability - Dangerous Conditions',
                'Workers Compensation - Construction Injury',
                'Workers Compensation - Repetitive Stress',
                'Dog Bite - Severe Injuries',
                'Wrongful Death - Motor Vehicle Accident',
                'Professional Liability - Legal Malpractice',
                'Catastrophic Injury - Spinal Cord'
            ]

            cases = []
            for i, client in enumerate(clients):
                case_title = insurance_case_types[i % len(insurance_case_types)]
                case_amount = Decimal(str(random.uniform(50000, 800000))).quantize(Decimal('0.01'))

                case = Case.objects.create(
                    case_title=f"{case_title} - {client.last_name} v. Insurance Co.",
                    client=client,
                    case_description=f"Insurance liability claim involving {case_title.lower()} resulting in significant injuries requiring ongoing medical treatment and loss of income.",
                    case_amount=case_amount,
                    case_status='Open',  # ALL CASES ARE ACTIVE
                    opened_date=date.today() - timedelta(days=random.randint(60, 400)),
                    is_active=True  # ALL CASES ARE ACTIVE
                )
                cases.append(case)

            self.stdout.write(f"✅ Created {len(cases)} ACTIVE insurance cases")

            # Create trust account transactions strategically
            self.stdout.write("💰 Creating strategic trust account transactions...")

            transaction_count = 0
            uncleared_count = 0

            # Phase 1: Create initial deposits for all cases (80% of case value)
            for case in cases:
                deposit_amount = (case.case_amount * Decimal('0.8')).quantize(Decimal('0.01'))
                deposit_date = case.opened_date + timedelta(days=random.randint(5, 20))

                is_cleared = random.choice([True, False])  # Some deposits uncleared
                cleared_date = deposit_date + timedelta(days=random.randint(1, 3)) if is_cleared else None

                if not is_cleared:
                    uncleared_count += 1

                BankTransaction.objects.create(
                    bank_account=bank_account,
                    transaction_type='DEPOSIT',
                    transaction_date=deposit_date,
                    amount=deposit_amount,
                    description=f'Insurance settlement payment - {case.case_title}',
                    client=case.client,
                    case=case,
                    payee='Insurance Settlement Funds',
                    item_type='CLIENT_DEPOSIT',
                    is_cleared=is_cleared,
                    cleared_date=cleared_date,
                    memo=f'Initial settlement funds for case {case.case_number}'
                )
                transaction_count += 1

            # Phase 2: Create vendor payments - strategic to create balance scenarios
            for i, case in enumerate(cases):
                case_balance = case.get_current_balance()

                # Last client (Kevin Clark) gets excessive payments to go negative
                if i == len(cases) - 1:  # Kevin Clark - will have negative balance
                    # Create payments that exceed his case balance
                    excess_payment_amount = case_balance + Decimal('15000.00')  # Goes $15k negative
                    selected_vendors = random.sample(list(vendors.values()), 3)

                    for j, vendor in enumerate(selected_vendors):
                        payment_amount = (excess_payment_amount / 3).quantize(Decimal('0.01'))
                        payment_date = case.opened_date + timedelta(days=random.randint(30, 180))

                        # Mix of cleared and uncleared
                        is_cleared = j < 2  # First 2 cleared, last uncleared
                        cleared_date = payment_date + timedelta(days=random.randint(1, 5)) if is_cleared else None

                        if not is_cleared:
                            uncleared_count += 1

                        BankTransaction.objects.create(
                            bank_account=bank_account,
                            transaction_type='WITHDRAWAL',
                            transaction_date=payment_date,
                            amount=payment_amount,
                            description=f'Medical services payment - {vendor.vendor_name}',
                            client=case.client,
                            case=case,
                            vendor=vendor,
                            payee=vendor.vendor_name,
                            item_type='VENDOR_PAYMENT',
                            is_cleared=is_cleared,
                            cleared_date=cleared_date,
                            memo=f'Treatment costs for case {case.case_number}'
                        )
                        transaction_count += 1

                else:  # Regular clients - keep positive balances
                    # Create 3-6 vendor payments per case, limited to 60% of balance
                    num_payments = random.randint(3, 6)
                    max_total_payments = case_balance * Decimal('0.6')

                    selected_vendors = random.sample(list(vendors.values()), min(num_payments, len(vendors)))

                    for vendor in selected_vendors:
                        payment_amount = (max_total_payments / num_payments * Decimal(str(random.uniform(0.7, 1.3)))).quantize(Decimal('0.01'))
                        payment_date = case.opened_date + timedelta(days=random.randint(25, 250))

                        # Strategic clearing to reach exactly 21 uncleared
                        if uncleared_count < 21:
                            status_value = random.choice(['cleared', 'cleared', 'pending'])  # 2/3 chance cleared
                        else:
                            status_value = 'cleared'  # All remaining cleared

                        cleared_date = payment_date + timedelta(days=random.randint(1, 7)) if status_value == 'cleared' else None

                        if status_value == 'pending':
                            uncleared_count += 1

                        BankTransaction.objects.create(
                            bank_account=bank_account,
                            transaction_type='WITHDRAWAL',
                            transaction_date=payment_date,
                            amount=payment_amount,
                            description=f'Professional services - {vendor.vendor_name}',
                            client=case.client,
                            case=case,
                            vendor=vendor,
                            payee=vendor.vendor_name,
                            item_type='VENDOR_PAYMENT',
                            status=status_value,
                            cleared_date=cleared_date,
                            memo=f'Medical/legal services for case {case.case_number}'
                        )
                        transaction_count += 1

            # Phase 3: Adjust to get exactly 21 uncleared transactions
            current_uncleared = BankTransaction.objects.filter(status='pending').count()

            if current_uncleared < 21:
                # Need more uncleared - mark some cleared ones as uncleared
                cleared_transactions = BankTransaction.objects.filter(status='cleared').order_by('?')[:21-current_uncleared]
                for txn in cleared_transactions:
                    txn.status = 'pending'
                    txn.cleared_date = None
                    txn.save()
            elif current_uncleared > 21:
                # Too many uncleared - clear some
                uncleared_transactions = BankTransaction.objects.filter(status='pending').order_by('?')[:current_uncleared-21]
                for txn in uncleared_transactions:
                    txn.status = 'cleared'
                    txn.cleared_date = txn.transaction_date + timedelta(days=random.randint(1, 5))
                    txn.save()

            final_uncleared = BankTransaction.objects.filter(status='pending').count()
            self.stdout.write(f"✅ Created {transaction_count} total transactions")
            self.stdout.write(f"⚠️  Exactly {final_uncleared} uncleared transactions for Warnings showcase")

            # Final verification and balance summary
            self.stdout.write("\n📊 SHOWCASE DATA VERIFICATION:")

            positive_clients = 0
            negative_clients = 0
            total_client_balance = Decimal('0')

            for client in clients:
                balance = client.get_current_balance()
                total_client_balance += balance

                if balance < 0:
                    negative_clients += 1
                    self.stdout.write(f"❌ {client.full_name}: ${balance:,.2f} (NEGATIVE)")
                else:
                    positive_clients += 1
                    self.stdout.write(f"✅ {client.full_name}: ${balance:,.2f}")

            bank_balance = bank_account.get_current_balance()
            balance_variance = abs(bank_balance - total_client_balance)

            # Dashboard Issues and Warnings Summary
            self.stdout.write(f"\n🎯 DASHBOARD SHOWCASE RESULTS:")
            self.stdout.write(f"🏦 Bank Account Balance: ${bank_balance:,.2f}")
            self.stdout.write(f"👥 Total Client Balances: ${total_client_balance:,.2f}")
            self.stdout.write(f"⚖️  Balance Variance: ${balance_variance:,.2f}")

            self.stdout.write(f"\n📋 ISSUES (3):")
            self.stdout.write(f"❌ Significant balance variance: ${balance_variance:,.2f}")
            self.stdout.write(f"❌ {negative_clients} client(s) with negative balances")
            self.stdout.write(f"❌ Large surplus funds: ${balance_variance:,.2f}")

            self.stdout.write(f"\n⚠️  WARNINGS (1):")
            self.stdout.write(f"⚠️  {final_uncleared} uncleared transactions")

            self.stdout.write(f"\n✅ ACTIVE STATUS:")
            self.stdout.write(f"✅ All {len(cases)} cases are ACTIVE (Open status)")
            self.stdout.write(f"✅ {positive_clients} clients with positive balances")
            self.stdout.write(f"✅ Single bank account: {bank_account.account_name}")

            self.stdout.write(self.style.SUCCESS(f"\n🎉 SHOWCASE DATA CREATED SUCCESSFULLY!"))
            self.stdout.write(self.style.SUCCESS(f"🎯 Perfect for demonstrating Issues and Warnings dashboard!"))
            self.stdout.write(self.style.SUCCESS(f"📊 {len(clients)} clients, {len(cases)} active cases, {len(vendors)} vendors"))