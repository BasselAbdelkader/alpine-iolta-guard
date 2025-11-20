# IOLTA Guard Documentation

**Last Updated:** November 14, 2025
**Version:** 1.1
**Status:** Professional Documentation Set Complete - Now Organized

---

## 📚 Documentation Overview

This directory contains comprehensive, professional documentation for the IOLTA Guard Trust Accounting System, organized by audience and purpose.

**Recent Update (November 14, 2025):** All documentation has been reorganized into logical categories:
- 15 session logs → `sessions/`
- 53 bug fix documents → `fixes/`
- 47 feature implementation documents → `features/`
- 15 deployment guides → `deployment/`

**Before:** 110+ .md files scattered in project root
**After:** 5 essential files in root, 130+ files organized in /docs

---

## 📁 Documentation Structure

### 👨‍💻 For Software Developers & Architects

**Directory:** `developer/`

| Document | Description | Audience |
|----------|-------------|----------|
| **[01_ARCHITECTURE_OVERVIEW.md](./developer/01_ARCHITECTURE_OVERVIEW.md)** | Complete system architecture, technology stack, design patterns, deployment architecture | Software Architects, Senior Developers, DevOps Engineers |
| **[02_DEVELOPER_GUIDE.md](./developer/02_DEVELOPER_GUIDE.md)** | Development environment setup, coding guidelines, API development, testing procedures | Software Developers, New Team Members |

**Contents:**
- System architecture diagrams
- Technology stack (Django, PostgreSQL, Docker)
- Component architecture (apps, models, APIs)
- Data architecture & database schema
- Security architecture
- Development workflow
- Code examples and best practices
- Debugging and troubleshooting

---

### 👥 For End Users (Law Firm Staff)

**Directory:** `userguide/`

| Document | Description | Audience |
|----------|-------------|----------|
| **[01_GETTING_STARTED.md](./userguide/01_GETTING_STARTED.md)** | Introduction, login, dashboard overview, first tasks | New Users, Attorneys, Paralegals, Bookkeepers |
| **[02_CLIENTS_AND_CASES.md](./userguide/02_CLIENTS_AND_CASES.md)** | Managing clients and cases, creating records, best practices | All Law Firm Staff |

**Future Additions:**
- 03_TRANSACTIONS.md (Recording deposits and withdrawals)
- 04_REPORTS.md (Generating compliance reports)
- 05_BANK_ACCOUNTS.md (Bank account management)

**Language:** Non-technical, simple, step-by-step instructions with screenshots

**Purpose:** Enable law firm staff to use the system effectively without technical knowledge

---

### 📋 For Auditors & Compliance Officers

**Directory:** `compliance/`

| Document | Description | Audience |
|----------|-------------|----------|
| **[AUDIT_AND_COMPLIANCE_GUIDE.md](./compliance/AUDIT_AND_COMPLIANCE_GUIDE.md)** | Complete audit controls, compliance features, regulatory framework, audit procedures | External Auditors, State Bar Officials, Compliance Officers, Managing Partners |

**Contents:**
- Regulatory framework (IOLTA, ABA Model Rules)
- System audit controls (immutability, audit trail, timestamps)
- Data integrity mechanisms
- Transaction audit trail
- Compliance reporting
- Internal controls (preventative, detective, corrective)
- Security & access controls
- Backup & disaster recovery
- Audit procedures with SQL queries
- Compliance checklists

**Purpose:** Demonstrate regulatory compliance and provide audit documentation

---

### 🔧 Technical Reference Materials

| Document | Description |
|----------|-------------|
| US_FORMAT_IMPLEMENTATION_SUMMARY.md | Date and money formatting (MM/DD/YYYY, $1,234.56) |
| TRANSACTION_ORDERING_SUMMARY.md | Chronological ordering implementation |
| FIELD_REPLACEMENT_SUMMARY.md | Field name changes and migrations |
| TRANSACTION_ORDER_FIX.md | Case detail transaction order fix |
| USER_REGISTRATION_AND_SECURITY.md | Multi-tenant SaaS security architecture design (2,100+ lines) |

