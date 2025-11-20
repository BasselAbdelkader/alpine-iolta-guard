# Session Log - Security Architecture Planning

**Date:** November 9, 2025 (Evening Session)
**Project:** IOLTA Guard Trust Accounting System
**Session Type:** Architecture Design & Planning
**Status:** Discussion Phase - No Code Implementation Yet

---

## 📋 Session Overview

This session focused on designing the security architecture for IOLTA Guard as a **multi-tenant SaaS platform**. All discussions were architectural in nature, with no code implementation. The goal was to finalize security requirements before beginning development.

---

## 🎯 Session Objectives

1. Define the overall architecture (single-firm vs multi-tenant SaaS)
2. Design user roles and permission structure
3. Plan security features (2FA, password reset, etc.)
4. Define support model and data access policies
5. Create comprehensive documentation for future implementation
6. Identify open questions requiring business decisions

---

## ✅ Major Decisions Made

### 1. Multi-tenant SaaS Architecture (FINALIZED)

**Decision:** IOLTA Guard will be a multi-tenant SaaS platform selling to multiple law firms.

**Rationale:**
- Scalable business model
- Serve multiple customers from one platform
- Complete data isolation between firms
- Each law firm = separate tenant

**Key Characteristics:**
- Two-level registration: Firm-level + User-level
- Firm registration: Self-service with instant activation
- User registration: Admin-only within each firm
- 30-day free trial for new firms
- First user becomes Firm Administrator

**Impact:**
- Need firm management infrastructure
- Need subscription/billing system
- Need customer success tools
- Need complete data isolation

---

### 2. Privacy-First Support Model (FINALIZED)

**Decision:** Platform team (IOLTA Guard employees) CANNOT access customer firm data.

**Support Method:**
- All support via screen sharing (Teams/Zoom)
- Customer controls what platform team sees
- Zero direct access to customer data
- Major selling point: "We cannot see your data"

**Rationale:**
- Attorney-client privilege protection
- Trust accounting regulations (IOLTA compliance)
- Competitive advantage for security-conscious law firms
- Reduces liability
- Better for SOC 2/compliance audits

**Customer Success Exception:**
- Can view billing info and usage metrics ONLY
- No access to client names, cases, transactions, or financial data
- All actions logged and visible to customers

**Advantages:**
- ✅ Maximum privacy and compliance
- ✅ Customer trust and confidence
- ✅ Reduced insider threat risk
- ✅ Clear audit trail

**Disadvantages:**
- ❌ Slower support (requires customer availability)
- ❌ Cannot fix issues after-hours without customer
- ❌ More complex troubleshooting

---

### 3. Role Architecture (FINALIZED)

**Platform-Level Roles (4 roles - IOLTA Guard Team):**

#### 1. Platform Administrator
- **Who:** DevOps/IT team
- **Access:** System infrastructure ONLY
- **Can:** Manage servers, databases, deployments, backups
- **Cannot:** View customer data, access customer accounts

