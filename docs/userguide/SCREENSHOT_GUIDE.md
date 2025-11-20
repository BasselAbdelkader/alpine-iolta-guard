# Screenshot Guide for User Documentation

**System URL:** http://localhost
**Date:** November 13, 2025
**Purpose:** Guide for capturing screenshots to complete user documentation

---

## Overview

The user guides contain screenshot placeholders that need to be replaced with actual screenshots. This guide provides:
- Exact URLs to navigate to
- What to show in each screenshot
- How to capture the screenshot
- Where to place it in the documentation

---

## Screenshot Requirements

### Tools Needed
- Web browser (Chrome, Firefox, or Safari recommended)
- Screenshot tool (built-in or third-party)
- Image editor (optional, for cropping/annotations)

### Image Specifications
- **Format:** PNG (recommended) or JPG
- **Size:** Full window width, or cropped to relevant area
- **Quality:** High resolution (no blur)
- **Annotations:** Optional (arrows, highlights)

---

## Screenshot List by Document

### Document 1: Getting Started Guide

**File:** `01_GETTING_STARTED.md`

---

#### Screenshot 1: Login Page
**URL:** http://localhost/html/login.html (or http://localhost/auth/login/)
**What to show:**
- Login form with username and password fields
- Login button
- IOLTA Guard logo/title
- Clean, professional appearance

**Where to capture:**
- Full browser window or just the login card

**Placeholder location:**
- Line ~28: `**Screenshot placeholder:** [URL_HERE - Login Page]`

**Screenshot name suggestion:** `01_login_page.png`

---

#### Screenshot 2: Login Form Filled
**URL:** http://localhost/html/login.html
**What to show:**
- Username field filled with example: "admin" or "john.smith"
- Password field showing dots (for security)
- Login button highlighted or ready to click

**Where to capture:**
- Just the login form area

**Placeholder location:**
- Line ~35: `**Screenshot placeholder:** [URL_HERE - Login Form Filled]`

**Screenshot name suggestion:** `02_login_form_filled.png`

---

#### Screenshot 3: Dashboard Overview
**URL:** http://localhost/html/dashboard.html
**What to show:**
- Full dashboard view
- Statistics cards (Total Clients, Active Cases, Total Balance)
- Quick action buttons
- Navigation menu visible
- Recent transactions or activities

**Where to capture:**
- Full page view showing all dashboard elements

**Placeholder location:**
- Line ~63: `**Screenshot placeholder:** [URL_HERE - Dashboard Overview]`

**Screenshot name suggestion:** `03_dashboard_overview.png`

---

#### Screenshot 4: Add New Client Form
**URL:** http://localhost/html/clients.html (click "Add New Client" button)
**What to show:**
- Modal or form for adding new client
- All fields visible (First Name, Last Name, Email, Phone, Address, etc.)
- Save/Cancel buttons
- Clear, readable form layout

**Where to capture:**
- The modal/form dialog

**Placeholder location:**
- Line ~88: `**Screenshot placeholder:** [URL_HERE - Add New Client Form]`

**Screenshot name suggestion:** `04_add_client_form.png`

---

#### Screenshot 5: Add New Case Form
**URL:** http://localhost/html/client-detail.html?id=X (click "Add New Case")
**What to show:**
- Case creation form/modal
- Fields: Case Number, Case Title, Opened Date, Matter Type, Description
- Save/Cancel buttons

**Where to capture:**
- The case form modal

**Placeholder location:**
- Line ~110: `**Screenshot placeholder:** [URL_HERE - Add New Case Form]`

**Screenshot name suggestion:** `05_add_case_form.png`

---

#### Screenshot 6: Add Deposit Form
**URL:** http://localhost/html/case-detail.html?id=X (click "Add Transaction")
**What to show:**
- Transaction form with "Deposit" type selected
- Fields: Amount, Transaction Date, Bank Account, Description
- Save/Cancel buttons
- Clear indication it's a deposit

**Where to capture:**
- Transaction form modal

