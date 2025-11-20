#!/usr/bin/env python
"""
MFLP-34: Test actual API response for inactive client case creation
Simulates what the frontend JavaScript receives from the API
"""

import os
import sys
import django
import json
from datetime import date

# Setup Django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import RequestFactory
from rest_framework.test import force_authenticate
from apps.clients.models import Client, User
from apps.clients.api.views import CaseViewSet

print("=" * 80)
print("MFLP-34: API Response Test for Inactive Client Case Creation")
print("=" * 80)
print()

# Get an inactive client
inactive_client = Client.objects.filter(is_active=False).first()
print(f"Testing with inactive client: {inactive_client.full_name} (ID: {inactive_client.id})")
print()

# Get a user for authentication
user = User.objects.filter(is_staff=True).first()
if not user:
    user = User.objects.first()

# Create test data
case_data = {
    'client': inactive_client.id,
    'case_title': 'Test Case for Inactive Client',
    'case_description': 'This should fail validation',
    'case_status': 'Open',
    'case_amount': 5000,
    'opened_date': str(date.today())
}

print("Request Data:")
print(json.dumps(case_data, indent=2))
print()

# Create a mock request to the API
factory = RequestFactory()
request = factory.post('/api/v1/cases/',
                       data=json.dumps(case_data),
                       content_type='application/json')
force_authenticate(request, user=user)

# Call the viewset create action
view = CaseViewSet.as_view({'post': 'create'})
response = view(request)

print("=" * 80)
print("API RESPONSE")
print("=" * 80)
print(f"Status Code: {response.status_code}")
print()

if response.status_code == 400:
    print("✅ Correctly returned 400 Bad Request")
    print()
    print("Response Data (what frontend receives):")
    print(json.dumps(response.data, indent=2, default=str))
    print()

    # Check error structure
    if isinstance(response.data, dict):
        print("✅ Response is a dictionary (correct format)")
        if 'client' in response.data:
            print("✅ 'client' field error exists")
            client_error = response.data['client']
            print(f"   Error: {client_error}")

            if isinstance(client_error, list):
                print("✅ Error is a list (frontend expects this)")
                error_msg = str(client_error[0])
                if 'inactive' in error_msg.lower():
                    print("✅ Error message mentions 'inactive'")
                else:
                    print("⚠️  Error doesn't mention 'inactive'")
            else:
                print("⚠️  Error is not a list, it's:", type(client_error))
        else:
            print("⚠️  No 'client' field in response")
            print("   Available fields:", list(response.data.keys()))
    else:
        print("⚠️  Response is not a dictionary:", type(response.data))

elif response.status_code == 201:
    print("❌ FAIL: Case was created successfully (should have been rejected)")
    print()
    print("Created case data:")
    print(json.dumps(response.data, indent=2, default=str))
else:
    print(f"Unexpected status code: {response.status_code}")
    print()
    print("Response:")
    print(json.dumps(response.data, indent=2, default=str))

print()
print("=" * 80)
print("FRONTEND COMPATIBILITY CHECK")
print("=" * 80)
print()

if response.status_code == 400 and isinstance(response.data, dict):
    # Simulate frontend error handling
    print("Simulating frontend error handler:")
    print()
    print("JavaScript code:")
    print("  if (!response.ok) {")
    print("    const errorData = await response.json();")
    print(f"    // errorData = {json.dumps(response.data, default=str)}")
    print("    error.validationErrors = errorData;")
    print("  }")
    print()
    print("  if (error.validationErrors) {")
    print("    let errorMessage = 'Please fix the following errors:\\n\\n';")

    error_display = "Please fix the following errors:\n\n"
    for field, messages in response.data.items():
        field_name = field.replace('_', ' ').title()
        message = messages[0] if isinstance(messages, list) else str(messages)
        error_display += f"• {field_name}: {message}\n"
        print(f"    errorMessage += '• {field_name}: {message}\\n';")

    print("    showErrorMessage(errorMessage);")
    print("  }")
    print()
    print("-" * 80)
    print("FINAL ERROR MESSAGE DISPLAYED TO USER:")
    print("-" * 80)
    print(error_display)
    print()
    print("✅ Frontend should display the error correctly!")

else:
    print("⚠️  Response format may not be compatible with frontend error handler")

print()
print("=" * 80)
print("CONCLUSION")
print("=" * 80)
print()

if response.status_code == 400:
    if 'client' in response.data:
        error_msg = str(response.data['client'][0]) if isinstance(response.data['client'], list) else str(response.data['client'])
        if 'inactive' in error_msg.lower():
            print("✅ Backend validation works correctly")
            print("✅ Error response format is compatible with frontend")
            print("✅ Error message is clear and helpful")
            print()
            print("If the bug still exists, the issue might be:")
            print("  1. Frontend JavaScript not loaded/executed")
            print("  2. showErrorMessage() function not working")
            print("  3. Error caught by different error handler")
            print("  4. Console errors preventing JavaScript execution")
            print()
            print("Recommendation: Check browser console for JavaScript errors")
        else:
            print("⚠️  Error message doesn't mention inactive client")
    else:
        print("⚠️  Error not on 'client' field")
else:
    print("❌ Backend validation not working")

print()
