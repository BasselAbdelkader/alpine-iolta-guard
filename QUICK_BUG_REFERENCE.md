# QUICK BUG REFERENCE - CODE LOCATIONS & FIXES

## Critical Bugs

### BUG #1: Voided Transactions in Balance History
**File:** `/backend/apps/clients/api/views.py`
**Lines:** 137-143
**Quick Fix:**
```python
# BEFORE (BUGGY):
for txn in transactions:
    if txn.transaction_type == 'DEPOSIT':
        running_balance += txn.amount

# AFTER (FIXED):
for txn in transactions:
    if txn.status == 'voided':
        continue
    if txn.transaction_type == 'DEPOSIT':
        running_balance += txn.amount
```

---

### BUG #5: Case Deposit Not Atomic
**File:** `/backend/apps/clients/models.py`
**Lines:** 284-309
**Quick Fix:**
```python
# BEFORE (BUGGY):
def save(self, *args, **kwargs):
    is_new = self.pk is None
    super().save(*args, **kwargs)  # Saves without transaction protection
    if is_new and self.case_amount and self.case_amount > 0:
        self._create_case_deposit()  # Could fail here

# AFTER (FIXED):
def save(self, *args, **kwargs):
    from django.db import transaction
    is_new = self.pk is None
    
    with transaction.atomic():
        super().save(*args, **kwargs)
        if is_new and self.case_amount and self.case_amount > 0:
            self._create_case_deposit()
```

---

### BUG #6: Check Number Race Condition
**File:** `/backend/apps/bank_accounts/models.py`
**Lines:** 313-324
**Quick Fix:**
```python
# BEFORE (BUGGY):
if (not self.pk and self.transaction_type == 'WITHDRAWAL' and 
    not self.check_number and self.status != 'voided' and
    self.reference_number and self.reference_number != 'TO PRINT'):
    self.check_number = self.bank_account.get_next_check_number()

# AFTER (FIXED):
from django.db import transaction
with transaction.atomic():
    # Get bank account with lock
    bank_account = BankAccount.objects.select_for_update().get(pk=self.bank_account.pk)
    
    # Fetch inside atomic context
    if (not self.pk and self.transaction_type == 'WITHDRAWAL' and 
        not self.check_number and self.status != 'voided' and
        self.reference_number and self.reference_number != 'TO PRINT'):
        self.check_number = bank_account.get_next_check_number()
    
    super().save(*args, **kwargs)
```

---

## High Severity Bugs

### BUG #15: Multiple Deposits Update Logic
**File:** `/backend/apps/clients/models.py`
**Lines:** 386-405
**Quick Fix:**
```python
# BEFORE (BUGGY):
def _update_case_deposit(self, old_amount):
    existing_transaction = BankTransaction.objects.filter(
        case=self,
        item_type='CLIENT_DEPOSIT',
        reference_number=f'{self.case_number}'
    ).first()  # Gets ANY transaction

# AFTER (FIXED):
def _update_case_deposit(self, old_amount):
    # Get the latest non-voided deposit
    existing_transaction = BankTransaction.objects.filter(
        case=self,
        item_type='CLIENT_DEPOSIT',
        reference_number=f'{self.case_number}',
        status__in=['pending', 'cleared', 'reconciled']
    ).order_by('-created_at').first()
```

---

### BUG #7: Smart Delete Gap
**File:** `/backend/apps/clients/api/views.py`
**Lines:** 278-285
**Quick Fix:**
```python
# BEFORE (BUGGY):
client_balance = Decimal(str(instance.get_current_balance() or 0))
# This only counts direct client FK, not case-linked transactions

# AFTER (FIXED):
# Calculate balance including case-linked transactions
client_balance = Decimal(str(instance.get_current_balance() or 0))

# Verify no transactions through cases either
case_transaction_balance = Decimal('0')
for case in instance.cases.all():
    case_transaction_balance += Decimal(str(case.get_current_balance() or 0))

total_balance = client_balance + case_transaction_balance

if total_balance != Decimal('0'):
    return Response({'error': f'Cannot delete client with balance of ${total_balance}'})
```

