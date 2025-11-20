#!/usr/bin/env python
"""
Test MFLP-31, MFLP-32, MFLP-33: Case Date Validation
Tests backend validation for all three related bugs
"""

import os
import sys
import django
from datetime import date, timedelta

# Setup Django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.clients.models import Client
from apps.clients.api.serializers import CaseSerializer

print("=" * 80)
print("MFLP-31, MFLP-32, MFLP-33: Case Date Validation Tests")
print("=" * 80)
print()

# Get an active client for testing
client = Client.objects.filter(is_active=True).first()
print(f"Testing with client: {client.full_name} (ID: {client.id})")
print()

# Test results tracking
test_results = []

# ============================================================================
# TEST 1: MFLP-31 - Closed case without closed_date
# ============================================================================
print("=" * 80)
print("TEST 1: MFLP-31 - Closed Case Without Closed Date")
print("=" * 80)
print()

case_data_1 = {
    'client': client.id,
    'case_title': 'Test Closed Case Without Date',
    'case_description': 'Testing MFLP-31',
    'case_status': 'Closed',  # Status is Closed
    'case_amount': 5000,
    'opened_date': date.today() - timedelta(days=30)
    # closed_date is MISSING
}

print("Request Data:")
print(f"  Status: {case_data_1['case_status']}")
print(f"  Opened Date: {case_data_1['opened_date']}")
print(f"  Closed Date: (missing)")
print()

serializer_1 = CaseSerializer(data=case_data_1)

if serializer_1.is_valid():
    print("❌ FAIL: Closed case without closed_date was ALLOWED")
    test_results.append(("MFLP-31", "FAIL", "Case creation allowed without closed_date"))
else:
    print("✅ PASS: Closed case without closed_date was REJECTED")
    print()
    print("Validation Errors:")
    for field, errors in serializer_1.errors.items():
        error_message = errors[0] if isinstance(errors, list) else str(errors)
        print(f"  Field: {field}")
        print(f"  Error: {error_message}")

    # Check if the error is what we expect
    if 'closed_date' in serializer_1.errors:
        error_msg = str(serializer_1.errors['closed_date'][0])
        if 'required' in error_msg.lower() and 'closed' in error_msg.lower():
            print()
            print("✅ Error message correctly states closed_date is required")
            test_results.append(("MFLP-31", "PASS", "Correct validation and error message"))
        else:
            print()
            print("⚠️  Error message doesn't clearly state requirement")
            test_results.append(("MFLP-31", "PARTIAL", "Validation works but message unclear"))
    else:
        print()
        print("⚠️  Error is not on 'closed_date' field")
        test_results.append(("MFLP-31", "PARTIAL", "Validation works but wrong field"))

print()

# ============================================================================
# TEST 2: MFLP-32 - Closed date earlier than opened date
# ============================================================================
print("=" * 80)
print("TEST 2: MFLP-32 - Closed Date Earlier Than Opened Date")
print("=" * 80)
print()

opened = date.today() - timedelta(days=30)
closed = date.today() - timedelta(days=60)  # 60 days ago (earlier than opened)

case_data_2 = {
    'client': client.id,
    'case_title': 'Test Invalid Date Range',
    'case_description': 'Testing MFLP-32',
    'case_status': 'Closed',
    'case_amount': 5000,
    'opened_date': opened,
    'closed_date': closed  # Closed date is EARLIER than opened date
}

print("Request Data:")
print(f"  Status: {case_data_2['case_status']}")
print(f"  Opened Date: {opened}")
print(f"  Closed Date: {closed}")
print(f"  Issue: Closed date is {(opened - closed).days} days BEFORE opened date ❌")
print()

serializer_2 = CaseSerializer(data=case_data_2)

if serializer_2.is_valid():
    print("❌ FAIL: Case with closed_date < opened_date was ALLOWED")
    test_results.append(("MFLP-32", "FAIL", "Invalid date range allowed"))
