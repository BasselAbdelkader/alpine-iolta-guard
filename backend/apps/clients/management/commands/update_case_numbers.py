from django.core.management.base import BaseCommand
from django.db import transaction
from apps.clients.models import Case


class Command(BaseCommand):
    help = 'Update existing case numbers to new state-prefixed format'

    def handle(self, *args, **options):
        state_counters = {}
        
        with transaction.atomic():
            # Get all cases that need updating (have old format)
            old_cases = Case.objects.filter(case_number__startswith='CASE-').order_by('id')
            
            self.stdout.write(f"Found {old_cases.count()} cases to update")
            
            for case in old_cases:
                client_state = case.client.state
                if not client_state or len(client_state) != 2:
                    client_state = 'XX'  # Default for invalid states
                
                client_state = client_state.upper()
                
                # Initialize counter for this state if not exists
                if client_state not in state_counters:
                    # Find highest existing number for this state
                    existing_cases = Case.objects.filter(
                        case_number__startswith=client_state
                    ).exclude(
                        case_number__startswith='CASE-'
                    ).order_by('-case_number')
                    
                    if existing_cases.exists():
                        try:
                            last_num_str = existing_cases.first().case_number[2:]
                            state_counters[client_state] = int(last_num_str)
                        except (ValueError, IndexError):
                            state_counters[client_state] = 0
                    else:
                        state_counters[client_state] = 0
                
                # Increment counter and generate new case number
                state_counters[client_state] += 1
                new_case_number = f'{client_state}{state_counters[client_state]:06d}'
                
                self.stdout.write(f'Updating Case ID {case.id}: {case.case_number} -> {new_case_number}')
                
                # Update case number
                case.case_number = new_case_number
                case.save()
        
        self.stdout.write(self.style.SUCCESS('Case number update completed!'))