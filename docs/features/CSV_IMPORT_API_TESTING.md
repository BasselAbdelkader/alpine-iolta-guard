# CSV Import API - Testing Guide

**Date:** November 13, 2025
**Status:** ✅ Backend API Complete - Ready for Frontend Integration

---

## 🎯 API Endpoints

### **Base URL:** `http://localhost/api/v1/settings/`

### **1. CSV Preview (POST)**
```
POST /api/v1/settings/csv/preview/
```

**Purpose:** Validate CSV file and show counts before import

**Request:**
```http
POST /api/v1/settings/csv/preview/
Content-Type: multipart/form-data

csv_file: [CSV file upload]
```

**Response (Success - 200 OK):**
```json
{
  "preview_summary": {
    "expected_clients": 3,
    "existing_clients": 0,
    "expected_cases": 3,
    "existing_cases": 0,
    "expected_vendors": 0,
    "existing_vendors": 0,
    "expected_transactions": 3,
    "total_rows": 3,
    "validation_errors_count": 0
  },
  "validation_errors": [],
  "preview_rows": [
    {
      "row": 2,
      "client": "John Smith",
      "client_status": "New",
      "case": "Personal Injury Case",
      "transaction_amount": "50000.00",
      "errors": []
    },
    {
      "row": 3,
      "client": "Jane Doe",
      "client_status": "Existing",
      "case": "Workers Compensation",
      "transaction_amount": "75000.00",
      "errors": []
    }
  ],
  "has_errors": false,
  "can_proceed": true
}
```

**Response (Validation Errors - 200 OK):**
```json
{
  "preview_summary": {
    "expected_clients": 2,
    "existing_clients": 0,
    "expected_cases": 1,
    "existing_cases": 0,
    "expected_vendors": 0,
    "existing_vendors": 0,
    "expected_transactions": 1,
    "total_rows": 3,
    "validation_errors_count": 2
  },
  "validation_errors": [
    {
      "row": 2,
      "errors": ["Row 2: Missing first_name or last_name"]
    },
    {
      "row": 4,
      "errors": ["Row 4: Invalid transaction amount format"]
    }
  ],
  "preview_rows": [...],
  "has_errors": true,
  "can_proceed": false
}
```

**Response (Invalid File - 400 Bad Request):**
```json
{
  "csv_file": ["File must be a CSV file"]
}
```

---

### **2. CSV Import Confirm (POST)**
```
POST /api/v1/settings/csv/import/
```

**Purpose:** Execute the CSV import after preview validation

**Request:**
```http
POST /api/v1/settings/csv/import/
Content-Type: multipart/form-data

csv_file: [CSV file upload]
```

**Response (Success - 201 Created):**
```json
{
  "message": "CSV import completed successfully",
  "audit": {
    "id": 1,
    "import_date": "2025-11-13T14:30:00Z",
    "import_type": "csv",
    "file_name": "clients_import.csv",
    "status": "completed",
    "total_records": 3,
    "successful_records": 3,
    "failed_records": 0,
    "clients_created": 3,
    "cases_created": 3,
    "transactions_created": 3,
    "vendors_created": 0,
    "expected_clients": 3,
    "expected_cases": 3,
    "expected_transactions": 3,
    "expected_vendors": 0,
    "existing_clients": 0,
    "existing_cases": 0,
    "existing_vendors": 0,
    "error_log": "",
    "imported_by": "admin",
    "created_at": "2025-11-13T14:30:00Z",
    "completed_at": "2025-11-13T14:30:15Z"
  }
}
```

**Response (Import Failed - 500 Internal Server Error):**
```json
{
  "error": "Import failed: No bank account found. Please create a bank account first."
}
```

---

### **3. List Import Audits (GET)**
```
GET /api/v1/settings/import-audits/
```

