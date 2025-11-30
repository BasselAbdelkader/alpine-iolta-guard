from django.core.management.base import BaseCommand
from apps.clients.models import Client
import re

class Command(BaseCommand):
    help = 'Standardize all phone numbers to USA format (123) 456-7890'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making actual changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes will be made'))
        
        clients_with_phones = Client.objects.exclude(phone__isnull=True).exclude(phone='')
        total_clients = clients_with_phones.count()
        
        self.stdout.write(f'Found {total_clients} clients with phone numbers')
        
        updated_count = 0
        
        for client in clients_with_phones:
            old_phone = client.phone
            new_phone = self.standardize_phone(old_phone)
            
            if old_phone != new_phone:
                if dry_run:
                    self.stdout.write(f'{client.full_name}: "{old_phone}" -> "{new_phone}"')
                else:
                    client.phone = new_phone
                    client.save(update_fields=['phone'])
                    self.stdout.write(f'Updated {client.full_name}: "{old_phone}" -> "{new_phone}"')
                
                updated_count += 1
            else:
                self.stdout.write(f'{client.full_name}: "{old_phone}" (no change needed)')
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'Would update {updated_count} of {total_clients} phone numbers'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} of {total_clients} phone numbers'))

    def standardize_phone(self, phone_number):
        """
        Standardize phone number to USA format (123) 456-7890
        """
        if not phone_number:
            return phone_number
        
        # Remove all non-digits
        digits = re.sub(r'\D', '', str(phone_number))
        
        # Handle different cases
        if len(digits) == 7:
            # Add default area code 555 for 7-digit numbers
            digits = '555' + digits
        elif len(digits) == 11 and digits[0] == '1':
            # Remove leading 1 for US numbers
            digits = digits[1:]
        elif len(digits) == 10:
            # Already correct length
            pass
        elif len(digits) > 11:
            # International numbers - keep first 10 digits after country code
            if digits.startswith('1') and len(digits) > 11:
                digits = digits[1:11]  # Remove country code, take next 10
            else:
                digits = digits[-10:]  # Take last 10 digits
        else:
            # Invalid length - return original
            return phone_number
        
        # Ensure we have exactly 10 digits
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        else:
            # Return original if we can't standardize
            return phone_number