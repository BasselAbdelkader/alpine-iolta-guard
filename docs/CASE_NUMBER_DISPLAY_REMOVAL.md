# Frontend Change: Display case_title Instead of case_number

**Date:** November 8, 2025
**Type:** Frontend UI Enhancement
**Reason:** Customer request to show only case titles, not case numbers

---

## Summary

Updated all frontend displays to show `case_title` instead of `case_number` while maintaining `id` for all backend API communication.

---

## Important: Backend Communication Unchanged ✅

**The frontend still uses `case.id` for all API operations:**
- ✅ Creating transactions
- ✅ Updating cases
- ✅ Deleting cases
- ✅ Filtering/searching

**What changed:** Only the visual display text
**What stayed the same:** All API communication using `id`

---

## Files Modified

### 1. **client-ledger.js** (Line 121)

**Before:**
```javascript
option.value = caseItem.id;
option.textContent = `${caseItem.case_number} - ${caseItem.case_title}`;
// Displayed: "CASE-000006 - Personal Injury Case"
```

**After:**
```javascript
option.value = caseItem.id;  // Backend uses ID for API calls
option.textContent = `${caseItem.case_title}`;  // Display only case title
// Displays: "Personal Injury Case"
```

**Backup:** `/usr/share/nginx/html/js/client-ledger.js.backup_before_case_title`

---

### 2. **bank-transactions.js** (Lines 730, 1431, 1436)

**Location 1 - Line 730:**
**Before:**
```javascript
option.value = caseObj.id;
option.textContent = `${caseObj.case_number} - ${caseObj.case_title || caseObj.case_description}`;
// Displayed: "CASE-000006 - Personal Injury Case"
```

**After:**
```javascript
option.value = caseObj.id;  // Backend uses ID for API calls
option.textContent = `${caseObj.case_title || caseObj.case_description}`;  // Display only case title
// Displays: "Personal Injury Case"
```

**Location 2 - Line 1431:**
**Before:**
```javascript
option.value = caseObj.id;
option.textContent = `${caseObj.case_number} - ${caseObj.case_title || caseObj.case_description}`;
```

**After:**
```javascript
option.value = caseObj.id;  // Backend uses ID for API calls
option.textContent = `${caseObj.case_title || caseObj.case_description}`;  // Display only case title
```

**Location 3 - Line 1436 (console log):**
**Before:**
```javascript
console.log('[CASE DROPDOWN] Added case:', caseObj.case_number, 'Balance:', caseObj.current_balance);
```

**After:**
```javascript
console.log('[CASE DROPDOWN] Added case:', caseObj.case_title, 'Balance:', caseObj.current_balance);
```

**Backup:** `/usr/share/nginx/html/js/bank-transactions.js.backup_before_case_title`

---

### 3. **print-checks.js** (Lines 103, 350)

**Variable Declaration - Line 103:**
**Before:**
```javascript
const caseNumber = check.case_number || '-';
```

**After:**
```javascript
const caseTitle = check.case_title || '-';  // Display case title instead of case number
```

**Display - Line 350:**
**Before:**
```javascript
<small class="text-muted">Case:</small> ${check.case_number || 'N/A'}
// Displayed: "Case: CASE-000006"
```

**After:**
```javascript
<small class="text-muted">Case:</small> ${check.case_title || 'N/A'}
// Displays: "Case: Personal Injury Case"
```

**Backup:** `/usr/share/nginx/html/js/print-checks.js.backup_before_case_title`

---

### 4. **settlements.js** (Line 150)

**Before:**
```javascript
<td>${settlement.case_number || settlement.case?.case_number || '-'}</td>
// Displayed in table: "CASE-000006"
```

**After:**
```javascript
<td>${settlement.case_title || settlement.case?.case_title || '-'}</td>
// Displays in table: "Personal Injury Case"
```

**Backup:** `/usr/share/nginx/html/js/settlements.js.backup_before_case_title`

---

## User-Visible Changes

### Before:
- Client Ledger dropdown: "CASE-000006 - Personal Injury Case"
- Bank Transactions dropdown: "CASE-000006 - Personal Injury Case"
- Check Print: "Case: CASE-000006"
- Settlements table: "CASE-000006"

### After:
- Client Ledger dropdown: "Personal Injury Case" ✅
- Bank Transactions dropdown: "Personal Injury Case" ✅
- Check Print: "Case: Personal Injury Case" ✅
- Settlements table: "Personal Injury Case" ✅

---

## Technical Details

### Why This Is Safe:

1. **ID-Based API Communication:**
   - All API endpoints use `/api/v1/cases/{id}/` (not `{case_number}`)
   - Django REST Framework ViewSet uses `pk` (primary key) by default
   - No `lookup_field` override in `CaseViewSet`

2. **Frontend Always Uses ID:**
   ```javascript
   // Example from bank-transactions.js
   option.value = caseObj.id;  // ← This is what's sent to backend
   option.textContent = `${caseObj.case_title}`;  // ← This is just display
   ```

3. **API Response Still Includes case_number:**
   - Backend serializer still returns both `case_number` and `case_title`
   - We just choose to display `case_title` instead
   - `case_number` still exists in the data, just not shown to users

### Example API Communication:

**Creating a Transaction:**
```javascript
POST /api/v1/bank-accounts/bank-transactions/
{
  "case": 42,  // ← Uses ID, not case_number
  "amount": 5000,
  ...
}
```

**The dropdown:**
```javascript
<select name="case">
  <option value="42">Personal Injury Case</option>
  <!--        ^^                ^^^^^^^^^^^^^^^^^^
              ID (sent to backend)  case_title (display only) -->
</select>
```

---

## Rollback Instructions

If needed, restore from backups:

```bash
# Client Ledger
docker exec iolta_frontend_alpine_fixed cp /usr/share/nginx/html/js/client-ledger.js.backup_before_case_title /usr/share/nginx/html/js/client-ledger.js

# Bank Transactions
docker exec iolta_frontend_alpine_fixed cp /usr/share/nginx/html/js/bank-transactions.js.backup_before_case_title /usr/share/nginx/html/js/bank-transactions.js

# Print Checks
docker exec iolta_frontend_alpine_fixed cp /usr/share/nginx/html/js/print-checks.js.backup_before_case_title /usr/share/nginx/html/js/print-checks.js

# Settlements
docker exec iolta_frontend_alpine_fixed cp /usr/share/nginx/html/js/settlements.js.backup_before_case_title /usr/share/nginx/html/js/settlements.js
```

---

## Testing Checklist

- [ ] Client Ledger: Case dropdown shows only titles
- [ ] Bank Transactions: Case dropdown shows only titles
- [ ] Check Printing: Case field shows only title
- [ ] Settlements: Case column shows only titles
- [ ] Creating transactions still works (uses ID internally)
- [ ] Updating cases still works (uses ID internally)
- [ ] Deleting cases still works (uses ID internally)

---

## Summary

**Files Changed:** 4 frontend JavaScript files
**Lines Changed:** 8 locations total
**Backend Changes:** None (still uses ID for all operations)
**Data Changes:** None (case_number still exists in database and API)
**Display Changes:** Shows `case_title` instead of `case_number - case_title`

**Status:** ✅ Complete and deployed
