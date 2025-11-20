# IOLTA Guard - Software Architecture Overview

**Document Version:** 1.0
**Last Updated:** November 13, 2025
**Target Audience:** Software Architects, Senior Developers, DevOps Engineers
**Classification:** Technical Documentation

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Design Principles](#design-principles)
5. [Component Architecture](#component-architecture)
6. [Data Architecture](#data-architecture)
7. [Security Architecture](#security-architecture)
8. [Deployment Architecture](#deployment-architecture)
9. [Integration Points](#integration-points)
10. [Scalability & Performance](#scalability--performance)

---

## Executive Summary

### System Purpose

IOLTA Guard is a trust accounting management system specifically designed for law firms to manage Interest on Lawyers' Trust Accounts (IOLTA) in compliance with state bar regulations. The system provides comprehensive client fund management, transaction tracking, reconciliation, and compliance reporting.

### Architectural Style

- **Pattern:** Monolithic with API-first design
- **Deployment:** Containerized microservices (Docker)
- **Data Tier:** PostgreSQL (RDBMS)
- **Frontend:** Server-side rendered HTML with JavaScript SPA components
- **API:** RESTful API (Django REST Framework)

### Key Architectural Decisions

1. **Monolithic Backend:** Django application serving both web pages and API endpoints
2. **Separate Frontend Container:** Nginx serving static files for performance optimization
3. **Session-Based Authentication:** Mature, secure authentication without token complexity
4. **PostgreSQL:** ACID compliance critical for financial transactions
5. **Alpine Linux:** Minimal attack surface, reduced container size

### System Characteristics

- **Domain:** Trust Accounting for Legal Industry
- **Users:** Law firm staff (attorneys, paralegals, bookkeepers)
- **Transaction Volume:** Low to medium (typically <10,000 transactions/month per firm)
- **Data Sensitivity:** HIGH - Client funds, attorney-client privilege
- **Compliance:** State bar regulations, IOLTA rules, financial auditing standards

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         IOLTA Guard System                       │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Frontend   │  HTTP   │   Backend    │  SQL    │   Database   │
│   Container  │────────▶│   Container  │────────▶│   Container  │
│   (Nginx)    │  :80    │   (Django)   │  :5432  │ (PostgreSQL) │
└──────────────┘         └──────────────┘         └──────────────┘
     Alpine                   Alpine                   Alpine
   Static Files           Python 3.12              PostgreSQL 16
   HTML/JS/CSS          Django 5.1.3               Trust Account DB
```

### Container Architecture

#### 1. Frontend Container (`iolta_frontend_alpine`)
- **Base Image:** nginx:alpine
- **Purpose:** Serve static files, reverse proxy to backend
- **Port:** 80 (HTTP)
- **Components:**
  - HTML pages (login, dashboard, clients, transactions, reports)
  - JavaScript application files
  - CSS stylesheets
  - Static assets (images, fonts)

#### 2. Backend Container (`iolta_backend_alpine`)
- **Base Image:** python:3.12-alpine
- **Purpose:** Business logic, API endpoints, data processing
- **Port:** 8000 (Gunicorn)
- **Components:**
  - Django 5.1.3 application
  - Django REST Framework 3.15.2
  - Business logic modules
  - Data models
  - API serializers and views

#### 3. Database Container (`iolta_db_alpine`)
- **Base Image:** postgres:16-alpine
- **Purpose:** Data persistence, transactional integrity
- **Port:** 5432 (PostgreSQL)
- **Components:**
  - PostgreSQL 16 database engine
  - Trust account database
  - Transaction logs
  - Backup/restore capabilities

### Network Architecture

```
┌────────────────────────────────────────────────────────┐
│                   Docker Bridge Network                 │
│                    (iolta_network)                      │
└────────────────────────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐       ┌────▼────┐      ┌────▼────┐
    │Frontend │       │Backend  │      │Database │
    │  :80    │──────▶│  :8000  │──────▶│  :5432  │
    └─────────┘       └─────────┘      └─────────┘
         │                 │                 │
    External           Internal          Internal
    (Public)           (Private)         (Private)
```

**Network Isolation:**
- Frontend: Exposed to host (port 80)
- Backend: Internal only (accessed via frontend proxy)
- Database: Internal only (accessed only by backend)

---

## Technology Stack

### Backend Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Runtime** | Python | 3.12 | Application language |
| **Framework** | Django | 5.1.3 | Web application framework |
| **API Framework** | Django REST Framework | 3.15.2 | RESTful API development |
| **Database ORM** | Django ORM | 5.1.3 | Object-relational mapping |
| **WSGI Server** | Gunicorn | 22.0.0 | Production WSGI server |
| **Database Driver** | psycopg2-binary | 2.9.9 | PostgreSQL adapter |
| **CORS** | django-cors-headers | 4.3.1 | Cross-origin resource sharing |
| **Filtering** | django-filter | 24.2 | QuerySet filtering |
| **OS** | Alpine Linux | 3.x | Minimal container OS |

### Frontend Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Web Server** | Nginx | 1.27-alpine | Static file serving, reverse proxy |
| **UI Framework** | Bootstrap | 5.3.0 | Responsive UI components |
| **JavaScript** | Vanilla JS | ES6+ | Client-side interactivity |
| **HTTP Client** | Fetch API | Native | API communication |
| **Templating** | Django Templates | 5.1.3 | Server-side rendering |

### Database Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **RDBMS** | PostgreSQL | 16-alpine | Relational database |
| **Connection Pooling** | pgBouncer | (optional) | Connection management |
| **Backup** | pg_dump | 16 | Database backup |

### DevOps & Infrastructure

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Containerization** | Docker | 24+ | Application containerization |
| **Orchestration** | Docker Compose | 2+ | Multi-container management |
| **CI/CD** | (TBD) | - | Continuous integration/deployment |
| **Monitoring** | (TBD) | - | System monitoring |
| **Logging** | (TBD) | - | Centralized logging |

---

## Design Principles

### 1. Security First

**Principle:** All design decisions prioritize security and data protection.

**Implementation:**
- Session-based authentication with secure cookies
- CSRF protection on all state-changing operations
- SQL injection prevention via ORM parameterized queries
- XSS prevention via template auto-escaping
- Password hashing with PBKDF2 (Django default)
- HTTPS enforcement in production
- Secure headers (X-Frame-Options, X-Content-Type-Options)

**Rationale:** Trust accounting involves client funds and confidential information requiring highest security standards.

### 2. Data Integrity

**Principle:** Financial data must maintain ACID properties at all times.

**Implementation:**
- PostgreSQL transactions for multi-step operations
- Database constraints (foreign keys, unique constraints, check constraints)
- No cascade deletes on financial records
- Soft deletes for audit trail preservation
- Balance calculations from source transactions (never cached)
- Void transactions instead of deletion

**Rationale:** Financial records must be immutable and auditable.

### 3. Audit Trail

**Principle:** Every action must be traceable and auditable.

**Implementation:**
- Created_at and updated_at timestamps on all models
- Void reasons for transaction voidance
- User tracking on all actions
- Immutable transaction history
- Chronological ordering (oldest-first) for clarity

**Rationale:** Legal and regulatory compliance requires complete audit trails.

### 4. Simplicity Over Complexity

**Principle:** Use the simplest solution that meets requirements.

**Implementation:**
- Monolithic architecture (not microservices)
- Session authentication (not JWT)
- Direct SQL queries (not caching layers)
- Server-side rendering with JavaScript enhancement
- Minimal dependencies

**Rationale:** Financial systems require reliability over sophistication.

### 5. Fail-Safe Defaults

**Principle:** System should fail securely and predictably.

**Implementation:**
- Transactions require client/case assignment (no orphans)
- Insufficient funds prevent negative balances
- Closed cases reject new transactions
- Default deny for permissions
- Explicit validation on all inputs

**Rationale:** Financial errors must be prevented, not corrected.

### 6. API-First Design

**Principle:** All functionality exposed via documented APIs.

**Implementation:**
- RESTful API for all operations
- Django REST Framework serializers
- Consistent error responses
- Comprehensive validation
- Swagger/OpenAPI documentation (future)

**Rationale:** Enables future mobile apps, integrations, and automation.

---

## Component Architecture

### Backend Components

#### 1. Django Apps (Bounded Contexts)

```
apps/
├── api/              # API routing and common API utilities
├── bank_accounts/    # Bank account management
├── checks/           # Check printing and management
├── clients/          # Client (person/entity) management
├── dashboard/        # Dashboard views and statistics
├── reports/          # Financial reports and compliance
├── settings/         # System settings and configuration
├── settlements/      # Settlement tracking
├── transactions/     # Transaction management (deprecated - moved to bank_accounts)
└── vendors/          # Vendor management
```

**App Responsibilities:**

| App | Domain | Key Models | Purpose |
|-----|--------|-----------|---------|
| **clients** | Client Management | Client, Case | Manage clients and their cases |
| **bank_accounts** | Financial Core | BankAccount, BankTransaction | Bank accounts and all financial transactions |
| **vendors** | Vendor Management | Vendor | Third-party payees |
| **reports** | Reporting | (queries) | Financial reports and exports |
| **dashboard** | Analytics | (aggregations) | Key metrics and statistics |
| **settings** | Configuration | Settings | System configuration |
| **checks** | Disbursement | CheckPrint | Check generation and printing |

#### 2. Model Layer (Data Models)

**Core Domain Models:**

```python
# Client Domain
Client
  - first_name, last_name, email, phone
  - address, city, state, zip_code
  - trust_account_status
  - is_active

Case
  - client (FK)
  - case_number, case_title, description
  - opened_date, closed_date
  - status (Open/Closed)
  - matter_type

# Financial Domain
BankAccount
  - account_name, account_number, routing_number
  - bank_name
  - account_type (Checking/Savings)
  - current_balance (calculated)

BankTransaction
  - account (FK)
  - client (FK)
  - case (FK)
  - transaction_type (DEPOSIT/WITHDRAWAL/TRANSFER_OUT/TRANSFER_IN)
  - amount, transaction_date
  - payee, description
  - check_number
  - status (cleared/voided)
  - void_reason
```

**Design Pattern:** Active Record pattern via Django ORM

**Key Methods:**
- `get_current_balance()` - Calculate real-time balance from transactions
- `get_formatted_balance()` - Format balance for display (parentheses for negatives)
- `void_transaction()` - Void instead of delete

#### 3. API Layer (REST Framework)

**Structure:**
```
apps/{app}/api/
├── serializers.py    # Data serialization/validation
├── views.py          # API endpoints (ViewSets)
└── permissions.py    # Custom permissions
```

**Example API Endpoint:**
```python
# apps/clients/api/views.py
class ClientViewSet(viewsets.ModelViewSet):
    """
    API endpoint for client management
    GET    /api/clients/          - List all clients
    POST   /api/clients/          - Create new client
    GET    /api/clients/{id}/     - Retrieve client details
    PUT    /api/clients/{id}/     - Update client
    DELETE /api/clients/{id}/     - Delete client
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email']
```

**Serializer Example:**
```python
class ClientSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    current_balance = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True,
        source='get_current_balance'
    )

    class Meta:
        model = Client
        fields = '__all__'

    def validate(self, data):
        # Custom validation logic
        return data
```

#### 4. View Layer (Django Views)

**Pattern:** Class-based views for consistency

```python
from django.views.generic import TemplateView

class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_clients'] = Client.objects.filter(is_active=True).count()
        context['total_balance'] = calculate_total_balance()
        return context
```

### Frontend Components

#### 1. Page Structure

```
html/
├── login.html              # Authentication
├── dashboard.html          # Main dashboard
├── clients.html            # Client list
├── client-detail.html      # Client details with cases
├── case-detail.html        # Case details with transactions
├── bank-accounts.html      # Bank account management
├── bank-transactions.html  # Transaction list
├── reports.html            # Report generation
└── settings.html           # System settings
```

#### 2. JavaScript Modules

```
js/
├── api.js                  # API communication layer
├── auth.js                 # Authentication logic
├── dashboard.js            # Dashboard functionality
├── clients.js              # Client management
├── client-detail.js        # Client detail page logic
├── case-detail.js          # Case detail page logic
├── bank-accounts.js        # Bank account management
├── bank-transactions.js    # Transaction management
├── reports.js              # Report generation
└── settings.js             # Settings management
```

**JavaScript Architecture:**
- **No Framework:** Vanilla JavaScript for simplicity
- **Module Pattern:** Each page has its own JS file
- **Fetch API:** For all backend communication
- **Progressive Enhancement:** Pages work with JS disabled (basic functionality)

#### 3. Common UI Patterns

**Bootstrap 5 Components:**
- Cards for data display
- Modals for forms
- Tables for data lists
- Alerts for notifications
- Buttons for actions

**Custom Components:**
- Transaction tables with balance calculation
- Client search with auto-complete
- Date pickers (US format MM/DD/YYYY)
- Currency formatters ($1,234.56 or ($1,234.56) for negatives)

---

## Data Architecture

### Database Schema Overview

```
┌──────────────────────────────────────────────────────────┐
│                    Database Schema                        │
└──────────────────────────────────────────────────────────┘

┌─────────────┐         ┌─────────────┐         ┌─────────────────┐
│   Client    │────────▶│    Case     │────────▶│ BankTransaction │
│             │  1:N    │             │  1:N    │                 │
│ - id        │         │ - id        │         │ - id            │
│ - name      │         │ - number    │         │ - amount        │
│ - email     │         │ - title     │         │ - type          │
│ - balance() │         │ - status    │         │ - date          │
└─────────────┘         └─────────────┘         └─────────────────┘
                                                         │
                                                         │ N:1
                                                         ▼
                                                 ┌──────────────┐
                                                 │ BankAccount  │
                                                 │              │
                                                 │ - id         │
                                                 │ - name       │
                                                 │ - number     │
                                                 └──────────────┘
```

### Core Entities

#### Client
- **Purpose:** Represents individuals or entities with funds in trust
- **Unique Constraint:** (first_name, last_name) combination
- **Balance:** Calculated dynamically from transactions
- **Status:** Active/Dormant/Closed

#### Case
- **Purpose:** Legal matter associated with client
- **Unique Constraint:** case_number (firm-wide)
- **Status:** Open/Closed
- **Business Rule:** No transactions allowed when closed

#### BankTransaction
- **Purpose:** All financial movements (deposits, withdrawals, transfers)
- **Immutability:** Cannot be deleted, only voided
- **Types:** DEPOSIT, WITHDRAWAL, TRANSFER_IN, TRANSFER_OUT
- **Status:** cleared, voided

#### BankAccount
- **Purpose:** Physical bank accounts holding trust funds
- **Type:** Checking or Savings
- **Balance:** Sum of all non-voided transactions

### Data Integrity Rules

1. **Referential Integrity:**
   - All transactions must reference valid client, case, and account
   - Foreign keys with PROTECT on delete (prevents orphaned data)

2. **Business Rules:**
   - Client-Case relationship: Transaction must use case belonging to transaction's client
   - Insufficient funds: Withdrawal cannot exceed available balance
   - Closed case: No new transactions allowed
   - Zero amount: Transactions must have amount > 0

3. **Audit Trail:**
   - All models have created_at, updated_at timestamps
   - Voided transactions preserve original data + void_reason
   - No cascade deletes on financial data

### Indexing Strategy

```sql
-- Performance-critical indexes
CREATE INDEX idx_client_name ON clients(last_name, first_name);
CREATE INDEX idx_case_number ON cases(case_number);
CREATE INDEX idx_case_client ON cases(client_id);
CREATE INDEX idx_transaction_date ON bank_transactions(transaction_date);
CREATE INDEX idx_transaction_client ON bank_transactions(client_id);
CREATE INDEX idx_transaction_case ON bank_transactions(case_id);
CREATE INDEX idx_transaction_status ON bank_transactions(status);

-- Unique constraints
CREATE UNIQUE INDEX idx_client_unique_name ON clients(first_name, last_name);
CREATE UNIQUE INDEX idx_case_unique_number ON cases(case_number);
```

---

## Security Architecture

### Authentication

**Method:** Session-based authentication (Django sessions)

**Flow:**
```
1. User submits username/password to /auth/login/
2. Django authenticates via django.contrib.auth
3. Session created, session ID stored in secure cookie
4. Session ID sent with all subsequent requests
5. Backend validates session on each request
6. Logout destroys session
```

**Configuration:**
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_COOKIE_AGE = 1800  # 30 minutes
SESSION_SAVE_EVERY_REQUEST = True  # Refresh on activity
SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF protection
```

### Authorization

**Pattern:** Role-based access control (future implementation)

**Current State:** All authenticated users have full access

**Planned:**
```python
# Permission classes
IsAuthenticated          # Must be logged in
IsFirmAdmin             # Firm administrator role
IsAttorney              # Attorney role
CanManageTransactions   # Can create/edit transactions
```

### Data Protection

**Encryption:**
- **In Transit:** HTTPS/TLS 1.3 (production)
- **At Rest:** Database encryption (PostgreSQL LUKS/dm-crypt)
- **Passwords:** PBKDF2 with 600,000 iterations

**Input Validation:**
- Django ORM prevents SQL injection
- Django templates auto-escape HTML (XSS prevention)
- CSRF tokens on all POST/PUT/DELETE requests
- Form validation via serializers

**Sensitive Data Handling:**
- Bank account numbers: Store full number (required for reconciliation)
- Social Security Numbers: NOT stored
- Credit Card Numbers: NOT stored

### Security Headers

```python
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

---

## Deployment Architecture

### Production Environment

```
┌────────────────────────────────────────────────────────┐
│               Production Infrastructure                 │
└────────────────────────────────────────────────────────┘

┌─────────────┐
│   Clients   │
│  (Browsers) │
└──────┬──────┘
       │ HTTPS (443)
       ▼
┌─────────────────┐
│  Load Balancer  │ (optional)
│   / Nginx Proxy │
└──────┬──────────┘
       │
       ▼
┌─────────────────────────┐
│   Docker Host Server    │
│  ┌──────────────────┐   │
│  │  Docker Compose  │   │
│  │  ┌────────────┐  │   │
│  │  │  Frontend  │  │   │
│  │  │  Backend   │  │   │
│  │  │  Database  │  │   │
│  │  └────────────┘  │   │
│  └──────────────────┘   │
│                          │
│  ┌──────────────────┐   │
│  │  Volume Storage  │   │
│  │  - Database data │   │
│  │  - Static files  │   │
│  │  - Logs          │   │
│  └──────────────────┘   │
└─────────────────────────┘
```

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    container_name: iolta_db_alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=iolta_guard_db
      - POSTGRES_USER=iolta_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    networks:
      - iolta_network

  backend:
    build: ./backend
    container_name: iolta_backend_alpine
    volumes:
      - ./backend:/app
      - static_volume:/app/staticfiles
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://iolta_user:${DB_PASSWORD}@db:5432/iolta_guard_db
    depends_on:
      - db
    networks:
      - iolta_network

  frontend:
    image: nginx:alpine
    container_name: iolta_frontend_alpine
    volumes:
      - ./frontend:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
      - "443:443"  # HTTPS
    depends_on:
      - backend
    networks:
      - iolta_network

networks:
  iolta_network:
    driver: bridge

volumes:
  postgres_data:
  static_volume:
```

### Container Resource Limits

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

---

## Integration Points

### External Integrations (Future)

1. **QuickBooks Integration**
   - Export transactions to QuickBooks format
   - Status: Planned (import UI exists)

2. **Banking APIs**
   - Bank statement import
   - Automated reconciliation
   - Status: Future consideration

3. **Email Services**
   - Welcome emails
   - Notification emails
   - Status: Design phase

4. **PDF Generation**
   - Check printing
   - Report exports
   - Status: Partially implemented

---

## Scalability & Performance

### Current Performance Characteristics

- **Concurrent Users:** Designed for 5-50 concurrent users per firm
- **Transaction Volume:** Optimized for <10,000 transactions/month
- **Response Time:** <200ms for most operations
- **Database Size:** Expected <10GB per firm annually

### Optimization Strategies

1. **Database Optimization:**
   - Strategic indexes on foreign keys and search fields
   - Query optimization via Django ORM select_related/prefetch_related
   - Balance calculation caching (future)

2. **Static File Optimization:**
   - Nginx for static file serving
   - Browser caching headers
   - Minification (future)

3. **Application Optimization:**
   - Pagination on large datasets
   - Lazy loading of transaction lists
   - Efficient serializers

### Future Scalability Considerations

**Multi-tenancy:**
- Separate database per firm, or
- Single database with firm_id filtering (tenant isolation)

**Horizontal Scaling:**
- Stateless backend (session in database)
- Load balancer ready
- Read replicas for reporting

**Caching:**
- Redis for session storage
- Cached balance calculations
- Query result caching

---

## Architectural Patterns Used

### Backend Patterns

1. **Model-View-Template (MVT):** Django's variation of MVC
2. **Repository Pattern:** Django ORM acts as repository
3. **Service Layer:** Business logic in model methods
4. **Active Record:** Models contain data + behavior
5. **Serializer Pattern:** DRF serializers for API data

### Frontend Patterns

1. **Progressive Enhancement:** Basic functionality without JavaScript
2. **Module Pattern:** Each page has isolated JavaScript module
3. **Fetch-Then-Render:** API calls then DOM updates
4. **Template Literals:** For dynamic HTML generation

### Data Patterns

1. **Soft Delete:** Voiding instead of deletion
2. **Calculated Fields:** Balance calculated on-demand
3. **Audit Trail:** Timestamps on all modifications
4. **Immutable Transactions:** Financial records never edited

---

## Future Architecture Evolution

### Planned Enhancements

1. **Multi-tenant SaaS Architecture**
   - Firm registration and management
   - User roles and permissions
   - Data isolation per firm

2. **Two-Factor Authentication (2FA)**
   - TOTP-based authentication
   - Backup codes
   - Mandatory for all users

3. **Advanced Reporting**
   - Custom report builder
   - Scheduled report generation
   - Export to Excel/PDF

4. **Mobile Application**
   - React Native or Flutter app
   - Read-only access initially
   - Full functionality later

5. **Banking Integration**
   - OFX file import
   - Automated reconciliation
   - Real-time balance checking

---

## Appendix

### A. Glossary

- **IOLTA:** Interest on Lawyers' Trust Accounts
- **Trust Account:** Bank account holding client funds
- **Client:** Person or entity with funds in trust
- **Case:** Legal matter associated with client
- **Transaction:** Financial movement (deposit/withdrawal)
- **Void:** Mark transaction as cancelled (not deleted)

### B. References

- Django Documentation: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Docker Documentation: https://docs.docker.com/

### C. Contact Information

- **Architecture Questions:** [Your contact]
- **Technical Support:** [Your contact]
- **Security Issues:** [Your contact]

---

**Document Control:**
- **Version:** 1.0
- **Authors:** Development Team
- **Reviewed By:** [Pending]
- **Next Review Date:** [TBD]

---

*This document is confidential and proprietary. Unauthorized distribution is prohibited.*
