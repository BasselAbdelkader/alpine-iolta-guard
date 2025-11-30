import sys

file_path = '/root/ve_demo/backend/apps/bank_accounts/models.py'

with open(file_path, 'r') as f:
    content = f.read()

# Find the void_transaction method
method_signature = "def void_transaction(self, void_reason, voided_by=None, ip_address=None):"
start_idx = content.find(method_signature)

if start_idx == -1:
    print("Could not find void_transaction method.")
    sys.exit(1)

# Find the "if self.status == 'cleared':" check
cleared_check = "if self.status == 'cleared':"
cleared_check_idx = content.find(cleared_check, start_idx)

if cleared_check_idx == -1:
    print("Could not find cleared check inside void_transaction method.")
    sys.exit(1)

# Construct the new check logic
new_check = """        # Check if voiding would cause a negative balance (for DEPOSITs)
        if self.transaction_type == 'DEPOSIT':
            client = self.client
            case = self.case
            
            if client and client.get_current_balance() - self.amount < 0:
                raise ValueError(
                    f"Cannot void deposit of ${self.amount:,.2f} because it would result in a negative balance "
                    f"for client '{client.full_name}' (Current Balance: ${client.get_current_balance():,.2f}). "
                    f"Negative balances are strictly prohibited."
                )
                
            if case and case.get_current_balance() - self.amount < 0:
                raise ValueError(
                    f"Cannot void deposit of ${self.amount:,.2f} because it would result in a negative balance "
                    f"for case '{case.case_title}' (Current Balance: ${case.get_current_balance():,.2f}). "
                    f"Negative balances are strictly prohibited."
                )

        if self.status == 'cleared':"""

# Replace the old check with the new check + the old check
new_content = content.replace(cleared_check, new_check)

with open(file_path, 'w') as f:
    f.write(new_content)

print("Successfully added negative balance check to void_transaction.")
