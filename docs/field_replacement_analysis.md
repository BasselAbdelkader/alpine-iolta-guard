# Field Replacement Analysis

**Date:** November 7, 2025
**Requirements:**
1. Replace `transaction_number` field with `RefNo` in all API responses
2. Replace `case_number` field with `case_title` in all API responses

---

## Part 1: Transaction Number → RefNo

### Files to Modify:

#### 1. `/app/apps/bank_accounts/api/serializers.py`
**Lines 165, 168:** BankTransactionSerializer

**Current:**
```python
fields = [..., 'transaction_number', ...]
read_only_fields = [..., 'transaction_number', ...]
```

**Change to:**
Use `SerializerMethodField` to rename the field in output

---

#### 2. `/app/apps/bank_accounts/api/views.py`
**Line 198:** balance_history() method
**Line 564:** audit_history() method

**Current:**
```python
'transaction_number': transaction.transaction_number,
```

**Change to:**
```python
'RefNo': transaction.transaction_number,
```

---

#### 3. `/app/apps/clients/api/views.py`
**Line 149:** balance_history() method
**Line 376:** transactions() method (case transactions)

**Current:**
```python
'transaction_number': txn.transaction_number,
```

**Change to:**
```python
'RefNo': txn.transaction_number,
```

---

## Part 2: Case Number → Case Title

### Files to Modify:

#### 1. `/app/apps/bank_accounts/api/views.py`
**Line 574:** audit_history() method

**Current:**
```python
'case_number': transaction.case.case_number if transaction.case else None,
```

**Change to:**
```python
'case_title': transaction.case.case_title if transaction.case else None,
```

---

#### 2. `/app/apps/clients/api/views.py`
**Line 348:** balance() method (CaseViewSet)
**Line 391:** transactions() method (CaseViewSet)

**Current:**
```python
'case_number': case.case_number,
```

**Change to:**
```python
'case_title': case.case_title,
```

---

#### 3. `/app/apps/clients/api/serializers.py`
**Line 146:** cases() method (within ClientSerializer)
**Lines 171, 176, 240:** CaseSerializer and CaseListSerializer

This is more complex because case_number is a field in the Meta.fields list.

**Strategy:** Use `to_representation()` to rename case_number to case_title in output

---

## Summary

### Transaction Number → RefNo
- **3 files to modify**
- **6 locations total**
- Method: Direct dictionary key replacement in custom views, SerializerMethodField in serializers

### Case Number → Case Title
- **3 files to modify**
- **6+ locations total**
- Method: Direct dictionary key replacement in custom views, to_representation() in serializers

---

## Implementation Plan

1. Modify `/app/apps/bank_accounts/api/serializers.py` - Add to_representation() to rename transaction_number
2. Modify `/app/apps/bank_accounts/api/views.py` - Replace transaction_number and case_number keys
3. Modify `/app/apps/clients/api/views.py` - Replace transaction_number and case_number keys
4. Modify `/app/apps/clients/api/serializers.py` - Add to_representation() to rename case_number
5. Test all APIs
6. Restart backend