---

## Medium Severity Bugs

### BUG #3: TRANSFER_OUT Aggregation Mismatch
**Files:** 
- `/backend/apps/clients/models.py` line 102
- `/backend/apps/transactions/api/views.py` line 93

**Issue:** Model includes TRANSFER_OUT in withdrawals but API queries for non-existent TRANSFER type

**Quick Fix:**
```python
# OPTION A: Keep TRANSFER_OUT in withdrawals (consistent)
# In transactions/api/views.py line 93, change:
transfers_amount=Sum('amount', filter=Q(transaction_type='TRANSFER'))
# TO:
# Remove this line - TRANSFER_OUT is already in withdrawals

# OPTION B: Separate TRANSFER_OUT (requires schema change)
# In clients/models.py, remove TRANSFER_OUT from withdrawal calculation
# and handle separately
```

---

### BUG #8: Transaction Ordering Inconsistent
**Files:**
- `/backend/apps/clients/api/views.py` line 120 (queries newest-first)
- `/backend/apps/bank_accounts/api/views.py` line 120 (queries newest-first)
- `/backend/apps/clients/api/views.py` line 161 (reverses after)

**Quick Fix:**
```python
# Change ALL transaction queries to oldest-first:
# FROM:
.order_by('-transaction_date', '-created_at')

# TO:
.order_by('transaction_date', 'id')

# Remove reversals like:
# return Response({'balance_history': list(reversed(balance_history))})
# Should be:
# return Response({'balance_history': balance_history})
```

---

### BUG #9: Settlement Distribution Overflow
**File:** `/backend/apps/settlements/models.py`
**Lines:** 100-112
**Quick Fix:**
```python
def clean(self):
    if self.amount <= 0:
        raise ValidationError("Distribution amount must be positive")
    
    # ADD THIS CHECK:
    other_distributions = self.settlement.distributions.exclude(pk=self.pk)
    other_total = other_distributions.aggregate(total=Sum('amount'))['total'] or 0
    
    if other_total + self.amount > self.settlement.total_amount:
        remaining = self.settlement.total_amount - other_total
        raise ValidationError(
            f"Distribution amount exceeds available balance. "
            f"Settlement total: ${self.settlement.total_amount}, "
            f"Other distributions: ${other_total}, "
            f"Remaining available: ${remaining}"
        )
    
    if not self.vendor and not self.client:
        raise ValidationError("Distribution must have either vendor or client")
    
    if self.vendor and self.client:
        raise ValidationError("Distribution cannot have both vendor and client")
```

---

### BUG #4: Reconciled Status Not Explicit
**File:** `/backend/apps/bank_accounts/models.py`
**Lines:** 37-51
**Quick Fix:**
```python
# BEFORE (BUGGY):
transactions = self.bank_transactions.exclude(status='voided')

# AFTER (FIXED):
transactions = self.bank_transactions.filter(
    status__in=['pending', 'cleared', 'reconciled']
)
```

---

### BUG #11: Amount Format Inconsistency
**Files:**
- `/backend/apps/bank_accounts/api/serializers.py` - returns Decimal
- `/backend/apps/dashboard/api/views.py` - returns string
- `/backend/apps/clients/api/views.py` - returns string

**Quick Fix:**
Standardize all to string format (JSON standard):
```python
# ALL serializers should do:
'balance': str(obj.get_current_balance())  # Always string

# OR all Decimal:
'balance': obj.get_current_balance()  # Serializer handles
```

---

