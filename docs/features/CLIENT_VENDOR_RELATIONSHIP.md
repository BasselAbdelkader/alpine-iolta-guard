# Client-Vendor Relationship in IOLTA Guard

**Date:** November 13, 2025
**Feature:** Handling when a Client is also a Vendor/Payee

---

## 🎯 Overview

In trust accounting, it's common for a **client to also be a vendor/payee**. This happens when:
- Client receives a disbursement from their own trust account
- Client is paid back expenses they advanced
- Settlement funds are distributed to the client

---

## 📊 Database Design

### **Vendor Model Has Client Link:**

**File:** `/app/apps/vendors/models.py` (line 55)

```python
class Vendor(models.Model):
    vendor_name = models.CharField(max_length=200)
    # ... other fields ...

    # Link to client if vendor is also a client
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="If vendor is also a client"
    )
```

### **Vendor Number Generation:**

When a vendor is linked to a client, it gets a special vendor number:

**Format:** `CV-XXX` (Client-Vendor)
- `CV-001` = First client-vendor
- `VEN-001` = Regular vendor (not a client)

**Example:**
- Client: John Smith (Client #CL-123)
- Vendor: John Smith (Vendor #CV-123) ← Linked to client

---

## 🔄 CSV Import Behavior (UPDATED)

### **Before Update:**
- Vendor created separately
- **NOT linked** to client even if same name
- `client` field = NULL

### **After Update (Now):**
- System detects if `vendor_name` matches `client full_name`
- If match found, vendor is **automatically linked** to client
- `client` field = Client object
- Vendor number auto-generated as `CV-XXX`

### **Import Logic:**

**File:** `/app/apps/settings/api/views.py` (lines 347-374)

```python
# Check if vendor name matches current client
client_full_name = f"{first_name} {last_name}"
is_client_vendor = vendor_name.lower() == client_full_name.lower()

# Create vendor with client link if same person
vendor = Vendor.objects.create(
    vendor_name=vendor_name,
    # ... other fields ...
    client=client if is_client_vendor else None,  # Auto-link
    data_source='csv_import',
    import_batch_id=audit.id,
)
```

### **Detection Rules:**

**Exact Match (Case-Insensitive):**
```
CSV Row:
  first_name: John
  last_name: Smith
  vendor_name: John Smith  ← Matches!

Result: Vendor "John Smith" linked to Client "John Smith"
```

**No Match:**
```
CSV Row:
  first_name: John
  last_name: Smith
  vendor_name: ABC Medical Supply  ← Different

Result: Vendor "ABC Medical Supply" created as regular vendor
```

---

## 📋 CSV Format Examples

### **Example 1: Client Receiving Settlement**

```csv
first_name,last_name,case_description,transaction_type,amount,vendor_name
John,Smith,Personal Injury,WITHDRAWAL,50000.00,John Smith
```

**Result:**
- Client created: John Smith
- Vendor created: John Smith ← **Linked to client**
- Transaction: $50,000 withdrawal to John Smith (client-vendor)

### **Example 2: Client Paid + Regular Vendor**

```csv
first_name,last_name,case_description,transaction_type,amount,vendor_name
Jane,Doe,Auto Accident,DEPOSIT,100000.00,
Jane,Doe,Auto Accident,WITHDRAWAL,25000.00,Jane Doe
Jane,Doe,Auto Accident,WITHDRAWAL,5000.00,Medical Records Plus
```

**Result:**
- Client: Jane Doe
- Vendor 1: Jane Doe ← **Linked to client** (CV-XXX)
- Vendor 2: Medical Records Plus (regular vendor, VEN-XXX)
- Transaction 1: $100,000 deposit
- Transaction 2: $25,000 to Jane Doe (client-vendor)
- Transaction 3: $5,000 to Medical Records Plus (regular vendor)

---

## 🔍 How to Identify Client-Vendors

### **In Database:**

```sql
-- Get all client-vendors
SELECT v.vendor_name, v.vendor_number, c.first_name, c.last_name
FROM vendors v
INNER JOIN clients c ON v.client_id = c.id
ORDER BY v.vendor_name;
```

### **In Django:**

```python
from apps.vendors.models import Vendor

# Get all client-vendors
client_vendors = Vendor.objects.filter(client__isnull=False)

for vendor in client_vendors:
    print(f'{vendor.vendor_name} (#{vendor.vendor_number}) → Client: {vendor.client.full_name}')
```

### **In API:**

The Vendor serializer includes the client relationship:

```json
{
  "vendor_name": "John Smith",
  "vendor_number": "CV-001",
  "client": {
    "id": 123,
    "first_name": "John",
    "last_name": "Smith"
  }
}
```

---

## 💰 Impact on Balances

### **Client Balance:**

When a client receives money as a vendor:

```
Transaction: WITHDRAWAL to John Smith (client-vendor)
Amount: $10,000

Client Balance Calculation:
  Deposits: $50,000
  Withdrawals: $10,000 ← This withdrawal
  Balance: $40,000
```

**The withdrawal REDUCES the client's trust balance** (as expected).

### **Vendor Balance:**

Vendors don't have balances. They only appear in:
- Transaction history (as payee)
- Vendor list
- Reports

---

## 🎨 UI Display Recommendations

### **Vendor List Page:**

Show indicator for client-vendors:

```
Vendor Name          | Vendor #  | Type
---------------------|-----------|------------------
John Smith          | CV-001    | Client-Vendor 👤
Medical Records     | VEN-002   | Regular Vendor
Jane Doe            | CV-003    | Client-Vendor 👤
ABC Supply          | VEN-004   | Regular Vendor
```

### **Transaction Display:**

```
Date       | Type       | Amount    | Payee/Vendor
-----------|------------|-----------|------------------
2025-11-13 | Deposit    | $50,000   | -
2025-11-14 | Withdrawal | $10,000   | John Smith (Client) 👤
2025-11-15 | Withdrawal | $5,000    | Medical Records
```

### **Vendor Detail Page:**

If vendor is linked to client, show:

```
┌─────────────────────────────────────────┐
│ Vendor: John Smith                      │
│ Vendor #: CV-001                        │
│                                         │
│ ⚠️ This vendor is also a client:       │
│   Client: John Smith (#CL-123)         │
│   [View Client Details]                │
└─────────────────────────────────────────┘
```

---

## 📊 Reporting Implications

### **Client Ledger Report:**

Shows withdrawals to self:

```
Client: John Smith (#CL-123)

Date       | Description        | Debit     | Credit    | Balance
-----------|--------------------|-----------|-----------|---------
2025-11-13 | Initial Deposit    | $50,000   |           | $50,000
2025-11-14 | Payment to Client  |           | $10,000   | $40,000
```

### **Vendor Payment Report:**

Shows payments to client-vendors separately:

```
VENDOR PAYMENTS - November 2025

Client-Vendors:
  John Smith (CV-001): $10,000
  Jane Doe (CV-003): $25,000

Regular Vendors:
  Medical Records (VEN-002): $5,000
  ABC Supply (VEN-004): $3,000
```

---

## ⚠️ Important Notes

### **1. One Client = One Vendor Record**

If a client appears as vendor multiple times in CSV, only ONE vendor record is created:

```csv
John,Smith,...,John Smith  ← Creates Vendor #CV-001
John,Smith,...,John Smith  ← Uses existing CV-001 (duplicate)
```

### **2. Name Must Match Exactly**

The system checks for exact match (case-insensitive):

```
✅ Match: "John Smith" = "john smith"
✅ Match: "JOHN SMITH" = "John Smith"
❌ No Match: "John Smith" ≠ "J. Smith"
❌ No Match: "John Smith" ≠ "John A. Smith"
```

### **3. Manual Override**

Users can manually link/unlink vendors to clients in the UI:
- Edit vendor
- Select client from dropdown
- Save

### **4. Deleting Client**

If client is deleted:
- Linked vendor is **also deleted** (CASCADE)
- Transactions remain but vendor_id becomes NULL

---

## 🔧 Testing the Feature

### **Test Scenario 1: Client as Vendor**

**CSV:**
```csv
first_name,last_name,transaction_type,amount,vendor_name
Alice,Brown,DEPOSIT,100000,
Alice,Brown,WITHDRAWAL,50000,Alice Brown
```

**Expected:**
- ✅ Client created: Alice Brown
- ✅ Vendor created: Alice Brown (CV-XXX)
- ✅ Vendor linked to client
- ✅ Client balance: $50,000 ($100k - $50k)

### **Test Scenario 2: Mixed Vendors**

**CSV:**
```csv
first_name,last_name,transaction_type,amount,vendor_name
Bob,Jones,DEPOSIT,75000,
Bob,Jones,WITHDRAWAL,25000,Bob Jones
Bob,Jones,WITHDRAWAL,10000,ABC Medical
```

**Expected:**
- ✅ Client: Bob Jones
- ✅ Vendor 1: Bob Jones (CV-XXX) ← Linked
- ✅ Vendor 2: ABC Medical (VEN-XXX) ← Not linked
- ✅ Client balance: $40,000

---

## 📁 Files Modified

1. **`/app/apps/settings/api/views.py`** (lines 347-374)
   - Added client-vendor detection logic
   - Auto-links vendor to client if name matches

---

## ✅ Summary

**Before:** Client-vendors were not linked (bug)

**Now:**
- ✅ System auto-detects when vendor name = client name
- ✅ Vendor automatically linked to client
- ✅ Special vendor number (CV-XXX) for client-vendors
- ✅ Balance calculations work correctly
- ✅ Transactions properly tracked

**Going Forward:**
- All new CSV imports will auto-link client-vendors
- Frontend UI can show client-vendor indicator
- Reports can distinguish client-vendors from regular vendors

---

**Status:** ✅ Implemented and Ready
**Next:** Update frontend UI to show client-vendor relationships
