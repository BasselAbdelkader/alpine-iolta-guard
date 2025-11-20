# Fix - Data Source Field Values

**Issue:** After adding `data_source` field with new choices (`'webapp'`, `'csv_import'`, `'api_import'`), old records had value `'csv'` which is not in the valid choices.

**Impact:** This could cause serialization/validation issues when the API tries to return clients.

---

## ✅ Fix Applied

Updated all old `'csv'` values to `'csv_import'`:

```sql
UPDATE clients SET data_source = 'csv_import' WHERE data_source = 'csv';
UPDATE cases SET data_source = 'csv_import' WHERE data_source = 'csv';
UPDATE bank_transactions SET data_source = 'csv_import' WHERE data_source = 'csv';
UPDATE vendors SET data_source = 'csv_import' WHERE data_source = 'csv';
```

**Results:**
- ✅ 166 clients updated
- ✅ 194 cases updated
- ✅ 1,263 transactions updated
- ✅ 0 vendors updated

---

## 📊 Current Distribution

```
Clients by data_source:
  - webapp: 79
  - csv_import: 166
  - api_import: 0

Total active clients: 243
```

---

## 🔧 How to Prevent This

When adding new fields with choices to existing tables:

1. **Add field with nullable or default first:**
   ```python
   data_source = models.CharField(max_length=20, null=True, blank=True)
   ```

2. **Run migration**

3. **Update existing data:**
   ```python
   # In data migration or SQL
   UPDATE table_name SET data_source = 'webapp' WHERE data_source IS NULL;
   ```

4. **Then add choices and make non-nullable:**
   ```python
   data_source = models.CharField(
       max_length=20,
       choices=[...],
       default='webapp'
   )
   ```

---

## ✅ Status

**Fixed:** All data_source values are now valid
**Client page:** Should now display all clients correctly
**No data lost:** All 243 clients are still active and accessible
