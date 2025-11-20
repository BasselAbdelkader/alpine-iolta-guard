#!/usr/bin/env python
"""
Test MFLP-34: Inactive Client Case Creation Validation
Tests backend validation and error response format
"""

import os
import sys
import django
from datetime import date

# Setup Django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.clients.models import Client
from apps.clients.api.serializers import CaseSerializer

print("=" * 80)
print("MFLP-34: Inactive Client Case Creation Test")
print("=" * 80)
print()

# Get an inactive client
inactive_client = Client.objects.filter(is_active=False).first()
if not inactive_client:
    print("⚠️  No inactive clients found. Creating one...")
    # Create a test inactive client
    inactive_client = Client.objects.create(
        first_name='Test',
        last_name='Inactive',
        is_active=False
    )

print(f"Testing with inactive client:")
print(f"  ID: {inactive_client.id}")
print(f"  Name: {inactive_client.full_name}")
print(f"  Active Status: {inactive_client.is_active}")
print()

# Try to create a case for this inactive client
case_data = {
    'client': inactive_client.id,
    'case_title': 'Test Case for Inactive Client',
    'case_description': 'This should fail validation',
    'case_status': 'Open',
    'case_amount': 5000,
    'opened_date': date.today()
}

print("Attempting to create case with data:")
for key, value in case_data.items():
    print(f"  {key}: {value}")
print()

# Test the serializer validation
serializer = CaseSerializer(data=case_data)

print("-" * 80)
print("VALIDATION RESULT:")
print("-" * 80)

if serializer.is_valid():
    print("❌ FAIL: Case creation for inactive client was ALLOWED")
    print("   This is a bug - inactive clients should not be able to have new cases!")
else:
    print("✅ PASS: Case creation for inactive client was REJECTED")
    print()
    print("Validation Errors:")
    for field, errors in serializer.errors.items():
        error_message = errors[0] if isinstance(errors, list) else str(errors)
        print(f"  Field: {field}")
        print(f"  Error: {error_message}")
        print()

    # Check if the error matches expected format
    if 'client' in serializer.errors:
        error_msg = str(serializer.errors['client'][0])
        if 'inactive' in error_msg.lower():
            print("✅ Error message correctly mentions 'inactive'")
        else:
            print("⚠️  Error message doesn't mention 'inactive'")
            print(f"   Actual message: {error_msg}")
    else:
        print("⚠️  Error is not on 'client' field")
        print(f"   Actual errors: {serializer.errors}")

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
print()

# Check error response format for frontend
print("FRONTEND ERROR FORMAT CHECK:")
print("-" * 80)
print("The frontend expects errors in this format:")
print("  { 'field_name': ['Error message'] }")
print()
print("Backend returns:")
print(f"  {dict(serializer.errors)}")
print()

# Test if frontend would properly display this error
if serializer.errors:
    frontend_display = "Please fix the following errors:\\n\\n"
    for field, messages in serializer.errors.items():
        field_name = field.replace('_', ' ').title()
        message = messages[0] if isinstance(messages, list) else str(messages)
        frontend_display += f"• {field_name}: {message}\\n"

    print("Frontend would display:")
    print(frontend_display)
    print()
    print("✅ Error format is compatible with frontend error handler")
else:
    print("⚠️  No errors returned (case was allowed)")

print()