#### 2. Customer Success Manager (NEW)
- **Who:** Customer success team
- **Access:** Billing + metrics ONLY (no data)
- **Can View:**
  - Firm name, contact info
  - Subscription plan, billing status
  - Usage metrics (# users, # transactions, storage)
  - Login activity, feature adoption, health scores
- **Can Do:**
  - Send messages to customers (in-app)
  - Extend trial period (ONE TIME only per firm)
  - Schedule check-ins, view support history
- **Cannot:**
  - View client/case/transaction data
  - Reset passwords
  - Modify billing plans
  - Access firm accounts
- **Logging:** All actions logged and visible to customers

#### 3. Support Specialist
- **Who:** Technical support team
- **Access:** ZERO data access
- **Method:** Screen sharing (Teams/Zoom) ONLY
- **Can:** View only what customer shows them
- **Cannot:** Login to customer accounts, view data without customer

#### 4. Developer/Engineer
- **Who:** Development team
- **Access:** Code, anonymized logs, test environments
- **Cannot:** Access production customer data

---

**Firm-Level Roles (5 roles - Customer Law Firm Employees):**

#### 1. Firm Administrator (REQUIRED: Minimum 2 per firm)
- **Who:** Managing partners, office managers
- **Access:** Full access to THEIR firm's data
- **Can:**
  - Manage firm settings
  - Create/edit/delete firm users
  - Reset passwords for firm users
  - Manage all clients, cases, transactions
  - Export all firm data
- **Cannot:** See other firms' data
- **Requirement:** Each firm MUST have minimum 2 admins (for password recovery)

#### 2. Attorney
- Full operational access (no user management)

#### 3. Paralegal/Assistant
- Limited access (cannot delete/void transactions)

#### 4. Bookkeeper
- Financial focus (can manage transactions, view-only for clients/cases)

#### 5. Auditor
- Read-only access for compliance

**Permission Matrix:** Complete matrix documented in USER_REGISTRATION_AND_SECURITY.md

---

### 4. Security Features (FINALIZED)

#### 1. Two-Factor Authentication (MANDATORY)
- **Status:** REQUIRED for ALL users (not optional)
- **Method:** TOTP (Time-based One-Time Password) with authenticator apps
- **Flow:**
  - User must set up 2FA on first login
  - QR code generated for authenticator app setup
  - 10 backup codes provided for account recovery
  - Cannot access system without completing 2FA setup
- **Implementation:** Complete code examples provided in documentation

#### 2. Password Reset (From Login Screen)
- **Status:** Available to all users
- **Method:** Email-based with temporary tokens
- **Flow:**
  - "Forgot Password?" link on login page
  - Email sent with reset link (1-hour expiration)
  - User resets password
  - **IMPORTANT:** 2FA is NOT disabled (user still needs 2FA code to login)
- **Security:**
  - No user enumeration (always return success message)
  - IP tracking for all reset attempts
  - Complete audit trail
- **Implementation:** Complete code examples provided in documentation

#### 3. Firm Admin Password Recovery
- **Prevention:** Require minimum 2 Firm Admins per firm
- **Recovery Process:**
  - If ALL admins locked out (lost password + 2FA)
  - Support team verifies identity (photo ID, bar number, phone verification)
  - One-time recovery code generated (expires in 1 hour)
  - User logs in with code (bypasses 2FA ONCE)
  - Forced to reset password + setup new 2FA immediately
  - Security alert sent to all firm contacts
  - Complete audit trail with support ticket reference

#### 4. Customer Success Manager Permissions
- **Can View:** Billing info, usage metrics, health scores
- **Can Do:** Send messages, extend trial ONCE per firm
- **Cannot:** View data, reset passwords, modify billing
- **Logging:** All actions logged and visible to customers

#### 5. Self-Service Data Export
- **Who:** Firm Admin only
- **Formats:** CSV, JSON, PDF
- **What:** All firm data (clients, cases, transactions, users, reports)
- **Method:** Background job, email notification when ready
- **Download:** Link expires in 48 hours
- **Purpose:** GDPR compliance (Right to Data Portability)

#### 6. Complete Audit Logging
- **What:** All user actions (create, update, delete, login, logout)
- **What's Logged:** User, action, timestamp, IP address, changes (before/after)
- **Who Can View:** Firm Admin can view their firm's logs
- **Customer Success:** All CS actions logged and visible to customers
- **Retention:** Documented in policy (to be decided)

---

### 5. Registration Flow (FINALIZED)

#### Level 1: Firm Registration (Self-Registration)

**Flow:**
```
1. Law firm visits www.ioltaguard.com
2. Clicks "Start Free Trial" or "Sign Up"
3. Fills out form:
   - Firm Name
   - Primary Contact Name/Email
   - Phone, Address
   - Firm Size
   - State Bar Number (verification)
   - Plan Selection
4. Email verification (6-digit code)
5. CAPTCHA to prevent bots
6. Firm account created:
   - Unique tenant ID
   - 30-day trial
   - First user becomes Firm Administrator
7. Welcome email with setup link
8. User sets password + sets up 2FA (MANDATORY)
9. Firm Admin can now:
   - Add more Firm Admins (REQUIRED - min 2 total)
   - Add users (attorneys, paralegals, etc.)
   - Configure firm settings
   - Start using the system
```

**What Gets Created:**
- Firm record (tenant)
- First Firm Administrator user
- Default settings
- Isolated data space
- Trial subscription (30 days)

#### Level 2: User Registration (Admin-Only Within Firm)

**Flow:**
```
1. Firm Admin logs in
2. Goes to "Settings" → "User Management"
3. Clicks "Add New User"
4. Fills out form:
   - Name, Email
   - Role (Attorney, Paralegal, Bookkeeper, Auditor, Firm Admin)
5. System creates user
6. Welcome email sent to user
7. User sets password + sets up 2FA (MANDATORY)
8. User can now access the firm's data
```

**Important:** Users ALWAYS tied to their firm. Cannot see other firms' data.

---

## 📄 Documentation Created

### Updated: `/docs/USER_REGISTRATION_AND_SECURITY.md`

**Size:** 2,100+ lines
**Status:** Comprehensive design document

**Contents:**

1. **Architecture Overview**
   - Multi-tenant SaaS model
   - Key principles (data isolation, privacy-first, two-level access)

2. **User Security Levels**
   - Platform-level roles (4 roles with complete descriptions)
   - Firm-level roles (5 roles with complete descriptions)
   - Permission matrix (complete table)

3. **Registration Workflow**
   - Level 1: Firm registration (complete flow with code)
   - Level 2: User registration (complete flow with code)

4. **Authentication & Authorization**
   - Session-based authentication
   - Multi-tenant data isolation (complete code examples)
   - Role-based permissions (complete code examples)

5. **Multi-tenant Implementation**
   - Database models (LawFirm, UserProfile with complete code)
   - Middleware (tenant isolation)
   - Model managers (automatic firm filtering)

6. **Platform Team Roles**
   - Customer Success dashboard (complete code)
   - Trial extension logic (complete code)
   - Activity logging (complete code)

7. **Support & Password Recovery**
   - Screen sharing support model
   - Firm Admin password recovery (complete code)
   - Emergency recovery request model (complete code)
   - Self-service data export (complete code)

8. **Security Best Practices**
   - 2FA implementation (complete code with pyotp)
   - Password reset implementation (complete code)
   - Account lockout (complete code)
   - Complete activity logging (complete code)
   - Session security configuration

9. **Permission Matrix**
   - Complete table showing all permissions for all roles

10. **Implementation Plan**
    - 10 phases over 12 weeks
    - Detailed tasks and deliverables for each phase

11. **OPEN QUESTIONS (10 questions requiring decisions)**
    - Break glass emergency access
    - Firm registration billing
    - User limits & pricing
    - Password expiration policy
    - Session & concurrent logins
    - Billing plan modifications
    - Multi-firm user access
    - Firm cancellation handling
    - Support ticket system
    - Legal & compliance

---

## 📋 Open Questions Requiring Decisions

These 10 questions are documented in detail in USER_REGISTRATION_AND_SECURITY.md:

### 1. "Break Glass" Emergency Access

**Question:** Should platform team have emergency access to customer data in critical situations?

**Options:**
- **A)** No break glass (maximum privacy) - Slower support
- **B)** Only with customer consent (balanced) - Customer must approve
- **C)** Allowed in emergencies (in TOS) - Can fix critical issues quickly