**Purpose:** Retrieve all import history

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "import_date": "2025-11-13T14:30:00Z",
    "import_type": "csv",
    "file_name": "clients_import.csv",
    "status": "completed",
    "total_records": 3,
    "successful_records": 3,
    "failed_records": 0,
    "clients_created": 3,
    "cases_created": 3,
    "transactions_created": 3,
    "vendors_created": 0,
    "expected_clients": 3,
    "expected_cases": 3,
    "expected_transactions": 3,
    "expected_vendors": 0,
    "existing_clients": 0,
    "existing_cases": 0,
    "existing_vendors": 0,
    "error_log": "",
    "imported_by": "admin",
    "created_at": "2025-11-13T14:30:00Z",
    "completed_at": "2025-11-13T14:30:15Z"
  }
]
```

---

### **4. Delete Import Batch (DELETE)**
```
DELETE /api/v1/settings/import-audits/{id}/delete/
```

**Purpose:** Delete an import batch and all its associated data

**Response (Success - 200 OK):**
```json
{
  "message": "Import batch deleted successfully",
  "deleted_counts": {
    "clients": 3,
    "cases": 3,
    "transactions": 3,
    "vendors": 0
  }
}
```

**Response (Not Found - 404):**
```json
{
  "error": "Import audit not found"
}
```

---

## 📋 CSV File Format

### **Headers (Required):**
```csv
first_name,last_name,email,phone,address,city,state,zip_code,case_description,case_amount,transaction_date,transaction_type,amount,description
```

### **Sample Data:**
```csv
first_name,last_name,email,phone,address,city,state,zip_code,case_description,case_amount,transaction_date,transaction_type,amount,description
John,Smith,john.smith@email.com,(555) 123-4567,123 Main St,New York,NY,10001,Personal Injury Case,50000.00,2025-01-15,DEPOSIT,50000.00,Initial deposit for settlement
Jane,Doe,jane.doe@email.com,(555) 987-6543,456 Oak Ave,Los Angeles,CA,90001,Workers Compensation,75000.00,2025-01-20,DEPOSIT,75000.00,Settlement payment
Michael,Johnson,mjohnson@email.com,(555) 456-7890,789 Pine Rd,Chicago,IL,60601,Auto Accident,35000.00,2025-02-01,DEPOSIT,35000.00,Insurance settlement
```

### **Field Specifications:**

**Required Fields:**
- `first_name` - Client first name (text)
- `last_name` - Client last name (text)

**Optional Client Fields:**
- `email` - Email address (email format)
- `phone` - Phone number (US format: (555) 123-4567)
- `address` - Street address
- `city` - City name
- `state` - 2-letter state code (AL, CA, NY, etc.)
- `zip_code` - ZIP code

**Optional Case Fields:**
- `case_description` - Case description/notes
- `case_amount` - Settlement amount (decimal: 50000.00)

**Optional Transaction Fields:**
- `transaction_date` - Date (YYYY-MM-DD or MM/DD/YYYY)
- `transaction_type` - One of: DEPOSIT, WITHDRAWAL, TRANSFER_OUT, TRANSFER_IN
- `amount` - Transaction amount (decimal: 50000.00)
- `description` - Transaction description

**Optional Vendor Fields:**
- `vendor_name` - Vendor company name
- `vendor_contact` - Contact person name
- `vendor_email` - Vendor email
- `vendor_phone` - Vendor phone

---

## 🧪 Testing with cURL

### **1. Test CSV Preview:**
```bash
curl -X POST http://localhost/api/v1/settings/csv/preview/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  -F "csv_file=@test_import_sample.csv"
```

### **2. Test CSV Import:**
```bash
curl -X POST http://localhost/api/v1/settings/csv/import/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  -F "csv_file=@test_import_sample.csv"
```

### **3. List Import Audits:**
```bash
curl -X GET http://localhost/api/v1/settings/import-audits/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID"
```

### **4. Delete Import Batch:**
```bash
curl -X DELETE http://localhost/api/v1/settings/import-audits/1/delete/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID"
```

---

## 🧪 Testing with Python

### **Test Preview Endpoint:**
```python
import requests

