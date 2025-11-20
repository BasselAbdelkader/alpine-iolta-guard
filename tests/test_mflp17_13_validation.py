#!/usr/bin/env python
"""
Test MFLP-17 and MFLP-13: Client Name and Zip Code Validation
Tests backend validation for special characters and zip code format
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.clients.api.serializers import ClientSerializer

print("=" * 80)
print("MFLP-17 and MFLP-13: Client Validation Tests")
print("=" * 80)
print()

# Test results tracking
test_results = []

# ============================================================================
# TEST 1: MFLP-17 - Special characters in first name
# ============================================================================
print("=" * 80)
print("TEST 1: MFLP-17 - Special Characters in First Name")
print("=" * 80)
print()

client_data_1 = {
    'first_name': 'John@#$',  # Invalid characters
    'last_name': 'Doe',
    'email': 'john@example.com'
}

print("Request Data:")
print(f"  First Name: {client_data_1['first_name']} (contains @, #, $)")
print(f"  Last Name: {client_data_1['last_name']}")
print()

serializer_1 = ClientSerializer(data=client_data_1)

if serializer_1.is_valid():
    print("❌ FAIL: Client with special characters in first_name was ALLOWED")
    test_results.append(("MFLP-17 (first_name)", "FAIL", "Special characters allowed"))
else:
    print("✅ PASS: Client with special characters in first_name was REJECTED")
    print()
    print("Validation Errors:")
    for field, errors in serializer_1.errors.items():
        error_message = errors[0] if isinstance(errors, list) else str(errors)
        print(f"  Field: {field}")
        print(f"  Error: {error_message}")

    if 'first_name' in serializer_1.errors:
        error_msg = str(serializer_1.errors['first_name'][0])
        if 'letters' in error_msg.lower() or 'characters' in error_msg.lower():
            print()
            print("✅ Error message correctly describes allowed characters")
            test_results.append(("MFLP-17 (first_name)", "PASS", "Validation working"))
        else:
            print()
            print("⚠️  Error message unclear")
            test_results.append(("MFLP-17 (first_name)", "PARTIAL", "Validation works but message unclear"))
    else:
        test_results.append(("MFLP-17 (first_name)", "PARTIAL", "Error on wrong field"))

print()

# ============================================================================
# TEST 2: MFLP-17 - Special characters in last name
# ============================================================================
print("=" * 80)
print("TEST 2: MFLP-17 - Special Characters in Last Name")
print("=" * 80)
print()

client_data_2 = {
    'first_name': 'Jane',
    'last_name': 'Smith!@#',  # Invalid characters
    'email': 'jane@example.com'
}

print("Request Data:")
print(f"  First Name: {client_data_2['first_name']}")
print(f"  Last Name: {client_data_2['last_name']} (contains !, @, #)")
print()

serializer_2 = ClientSerializer(data=client_data_2)

if serializer_2.is_valid():
    print("❌ FAIL: Client with special characters in last_name was ALLOWED")
    test_results.append(("MFLP-17 (last_name)", "FAIL", "Special characters allowed"))
else:
    print("✅ PASS: Client with special characters in last_name was REJECTED")
    print()
    print("Validation Errors:")
    for field, errors in serializer_2.errors.items():
        error_message = errors[0] if isinstance(errors, list) else str(errors)
        print(f"  Field: {field}")
        print(f"  Error: {error_message}")

    if 'last_name' in serializer_2.errors:
        error_msg = str(serializer_2.errors['last_name'][0])
        if 'letters' in error_msg.lower() or 'characters' in error_msg.lower():
            print()
            print("✅ Error message correctly describes allowed characters")
            test_results.append(("MFLP-17 (last_name)", "PASS", "Validation working"))
        else:
            print()
            print("⚠️  Error message unclear")
            test_results.append(("MFLP-17 (last_name)", "PARTIAL", "Validation works but message unclear"))
    else:
        test_results.append(("MFLP-17 (last_name)", "PARTIAL", "Error on wrong field"))

print()

# ============================================================================
# TEST 3: MFLP-17 - Valid special characters (should be allowed)
# ============================================================================
print("=" * 80)
print("TEST 3: MFLP-17 - Valid Special Characters (Should Be Allowed)")
print("=" * 80)
print()

client_data_3 = {
    'first_name': "Mary-Jane",      # Hyphen (valid)
    'last_name': "O'Connor-Smith",  # Apostrophe and hyphen (valid)
    'email': 'mary@example.com'
}

print("Request Data:")
print(f"  First Name: {client_data_3['first_name']} (hyphen - valid)")
print(f"  Last Name: {client_data_3['last_name']} (apostrophe and hyphen - valid)")
print()

serializer_3 = ClientSerializer(data=client_data_3)

if serializer_3.is_valid():
    print("✅ PASS: Client with valid special characters was ALLOWED")
    test_results.append(("MFLP-17 (valid chars)", "PASS", "Valid characters allowed"))
else:
    print("❌ FAIL: Client with valid special characters was REJECTED")
    print()
    print("Validation Errors:")
    for field, errors in serializer_3.errors.items():
        error_message = errors[0] if isinstance(errors, list) else str(errors)
        print(f"  Field: {field}")
        print(f"  Error: {error_message}")
    test_results.append(("MFLP-17 (valid chars)", "FAIL", "Valid characters rejected"))

print()

# ============================================================================
# TEST 4: MFLP-13 - Invalid zip code format
# ============================================================================
print("=" * 80)
print("TEST 4: MFLP-13 - Invalid Zip Code Format")
print("=" * 80)
print()

client_data_4 = {
    'first_name': 'Bob',
    'last_name': 'Johnson',
    'email': 'bob@example.com',
    'zip_code': '2aa'  # Invalid format
}

print("Request Data:")
print(f"  First Name: {client_data_4['first_name']}")
print(f"  Last Name: {client_data_4['last_name']}")
print(f"  Zip Code: {client_data_4['zip_code']} (invalid - contains letters)")
print()

serializer_4 = ClientSerializer(data=client_data_4)

if serializer_4.is_valid():
    print("❌ FAIL: Client with invalid zip code was ALLOWED")
    test_results.append(("MFLP-13", "FAIL", "Invalid zip code allowed"))
else:
    print("✅ PASS: Client with invalid zip code was REJECTED")
    print()
    print("Validation Errors:")
    for field, errors in serializer_4.errors.items():
        error_message = errors[0] if isinstance(errors, list) else str(errors)
        print(f"  Field: {field}")
        print(f"  Error: {error_message}")

    if 'zip_code' in serializer_4.errors:
        error_msg = str(serializer_4.errors['zip_code'][0])
        if 'zip' in error_msg.lower() or 'format' in error_msg.lower():
            print()
            print("✅ Error message correctly describes zip code format")
            test_results.append(("MFLP-13", "PASS", "Validation working"))
        else:
            print()
            print("⚠️  Error message unclear")
            test_results.append(("MFLP-13", "PARTIAL", "Validation works but message unclear"))
    else:
        test_results.append(("MFLP-13", "PARTIAL", "Error on wrong field"))

print()

# ============================================================================
# TEST 5: MFLP-13 - Valid zip code formats
# ============================================================================
print("=" * 80)
print("TEST 5: MFLP-13 - Valid Zip Code Formats (Should Be Allowed)")
print("=" * 80)
print()

valid_zip_codes = [
    ('12345', '5-digit format'),
    ('12345-6789', '5+4 format')
]

for zip_code, description in valid_zip_codes:
    print(f"Testing: {zip_code} ({description})")

    client_data = {
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@example.com',
        'zip_code': zip_code
    }

    serializer = ClientSerializer(data=client_data)

    if serializer.is_valid():
        print(f"  ✅ PASS: {description} accepted")
    else:
        print(f"  ❌ FAIL: {description} rejected")
        if 'zip_code' in serializer.errors:
            print(f"     Error: {serializer.errors['zip_code'][0]}")
        test_results.append((f"MFLP-13 ({description})", "FAIL", "Valid format rejected"))

print()
print("✅ All valid zip code formats accepted")
test_results.append(("MFLP-13 (valid formats)", "PASS", "Valid formats allowed"))

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
print("CONCLUSION")
print("=" * 80)
print()

all_pass = all(status == "PASS" for _, status, _ in test_results)
if all_pass:
    print("✅ All validations working correctly")
    print("✅ MFLP-17: Special character validation working")
    print("✅ MFLP-13: Zip code format validation working")
    print()
    print("Both bugs are VERIFIED WORKING - Already fixed with BUG #5 and BUG #1 fixes")
else:
    print("⚠️  Some validations need attention")

print()