**Your Decision:** [ ] A, B, or C?

---

### 2. Firm Registration Billing

**Question:** How should billing work for trial registrations?

**Options:**
- **A)** No credit card for trial (lower barrier, more signups)
- **B)** Credit card required for trial (higher conversion, fewer tire-kickers)

**Trial Expiration Options:**
- Account paused (read-only)
- Account locked (no access)
- Grace period (3-7 days)

**Your Decision:** [ ] A or B? [ ] Expiration handling?

---

### 3. User Limits & Pricing

**Question:** How should pricing work?

**Options:**
- **A)** Per-user pricing ($X/user/month, unlimited users)
- **B)** Tiered plans (Basic $99 for 5 users, Pro $299 for 25 users, etc.)
- **C)** Hybrid ($199 base + 10 users, $15/each additional)

**Other Limits:**
- Max transactions per month?
- Max storage per firm?

**Your Decision:** [ ] A, B, or C? [ ] Other limits?

---

### 4. Password Expiration Policy

**Question:** Should passwords expire periodically?

**Options:**
- **A)** Expire every 90 days (meets compliance, annoying for users)
- **B)** No expiration (modern approach, better UX)
- **C)** Firm choice (flexible, more complex)

**Password History:**
- Prevent reusing last 5 passwords?

**Your Decision:** [ ] A, B, or C? [ ] Password history?

---

### 5. Session & Concurrent Login Policy

**Questions:**
- **Session timeout:** Keep 30 minutes or change?
- **Concurrent logins:** Allow multiple devices? One session only?
- **"Remember Me":** Allow extended sessions (30 days)?

**Your Decisions:**
- [ ] Session timeout: ___ minutes
- [ ] Concurrent logins: Allow / Block / Limit to X
- [ ] "Remember Me": Yes / No

---

### 6. Customer Success Permissions

**Question:** Who can modify billing plans?

**Options:**
- Firm Admin only (self-service)
- Sales team (separate role)
- Platform Administrator

**Automatic Billing:**
- Auto-upgrade if limit exceeded?
- Block adding users if limit reached?