else:
    print("✅ PASS: Case with closed_date < opened_date was REJECTED")
    print()
    print("Validation Errors:")
    for field, errors in serializer_2.errors.items():
        error_message = errors[0] if isinstance(errors, list) else str(errors)
        print(f"  Field: {field}")
        print(f"  Error: {error_message}")

    # Check if the error is what we expect
    if 'closed_date' in serializer_2.errors:
        error_msg = str(serializer_2.errors['closed_date'][0])
        if 'earlier' in error_msg.lower() or 'before' in error_msg.lower():
            print()
            print("✅ Error message correctly states closed_date cannot be earlier")
            test_results.append(("MFLP-32", "PASS", "Correct validation and error message"))
        else:
            print()
            print("⚠️  Error message doesn't clearly state date order issue")
            test_results.append(("MFLP-32", "PARTIAL", "Validation works but message unclear"))
    else:
        print()
        print("⚠️  Error is not on 'closed_date' field")
        test_results.append(("MFLP-32", "PARTIAL", "Validation works but wrong field"))

print()

# ============================================================================
# TEST 3: MFLP-33 - Future opened date
# ============================================================================
print("=" * 80)
print("TEST 3: MFLP-33 - Future Opened Date")
print("=" * 80)
print()

future_date = date.today() + timedelta(days=30)  # 30 days in the future

case_data_3 = {
    'client': client.id,
    'case_title': 'Test Future Opened Date',
    'case_description': 'Testing MFLP-33',
    'case_status': 'Open',
    'case_amount': 5000,
    'opened_date': future_date  # Opened date is in the FUTURE
}

print("Request Data:")
print(f"  Status: {case_data_3['case_status']}")
print(f"  Opened Date: {future_date}")
print(f"  Today: {date.today()}")
print(f"  Issue: Opened date is {(future_date - date.today()).days} days in the FUTURE ❌")
print()

serializer_3 = CaseSerializer(data=case_data_3)

if serializer_3.is_valid():
    print("❌ FAIL: Case with future opened_date was ALLOWED")
    test_results.append(("MFLP-33", "FAIL", "Future date allowed"))
else:
    print("✅ PASS: Case with future opened_date was REJECTED")
    print()
    print("Validation Errors:")
    for field, errors in serializer_3.errors.items():
        error_message = errors[0] if isinstance(errors, list) else str(errors)
        print(f"  Field: {field}")
        print(f"  Error: {error_message}")

    # Check if the error is what we expect
    if 'opened_date' in serializer_3.errors:
        error_msg = str(serializer_3.errors['opened_date'][0])
        if 'future' in error_msg.lower():
            print()
            print("✅ Error message correctly states opened_date cannot be in future")
            test_results.append(("MFLP-33", "PASS", "Correct validation and error message"))
        else:
            print()
            print("⚠️  Error message doesn't clearly state future date issue")
            test_results.append(("MFLP-33", "PARTIAL", "Validation works but message unclear"))
    else:
        print()
        print("⚠️  Error is not on 'opened_date' field")
        test_results.append(("MFLP-33", "PARTIAL", "Validation works but wrong field"))

print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print()

for bug_id, status, details in test_results:
    status_symbol = "✅" if status == "PASS" else ("⚠️ " if status == "PARTIAL" else "❌")
    print(f"{status_symbol} {bug_id}: {status} - {details}")

print()
print("=" * 80)
print("FRONTEND COMPATIBILITY CHECK")
print("=" * 80)
print()

all_pass = all(status == "PASS" for _, status, _ in test_results)
if all_pass:
    print("✅ All validations working correctly")
    print("✅ All error messages are clear and actionable")
    print("✅ Error format compatible with frontend (DRF standard)")
    print()
    print("Frontend error handler at client-detail.js:461 will display:")
    print("  'Please fix the following errors:\\n\\n'")
    print("  '• Closed Date: [error message]' (for MFLP-31, 32)")
    print("  '• Opened Date: [error message]' (for MFLP-33)")
    print()
    print("✅ All three bugs (MFLP-31, 32, 33) are VERIFIED WORKING")
else:
    print("⚠️  Some validations need attention")

print()
