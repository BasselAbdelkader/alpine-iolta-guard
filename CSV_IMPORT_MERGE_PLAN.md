# CSV IMPORT FEATURE MERGE PLAN
## From Amin-branch → bassel-prod (master)

**Created:** 2025-11-27
**Author:** Claude Code
**Estimated Time:** 4-6 hours
**Complexity:** HIGH
**Risk Level:** MEDIUM

---

## 📋 TABLE OF CONTENTS

1. [Executive Summary](#executive-summary)
2. [What You're Getting](#what-youre-getting)
3. [Pre-Merge Checklist](#pre-merge-checklist)
4. [Merge Strategy](#merge-strategy)
5. [Step-by-Step Implementation](#step-by-step-implementation)
6. [Database Migrations](#database-migrations)
7. [Testing Plan](#testing-plan)
8. [Rollback Plan](#rollback-plan)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 EXECUTIVE SUMMARY

This plan merges the **two-stage CSV import workflow** from Amin-branch into bassel-prod master. This feature adds:

- **Staging tables** for preview before commit
- **Approval workflow** with maker-checker pattern
- **Dual control** - creator cannot approve own import
- **Chronological processing** - transactions ordered by date
- **Complete audit trail** - all imports tracked

**Why This Matters:**
- Trust accounting compliance requires human review before committing financial data
- Prevents accidental data corruption from bad CSV files
- Provides rollback capability (reject before commit)
- Meets state bar requirements for dual control

---

## 📦 WHAT YOU'RE GETTING

### New Backend Features

1. **Staging Tables** (3 new Django models)
   - `StagingClient` - Temporary client records
   - `StagingCase` - Temporary case records
   - `StagingBankTransaction` - Temporary transaction records

2. **Approval Workflow** (New `imports` app)
   - Approve import API - Copies staging → production
   - Reject import API - Deletes staging data
   - Get pending imports API - Lists awaiting approval

3. **Enhanced ImportLog Model**
   - `approval_status` field - pending_review, committed, rejected
   - `reviewed_by` field - who approved/rejected
   - `reviewed_at` field - when reviewed
   - `review_notes` field - approval/rejection reason

4. **Import Notifications** (Optional)
   - `ImportNotification` model for in-app alerts
   - Notifies importer when approved/rejected

### New Frontend Features

1. **Import Approval Page** (`import-approval.html`)
   - View staging data before committing
   - Preview clients, cases, transactions
   - Approve or reject with notes

2. **Approval Dashboard** (`approval-dashboard.html`)
   - See all pending imports
   - Badge showing count
   - Quick approve/reject actions

3. **Enhanced Sidebar**
   - Approval badge showing pending count
   - Link to approval dashboard

### Architecture Changes

**Two-Stage Workflow:**
```
Stage 1: CSV → Staging Tables (any user)
  ↓
Stage 2: Approval → Production Tables (approvers only)
```

**Security:**
- Dual control enforced (creator ≠ approver)
- Permission: `can_approve_imports`
- Complete audit logging

---

## ✅ PRE-MERGE CHECKLIST

### Prerequisites

- [ ] **Backup database** - CRITICAL!
  ```bash
  docker exec iolta_db_prod pg_dump -U iolta_user iolta_guard_db > backup_before_import_merge_$(date +%Y%m%d).sql
  ```

- [ ] **Create git branch** for safety
  ```bash
  cd /Users/bassel/Desktop/merge/bassel-prod/iolta-production
  git checkout -b feature/csv-import-approval
  ```

- [ ] **Document current state**
  - Current import workflow: Direct to production
  - Number of existing imports in `import_logs` table

- [ ] **Test environment ready**
  - Containers running: `docker-compose -f docker-compose.prod.yml ps`
  - Can access frontend: http://localhost
  - Can access backend: http://localhost/api/

### What You'll Need

- **Time:** 4-6 hours (including testing)
- **Access:** Shell access to Docker containers
- **Skills:** Python/Django, SQL, JavaScript
- **Tools:** Text editor, database client (optional)

---

## 🎯 MERGE STRATEGY

### Approach: Incremental Merge

We'll merge in 3 phases:

**Phase 1: Backend Models & Database** (90 minutes)
- Create `imports` app
- Add staging models
- Update `ImportLog` model
- Run migrations

**Phase 2: Backend APIs** (90 minutes)
- Add approval endpoints
- Update CSV import to use staging
- Add permissions

**Phase 3: Frontend** (90 minutes)
- Add approval pages
- Update sidebar
- Wire up APIs

**Phase 4: Testing** (60 minutes)
- End-to-end import workflow
- Approval workflow
- Permission checks
- Rollback testing

---

## 📝 STEP-BY-STEP IMPLEMENTATION

### PHASE 1: Backend Models & Database

#### Step 1.1: Create `imports` App

```bash
# In backend container
docker exec -it iolta_backend_prod python manage.py startapp imports apps/imports
```

#### Step 1.2: Copy Staging Models

**Source:** `/Users/bassel/Desktop/merge/Amin-branch/backend/apps/imports/models.py`
**Dest:** `/Users/bassel/Desktop/merge/bassel-prod/iolta-production/backend/apps/imports/models.py`

**Action:**
```bash
# Copy the file
cp /Users/bassel/Desktop/merge/Amin-branch/backend/apps/imports/models.py \
   /Users/bassel/Desktop/merge/bassel-prod/iolta-production/backend/apps/imports/models.py
```

**File contains:**
- `StagingClient` - 263 lines
- `StagingCase` - 145 lines
- `StagingBankTransaction` - 217 lines
- `ImportNotification` - 156 lines

#### Step 1.3: Register `imports` App

**File:** `backend/trust_account_project/settings.py`

**Add to `INSTALLED_APPS`:**
```python
INSTALLED_APPS = [
    # ... existing apps ...
    'apps.imports',  # NEW - Two-stage import system
]
```

#### Step 1.4: Update `ImportLog` Model

**File:** `backend/apps/settings/models.py`

**Add these fields to `ImportLog` class:**
```python
class ImportLog(models.Model):
    # ... existing fields ...

    # TWO-STAGE APPROVAL WORKFLOW
    approval_status = models.CharField(
        max_length=20,
        choices=[
            ('pending_review', 'Pending Review'),
            ('committed', 'Committed to Production'),
            ('rejected', 'Rejected'),
        ],
        default='pending_review',
        help_text='Approval status for two-stage import'
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_imports',
        help_text='User who approved or rejected this import'
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When import was reviewed'
    )
    review_notes = models.TextField(
        blank=True,
        help_text='Reason for approval or rejection'
    )

    def get_approval_status_display(self):
        """Get human-readable approval status"""
        status_map = {
            'pending_review': 'Pending Review',
            'committed': 'Committed',
            'rejected': 'Rejected'
        }
        return status_map.get(self.approval_status, self.approval_status)
```

#### Step 1.5: Create & Run Migrations

```bash
# Create migrations
docker exec -it iolta_backend_prod python manage.py makemigrations imports
docker exec -it iolta_backend_prod python manage.py makemigrations settings

# Review migrations (IMPORTANT!)
docker exec -it iolta_backend_prod python manage.py showmigrations

# Apply migrations
docker exec -it iolta_backend_prod python manage.py migrate imports
docker exec -it iolta_backend_prod python manage.py migrate settings
```

#### Step 1.6: Verify Database Tables

```bash
# Connect to database
docker exec -it iolta_db_prod psql -U iolta_user -d iolta_guard_db

# Check tables exist
\dt staging_*
\d import_logs

# Expected tables:
# - staging_clients
# - staging_cases
# - staging_bank_transactions
# - import_notifications

# Verify import_logs has new fields
\d import_logs

# Expected new columns:
# - approval_status
# - reviewed_by_id
# - reviewed_at
# - review_notes

\q
```

---

### PHASE 2: Backend APIs

#### Step 2.1: Create `imports` API Directory

```bash
mkdir -p /Users/bassel/Desktop/merge/bassel-prod/iolta-production/backend/apps/imports/api
```

#### Step 2.2: Copy Approval API Views

**Source:** `/Users/bassel/Desktop/merge/Amin-branch/backend/apps/imports/api/views.py`
**Dest:** `/Users/bassel/Desktop/merge/bassel-prod/iolta-production/backend/apps/imports/api/views.py`

```bash
cp /Users/bassel/Desktop/merge/Amin-branch/backend/apps/imports/api/views.py \
   /Users/bassel/Desktop/merge/bassel-prod/iolta-production/backend/apps/imports/api/views.py
```

**File contains:**
- `approve_import()` - 350 lines - Copies staging → production
- `reject_import()` - 150 lines - Deletes staging data
- `get_pending_imports()` - 103 lines - Lists pending imports

#### Step 2.3: Create URL Routes

**Create:** `backend/apps/imports/api/urls.py`

```python
from django.urls import path
from apps.imports.api import views

urlpatterns = [
    # Approval workflow endpoints
    path('approve/<int:import_batch_id>/', views.approve_import, name='approve_import'),
    path('reject/<int:import_batch_id>/', views.reject_import, name='reject_import'),
    path('pending/', views.get_pending_imports, name='get_pending_imports'),
]
```

#### Step 2.4: Register API Routes

**File:** `backend/trust_account_project/urls.py`

**Add to `urlpatterns`:**
```python
from django.urls import path, include

urlpatterns = [
    # ... existing patterns ...

    # Import approval APIs (two-stage workflow)
    path('api/v1/imports/', include('apps.imports.api.urls')),
]
```

#### Step 2.5: Add Permission to UserProfile

**File:** `backend/apps/settings/models.py`

**Add field to `UserProfile` class:**
```python
class UserProfile(models.Model):
    # ... existing fields ...

    # Import approval permission
    can_approve_imports = models.BooleanField(
        default=False,
        help_text='Can approve CSV imports (Managing Attorney, Accountant)'
    )
```

**Create migration:**
```bash
docker exec -it iolta_backend_prod python manage.py makemigrations settings
docker exec -it iolta_backend_prod python manage.py migrate settings
```

#### Step 2.6: Update Existing CSV Import Logic

**File:** `backend/apps/settings/api/views.py`

**Modify `csv_import()` function** to write to **staging tables** instead of production:

**Current behavior:** Directly creates Client, Case, BankTransaction
**New behavior:** Creates StagingClient, StagingCase, StagingBankTransaction

**Changes needed:**
1. Import staging models at top:
   ```python
   from apps.imports.models import StagingClient, StagingCase, StagingBankTransaction
   ```

2. Replace production model creation with staging:
   ```python
   # OLD
   client = Client.objects.create(...)

   # NEW
   staging_client = StagingClient.objects.create(
       import_batch_id=import_log.id,
       ...
   )
   ```

3. Set `approval_status='pending_review'` in ImportLog:
   ```python
   import_log.approval_status = 'pending_review'
   import_log.save()
   ```

**⚠️ CRITICAL:** This is the most complex change. I recommend creating a NEW function `csv_import_to_staging()` and keeping the old one temporarily for rollback.

#### Step 2.7: Restart Backend

```bash
docker restart iolta_backend_prod

# Verify restart
docker logs -f iolta_backend_prod
# Wait for "Booting worker" message
```

---

### PHASE 3: Frontend

#### Step 3.1: Copy Import Approval Page

**Source:** `/Users/bassel/Desktop/merge/Amin-branch/frontend/html/import-approval.html`
**Dest:** `/Users/bassel/Desktop/merge/bassel-prod/iolta-production/frontend/html/import-approval.html`

```bash
cp /Users/bassel/Desktop/merge/Amin-branch/frontend/html/import-approval.html \
   /Users/bassel/Desktop/merge/bassel-prod/iolta-production/frontend/html/import-approval.html
```

#### Step 3.2: Copy Approval Dashboard

**Source:** `/Users/bassel/Desktop/merge/Amin-branch/frontend/html/approval-dashboard.html`
**Dest:** `/Users/bassel/Desktop/merge/bassel-prod/iolta-production/frontend/html/approval-dashboard.html`

```bash
cp /Users/bassel/Desktop/merge/Amin-branch/frontend/html/approval-dashboard.html \
   /Users/bassel/Desktop/merge/bassel-prod/iolta-production/frontend/html/approval-dashboard.html
```

#### Step 3.3: Copy JavaScript Files

**Source:** `/Users/bassel/Desktop/merge/Amin-branch/frontend/js/import-approval.js`
**Dest:** `/Users/bassel/Desktop/merge/bassel-prod/iolta-production/frontend/js/import-approval.js`

```bash
cp /Users/bassel/Desktop/merge/Amin-branch/frontend/js/import-approval.js \
   /Users/bassel/Desktop/merge/bassel-prod/iolta-production/frontend/js/import-approval.js
```

**Source:** `/Users/bassel/Desktop/merge/Amin-branch/frontend/js/approval-dashboard.js`
**Dest:** `/Users/bassel/Desktop/merge/bassel-prod/iolta-production/frontend/js/approval-dashboard.js`

```bash
cp /Users/bassel/Desktop/merge/Amin-branch/frontend/js/approval-dashboard.js \
   /Users/bassel/Desktop/merge/bassel-prod/iolta-production/frontend/js/approval-dashboard.js
```

#### Step 3.4: Update Sidebar (Optional)

**Add approval badge to sidebar** on all pages that show import count:

**Example for `dashboard.html`:**
```html
<li class="nav-item">
    <a class="nav-link" href="/approval-dashboard.html">
        <i class="fas fa-check-circle"></i> Approvals
        <span id="approval-badge" class="badge bg-warning ms-2" style="display:none;">0</span>
    </a>
</li>
```

**Add JavaScript to load count:**
```javascript
// Load pending approval count
async function loadApprovalCount() {
    try {
        const data = await api.get('/imports/pending/');
        const count = data.pending_imports?.length || 0;
        const badge = document.getElementById('approval-badge');
        if (badge && count > 0) {
            badge.textContent = count;
            badge.style.display = 'inline';
        }
    } catch (error) {
        console.error('Error loading approval count:', error);
    }
}

// Call on page load
document.addEventListener('DOMContentLoaded', loadApprovalCount);
```

#### Step 3.5: Rebuild Frontend Container

```bash
docker-compose -f docker-compose.prod.yml up -d --build frontend

# Verify rebuild
docker logs iolta_frontend_prod
```

---

## 🗄️ DATABASE MIGRATIONS

### Migration Summary

**3 New Tables:**
1. `staging_clients` - Temporary client records
2. `staging_cases` - Temporary case records
3. `staging_bank_transactions` - Temporary transaction records
4. `import_notifications` - In-app notifications

**Updated Tables:**
1. `import_logs` - Added approval fields
2. `user_profiles` - Added `can_approve_imports` field

### Migration Files Created

```
backend/apps/imports/migrations/
  └── 0001_initial.py - Creates staging tables

backend/apps/settings/migrations/
  └── 0XXX_add_approval_fields.py - Updates ImportLog
  └── 0XXX_add_can_approve_imports.py - Updates UserProfile
```

### Data Migration Needed?

**NO** - This is a new feature. Existing data remains unchanged.

**However,** you may want to:
1. Grant `can_approve_imports=True` to managing attorneys
2. Update existing `ImportLog` records to `approval_status='committed'`

**SQL to update existing imports:**
```sql
-- Mark all existing imports as already committed
UPDATE import_logs
SET approval_status = 'committed',
    reviewed_at = created_at,
    reviewed_by_id = created_by_id
WHERE approval_status IS NULL;
```

---

## 🧪 TESTING PLAN

### Test 1: End-to-End Import Workflow

**Duration:** 20 minutes

**Steps:**
1. Login as regular user (not approver)
2. Go to Settings → Import CSV Data
3. Upload a CSV file (use test data)
4. Verify preview shows data correctly
5. Click "Import" button
6. **Expected:** Import status = "Pending Review"
7. **Expected:** Data in staging tables, NOT in production

**Verify:**
```sql
-- Check staging data exists
SELECT COUNT(*) FROM staging_clients;
SELECT COUNT(*) FROM staging_cases;
SELECT COUNT(*) FROM staging_bank_transactions;

-- Check production data NOT created yet
SELECT COUNT(*) FROM clients WHERE data_source = 'csv_import' ORDER BY id DESC LIMIT 10;
```

### Test 2: Approval Workflow

**Duration:** 15 minutes

**Steps:**
1. Login as approver (has `can_approve_imports=True`)
2. Go to Approval Dashboard
3. See pending import from Test 1
4. Click "View Details"
5. Review staging data
6. Click "Approve" with notes: "Test approval"
7. **Expected:** Success message
8. **Expected:** Data moved to production
9. **Expected:** Staging data deleted

**Verify:**
```sql
-- Check staging deleted
SELECT COUNT(*) FROM staging_clients;  -- Should be 0

-- Check production created
SELECT COUNT(*) FROM clients WHERE data_source = 'csv_import' ORDER BY id DESC LIMIT 10;

-- Check import_logs updated
SELECT approval_status, reviewed_by_id, review_notes
FROM import_logs
ORDER BY id DESC LIMIT 1;
-- Expected: approval_status='committed', reviewed_by_id=approver's ID
```

### Test 3: Rejection Workflow

**Duration:** 15 minutes

**Steps:**
1. Login as regular user
2. Upload another CSV file
3. **Expected:** Import status = "Pending Review"
4. Logout, login as approver
5. Go to Approval Dashboard
6. Click "Reject" with notes: "Test rejection"
7. **Expected:** Success message
8. **Expected:** Staging data deleted
9. **Expected:** Production data NOT created

**Verify:**
```sql
-- Check staging deleted
SELECT COUNT(*) FROM staging_clients WHERE import_batch_id = <batch_id>;  -- Should be 0

-- Check import_logs updated
SELECT approval_status, review_notes
FROM import_logs
WHERE id = <batch_id>;
-- Expected: approval_status='rejected', review_notes='Test rejection'
```

### Test 4: Dual Control Enforcement

**Duration:** 10 minutes

**Steps:**
1. Login as user with approval permission
2. Upload CSV file as THIS USER
3. Try to approve OWN import
4. **Expected:** Error: "Cannot approve your own import"

**Verify:**
- Error message displayed
- Staging data remains
- `approval_status` still 'pending_review'

### Test 5: Permission Checks

**Duration:** 10 minutes

**Test 5a: User without permission**
1. Login as user with `can_approve_imports=False`
2. Navigate to `/approval-dashboard.html` directly
3. **Expected:** Can only see OWN pending imports
4. Try to approve ANY import (via API call)
5. **Expected:** 403 Forbidden error

**Test 5b: User with permission**
1. Login as user with `can_approve_imports=True`
2. Navigate to `/approval-dashboard.html`
3. **Expected:** See ALL pending imports (except own)
4. Can approve others' imports successfully

### Test 6: Chronological Transaction Ordering

**Duration:** 10 minutes

**Steps:**
1. Create CSV with transactions in random date order:
   ```
   2024-01-15, Deposit, $100
   2024-01-10, Deposit, $50
   2024-01-20, Withdrawal, $30
   ```
2. Import to staging
3. Approve import
4. Check production transactions

**Verify:**
```sql
SELECT transaction_date, transaction_type, amount
FROM bank_transactions
WHERE data_source = 'csv_import'
ORDER BY id DESC LIMIT 10;

-- Expected order (oldest first):
-- 2024-01-10, DEPOSIT, $50
-- 2024-01-15, DEPOSIT, $100
-- 2024-01-20, WITHDRAWAL, $30
```

**File:** `backend/apps/imports/api/views.py:130`
```python
staging_transactions = StagingBankTransaction.objects.filter(
    import_batch_id=import_batch_id
).order_by('transaction_date', 'staging_id')  # ← Chronological
```

---

## 🔄 ROLLBACK PLAN

### If Things Go Wrong

#### Scenario 1: Migrations Fail

**Rollback:**
```bash
# Undo migrations
docker exec -it iolta_backend_prod python manage.py migrate imports zero
docker exec -it iolta_backend_prod python manage.py migrate settings <previous_migration>

# Drop staging tables manually if needed
docker exec -it iolta_db_prod psql -U iolta_user -d iolta_guard_db
DROP TABLE IF EXISTS staging_clients CASCADE;
DROP TABLE IF EXISTS staging_cases CASCADE;
DROP TABLE IF EXISTS staging_bank_transactions CASCADE;
DROP TABLE IF EXISTS import_notifications CASCADE;
\q
```

#### Scenario 2: Import Breaks

**Rollback:**
1. Revert `apps/settings/api/views.py` to old version
2. Remove staging imports from code
3. Restart backend container

**Quick fix:**
```bash
# Restore from git
git checkout HEAD -- backend/apps/settings/api/views.py
docker restart iolta_backend_prod
```

#### Scenario 3: Frontend Broken

**Rollback:**
```bash
# Remove new HTML files
rm frontend/html/import-approval.html
rm frontend/html/approval-dashboard.html
rm frontend/js/import-approval.js
rm frontend/js/approval-dashboard.js

# Rebuild frontend
docker-compose -f docker-compose.prod.yml up -d --build frontend
```

#### Scenario 4: Complete Rollback

**Nuclear option:**
```bash
# Restore database from backup
docker exec -i iolta_db_prod psql -U iolta_user -d iolta_guard_db < backup_before_import_merge_YYYYMMDD.sql

# Restore code from git
git reset --hard HEAD
git clean -fd

# Rebuild everything
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 🔧 TROUBLESHOOTING

### Problem: Staging tables not created

**Check:**
```bash
docker exec -it iolta_backend_prod python manage.py showmigrations imports
```

**Fix:**
```bash
docker exec -it iolta_backend_prod python manage.py migrate imports
```

### Problem: API returns 404 for `/api/v1/imports/pending/`

**Check:**
1. URL routing configured in `trust_account_project/urls.py`
2. `apps.imports` in `INSTALLED_APPS`
3. Backend restarted after changes

**Fix:**
```bash
# Check URLs
docker exec -it iolta_backend_prod python manage.py show_urls | grep imports

# Restart backend
docker restart iolta_backend_prod
```

### Problem: "Cannot approve your own import" error when it should work

**Check:**
1. User has `can_approve_imports=True`
2. User did NOT create the import (check `import_logs.created_by_id`)

**Verify:**
```sql
SELECT id, created_by_id, approval_status
FROM import_logs
WHERE id = <import_id>;
```

### Problem: Transactions not in chronological order

**Check:** `apps/imports/api/views.py:130`

**Should be:**
```python
.order_by('transaction_date', 'staging_id')
```

**NOT:**
```python
.order_by('staging_id')  # Wrong!
```

### Problem: Staging data not deleted after approval

**Check:** Transaction commit in `approve_import()` function

**Verify:**
```sql
SELECT COUNT(*) FROM staging_clients;
SELECT COUNT(*) FROM staging_cases;
SELECT COUNT(*) FROM staging_bank_transactions;
```

**Manual cleanup if needed:**
```sql
DELETE FROM staging_bank_transactions WHERE import_batch_id = <id>;
DELETE FROM staging_cases WHERE import_batch_id = <id>;
DELETE FROM staging_clients WHERE import_batch_id = <id>;
```

---

## 📊 SUCCESS CRITERIA

Merge is successful when:

- [ ] All database migrations applied without errors
- [ ] All 3 staging tables created (`staging_clients`, `staging_cases`, `staging_bank_transactions`)
- [ ] `ImportLog` has 4 new approval fields
- [ ] CSV import creates staging data (not production)
- [ ] Approval dashboard shows pending imports
- [ ] Approve workflow copies staging → production
- [ ] Reject workflow deletes staging data
- [ ] Dual control enforced (creator ≠ approver)
- [ ] Transactions processed in chronological order
- [ ] All tests pass (6 tests above)
- [ ] No errors in browser console
- [ ] No errors in backend logs

---

## 📈 ESTIMATED TIMELINE

| Phase | Task | Duration |
|-------|------|----------|
| **Phase 1** | Backend Models & Database | 90 min |
| - | Create `imports` app | 10 min |
| - | Copy staging models | 15 min |
| - | Update `ImportLog` model | 20 min |
| - | Create & run migrations | 25 min |
| - | Verify database tables | 20 min |
| **Phase 2** | Backend APIs | 90 min |
| - | Copy approval API views | 15 min |
| - | Create URL routes | 10 min |
| - | Add permissions | 15 min |
| - | Update CSV import logic | 40 min |
| - | Test APIs with curl | 10 min |
| **Phase 3** | Frontend | 90 min |
| - | Copy HTML/JS files | 20 min |
| - | Update sidebar | 30 min |
| - | Wire up APIs | 30 min |
| - | Manual testing | 10 min |
| **Phase 4** | Testing | 60 min |
| - | Test 1-6 (see above) | 60 min |
| **TOTAL** | | **5.5 hours** |

---

## 🎯 NEXT STEPS

After successful merge:

1. **Grant approval permissions** to managing attorneys:
   ```python
   # In Django shell
   from apps.settings.models import UserProfile
   admin_profile = UserProfile.objects.get(user__username='admin')
   admin_profile.can_approve_imports = True
   admin_profile.save()
   ```

2. **Update existing imports** to 'committed' status:
   ```sql
   UPDATE import_logs
   SET approval_status = 'committed',
       reviewed_at = created_at
   WHERE approval_status IS NULL;
   ```

3. **User training** on new workflow:
   - Stage 1: Import to staging
   - Stage 2: Wait for approval
   - Don't expect immediate data in production

4. **Monitor** first few imports:
   - Check staging tables
   - Verify approval workflow
   - Watch for errors

---

## 📚 ADDITIONAL RESOURCES

**From Amin-branch:**
- `/Users/bassel/Desktop/merge/Amin-branch/merge_amin.md` - Original merge guide
- `/Users/bassel/Desktop/merge/Amin-branch/docs/sessions/SESSION_LOG_2025_11_21_CSV_IMPORT_FIXES.md` - Latest session
- `/Users/bassel/Desktop/merge/Amin-branch/docs/features/CSV_IMPORT_COMPLETE_BREAKDOWN.md` - Feature docs

**Code Reference:**
- Staging models: `apps/imports/models.py` (Amin-branch)
- Approval APIs: `apps/imports/api/views.py` (Amin-branch)
- Frontend pages: `frontend/html/import-approval.html`, `approval-dashboard.html` (Amin-branch)

---

## ⚠️ WARNINGS

1. **Database Backup CRITICAL** - Do NOT skip this step
2. **Test on staging first** - Don't merge directly to production
3. **Existing imports** - Update to 'committed' status after merge
4. **User permissions** - Grant `can_approve_imports` to appropriate users
5. **CSV format** - Ensure format matches Amin-branch parser
6. **Chronological ordering** - Verify `.order_by()` in approval view

---

## 📞 NEED HELP?

If you encounter issues:

1. **Check logs:**
   ```bash
   docker logs iolta_backend_prod
   docker logs iolta_frontend_prod
   ```

2. **Check database:**
   ```bash
   docker exec -it iolta_db_prod psql -U iolta_user -d iolta_guard_db
   ```

3. **Rollback if needed** - See Rollback Plan above

4. **Contact:** Reference this plan and provide specific error messages

---

**Good luck with the merge! 🚀**

---

**Document Version:** 1.0
**Last Updated:** 2025-11-27
**Status:** Ready for Implementation
