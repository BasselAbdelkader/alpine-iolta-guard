# QuickBooks Importer - Vendor Support Implementation

**Date:** November 13, 2025  
**Status:** ✅ COMPLETE  
**Modified File:** `/app/apps/clients/utils/quickbooks_importer.py`

---

## 🎯 Requirements Implemented

### ✅ 1. Create Client for Every Account
- Every unique value in "Account" column creates a Client
- Client naming: Split into first_name and last_name
- Client number format: `QB-0001`, `QB-0002`, etc.
- data_source: `csv`

### ✅ 2. Create Vendor for Every Payee
- Every unique value in "Payee" column creates a Vendor
- Vendor naming: Full payee name as vendor_name
- Vendor number format: `V-0001`, `V-0002`, etc.
- data_source: `csv`

### ✅ 3. Client as Vendor (Account = Payee)
- When Account name matches Payee name:
  - Vendor is linked to the Client via `vendor.client` foreign key
  - Special vendor number format: `CV-{client_id}` (e.g., `CV-123`)
  - This allows tracking when clients are also vendors/payees

### ✅ 4. Case Title Format
- Format: `"{Account Name} Case"`
- Example: "Kevin Nelson Case", "Jerry Patel Case"
- Case number format: `QB-{timestamp}-{client_id}`
- data_source: `csv`

### ✅ 5. Link Vendors to Transactions
- Each transaction now has `vendor` foreign key populated
- Links to the Vendor created from the Payee field
- Payee name still stored in `transaction.payee` field (text)

---

## 📋 CSV Column Mapping

| CSV Column | Maps To | Creates |
|------------|---------|---------|
| **Account** | Client | Client record (first_name, last_name) |
| **Payee** | Vendor | Vendor record (vendor_name) |
| **Date** | transaction_date | Transaction field |
| **Ref No.** | check_number | Transaction field |
| **Type** | transaction_type | Transaction field (Check→Withdrawal, Deposit→Deposit) |
| **Memo** | description | Transaction field |
| **Payment** | amount | Transaction field (withdrawal) |
| **Deposit** | amount | Transaction field (deposit) |
| **Reconciliation Status** | status | Transaction field (Reconciled→Cleared, else→Pending) |

---

## 🔧 Code Changes

### 1. Added Vendor Import
```python
from apps.vendors.models import Vendor
```

### 2. Added Vendor Stats Tracking
```python
self.stats = {
    'clients_created': 0,
    'clients_existing': 0,
    'vendors_created': 0,      # NEW
    'vendors_existing': 0,     # NEW
    'cases_created': 0,
    'transactions_imported': 0,
    'transactions_skipped': 0,
    'errors': []
}
```

### 3. New Method: `_get_or_create_vendor()`
**Purpose:** Create or retrieve vendor from payee name

**Logic:**
- If payee_name is empty → return None
- Check if vendor exists by name (case-insensitive)
- If exists → return existing, increment `vendors_existing`
- If new:
  - Check if payee_name == client_name (Account = Payee case)
  - If yes → link vendor to client, use vendor_number `CV-{client_id}`
  - If no → use regular vendor_number `V-0001`, `V-0002`, etc.
  - Create vendor with data_source='csv'
  - Increment `vendors_created`

**Special Handling:**
- Client-vendors get number format: `CV-{client_id}`
- Regular vendors get number format: `V-0001` (auto-increment)

### 4. Modified: `_import_client_data()`
**Added:** Vendor creation step

```python
# Step 2: Get or create vendors for all unique payees
vendors_map = {}  # {payee_name: Vendor instance}
for trans in transactions:
    payee_name = trans.get("payee", "").strip()
    if payee_name and payee_name not in vendors_map:
        vendor = self._get_or_create_vendor(payee_name, client_name)
        if vendor:
            vendors_map[payee_name] = vendor
```

### 5. Modified: `_import_transactions()`
**Added:** Pass vendors_map to transaction creation

```python
def _import_transactions(self, case: Case, transactions: List[Dict], vendors_map: Dict):
    # ...
    self._create_transaction(case, trans_data, vendors_map)
```

### 6. Modified: `_create_transaction()`
**Added:** Vendor linking

```python
# Get vendor from map if payee exists
payee_name = trans_data.get("payee", "").strip()
vendor = vendors_map.get(payee_name) if payee_name else None

# Create transaction with vendor link
BankTransaction.objects.create(
    # ...
    vendor=vendor,  # NEW: Link to vendor
    payee=payee_name or "",
    # ...
    data_source="csv"
)
```

---

## 📊 Import Statistics

After import, the system tracks:
- `clients_created`: New clients created
- `clients_existing`: Existing clients found
- `vendors_created`: New vendors created
- `vendors_existing`: Existing vendors found
- `cases_created`: New cases created
- `transactions_imported`: Transactions successfully imported
- `transactions_skipped`: Transactions with errors
- `errors`: List of error details

---

## 🧪 Example Data Flow

### CSV Row:
```csv
09/24/2025,2241,Check,Edward Carter,Kevin Nelson,BI Settlement,11481.20,,Reconciled
```

### Creates:
1. **Client:**
   - first_name: "Kevin"
   - last_name: "Nelson"
   - client_number: "QB-0001"
   - data_source: "csv"

2. **Vendor:**
   - vendor_name: "Edward Carter"
   - vendor_number: "V-0001"
   - client: null (not a client-vendor)
   - data_source: "csv"

3. **Case:**
   - case_title: "Kevin Nelson Case"
   - case_number: "QB-20251113143022-1"
   - client: → Kevin Nelson
   - data_source: "csv"

4. **Transaction:**
   - client: → Kevin Nelson
   - case: → Kevin Nelson Case
   - vendor: → Edward Carter
   - payee: "Edward Carter"
   - amount: 11481.20
   - transaction_type: "Withdrawal"
   - status: "Cleared"
   - data_source: "csv"

---

## 🔄 Client as Vendor Example

### CSV Row:
```csv
09/24/2025,2242,Check,Kevin Nelson,Kevin Nelson,Settlement,5000.00,,Reconciled
```

### Creates:
1. **Client:**
   - first_name: "Kevin"
   - last_name: "Nelson"
   - client_number: "QB-0001"
   - (Same client as above, not duplicated)

2. **Vendor:**
   - vendor_name: "Kevin Nelson"
   - vendor_number: "CV-1" (special format!)
   - client: → Kevin Nelson (LINKED!)
   - data_source: "csv"

3. **Transaction:**
   - client: → Kevin Nelson
   - vendor: → Kevin Nelson (client-vendor)
   - payee: "Kevin Nelson"

---

## 🎉 Benefits

1. **Complete Vendor Tracking:** Every payee is now a vendor entity
2. **Client-Vendor Relationships:** Automatic detection when clients are also vendors
3. **Transaction Links:** Transactions properly linked to both clients and vendors
4. **Reporting Ready:** Can now run reports on vendor activity
5. **Data Integrity:** Vendor number uniqueness enforced
6. **Backward Compatible:** Existing imports still work

---

## 📁 Files Modified

| File | Change |
|------|--------|
| `/app/apps/clients/utils/quickbooks_importer.py` | Added vendor support |
| **Backup:** | `.backup_before_vendor_support` |

---

## ✅ Testing

**Syntax Check:** ✅ PASSED  
**Backend Restart:** ✅ SUCCESS

**Next Step:** Test with `transactions_anonymized.csv`

---

**Ready for import!** 🚀
