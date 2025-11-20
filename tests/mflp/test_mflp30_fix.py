#!/usr/bin/env python
"""
MFLP-30 Fix Test: Verify deleted case numbers are not reused

This script tests that:
1. New cases get sequential case numbers
2. When a case is deleted, its number is NOT reused
3. The next case gets the next sequential number
"""

import os
import sys
import django

sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.clients.models import Client, Case, CaseNumberCounter
from datetime import date

def main():
    print("=" * 70)
    print("MFLP-30 FIX TEST: Deleted Case Numbers Should Not Be Reused")
    print("=" * 70)
    print()

    # Get a test client
    client = Client.objects.first()
    if not client:
        print("❌ No clients found in database. Cannot test.")
        return False

    print(f"Using client: {client.full_name} (ID: {client.id})")
    print()

    # Step 1: Check current counter value
    try:
        counter = CaseNumberCounter.objects.get(id=1)
        initial_counter = counter.last_number
        print(f"📊 Initial counter value: {initial_counter}")
    except CaseNumberCounter.DoesNotExist:
        print("❌ CaseNumberCounter not found. Creating...")
        counter = CaseNumberCounter.objects.create(id=1, last_number=0)
        initial_counter = 0

    print()

    # Step 2: Create first test case
    print("Step 1: Creating first test case...")
    case1 = Case.objects.create(
        case_title="MFLP-30 Test Case 1",
        client=client,
        case_description="Test case for MFLP-30 fix",
        opened_date=date.today(),
        case_status='Open'
    )
    print(f"✅ Created case: {case1.case_number}")
    expected_num_1 = initial_counter + 1
    print(f"   Expected: CASE-{expected_num_1:06d}")

    if case1.case_number == f"CASE-{expected_num_1:06d}":
        print(f"   ✅ PASS: Case number is correct")
    else:
        print(f"   ❌ FAIL: Case number mismatch!")
        return False

    print()

    # Step 3: Delete the case
    print("Step 2: Deleting the test case...")
    deleted_case_number = case1.case_number
    case1_id = case1.id
    case1.delete()
    print(f"✅ Deleted case: {deleted_case_number}")
    print()

    # Step 4: Verify case was deleted
    print("Step 3: Verifying case was deleted from database...")
    try:
        Case.objects.get(id=case1_id)
        print("   ❌ FAIL: Case still exists in database!")
        return False
    except Case.DoesNotExist:
        print("   ✅ PASS: Case was hard-deleted from database")
    print()

    # Step 5: Create second test case
    print("Step 4: Creating second test case...")
    case2 = Case.objects.create(
        case_title="MFLP-30 Test Case 2",
        client=client,
        case_description="Test case to verify no reuse",
        opened_date=date.today(),
        case_status='Open'
    )
    print(f"✅ Created case: {case2.case_number}")
    expected_num_2 = expected_num_1 + 1  # Should be next number, NOT the deleted one
    print(f"   Expected: CASE-{expected_num_2:06d} (NOT {deleted_case_number})")

    if case2.case_number == deleted_case_number:
        print(f"   ❌ FAIL: Case number was reused! Bug NOT fixed.")
        case2.delete()
        return False
    elif case2.case_number == f"CASE-{expected_num_2:06d}":
        print(f"   ✅ PASS: Case number is sequential, not reused")
    else:
        print(f"   ❌ FAIL: Unexpected case number!")
        case2.delete()
        return False

    print()

    # Step 6: Clean up
    print("Step 5: Cleaning up test data...")
    case2.delete()
    print("✅ Deleted test case 2")
    print()

    # Final verification
    print("=" * 70)
    print("FINAL RESULT:")
    print("=" * 70)
    print("✅ MFLP-30 FIX VERIFIED: Deleted case numbers are NOT reused")
    print()
    print(f"Summary:")
    print(f"  - Created case with number: {deleted_case_number}")
    print(f"  - Deleted that case")
    print(f"  - Created new case with number: {case2.case_number}")
    print(f"  - ✅ New case did NOT reuse the deleted number")
    print()

    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