### BUG #12: Validation Conflicts
**File:** `/backend/apps/bank_accounts/api/serializers.py`
**Lines:** 133-199
**Quick Fix:**
```python
def validate(self, data):
    # If updating cleared/reconciled transaction
    if self.instance and self.instance.status in ['cleared', 'reconciled']:
        # Only check description changes, skip other validations
        if 'description' in data:
            # Allow only description
            for key in data:
                if key != 'description':
                    data.pop(key)
        return data  # Skip all other validation
    
    # For new/pending transactions, do normal validation
    # ... rest of validation code
```

---

### BUG #10: UNMATCHED Status Doesn't Exist
**File:** `/backend/apps/bank_accounts/api/views.py`
**Line:** 335
**Quick Fix:**
```python
# BEFORE (BUGGY):
unmatched = BankTransaction.objects.filter(status='UNMATCHED')

# AFTER (FIXED - OPTION A):
# Use pending status instead
unmatched = BankTransaction.objects.filter(status='pending')

# OR OPTION B: Include both pending and voided that aren't printed
unmatched = BankTransaction.objects.filter(
    Q(status='pending') | Q(reference_number='TO PRINT')
).exclude(status='voided')
```

---

## Low Severity Bugs

### BUG #16: Zero Balance Float Comparison
**File:** `/backend/apps/clients/models.py`
**Lines:** 154-165
**Quick Fix:**
```python
# BEFORE (BUGGY):
elif current_balance == 0:

# AFTER (FIXED):
elif abs(current_balance) < 0.01:  # Within 1 cent
```

---

### BUG #2: Voided Amount Handling
**File:** `/backend/apps/bank_accounts/models.py`
**Line:** 418
**Quick Fix:**
```python
# BEFORE (BUGGY):
def void_transaction(self):
    self.status = 'voided'
    self.amount = 0  # Loses original amount

# AFTER (FIXED):
def void_transaction(self):
    self.status = 'voided'
    # Don't modify amount - keep original for audit trail
    # Balance calculations already exclude voided transactions
```

---

### BUG #13: Orphaned Transactions
**File:** `/backend/apps/bank_accounts/models.py`
**Lines:** 176-177
**Note:** on_delete=PROTECT prevents deletion, add monitoring:
```python
# Add a management command or API endpoint:
@action(detail=False, methods=['get'])
def orphaned_transactions(self, request):
    """Find transactions with NULL case/client that shouldn't be"""
    orphaned = BankTransaction.objects.filter(
        Q(client__isnull=True) | Q(case__isnull=True)
    ).exclude(status='voided')
    
    serializer = BankTransactionSerializer(orphaned, many=True)
    return Response({
        'orphaned_count': orphaned.count(),
        'transactions': serializer.data
    })
```

---

### BUG #14: Missing Import Batch Tracking
**File:** `/backend/apps/clients/models.py`
**Lines:** 343-384
**Quick Fix:**
```python
def _create_case_deposit(self, import_batch_id=None):
    """Create automatic deposit transaction for this case"""
    transaction = BankTransaction.objects.create(
        # ... other fields ...
        data_source='csv_import' if import_batch_id else 'webapp',
        import_batch_id=import_batch_id,
    )
    return transaction

# In Case.save():
if is_new and self.case_amount and self.case_amount > 0:
    self._create_case_deposit(import_batch_id=self.import_batch_id)
```

---

## Testing Recommendations

After fixing these bugs, test:

1. **Balance Calculations**: Create 10 transactions, void 3, verify balance
2. **Check Numbers**: Create 5 checks simultaneously, verify no duplicates
3. **Case Deposits**: Create case, update amount, verify one deposit updated
4. **Smart Delete**: Try deleting client with zero balance but linked transactions
5. **Transaction Ordering**: Verify all endpoints show oldest-first
6. **Settlement Distributions**: Try adding distribution > settlement amount
7. **Reconciliation**: Mark transaction as reconciled, verify included in balance

---

## Files to Review After Fixes

- `/backend/tests/test_balance_calculations.py` - Add test suite
- `/backend/tests/test_concurrency.py` - Test race conditions
- `/backend/tests/test_data_integrity.py` - Test atomic operations

---
