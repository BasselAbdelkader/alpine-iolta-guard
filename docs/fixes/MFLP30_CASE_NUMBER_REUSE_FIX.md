# MFLP-30: Deleted Case Number Reused When Creating a New Case - FIX

**Bug ID:** MFLP-30
**Priority:** Medium
**Type:** Back-End Bug
**Fixed Date:** 2025-11-08

---

## Bug Description

When deleting a case from the Trust Account Management System and then creating a new case, the system incorrectly reused the case number of the deleted case. Case numbers should be unique and sequential, even for deleted records, to maintain accurate historical tracking and prevent duplication issues.

### Steps to Reproduce (Before Fix):
1. Open the Trust Account Management System
2. Navigate to the Client tab
3. Locate a case (e.g., CASE-002043)
4. Delete the case
5. Create a new case for any client

### Expected Result:
The newly created case should have the next sequential number (e.g., CASE-002044).
Deleted case numbers should NOT be reused.

### Actual Result (Before Fix):
The new case was created with the deleted case number (CASE-002043), reusing it.

---

## Root Cause

The `_generate_case_number()` method in the Case model (models.py:304-312) queries the `cases` table to find the highest case number:

```python
def _generate_case_number(self):
    """BUG #16 FIX: Generate auto-incremental case number - never reuse deleted numbers"""
    from django.db import connection

    # Query the database directly to get the highest case number ever used
    # This includes deleted cases to prevent number reuse  ← INCORRECT COMMENT
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT case_number
            FROM cases
            WHERE case_number LIKE 'CASE-%%'
            ORDER BY CAST(SUBSTRING(case_number FROM 6) AS INTEGER) DESC
            LIMIT 1
        """)
```

**Problem:** When a case is hard-deleted (removed from the database), it no longer exists in the `cases` table, so the query cannot see it. This allows the case number to be reused.

---

## Solution

Created a separate `CaseNumberCounter` model that tracks the last used case number. This counter only increments, never decreases, even when cases are deleted.

### Changes Made

#### 1. Added CaseNumberCounter Model (models.py:184-208)

```python
class CaseNumberCounter(models.Model):
    """
    MFLP-30 FIX: Stores the last used case number to prevent reuse of deleted case numbers.
    This model ensures case numbers are always incremental, even when cases are deleted.
    """
    last_number = models.IntegerField(default=0)

    class Meta:
        db_table = 'case_number_counter'

    @classmethod
    def get_next_number(cls):
        """
        Thread-safe method to get the next case number.
        Uses database-level locking to prevent race conditions.
        """
        with transaction.atomic():
            # Use select_for_update() to lock the row during the transaction
            counter, created = cls.objects.select_for_update().get_or_create(
                id=1,
                defaults={'last_number': 0}
            )
            counter.last_number += 1
            counter.save()
            return counter.last_number
```

**Key Features:**
- Thread-safe using `select_for_update()` (database row locking)
- Never decreases, only increments
- Survives case deletions
- Prevents race conditions in concurrent environments

#### 2. Updated _generate_case_number() Method (models.py:304-312)

**Before:**
```python
def _generate_case_number(self):
    """BUG #16 FIX: Generate auto-incremental case number - never reuse deleted numbers"""
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT case_number
            FROM cases
            WHERE case_number LIKE 'CASE-%%'
            ORDER BY CAST(SUBSTRING(case_number FROM 6) AS INTEGER) DESC
            LIMIT 1
        """)
        row = cursor.fetchone()

        if row and row[0]:
            try:
                numeric_part = row[0].split('-')[1]
                highest_num = int(numeric_part)
            except (ValueError, IndexError):
                highest_num = 0
        else:
            highest_num = 0

    next_num = highest_num + 1
    return f"CASE-{next_num:06d}"
```

**After:**
```python
def _generate_case_number(self):
    """
    MFLP-30 FIX: Generate auto-incremental case number - never reuse deleted numbers.
    Uses CaseNumberCounter model to ensure case numbers are always incremental,
    even when cases are deleted (hard delete).
    """
    # Get next number from counter (thread-safe, never reuses deleted numbers)
    next_num = CaseNumberCounter.get_next_number()
    return f"CASE-{next_num:06d}"  # 6-digit zero-padded (e.g., CASE-000001)
```

#### 3. Updated Import Statement (models.py:1)

**Before:**
```python
from django.db import models
```

**After:**
```python
from django.db import models, transaction
```

#### 4. Created Database Table

```sql
CREATE TABLE IF NOT EXISTS case_number_counter (
    id INTEGER PRIMARY KEY DEFAULT 1,
    last_number INTEGER NOT NULL DEFAULT 0
);
```

#### 5. Initialized Counter

The counter was initialized with the highest existing case number in the database:

```sql
WITH highest AS (
    SELECT COALESCE(MAX(CAST(SUBSTRING(case_number FROM 6) AS INTEGER)), 0) AS max_num
    FROM cases
    WHERE case_number ~ '^CASE-[0-9]+$'
)
INSERT INTO case_number_counter (id, last_number)
SELECT 1, max_num FROM highest
ON CONFLICT (id) DO UPDATE SET last_number = EXCLUDED.last_number;
```

Result: Counter initialized to 5 (based on existing CASE-000001 through CASE-000005)

---

## Testing

### Test Script: test_mflp30_fix.py

Created comprehensive test that verifies:
1. New cases get sequential case numbers
2. When a case is deleted, its number is NOT reused
3. The next case gets the next sequential number

### Test Results:

```
======================================================================
MFLP-30 FIX TEST: Deleted Case Numbers Should Not Be Reused
======================================================================

Using client: Dorothy Adams (ID: 57)

📊 Initial counter value: 5

Step 1: Creating first test case...
✅ Created case: CASE-000006
   Expected: CASE-000006
   ✅ PASS: Case number is correct

Step 2: Deleting the test case...
✅ Deleted case: CASE-000006

Step 3: Verifying case was deleted from database...
   ✅ PASS: Case was hard-deleted from database

Step 4: Creating second test case...
✅ Created case: CASE-000007
   Expected: CASE-000007 (NOT CASE-000006)
   ✅ PASS: Case number is sequential, not reused

Step 5: Cleaning up test data...
✅ Deleted test case 2

======================================================================
FINAL RESULT:
======================================================================
✅ MFLP-30 FIX VERIFIED: Deleted case numbers are NOT reused

Summary:
  - Created case with number: CASE-000006
  - Deleted that case
  - Created new case with number: CASE-000007
  - ✅ New case did NOT reuse the deleted number
```

**Status:** ✅ ALL TESTS PASSING

---

## Files Modified

### Backend:
1. **`/app/apps/clients/models.py`**
   - Added `transaction` import (line 1)
   - Added `CaseNumberCounter` model (lines 184-208)
   - Simplified `_generate_case_number()` method (lines 304-312)
   - Backup: `/app/apps/clients/models.py.backup`

### Database:
1. **New table:** `case_number_counter`
   - Stores last used case number
   - Initialized with highest existing number

### Test Files:
1. **`test_mflp30_fix.py`** - Comprehensive test script

---

## Deployment Steps

1. ✅ Backup original models.py
2. ✅ Update models.py with new CaseNumberCounter model
3. ✅ Copy modified file to container
4. ✅ Create case_number_counter table in database
5. ✅ Initialize counter with current highest case number
6. ✅ Restart backend container
7. ✅ Run test script to verify fix
8. ✅ Update Jira.csv with fix date (2025-11-08)

---

## Benefits of This Fix

1. **Data Integrity:** Case numbers are never reused, maintaining audit trail
2. **Thread-Safe:** Uses database row locking to prevent race conditions
3. **Simple Logic:** Much simpler than the previous complex SQL query
4. **Reliable:** Counter persists even when all cases are deleted
5. **Future-Proof:** Works regardless of case deletion patterns

---

## Technical Details

### Why CaseNumberCounter is Better:

**Old approach (querying cases table):**
- ❌ Fails when cases are hard-deleted
- ❌ Complex SQL query with string parsing
- ❌ Could have race conditions in high-concurrency scenarios
- ❌ Relies on existing data being present

**New approach (dedicated counter):**
- ✅ Works even when all cases are deleted
- ✅ Simple atomic increment operation
- ✅ Database-level row locking prevents race conditions
- ✅ Independent of case table state

### Thread Safety:

The `select_for_update()` method ensures that when multiple requests try to create cases simultaneously:
1. First request locks the counter row
2. Other requests wait for the lock
3. Each request gets a unique sequential number
4. No duplicates possible

---

## Verification Steps

To verify the fix is working in production:

```bash
# 1. Check counter exists and has correct value
docker exec iolta_db_alpine psql -U iolta_user -d iolta_guard_db -c "SELECT * FROM case_number_counter;"

# 2. Run the test script
docker cp test_mflp30_fix.py iolta_backend_alpine:/tmp/
docker exec iolta_backend_alpine python /tmp/test_mflp30_fix.py

# 3. Manually test:
# - Create a case (note the case number)
# - Delete that case
# - Create another case
# - Verify the new case number is sequential, not reused
```

---

## Status

**Fix Status:** ✅ COMPLETE
**Testing Status:** ✅ PASSING
**Deployment Status:** ✅ DEPLOYED
**Documentation Status:** ✅ COMPLETE

---

## Related Files

- **Model:** `/app/apps/clients/models.py`
- **Test:** `/home/amin/Projects/ve_demo/test_mflp30_fix.py`
- **Backup:** `/app/apps/clients/models.py.backup`
- **Bug Tracking:** `/home/amin/Projects/ve_demo/Jira.csv`

---

**Fixed by:** Claude Code
**Date:** November 8, 2025
**Jira:** Updated with fix date 2025-11-08
