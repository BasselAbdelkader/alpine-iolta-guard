"""
Management command to set up import approval roles and permissions
Usage: python manage.py setup_import_roles
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.imports.models import StagingClient, StagingCase, StagingBankTransaction, ImportNotification


class Command(BaseCommand):
    help = 'Set up import approval roles and permissions'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up import approval roles...'))

        # Create custom permissions for imports
        content_type = ContentType.objects.get_for_model(StagingClient)

        # Create permissions if they don't exist
        perm_import, created = Permission.objects.get_or_create(
            codename='can_import_csv',
            name='Can import CSV files',
            content_type=content_type,
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  ✅ Created permission: can_import_csv'))
        else:
            self.stdout.write('  ℹ️  Permission already exists: can_import_csv')

        perm_approve, created = Permission.objects.get_or_create(
            codename='can_approve_imports',
            name='Can approve imports',
            content_type=content_type,
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  ✅ Created permission: can_approve_imports'))
        else:
            self.stdout.write('  ℹ️  Permission already exists: can_approve_imports')

        perm_reject, created = Permission.objects.get_or_create(
            codename='can_reject_imports',
            name='Can reject imports',
            content_type=content_type,
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  ✅ Created permission: can_reject_imports'))
        else:
            self.stdout.write('  ℹ️  Permission already exists: can_reject_imports')

        # Create Managing Attorney group
        managing_attorney_group, created = Group.objects.get_or_create(name='Managing Attorney')
        if created:
            self.stdout.write(self.style.SUCCESS('\n  ✅ Created group: Managing Attorney'))
        else:
            self.stdout.write('\n  ℹ️  Group already exists: Managing Attorney')

        # Add permissions to Managing Attorney
        managing_attorney_group.permissions.add(perm_import, perm_approve, perm_reject)
        self.stdout.write(self.style.SUCCESS('     Added permissions: can_import_csv, can_approve_imports, can_reject_imports'))

        # Create Accountant group
        accountant_group, created = Group.objects.get_or_create(name='Accountant')
        if created:
            self.stdout.write(self.style.SUCCESS('\n  ✅ Created group: Accountant'))
        else:
            self.stdout.write('\n  ℹ️  Group already exists: Accountant')

        # Add permissions to Accountant
        accountant_group.permissions.add(perm_import, perm_approve, perm_reject)
        self.stdout.write(self.style.SUCCESS('     Added permissions: can_import_csv, can_approve_imports, can_reject_imports'))

        # Create Staff group (can import but not approve)
        staff_group, created = Group.objects.get_or_create(name='Staff')
        if created:
            self.stdout.write(self.style.SUCCESS('\n  ✅ Created group: Staff'))
        else:
            self.stdout.write('\n  ℹ️  Group already exists: Staff')

        # Add import permission to Staff (but NOT approve/reject)
        staff_group.permissions.add(perm_import)
        self.stdout.write(self.style.SUCCESS('     Added permissions: can_import_csv'))

        self.stdout.write(self.style.SUCCESS('\n✅ Import roles and permissions setup complete!'))
        self.stdout.write('\nRole Summary:')
        self.stdout.write('  • Managing Attorney: Can import, approve, and reject imports')
        self.stdout.write('  • Accountant: Can import, approve, and reject imports')
        self.stdout.write('  • Staff: Can import only (cannot approve or reject)')
        self.stdout.write('\nTo assign roles to users:')
        self.stdout.write('  1. Go to Django Admin → Users')
        self.stdout.write('  2. Edit user → Groups → Add to appropriate group')