**Purpose:** Detailed technical implementation documentation for developers

---

### 📦 Development History

**Directory:** `sessions/` - 15 files
Development session logs documenting all major work sessions, decisions, and progress.

**Directory:** `fixes/` - 53 files
Bug fix documentation for all 30 MFLP bugs plus additional fixes.

**Directory:** `features/` - 47 files
Feature implementation documentation including:
- CSV Import System
- QuickBooks Integration
- Pagination Implementation
- Negative Balances Report
- Import Management UI
- And more...

**Directory:** `deployment/` - 15 files
Deployment guides for various scenarios (production, customer, Alpine migration, Docker setup).

**Purpose:** Preserve development history and provide context for future work

---

## Quick Start Guides

### For New Developers

1. **Read:** [Architecture Overview](./developer/01_ARCHITECTURE_OVERVIEW.md#executive-summary)
2. **Setup:** [Development Environment](./developer/02_DEVELOPER_GUIDE.md#development-environment-setup)
3. **Code:** [Your First Feature](./developer/02_DEVELOPER_GUIDE.md#creating-a-new-django-app)

**Estimated Time:** 2-3 hours

### For New Users

1. **Read:** [Getting Started Guide](./userguide/01_GETTING_STARTED.md)
2. **Try:** [Your First Tasks](./userguide/01_GETTING_STARTED.md#your-first-tasks)
3. **Learn:** [Clients & Cases](./userguide/02_CLIENTS_AND_CASES.md)

**Estimated Time:** 30 minutes

### For Auditors

1. **Read:** [Audit Guide Executive Summary](./compliance/AUDIT_AND_COMPLIANCE_GUIDE.md#executive-summary)
2. **Review:** [System Audit Controls](./compliance/AUDIT_AND_COMPLIANCE_GUIDE.md#system-audit-controls)
3. **Perform:** [Audit Procedures](./compliance/AUDIT_AND_COMPLIANCE_GUIDE.md#audit-procedures)

**Estimated Time:** 2-4 hours for full audit review

---

## Additional Resources

### In Project Root
- **[CLAUDE.md](../CLAUDE.md)** - Project guide for AI development sessions
- **[README.md](../README.md)** - Project overview and quick reference
- **[Jira.csv](../Jira.csv)** - Bug tracking (30 bugs, 100% fixed)

### Cleanup Guide
- **[DOCUMENTATION_CLEANUP_RECOMMENDATIONS.md](./DOCUMENTATION_CLEANUP_RECOMMENDATIONS.md)** - Recommendations for organizing and archiving documentation

### External Resources
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [ABA Model Rules](https://www.americanbar.org/groups/professional_responsibility/publications/model_rules_of_professional_conduct/)

---

## Documentation Roadmap

### Completed ✅
- [x] Architecture Overview
- [x] Developer Guide
- [x] Getting Started (User Guide)
- [x] Clients & Cases (User Guide)
- [x] Audit & Compliance Guide
- [x] Documentation Cleanup Recommendations

### Planned 📝
- [ ] User Guide: 03_TRANSACTIONS.md
- [ ] User Guide: 04_REPORTS.md
- [ ] User Guide: 05_BANK_ACCOUNTS.md
- [ ] Developer Guide: 03_TROUBLESHOOTING_GUIDE.md
- [ ] Developer Guide: 04_API_REFERENCE.md
- [ ] Compliance: COMPLIANCE_REPORTS.md (sample report templates)
- [ ] Architecture: DEPLOYMENT_GUIDE.md (production deployment)
- [ ] Architecture: PERFORMANCE_TUNING.md
- [ ] Screenshots for all user guides

---

**For the latest project status and development guidelines, see [CLAUDE.md](../CLAUDE.md) in the project root.**

---

*IOLTA Guard Documentation | Version 1.0 | November 13, 2025*
*Quality Documentation for Quality Software*