**Your Decisions:**
- [ ] Who modifies billing?
- [ ] Auto-upgrade or block?

---

### 7. Multi-Firm User Access

**Question:** Can one user belong to multiple firms?

**Context:** Some attorneys work for multiple firms (consultants, part-time)

**Options:**
- **A)** One firm per user (simpler, clearer audit trail)
- **B)** Multiple firms per user (better UX, more complex)

**Your Decision:** [ ] A or B?

---

### 8. Firm Deactivation / Cancellation

**Question:** What happens when a firm cancels?

**Options:**
- **A)** Immediate lock + 30-day deletion (clean, harsh)
- **B)** Active until billing cycle end (customer-friendly)
- **C)** Read-only grace period 60 days (encourages exports)

**Data Deletion:**
- Permanently deleted?
- Soft deleted (recoverable with fee)?
- Archived (anonymized for compliance)?

**Your Decisions:**
- [ ] Cancellation handling: A, B, or C?
- [ ] Data deletion: Permanent / Soft / Archived?

---

### 9. Support Ticket System

**Question:** In-app ticketing or email-only?

**Options:**
- **A)** Email-only (simple, less integrated)
- **B)** In-app ticketing (better UX, more dev work)

**Your Decision:** [ ] A or B?

---

### 10. Legal & Compliance

**Questions for Legal Review:**
- [ ] Data storage region/country?
- [ ] SOC 2 compliance timeline?
- [ ] GDPR compliance needed?
- [ ] Cyber insurance required?
- [ ] Data breach notification procedure?
- [ ] Subpoena response procedure?
- [ ] Attorney-client privilege protections?
- [ ] IOLTA regulation compliance by state?

---

## 🎯 Next Steps

### Immediate
1. **Review** `/docs/USER_REGISTRATION_AND_SECURITY.md` (2,100+ lines)
2. **Make decisions** on all 10 open questions above
3. **Prioritize** features for MVP vs later phases

### Implementation (After Decisions Made)
1. **Phase 1 (Week 1-2):** Multi-tenant database schema
2. **Phase 2 (Week 3):** Firm registration & onboarding
3. **Phase 3 (Week 4):** 2FA implementation (MANDATORY)
4. **Phase 4 (Week 5):** Password reset workflow
5. **Phase 5 (Week 6-7):** Role-based permissions
6. **Phase 6 (Week 8):** Customer Success portal
7. **Phase 7 (Week 9):** Audit logging
8. **Phase 8 (Week 10):** Emergency recovery
9. **Phase 9 (Week 11):** Data export
10. **Phase 10 (Week 12):** Testing & launch

**Total Timeline:** 12 weeks from start to launch

---

## 📊 Session Statistics

**Time Spent:** ~2 hours (discussion and documentation)
**Code Written:** 0 lines (design phase only)
**Documentation Created:** 1 comprehensive document (2,100+ lines)
**Decisions Made:** 5 major architectural decisions
**Open Questions:** 10 business decisions required
**Next Phase:** Make decisions → Begin implementation

---

## 🔑 Key Takeaways

1. **Multi-tenant SaaS** - Selling to multiple law firms, not single-firm deployment
2. **Privacy-First** - Platform team cannot see customer data (major selling point)
3. **Two-Level Registration** - Firm signs up → Firm Admin adds users
4. **2FA Mandatory** - All users must enable 2FA (no exceptions)
5. **Customer Success** - New role with metrics-only access (no data)
6. **Minimum 2 Admins** - Required per firm for password recovery
7. **Screen Sharing Support** - All support via Teams/Zoom (no direct access)
8. **Self-Service Export** - Firm Admin can export all data (GDPR compliance)
9. **Complete Audit Trail** - All actions logged with IP tracking
10. **10 Open Questions** - Business decisions needed before implementation

---

## 📝 Files Modified

### Updated:
- `/docs/USER_REGISTRATION_AND_SECURITY.md` - Complete rewrite (2,100+ lines)
- `/home/amin/Projects/ve_demo/CLAUDE.md` - Updated security section

### Created:
- `/home/amin/Projects/ve_demo/SESSION_LOG_2025_11_09_SECURITY_ARCHITECTURE.md` (this file)

---

**Session End Time:** November 9, 2025 (Evening)
**Status:** Design Complete - Awaiting Business Decisions
**Next Session:** Review decisions and begin Phase 1 implementation

---

**Remember:** All 30 bugs are fixed. Core system is production-ready. Security features are designed but not implemented yet. No code changes until decisions are finalized.