**Placeholder location:**
- Line ~132: `**Screenshot placeholder:** [URL_HERE - Add Deposit Form]`

**Screenshot name suggestion:** `06_add_deposit_form.png`

---

#### Screenshot 7: Add Withdrawal Form
**URL:** http://localhost/html/case-detail.html?id=X (click "Add Transaction", select Withdrawal)
**What to show:**
- Transaction form with "Withdrawal" type selected
- Fields: Amount, Date, Account, Payee, Description, Check Number
- Emphasis on withdrawal-specific fields (Payee, Check #)

**Where to capture:**
- Transaction form modal

**Placeholder location:**
- Line ~154: `**Screenshot placeholder:** [URL_HERE - Add Withdrawal Form]`

**Screenshot name suggestion:** `07_add_withdrawal_form.png`

---

### Document 2: Clients and Cases Guide

**File:** `02_CLIENTS_AND_CASES.md`

---

#### Screenshot 8: Clients List Page
**URL:** http://localhost/html/clients.html
**What to show:**
- Full list of clients
- Columns: Name, Email, Phone, Balance, Status
- Search box at top
- "Add New Client" button
- Several client records visible

**Where to capture:**
- Full page or main content area

**Placeholder location:**
- Line ~51: `**Screenshot placeholder:** [URL_HERE - Clients List Page]`

**Screenshot name suggestion:** `08_clients_list.png`

---

#### Screenshot 9: Client Detail Page
**URL:** http://localhost/html/client-detail.html?id=X
**What to show:**
- Client information section (name, contact details, balance)
- List of cases for this client
- Action buttons (Edit Client, Add New Case)
- Transaction history or case details

**Where to capture:**
- Full page showing client info and cases

**Placeholder location:**
- Line ~124: `**Screenshot placeholder:** [URL_HERE - Client Detail Page]`

**Screenshot name suggestion:** `09_client_detail_page.png`

---

#### Screenshot 10: Edit Client Form
**URL:** http://localhost/html/client-detail.html?id=X (click "Edit Client")
**What to show:**
- Edit client modal/form
- Fields populated with existing client data
- All editable fields visible
- Save/Cancel buttons

**Where to capture:**
- Edit form modal

**Placeholder location:**
- Line ~176: `**Screenshot placeholder:** [URL_HERE - Edit Client Form]`

**Screenshot name suggestion:** `10_edit_client_form.png`

---

#### Screenshot 11: Add Client Form (duplicate reference)
**URL:** http://localhost/html/clients.html (click "Add New Client")
**What to show:**
- Same as Screenshot 4
- Empty form ready for new client entry

**Placeholder location:**
- Line ~223: `**Screenshot placeholder:** [URL_HERE - Add Client Form]`

**Screenshot name suggestion:** `11_add_client_form_full.png`

---

#### Screenshot 12: Add Case Form (from client detail)
**URL:** http://localhost/html/client-detail.html?id=X (click "Add New Case")
**What to show:**
- Case creation form
- Client name shown or pre-selected
- All case fields visible

**Placeholder location:**
- Line ~268: `**Screenshot placeholder:** [URL_HERE - Add Case Form]`

**Screenshot name suggestion:** `12_add_case_form.png`

---

#### Screenshot 13: Case Detail Page
**URL:** http://localhost/html/case-detail.html?id=X
**What to show:**
- Case information (case number, title, status, dates)
- Client information (breadcrumb or link back)
- Transaction list with dates, types, amounts, balances
- Current balance prominently displayed
- Add Transaction button

**Where to capture:**
- Full page view

**Placeholder location:**
- Line ~295: `**Screenshot placeholder:** [URL_HERE - Case Detail Page]`

**Screenshot name suggestion:** `13_case_detail_page.png`

---

#### Screenshot 14: Close Case
**URL:** http://localhost/html/case-detail.html?id=X (Edit case, set to Closed)
**What to show:**
- Edit case form/modal
- Status dropdown showing "Closed" selected
- Closed Date field visible and required
- Save button

**Placeholder location:**
- Line ~360: `**Screenshot placeholder:** [URL_HERE - Close Case]`

**Screenshot name suggestion:** `14_close_case.png`

---

## Complete Screenshot Checklist

Use this checklist to track your progress:

- [ ] 01_login_page.png - http://localhost/html/login.html
- [ ] 02_login_form_filled.png - http://localhost/html/login.html
- [ ] 03_dashboard_overview.png - http://localhost/html/dashboard.html
- [ ] 04_add_client_form.png - http://localhost/html/clients.html
- [ ] 05_add_case_form.png - http://localhost/html/client-detail.html
- [ ] 06_add_deposit_form.png - http://localhost/html/case-detail.html
- [ ] 07_add_withdrawal_form.png - http://localhost/html/case-detail.html
- [ ] 08_clients_list.png - http://localhost/html/clients.html
- [ ] 09_client_detail_page.png - http://localhost/html/client-detail.html
- [ ] 10_edit_client_form.png - http://localhost/html/client-detail.html
- [ ] 11_add_client_form_full.png - http://localhost/html/clients.html
- [ ] 12_add_case_form.png - http://localhost/html/client-detail.html
- [ ] 13_case_detail_page.png - http://localhost/html/case-detail.html
- [ ] 14_close_case.png - http://localhost/html/case-detail.html

**Total Screenshots Needed:** 14

---

## How to Capture Screenshots

### Windows
- **Full Screen:** Press `PrtScn` or `Windows + Shift + S`
- **Snipping Tool:** Search for "Snipping Tool" in Start Menu
- **Region:** Windows + Shift + S, then drag to select area

### macOS
- **Full Screen:** Press `Cmd + Shift + 3`
- **Region:** Press `Cmd + Shift + 4`, then drag to select area
- **Window:** Press `Cmd + Shift + 4`, then press `Space`, click window

### Linux
- **Full Screen:** Press `PrtScn`
- **Region:** Press `Shift + PrtScn`, drag to select area
- **Screenshot Tool:** Most distros have built-in screenshot tools

### Browser Extensions (Recommended)
- **Awesome Screenshot** (Chrome, Firefox)
- **Nimbus Screenshot** (Chrome, Firefox)
- **Fireshot** (Chrome, Firefox)

Benefits: Capture full page, annotate, auto-save

---

## Screenshot Storage

### Recommended Structure
```
docs/userguide/screenshots/
├── 01_login_page.png
├── 02_login_form_filled.png
├── 03_dashboard_overview.png
├── 04_add_client_form.png
├── 05_add_case_form.png
├── 06_add_deposit_form.png
├── 07_add_withdrawal_form.png
├── 08_clients_list.png
├── 09_client_detail_page.png
├── 10_edit_client_form.png
├── 11_add_client_form_full.png
├── 12_add_case_form.png
├── 13_case_detail_page.png
└── 14_close_case.png
```

### Create Directory
```bash
mkdir -p /home/amin/Projects/ve_demo/docs/userguide/screenshots
```

---

## How to Add Screenshots to Documentation

### Option 1: Markdown Image Syntax
Replace placeholder:
```markdown
**Screenshot placeholder:** [URL_HERE - Login Page]
```

With:
```markdown
![Login Page](./screenshots/01_login_page.png)
```

### Option 2: HTML Image Tag (with sizing)
```markdown
<img src="./screenshots/01_login_page.png" alt="Login Page" width="800">
```

### Option 3: Keep Placeholder + Add Image
```markdown
![Login Page](./screenshots/01_login_page.png)

**URL:** http://localhost/html/login.html
```

---

## Best Practices

### Before Capturing

1. **Clean Data:** Use realistic but safe data (no real client info)
2. **Example Names:** Use "John Doe", "Jane Smith", etc.
3. **Example Amounts:** Use clear amounts like $1,000.00, $5,000.00
4. **Browser Zoom:** Set to 100% for consistency
5. **Clear Cache:** Ensure fresh page load

### While Capturing

1. **Consistent Browser:** Use same browser for all screenshots
2. **Same Window Size:** Keep browser window same size
3. **Hide Personal Info:** No real names, emails, or sensitive data
4. **Clean UI:** Close developer tools, bookmarks bar
5. **Mouse Cursor:** Decide if cursor should be visible

### After Capturing

1. **Crop:** Remove unnecessary browser chrome if desired
2. **Resize:** Optimize for web (800-1200px width recommended)
3. **Annotate:** Add arrows/highlights if needed
4. **Compress:** Optimize file size (use tools like TinyPNG)
5. **Review:** Check readability and quality

---

## Sample Data for Screenshots

Use this sample data for consistent, professional screenshots:

### Clients
- John Doe (john.doe@example.com)
- Jane Smith (jane.smith@example.com)
- Robert Johnson (robert.j@example.com)

### Cases
- 2025-001: Personal Injury Settlement
- 2025-002: Real Estate Closing
- 2025-003: Estate Administration

### Transactions
- Deposits: $10,000.00, $5,000.00, $2,500.00
- Withdrawals: $1,000.00, $500.00, $250.00

### Bank Accounts
- IOLTA Trust Account - Checking
- Account #: ****1234
- Bank: First National Bank

---

## Testing Navigation

Before taking screenshots, verify these URLs work:

```bash
# Login page
http://localhost/html/login.html

# Dashboard (after login)
http://localhost/html/dashboard.html

# Clients list
http://localhost/html/clients.html

# Client detail (replace X with actual client ID)
http://localhost/html/client-detail.html?id=X

# Case detail (replace X with actual case ID)
http://localhost/html/case-detail.html?id=X

# Bank accounts
http://localhost/html/bank-accounts.html

# Reports
http://localhost/html/reports.html
```

---

## Troubleshooting

### Issue: Page doesn't load
**Solution:** Ensure Docker containers are running
```bash
docker ps
docker-compose up -d
```

### Issue: Not logged in
**Solution:** Login first at http://localhost/html/login.html

### Issue: No data to show
**Solution:** Create sample data:
1. Add a client
2. Add a case for that client
3. Add transactions to the case

### Issue: Page looks different than expected
**Solution:**
- Clear browser cache
- Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
- Check if latest code is deployed

---

## Screenshot Quality Checklist

For each screenshot, verify:
- [ ] Clear and readable text
- [ ] No personal/sensitive information
- [ ] Consistent with other screenshots (same browser, size)
- [ ] Properly cropped (no unnecessary elements)
- [ ] Good color and contrast
- [ ] File size optimized (<500KB ideally)
- [ ] Correctly named
- [ ] Saved in correct directory

---

## Timeline Estimate

**Per Screenshot:** 2-3 minutes
**Total for 14 Screenshots:** 30-45 minutes

**Breakdown:**
- Navigation: 30 seconds
- Setup data (if needed): 1 minute
- Capture: 30 seconds
- Review/crop: 30-60 seconds
- Save/name: 30 seconds

---

## After Screenshots Are Captured

1. **Update Documentation:**
   - Replace all placeholders with actual images
   - Verify images display correctly
   - Check file paths are correct

2. **Review:**
   - Read through docs with screenshots
   - Ensure flow makes sense
   - Verify quality and consistency

3. **Commit to Git:**
   ```bash
   git add docs/userguide/screenshots/
   git commit -m "docs: Add user guide screenshots"
   ```

---

## Alternative: Keep Placeholders

If you prefer not to add screenshots now:
1. Keep placeholders as-is
2. Screenshots can be added later
3. Documentation is still useful without them
4. Users can reference this guide when needed

---

## Contact

For questions about screenshots or documentation:
- See main documentation in `docs/README.md`
- Contact development team

---

**Created:** November 13, 2025
**Last Updated:** November 13, 2025
**Version:** 1.0

---

*This guide ensures consistent, high-quality screenshots for professional user documentation.*
