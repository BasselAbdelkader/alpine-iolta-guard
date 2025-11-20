# Negative Trust Account Balances - Data Integrity Issue

**Date:** November 10, 2025
**Severity:** 🟡 **HIGH** - Trust account compliance issue
**Status:** ⚠️ **REQUIRES REVIEW**

---

## 📊 SUMMARY

The dashboard reports **75 clients with negative balances totaling -$826,104.13**.

This is a **data integrity issue** from the QuickBooks CSV import. Trust accounts should NEVER have negative balances - this violates IOLTA regulations.

---

## 🔍 ANALYSIS

### Overall Statistics:

```sql
Clients with Negative Balances: 75
Total Negative Amount: -$826,104.13
Worst Balance: -$77,911.77 (Daniel Gonzales)
Best Negative Balance: -$458.08
```

### Breakdown by Source:

| Data Source | Clients | Percentage |
|-------------|---------|------------|
| CSV Import  | 74      | 98.7%      |
| Webapp      | 1       | 1.3%       |

**Finding:** Nearly all negative balances (74 out of 75) came from the QuickBooks CSV import, indicating this is historical data that already had issues.

---

## 📋 TOP 20 CLIENTS WITH NEGATIVE BALANCES

| Client Number | Client Name        | Balance      | Transactions | Source |
|---------------|-------------------|--------------|--------------|--------|
| QB-0021       | Daniel Gonzales    | -$77,911.77  | 1            | csv    |
| QB-0138       | Pamela Ramos       | -$71,792.80  | 2            | csv    |
| QB-0094       | Jessica Russell    | -$67,561.66  | 8            | csv    |
| QB-0058       | Melissa Young      | -$37,142.70  | 15           | csv    |
| QB-0017       | John Dunn          | -$26,192.16  | 13           | csv    |
| QB-0032       | Margaret Lopez     | -$26,088.65  | 9            | csv    |
| QB-0073       | Emma Bailey        | -$24,982.97  | 8            | csv    |
| QB-0099       | Patricia Alvarez   | -$23,612.75  | 7            | csv    |
| QB-0006       | Carolyn Stephens   | -$21,694.94  | 15           | csv    |
| QB-0081       | Sharon Woods       | -$19,662.96  | 9            | csv    |
| QB-0080       | James Ruiz         | -$16,664.59  | 7            | csv    |
| TEST-0061     | George Campbell    | -$16,473.47  | 6            | webapp |
| QB-0023       | Linda Hawkins      | -$15,996.96  | 4            | csv    |
| QB-0095       | Edward Washington  | -$15,234.31  | 7            | csv    |
| QB-0117       | Linda Myers        | -$14,826.32  | 5            | csv    |
| QB-0166       | Jennifer Jenkins   | -$14,634.93  | 5            | csv    |
| QB-0061       | Jack Salazar       | -$14,634.52  | 6            | csv    |
| QB-0139       | Steven Harris      | -$13,768.79  | 4            | csv    |
| QB-0149       | Paul Jackson       | -$12,959.86  | 7            | csv    |
| QB-0068       | George Walker      | -$11,735.03  | 13           | csv    |

---

## 🔍 CASE STUDY: Ashley Thomas (Case #286)

### Transaction History:

| Date       | Type       | Amount      | Description          | Running Balance |
|------------|------------|-------------|----------------------|-----------------|
| 07/14/2023 | DEPOSIT    | $27,670.74  | Settlement Check     | $27,670.74      |
| 07/14/2023 | DEPOSIT    | $6,880.48   | Settlement Check     | $34,551.22      |
| 08/15/2023 | WITHDRAWAL | $464.38     | Provider             | $34,086.84      |
| 08/15/2023 | WITHDRAWAL | $3,989.37   | Provider             | $30,097.47      |
| 08/15/2023 | WITHDRAWAL | $1,706.63   | Provider             | $28,390.84      |
| 08/15/2023 | WITHDRAWAL | $728.44     | Provider             | $27,662.40      |
| 08/15/2023 | WITHDRAWAL | $18,966.73  | Settlement to client | $8,695.67       |
| 08/31/2023 | WITHDRAWAL | $14.81      | CJ Reimbursement     | $8,680.86       |
| 08/31/2023 | WITHDRAWAL | **$15,869.25** | **Lawyer Fee**    | **-$7,188.39** ⚠️ |

### What Happened:

1. Client received total deposits of $34,551.22
2. Multiple withdrawals for providers and client settlement
3. Balance was $8,680.86 before final withdrawal
4. **Lawyer fee of $15,869.25 exceeded available balance** by $7,188.39
5. Result: Trust account went negative

### Why This Is a Problem:

- **IOLTA Violation:** Trust accounts cannot have negative balances
- **Commingling:** Negative balance means law firm used its own funds or another client's money
- **Compliance Risk:** This could trigger IOLTA audit findings

---

## 🚨 ROOT CAUSES

### 1. CSV Import Allowed Negative Balances

The QuickBooks CSV import did NOT validate sufficient funds before creating withdrawal transactions.

**Issue:** The import script should have checked:
```python
if transaction_type == 'WITHDRAWAL':
    current_balance = case.calculate_balance()
    if current_balance < amount:
        raise ValidationError("Insufficient funds")
```

### 2. Historical Data Issues

The QuickBooks data itself had negative balances, meaning:
- The original QuickBooks setup allowed overdrafts
- These may have been corrected later (not reflected in CSV export date range)
- Data may represent partial account history

### 3. Missing Deposits