# Login first to get session
session = requests.Session()
session.post('http://localhost/api/auth/login/', json={
    'username': 'admin',
    'password': 'your_password'
})

# Test preview
with open('test_import_sample.csv', 'rb') as f:
    response = session.post(
        'http://localhost/api/v1/settings/csv/preview/',
        files={'csv_file': f}
    )
    print(response.json())
```

### **Test Import Endpoint:**
```python
# Import CSV
with open('test_import_sample.csv', 'rb') as f:
    response = session.post(
        'http://localhost/api/v1/settings/csv/import/',
        files={'csv_file': f}
    )
    print(response.json())
```

---

## ✅ Validation Rules

The API validates:

1. **File Type:** Must be .csv extension
2. **File Size:** Maximum 10MB
3. **Required Fields:** first_name and last_name must exist
4. **Client Uniqueness:** Checks if client already exists (case-insensitive)
5. **Case Amount:** Must be positive decimal
6. **Transaction Amount:** Must be greater than zero
7. **Transaction Date:** Valid date format (YYYY-MM-DD or MM/DD/YYYY)
8. **Transaction Type:** Must be valid type (DEPOSIT, WITHDRAWAL, etc.)
9. **State Code:** Must be valid 2-letter US state code
10. **Vendor Uniqueness:** Checks if vendor already exists (case-insensitive)

---

## 🔄 Import Process Flow

```
1. User uploads CSV file
   ↓
2. Backend validates file format
   ↓
3. Backend analyzes CSV content
   ↓
4. Backend checks for existing entities
   ↓
5. Backend returns preview with counts
   ↓
6. User reviews preview
   ↓
7. User confirms or cancels
   ↓
8. If confirmed:
   - Creates ImportAudit record
   - Creates/updates clients
   - Creates cases with formatted titles
   - Creates transactions
   - Creates vendors (if applicable)
   - Tags all with data_source='csv_import'
   - Links all to import_batch_id
   - Updates ImportAudit with statistics
   ↓
9. Returns import results
```

---

## 📊 Expected vs Actual Counts

The ImportAudit record stores both:

**Preview Counts (before import):**
- `expected_clients` - How many NEW clients will be created
- `expected_cases` - How many NEW cases will be created
- `expected_transactions` - How many transactions will be created
- `expected_vendors` - How many NEW vendors will be created
- `existing_clients` - How many clients already exist
- `existing_cases` - How many cases already exist
- `existing_vendors` - How many vendors already exist

**Actual Counts (after import):**
- `clients_created` - Actual clients created
- `cases_created` - Actual cases created
- `transactions_created` - Actual transactions created
- `vendors_created` - Actual vendors created
- `successful_records` - Total successful records
- `failed_records` - Total failed records

This allows comparison to verify the import executed as expected.

---

## 🎯 Next Steps

1. **Create Frontend UI** for Import Management page
2. **Replace Export page** with Import Management
3. **Add progress indicators** during import
4. **Implement delete confirmation** with count display
5. **Add import history filtering** by date, type, status

---

## 📁 Files Created

**Backend:**
- `/app/apps/settings/models.py` - ImportAudit model (updated)
- `/app/apps/settings/api/__init__.py` - API module
- `/app/apps/settings/api/serializers.py` - API serializers
- `/app/apps/settings/api/views.py` - API views (preview, import, list, delete)
- `/app/apps/settings/api/urls.py` - API URL routing
- `/app/apps/api/urls.py` - Main API routing (updated)

**Test Files:**
- `/home/amin/Projects/ve_demo/test_import_sample.csv` - Sample CSV for testing

**Documentation:**
- `/home/amin/Projects/ve_demo/DATA_SOURCE_IMPLEMENTATION_SUMMARY.md` - Implementation summary
- `/home/amin/Projects/ve_demo/CSV_IMPORT_API_TESTING.md` - This file

---

**Status:** ✅ Backend API Complete and Ready for Testing
**Next:** Frontend UI Development
