# JavaScript and Python Files Cleanup - Action Plan

**Date:** November 14, 2025
**Status:** ⚠️ MISPLACED CODE FILES FOUND - ACTION PLAN CREATED

---

## Summary of Issues

### JavaScript Files (12 files in root)
- **12 .js files in project root** (should be in `/frontend/js/` or archived)
- **4 .js files in backend/static/** (legitimate - for backend UI)
- All root .js files are DIFFERENT from frontend versions (older versions or fix attempts)

### Python Files (26 files in root)
- **26 .py files in project root** (should be in `/scripts/` or `/tests/` or deleted)
- **1 .py file in frontend** (`serve.py` - development server, legitimate)
- **12 .py files in `/scripts/archive/`** (already archived ✅)

---

## JavaScript Files Analysis

### Root Level JavaScript Files (12 files)

#### Category A: Working Frontend Files (Different Versions)
These are OLDER/DIFFERENT versions than what's in frontend/js/

```
api.js                    - 4.4K  (Nov 9)  - Different from frontend version
bank-transactions.js      - 82.1K (Nov 8)  - Different from frontend version
case-detail.js           - 75.1K (Nov 9)  - Different from frontend version
client-detail.js         - 33.2K (Nov 8)  - Different from frontend version
clients.js               - 33.4K (Nov 9)  - Different from frontend version
client-ledger.js         - 13.9K (Nov 8)  - Different from frontend version
print-checks.js          - 27.9K (Nov 8)  - Different from frontend version
settlements.js           - 8.1K  (Nov 8)  - Different from frontend version
import-quickbooks.js     - 13.5K (Nov 10) - Different from frontend version
```

**Problem:** These are old versions or work-in-progress files from bug fixes

**Action:** ARCHIVE to `/reference/old-versions/` or DELETE

#### Category B: Fix Attempts / Modified Versions
```
client-ledger-fixed.js       - 13.8K (Nov 7)  - Fix attempt
clients_pagination_fix.js    - 4.3K  (Nov 7)  - Fix attempt
import-management-fixed.js   - 14.5K (Nov 13) - Fix attempt
```

**Problem:** These are intermediate fix attempts, NOT final versions

**Action:** ARCHIVE to `/reference/fix-attempts/` or DELETE

#### Category C: Backend Static Files (LEGITIMATE ✅)
```
backend/static/js/phone_formatter.js
backend/static/js/datatables.min.js
backend/static/js/tams-api-client.js
backend/static/js/main.js
```

**Status:** These are CORRECT - used by Django admin interface
**Action:** KEEP (no action needed)

---

## Python Files Analysis

### Root Level Python Files (26 files)

#### Category A: One-Time Migration Scripts (3 files)
```
0006_case_number_counter.py     - 1.5K (Nov 8)  - Migration file
add_data_source_field.py        - 1.9K (Nov 10) - Data migration
add_fixed_date_column.py        - 1.5K (Nov 7)  - Schema change
```

**Purpose:** One-time database migrations/fixes
**Status:** Already applied to database
**Action:** ARCHIVE to `/scripts/archive/migrations/`

#### Category B: Test Scripts (6 files)
```
test_closed_case_transaction.py - 3.8K (Nov 8)  - MFLP test
test_mflp20_search.py           - 3.8K (Nov 8)  - MFLP-20 test
test_mflp26_delete.py           - 2.4K (Nov 8)  - MFLP-26 test
test_mflp29_payee.py            - 2.2K (Nov 8)  - MFLP-29 test
test_mflp30_fix.py              - 4.2K (Nov 8)  - MFLP-30 test
test_mflp31_validation.py       - 2.8K (Nov 8)  - MFLP-31 test
```

**Purpose:** Test scripts for specific bug fixes
**Status:** Bugs already fixed
**Action:** MOVE to `/tests/mflp/`

#### Category C: Jira Update Scripts (5 files)
```
update_jira_final_3_bugs.py     - 2.4K (Nov 9)  - Jira automation
update_jira_mflp18_17_13.py     - 1.9K (Nov 9)  - Jira automation
update_jira_mflp31_32_33.py     - 1.8K (Nov 9)  - Jira automation
update_jira_mflp34.py           - 1.3K (Nov 9)  - Jira automation
update_jira_mflp39_37_27.py     - 2.0K (Nov 9)  - Jira automation
```

**Purpose:** Scripts to update Jira bug status
**Status:** Already used, Jira.csv up to date
**Action:** ARCHIVE to `/scripts/archive/jira/`

#### Category D: Code Snippets/Backups (6 files)
```
bank_transaction_serializers.py - 19.0K (Nov 8)  - Code snippet
clients_api_serializers.py      - 13.1K (Nov 10) - Code snippet
clients_api_views.py             - 22.0K (Nov 10) - Code snippet
dashboard_api_views.py           - 16.0K (Nov 10) - Code snippet
dashboard_views.py               - 20.9K (Nov 10) - Code snippet
dashboard_views_original.py      - 22.9K (Nov 10) - Original before edits
models.py                        - 15.4K (Nov 8)  - Code snippet
```

**Problem:** These are code snippets extracted during debugging/development
**Status:** Code is already in proper backend files
**Action:** DELETE (redundant) or ARCHIVE to `/reference/code-snippets/`

#### Category E: Utility Scripts (6 files)
```
create_migrations.py            - 626 bytes (Nov 13) - Migration helper
create_test_clients.py          - 7.0K (Nov 7)      - Test data generator
analyze_dump_safety.py          - 6.1K (Nov 7)      - Database analysis
fix_sidebar_consistency.py      - 6.2K (Nov 13)     - One-time fix
dashboard_api_urls.py           - 498 bytes (Nov 10) - URL snippet
```

**Purpose:** Utility and one-time fix scripts
**Action:**
- `create_test_clients.py` → MOVE to `/tests/`
- `analyze_dump_safety.py` → ARCHIVE to `/scripts/archive/`
- Others → ARCHIVE to `/scripts/archive/`

#### Category F: Frontend Development Server (1 file - LEGITIMATE ✅)
```
frontend/serve.py               - Development HTTP server
```

**Status:** This is CORRECT - used for local frontend development
**Action:** KEEP (no action needed)

---

## Action Plan

### Phase 1: Create Archive Directories
```bash
mkdir -p reference/old-js-versions
mkdir -p reference/fix-attempts
mkdir -p reference/code-snippets
mkdir -p scripts/archive/migrations
mkdir -p scripts/archive/jira
mkdir -p tests/mflp
```

### Phase 2: Move JavaScript Files

#### Archive Old JS Versions (9 files)
```bash
mv api.js reference/old-js-versions/
mv bank-transactions.js reference/old-js-versions/
mv case-detail.js reference/old-js-versions/
mv client-detail.js reference/old-js-versions/
mv clients.js reference/old-js-versions/
mv client-ledger.js reference/old-js-versions/
mv print-checks.js reference/old-js-versions/
mv settlements.js reference/old-js-versions/
mv import-quickbooks.js reference/old-js-versions/
```

#### Archive Fix Attempts (3 files)
```bash
mv client-ledger-fixed.js reference/fix-attempts/
mv clients_pagination_fix.js reference/fix-attempts/
mv import-management-fixed.js reference/fix-attempts/
```

### Phase 3: Move Python Files

#### Move Test Scripts (6 files)
```bash
mv test_*.py tests/mflp/
```

#### Archive Migration Scripts (3 files)
```bash
mv 0006_case_number_counter.py scripts/archive/migrations/
mv add_data_source_field.py scripts/archive/migrations/
mv add_fixed_date_column.py scripts/archive/migrations/
```

#### Archive Jira Scripts (5 files)
```bash
mv update_jira*.py scripts/archive/jira/
```

#### Archive Utility Scripts (4 files)
```bash
mv create_migrations.py scripts/archive/
mv analyze_dump_safety.py scripts/archive/
mv fix_sidebar_consistency.py scripts/archive/
mv dashboard_api_urls.py scripts/archive/
```

#### Move Test Data Generator (1 file)
```bash
mv create_test_clients.py tests/
```

#### Archive Code Snippets (7 files)
```bash
mv bank_transaction_serializers.py reference/code-snippets/
mv clients_api_serializers.py reference/code-snippets/
mv clients_api_views.py reference/code-snippets/
mv dashboard_api_views.py reference/code-snippets/
mv dashboard_views.py reference/code-snippets/
mv dashboard_views_original.py reference/code-snippets/
mv models.py reference/code-snippets/
```

---

## Expected Results

### Before Cleanup
```
Project Root:
  - 12 .js files (misplaced)
  - 26 .py files (misplaced)
  - Total: 38 code files in root
```

### After Cleanup
```
Project Root:
  - 0 .js files ✅
  - 0 .py files ✅

/reference/old-js-versions/     - 9 files
/reference/fix-attempts/        - 3 files
/reference/code-snippets/       - 7 files
/scripts/archive/migrations/    - 3 files
/scripts/archive/jira/          - 5 files
/tests/mflp/                    - 6 files
/tests/                         - 1 file (create_test_clients.py)
/scripts/archive/               - +4 files (utilities)
```

---

## Impact Analysis

### File Count Impact
- Root .js files: 12 → 0 (100% cleanup)
- Root .py files: 26 → 0 (100% cleanup)
- Total root code files: 38 → 0 (100% cleanup)

### Size Impact
```
Root .js files:  ~312 KB
Root .py files:  ~200 KB
Total:           ~512 KB to be organized
```

### Organization Benefit
- ✅ No code files in project root
- ✅ Old versions archived for reference
- ✅ Test scripts in proper test directory
- ✅ One-time scripts archived
- ✅ Clear separation of active vs historical code

---

## Why This Matters

### Current Problems
1. **Confusing:** Mix of old and new code in root
2. **Unprofessional:** Code files scattered everywhere
3. **Risk:** Might accidentally use old versions
4. **Maintenance:** Hard to know what's active vs archive

### After Cleanup
1. **Clear:** Only documentation in root
2. **Professional:** Proper file organization
3. **Safe:** Old code clearly marked as archive
4. **Maintainable:** Easy to find active vs historical code

---

## Alternative: DELETE Instead of ARCHIVE

If disk space is a concern or files are not needed for reference:

### Safe to DELETE
- Old JS versions (9 files) - Current frontend versions work fine
- Fix attempts (3 files) - Final fixes are in frontend
- Code snippets (7 files) - Code is in proper backend files
- Jira scripts (5 files) - Already executed, Jira up to date
- Some utility scripts - One-time use completed

### Keep as ARCHIVE
- Migration scripts - May need reference for future migrations
- Test scripts - May need to re-run tests
- Test data generator - Useful for creating test environments

**Recommendation:** ARCHIVE everything first, can delete later if truly not needed

---

## Verification Commands

### After Cleanup
```bash
# Should return 0
find . -maxdepth 1 -name "*.js" -type f | wc -l

# Should return 0
find . -maxdepth 1 -name "*.py" -type f | wc -l

# Verify archives created
ls -la reference/old-js-versions/
ls -la reference/fix-attempts/
ls -la reference/code-snippets/
ls -la scripts/archive/migrations/
ls -la scripts/archive/jira/
ls -la tests/mflp/
```

---

## Summary

**Files to Organize:** 38 code files (12 JS + 26 Python)

**Categories:**
- Old JS versions: 9 files → `/reference/old-js-versions/`
- Fix attempts: 3 files → `/reference/fix-attempts/`
- Code snippets: 7 files → `/reference/code-snippets/`
- Test scripts: 6 files → `/tests/mflp/`
- Migration scripts: 3 files → `/scripts/archive/migrations/`
- Jira scripts: 5 files → `/scripts/archive/jira/`
- Utility scripts: 5 files → `/scripts/archive/` or `/tests/`

**Result:** Zero code files in project root, all organized by purpose

**Status:** Ready to execute cleanup

---

**Action Plan Created - Awaiting User Approval to Execute**
