#!/usr/bin/env python
"""
Test script to verify auto-incremental case number generation
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trust_account_project.settings')
django.setup()

from apps.clients.models import Client, Case

def test_case_number_generation():
    """Test the auto-incremental case number generation"""
    print("🧪 Testing Auto-Incremental Case Number Generation")
    
    # Get a client to use for testing
    client = Client.objects.first()
    if not client:
        print("❌ No clients found. Cannot test case creation.")
        return
    
    print(f"📋 Using client: {client.full_name} (ID: {client.id})")
    
    # Check current cases with CASE- prefix
    existing_case_numbers = list(Case.objects.filter(
        case_number__startswith='CASE-'
    ).values_list('case_number', flat=True).order_by('case_number'))
    
    print(f"📊 Existing CASE-XXXXXX numbers: {existing_case_numbers}")
    
    # Test creating a new case
    print(f"\n🚀 Creating new test case...")
    
    try:
        test_case = Case.objects.create(
            case_title="Test Auto-Generated Case",
            client=client,
            case_description="Testing auto-incremental case number generation",
            case_status="Open",
            is_active=True
        )
        
        print(f"✅ New case created successfully!")
        print(f"   📝 Case Title: {test_case.case_title}")
        print(f"   🔢 Auto-generated Case Number: {test_case.case_number}")
        print(f"   👤 Client: {test_case.client.full_name}")
        print(f"   📅 Created: {test_case.created_at}")
        
        # Verify format
        if test_case.case_number.startswith('CASE-') and len(test_case.case_number) == 12:
            print(f"✅ Format verification: CORRECT (CASE-XXXXXX)")
            numeric_part = test_case.case_number[5:]  # Remove 'CASE-'
            if numeric_part.isdigit() and len(numeric_part) == 6:
                print(f"✅ Numeric part verification: CORRECT ({numeric_part})")
            else:
                print(f"❌ Numeric part verification: FAILED ({numeric_part})")
        else:
            print(f"❌ Format verification: FAILED ({test_case.case_number})")
        
        # Test creating another case
        print(f"\n🚀 Creating second test case...")
        
        test_case2 = Case.objects.create(
            case_title="Second Test Case",
            client=client,
            case_description="Testing sequential numbering",
            case_status="Open",
            is_active=True
        )
        
        print(f"✅ Second case created successfully!")
        print(f"   📝 Case Title: {test_case2.case_title}")
        print(f"   🔢 Auto-generated Case Number: {test_case2.case_number}")
        
        # Verify sequential increment
        first_num = int(test_case.case_number[5:])
        second_num = int(test_case2.case_number[5:])
        
        if second_num == first_num + 1:
            print(f"✅ Sequential increment verification: CORRECT ({first_num} → {second_num})")
        else:
            print(f"❌ Sequential increment verification: FAILED ({first_num} → {second_num})")
        
        # Show all current CASE- numbers
        print(f"\n📊 All CASE-XXXXXX numbers after test:")
        updated_case_numbers = list(Case.objects.filter(
            case_number__startswith='CASE-'
        ).values_list('case_number', flat=True).order_by('case_number'))
        
        for case_number in updated_case_numbers:
            print(f"   - {case_number}")
        
        # Cleanup test cases
        print(f"\n🧹 Cleaning up test cases...")
        test_case.delete()
        test_case2.delete()
        print(f"✅ Test cases deleted successfully!")
        
    except Exception as e:
        print(f"❌ Error creating test case: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_case_number_generation()