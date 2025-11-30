# OLD TRANSACTION MODELS - COMMENTED OUT FOR CONSOLIDATION
# These models have been replaced by the consolidated BankTransaction model
# in apps.bank_accounts.models
#
# The old architecture used separate Transaction and TransactionItem models
# which has been consolidated into a single BankTransaction model for better
# data consistency and simpler queries.
#
# All transaction-related operations should now use:
# from apps.bank_accounts.models import BankTransaction

"""
Legacy Transaction Models (DEPRECATED)

This file previously contained Transaction and TransactionItem models
that have been consolidated into a single BankTransaction model located
in apps.bank_accounts.models.

IMPORTANT: Do not use these models in new code. They are kept here
for reference only during the migration period.

For all transaction operations, use:
from apps.bank_accounts.models import BankTransaction
"""

pass  # Empty module - models moved to bank_accounts.models