Some clients may have had deposits that:
- Occurred before the CSV export date range
- Were in a different QuickBooks account not included in export
- Were manually recorded elsewhere

---

## ⚖️ LEGAL & COMPLIANCE IMPLICATIONS

### IOLTA Rules:

1. **No Negative Balances:** Trust accounts must never go negative
2. **No Commingling:** Each client's funds must be tracked separately
3. **Immediate Correction:** Negative balances must be corrected immediately
4. **Reporting:** May need to be reported to bar association

### Possible Explanations (Legal):

1. **Operating Account Transfer:** Law firm transferred from operating account to cover shortage
2. **Delayed Deposits:** Deposit was pending but withdrawal processed first
3. **Account Reconciliation:** Adjustments made in a different system
4. **Data Export Timing:** Partial data snapshot

---

## ✅ RECOMMENDATIONS

### Immediate Actions:

1. **Review Each Negative Balance Case:**
   - Identify why it went negative
   - Check if correction transactions exist
   - Verify actual bank statement balances

2. **Data Validation:**
   - Compare CSV data to actual QuickBooks reports
   - Check for missing deposits or duplicate withdrawals
   - Verify date ranges of exported data

3. **Client Communication:**
   - Determine if these are active or closed cases
   - For active cases, verify current actual balances
   - Reconcile with bank statements

### Long-Term Solutions:

1. **Add Insufficient Funds Validation:**
```python
# In serializers.py
def validate(self, data):
    if data['transaction_type'] == 'WITHDRAWAL':
        case = data['case']
        current_balance = case.calculate_balance()
        if current_balance < data['amount']:
            raise serializers.ValidationError({
                'amount': f'Insufficient funds. Current balance: ${current_balance:.2f}'
            })
    return data
```

2. **Add Database Constraint:**
```sql
-- Prevent negative case balances at database level
CREATE OR REPLACE FUNCTION check_case_balance()
RETURNS TRIGGER AS $$
DECLARE
    case_balance NUMERIC(12,2);
BEGIN
    SELECT COALESCE(SUM(
        CASE WHEN transaction_type = 'DEPOSIT' THEN amount
             WHEN transaction_type = 'WITHDRAWAL' THEN -amount
             ELSE 0 END
    ), 0) INTO case_balance
    FROM bank_transactions
    WHERE case_id = NEW.case_id;
    
    IF case_balance < 0 THEN
        RAISE EXCEPTION 'Transaction would result in negative balance';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER prevent_negative_balance
AFTER INSERT OR UPDATE ON bank_transactions
FOR EACH ROW EXECUTE FUNCTION check_case_balance();
```

3. **Audit Report:**
   - Create report showing all negative balances
   - Include date when balance went negative
   - Track correction transactions

4. **Dashboard Alert:**
   - Add prominent warning for negative balances
   - Highlight in red on client list
   - Send email alerts for new negative balances

---

## 📊 QUERIES FOR INVESTIGATION

### List All Clients with Negative Balances:
```sql
WITH client_balances AS (
    SELECT 
        c.id,
        c.client_number,
        c.first_name || ' ' || c.last_name as client_name,
        COALESCE(SUM(CASE WHEN bt.transaction_type = 'DEPOSIT' THEN bt.amount 
                          WHEN bt.transaction_type = 'WITHDRAWAL' THEN -bt.amount 
                          ELSE 0 END), 0) as balance
    FROM clients c
    LEFT JOIN cases ca ON ca.client_id = c.id
    LEFT JOIN bank_transactions bt ON bt.case_id = ca.id
    GROUP BY c.id
)
SELECT * FROM client_balances WHERE balance < 0 ORDER BY balance;
```

### Find When Balance Went Negative:
```sql
WITH RECURSIVE transaction_history AS (
    SELECT 
        bt.id,
        bt.case_id,
        bt.transaction_date,
        bt.transaction_type,
        bt.amount,
        SUM(CASE WHEN bt.transaction_type = 'DEPOSIT' THEN bt.amount 
                 WHEN bt.transaction_type = 'WITHDRAWAL' THEN -bt.amount 
                 ELSE 0 END) OVER (PARTITION BY bt.case_id ORDER BY bt.transaction_date, bt.id) as running_balance
    FROM bank_transactions bt
)
SELECT * FROM transaction_history WHERE running_balance < 0;
```

---

## 🎯 DECISION REQUIRED

You need to decide how to handle these negative balances:

### Option A: Accept Historical Data As-Is
- Mark these as "historical import issues"
- Document that they existed in QuickBooks
- Monitor for NEW negative balances only

### Option B: Require Correction
- Do not allow system to show negative balances
- Add correcting deposit transactions
- Mark corrections with "Balance Adjustment" description

### Option C: Data Investigation
- Review QuickBooks source data
- Re-export with wider date range
- Import missing transactions

### Option D: Case Closure
- If cases are closed, mark balances as "final settlement"
- Document reason for negative balance
- Transfer to operating account to clear

---

## ✅ CURRENT STATUS

**System Behavior:**
- ✅ Dashboard correctly shows 75 negative balances
- ✅ Total amount correctly calculated: -$826,104.13
- ✅ Balances display in red (warning color)
- ⚠️ System ALLOWS negative balances (no validation)
- ⚠️ No alerts or warnings when creating negative balances

**Recommended Next Step:**
1. Review top 10 worst negative balances
2. Determine if correction is needed
3. Add validation to prevent NEW negative balances
4. Document historical issues

---

**Documentation Date:** November 10, 2025
**Issue Status:** ⚠️ ACTIVE - Requires decision on handling
**Files:** 75 clients affected, 74 from CSV import

