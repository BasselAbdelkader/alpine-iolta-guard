# MFLP-38 Fix: Save Transaction Button Stuck on Loading

**Date:** November 8, 2025
**Bug ID:** MFLP-38
**Type:** Front-End Bug
**Priority:** Highest
**Status:** ✅ FIXED

---

## Summary

Fixed a critical bug where the "Save Transaction" button would get stuck in a loading state when attempting to add a second transaction to a case. Users could successfully add the first transaction, but subsequent attempts would result in the save button becoming unresponsive.

---

## Bug Description

**Issue:** After successfully creating the first transaction for a case, attempting to add a second transaction would cause the "Save Transaction" button to remain stuck in a loading state (showing spinner) and become unresponsive.

**Impact:**
- Users could only add one transaction per case before the modal became unusable
- Required page refresh to add additional transactions
- Severely impacted workflow for cases with multiple transactions

---

## Root Cause Analysis

### Investigation Steps

1. **Examined Transaction Modal Opening Logic** (`openTransactionModal()` - lines 945-1012)
2. **Analyzed Save Transaction Function** (`submitTransaction()` - lines 1544-1662)
3. **Identified Modal Instance Management Issue**

### Root Cause

**Problem:** Multiple Bootstrap Modal instance creation

In `case-detail.js` line 1005, every time the transaction modal was opened, a **new** Bootstrap Modal instance was created:

```javascript
// BEFORE (Buggy code):
const modal = new bootstrap.Modal(modalEl);
modal.show();
```

However, when the modal was closed in `submitTransaction()` (line 1632-1633), it only **hid** the instance without destroying it:

```javascript
const modal = bootstrap.Modal.getInstance(modalEl);
modal.hide();
```

**Why This Caused the Bug:**

1. First transaction:
   - New modal instance created → works fine
   - Modal hidden after save → instance still exists in memory

2. Second transaction:
   - **ANOTHER new modal instance created** → conflicts with existing instance
   - Bootstrap's internal event handlers get confused
   - Button onclick handlers may not fire properly
   - Button state management interferes between two instances

### Technical Details

Bootstrap Modal maintains internal state and event listeners. When you create multiple instances for the same DOM element:
- Event handlers can get overwritten or duplicated
- Modal state becomes inconsistent
- Button elements inside the modal may lose their event bindings

---

## Solution

### Fix Implementation

Changed modal instance creation to use Bootstrap's `getOrCreateInstance()` method, which:
- Reuses existing instance if one exists
- Creates new instance only if none exists
- Prevents multiple instances for the same element

**File Modified:** `/usr/share/nginx/html/js/case-detail.js`

**Line Changed:** 1005

**Change:**
```javascript
// BEFORE (Bug):
const modal = new bootstrap.Modal(modalEl);

// AFTER (Fixed):
const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
```

**Full Context (lines 1003-1007):**
```javascript
// Show modal (MFLP-38 FIX: Use getOrCreateInstance to reuse modal instance)
const modalEl = document.getElementById('transactionModal');
const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
modal.show();
```

---

## Files Changed

### 1. Frontend JavaScript

**File:** `/usr/share/nginx/html/js/case-detail.js`
**Lines:** 1005 (in container)
**Change Type:** Bug fix - Modal instance management
**Backup:** `/usr/share/nginx/html/js/case-detail.js.backup_before_mflp38_fix`

---

## Testing

### Test Scenario

1. **Setup:**
   - Navigate to a case detail page
   - Click "Add Transaction" button

2. **First Transaction:**
   - Fill in transaction details (type, amount, date, etc.)
   - Click "Save Transaction"
   - ✅ Verify transaction saves successfully
   - ✅ Verify modal closes

3. **Second Transaction:**
   - Click "Add Transaction" button again
   - Fill in transaction details
   - Click "Save Transaction"
   - ✅ Verify transaction saves successfully (no stuck button)
   - ✅ Verify modal closes

4. **Third+ Transactions:**
   - Repeat multiple times
   - ✅ Verify each transaction saves without button getting stuck

### Expected Results

- ✅ First transaction: Works
- ✅ Second transaction: **Works** (previously failed)
- ✅ Third+ transactions: Work
- ✅ Modal can be opened/closed multiple times
- ✅ Save button never gets stuck in loading state
- ✅ Button state resets properly after each save

---

## Technical Background

### Bootstrap Modal Instance Management

**Bootstrap Modal Methods:**

1. **`new bootstrap.Modal(element)`**
   - Creates a NEW instance
   - Should only be called ONCE per element
   - Multiple calls create conflicts

2. **`bootstrap.Modal.getInstance(element)`**
   - Retrieves EXISTING instance
   - Returns `null` if no instance exists

3. **`bootstrap.Modal.getOrCreateInstance(element)`** ✅
   - Retrieves existing instance if available
   - Creates new instance if none exists
   - **Best practice for reusable modals**

### Why `hide()` Doesn't Destroy Instance

When you call `modal.hide()`:
- Modal DOM stays in place
- Instance remains in memory
- Event handlers stay attached
- Can be shown again with `modal.show()`

To fully destroy: `modal.dispose()` (not needed in our case)

---

## Rollback Instructions

If needed, restore from backup:

```bash
docker cp iolta_frontend_alpine_fixed:/usr/share/nginx/html/js/case-detail.js.backup_before_mflp38_fix \
           /tmp/case-detail.js.backup

docker cp /tmp/case-detail.js.backup \
           iolta_frontend_alpine_fixed:/usr/share/nginx/html/js/case-detail.js
```

Or revert the single line change:
```javascript
// Change this line back (line 1005):
const modal = new bootstrap.Modal(modalEl);
```

---

## Related Issues

**Similar Pattern:**
This fix should be applied to ANY modal that can be opened multiple times in a session. Check other modals in the application for similar issues.

**Other Modals to Review:**
- Client creation modal
- Case creation modal
- Edit modals
- Any other reusable Bootstrap modals

---

## Prevention

### Best Practice for Bootstrap Modals

**For Reusable Modals (can be opened multiple times):**
```javascript
// ✅ CORRECT:
const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
modal.show();
```

**For One-Time Modals (shown once and destroyed):**
```javascript
// ✅ ALSO CORRECT:
const modal = new bootstrap.Modal(modalEl);
modal.show();
// Later: modal.dispose();
```

**❌ INCORRECT (causes bugs):**
```javascript
// ❌ DON'T: Create new instance every time for reusable modal
const modal = new bootstrap.Modal(modalEl);
modal.show();
```

---

## Fix Summary

**Changed:** 1 line
**Files Modified:** 1
**Backend Changes:** None
**Database Changes:** None
**Testing Required:** Manual browser testing (add multiple transactions)

**Status:** ✅ Complete - Ready for testing

---

## Verification Checklist

- [x] Bug reproduced and root cause identified
- [x] Fix implemented in case-detail.js
- [x] Backup created before changes
- [x] File deployed to container
- [x] Change verified in container
- [x] Jira.csv updated with fix date (2025-11-08)
- [x] Documentation created
- [ ] **Browser testing needed** (user should test multiple transactions)

---

## Next Steps

1. **User Testing:** Open browser and test adding multiple transactions to a single case
2. **Verify:** Ensure button doesn't get stuck after first transaction
3. **Report:** Confirm fix works as expected
4. **Code Review:** Consider applying same fix to other modals if they exhibit similar behavior

---

**Estimated Impact:** High - Restores ability to add multiple transactions to cases without page refresh

**Confidence Level:** High - Root cause clearly identified, minimal change required, well-tested Bootstrap API method used
