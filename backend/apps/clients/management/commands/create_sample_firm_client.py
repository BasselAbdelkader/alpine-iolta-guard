"""
Management command to create Sample Firm client for bank fees
"""
from django.core.management.base import BaseCommand
from apps.clients.models import Client


class Command(BaseCommand):
    help = 'Creates Sample Firm client for handling bank fee deposits'

    def handle(self, *args, **options):
        # Check if Sample Firm already exists
        existing = Client.objects.filter(
            first_name='Sample',
            last_name='Firm'
        ).first()

        if existing:
            self.stdout.write(
                self.style.WARNING(
                    f'Sample Firm client already exists (ID: {existing.id}, '
                    f'Client Number: {existing.client_number})'
                )
            )
            return

        # Create Sample Firm client
        sample_firm = Client.objects.create(
            first_name='Sample',
            last_name='Firm',
            email='sample.firm@example.com',
            phone='(555) 000-0000',
            address='Law Firm Address',
            city='City',
            state='NY',
            zip_code='10001',
            trust_account_status='ACTIVE_ZERO_BALANCE',
            is_active=True
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created Sample Firm client:\n'
                f'  - ID: {sample_firm.id}\n'
                f'  - Client Number: {sample_firm.client_number}\n'
                f'  - Email: {sample_firm.email}\n'
                f'  - Status: {sample_firm.trust_account_status}'
            )
        )
