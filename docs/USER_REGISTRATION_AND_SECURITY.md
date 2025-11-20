# User Registration and Security Levels - IOLTA Guard

**Project:** IOLTA Guard Trust Accounting System (Multi-tenant SaaS)
**Date:** November 9, 2025
**Purpose:** Document user registration, authentication, and security level implementation
**Status:** Design & Implementation Guide
**Architecture:** Multi-tenant SaaS serving multiple law firms

---

## ⚡ KEY SECURITY DECISIONS (FINALIZED)

### 🏢 **SaaS Architecture:**

**IOLTA Guard is a Multi-tenant SaaS Platform**
- Sell to multiple law firms (each firm = separate tenant)
- Complete data isolation between firms
- Two-level registration: Firm-level + User-level

### 🔒 **Mandatory Security Requirements:**

1. **✅ 2FA is REQUIRED for ALL users** (Not optional)
   - All users must set up 2FA on first login
   - Uses TOTP (Time-based One-Time Password) with authenticator apps
   - 10 backup codes provided for account recovery

2. **✅ Password Reset from Login Screen** (Available to all users)
   - "Forgot Password?" link on login page
   - Email-based reset with 1-hour expiration tokens
   - Does NOT disable 2FA (security feature)
   - Fully audited with IP tracking

3. **✅ NO Platform Team Data Access** (Privacy-first approach)
   - Platform team CANNOT see customer firm data
   - Support via screen sharing only (Teams/Zoom)
   - Customer Success can view billing + metrics only (no data)
   - Major selling point: "We cannot see your data"

4. **✅ Firm Admin Password Recovery**
   - **Prevention:** Require minimum 2 Firm Admins per firm
   - **Recovery:** Identity verification + one-time recovery code
   - Full audit trail with support ticket reference

5. **✅ Customer Success Manager Role**
   - Can view billing info and usage metrics
   - Can send messages to customers
   - Can extend trial ONCE per firm
   - Cannot reset passwords or view data
   - All actions logged

6. **✅ Self-Service Data Export**
   - Firm Admin can export all data (CSV/JSON/PDF)
   - GDPR compliance (Right to Data Portability)
   - No platform team involvement

7. **✅ Complete Activity Logging**
   - All Customer Success actions logged
   - Customers can view access logs
   - Full audit trail for compliance

### 🎯 **Registration Model:**

**Two-Level Registration:**
1. **Firm Registration** (Self-registration with instant activation)
   - Law firms sign up for free trial
   - First user becomes Firm Administrator
   - 30-day trial period

2. **User Registration** (Admin-only within each firm)
   - Only Firm Admins can create users
   - Users tied to specific firm
   - Cannot see other firms' data

### 🎯 **Implementation Priority:**
- Phase 1: Multi-tenant database schema
- Phase 2: Firm registration & onboarding
- Phase 3: 2FA implementation (MANDATORY)
- Phase 4: Password reset workflow
- Phase 5: Role-based permissions
- Phase 6: Customer Success portal
- Phase 7: Audit logging

**See sections below for complete implementation details.**

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [User Security Levels](#user-security-levels)
3. [Registration Workflow](#registration-workflow)
4. [Authentication & Authorization](#authentication--authorization)
5. [Multi-tenant Implementation](#multi-tenant-implementation)
6. [Platform Team Roles](#platform-team-roles)
7. [Support & Password Recovery](#support--password-recovery)
8. [Implementation Plan](#implementation-plan)
9. [Security Best Practices](#security-best-practices)
10. [Open Questions](#open-questions)

---

## 🏗️ Architecture Overview

### Multi-tenant SaaS Model

IOLTA Guard operates as a **multi-tenant SaaS platform** serving multiple law firms:

```
┌─────────────────────────────────────────────────────────────┐
│              IOLTA Guard SaaS Platform                      │
│            (Platform Team - No Data Access)                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          │                               │
    ┌─────▼──────┐                 ┌─────▼──────┐
    │  Firm A    │                 │  Firm B    │
    │ (Tenant 1) │                 │ (Tenant 2) │
    │ Smith Law  │                 │ Jones Law  │
    └─────┬──────┘                 └─────┬──────┘
          │                               │
    ┌─────┴──────┐                 ┌─────┴──────┐
    │            │                 │            │
┌───▼───┐  ┌────▼────┐       ┌────▼───┐  ┌────▼────┐
│Admin 1│  │Attorney │       │Admin 1 │  │Paralegal│
│(Jane) │  │  (Bob)  │       │ (Tom)  │  │ (Sarah) │
└───────┘  └─────────┘       └────────┘  └─────────┘
```

### Key Principles

1. **Complete Data Isolation**
   - Each firm's data completely separate
   - No cross-tenant data access
   - Firm-specific database queries

2. **Privacy-First Support Model**
   - Platform team cannot access firm data
   - Support via screen sharing only
   - Customer controls what's visible

3. **Two-Level Access Control**
   - Platform-level (infrastructure, billing, metrics)
   - Firm-level (operational, client data)

---

## 🔍 Current Implementation

### Existing Authentication

**Backend Framework:** Django 5.1.3 with built-in authentication
**Authentication Method:** Session-based authentication
**User Model:** Django's default `User` model

**Current Features:**
- ✅ Login/Logout functionality
- ✅ Session management
- ✅ Password hashing (Django PBKDF2)
- ✅ CSRF protection
- ✅ IsAuthenticated permission on API endpoints

**API Authentication:**
```python
# From apps/clients/api/views.py
permission_classes = [IsAuthenticated]
authentication_classes = [SecureSessionAuthentication]
```

---

## 👥 User Security Levels

### Platform-Level Roles (IOLTA Guard Team)

These roles are for YOUR team - employees of IOLTA Guard who operate the platform.

#### 1. **Platform Administrator**
- **Who:** DevOps/IT team
- **Access:** System infrastructure ONLY
- **Can:**
  - Manage servers, databases, deployments
  - Monitor system health
  - Perform backups
  - Scale infrastructure
- **Cannot:**
  - View customer firm data
  - Access customer accounts
  - Reset customer passwords
- **Use Case:** System maintenance, infrastructure management

#### 2. **Customer Success Manager** ⭐ NEW
- **Who:** Customer success team
- **Access:** Billing + metrics ONLY (no data)
- **Can View:**
  - Firm name, contact info
  - Subscription plan, billing status
  - Usage metrics (# users, # transactions, storage)
  - Login activity
  - Feature adoption
  - Health scores
- **Can Do:**
  - Send messages to customers (in-app)
  - Extend trial period (ONE TIME only per firm)
  - Schedule check-ins
  - View support history
- **Cannot:**
  - View client names, cases, transactions
  - Reset passwords
  - Access firm accounts
  - Modify billing plans
  - View financial data
- **Logging:** All actions logged and visible to customers
- **Use Case:** Customer onboarding, renewals, upsells, health monitoring

#### 3. **Support Specialist**
- **Who:** Technical support team
- **Access:** ZERO direct access to customer data
- **Support Method:** Screen sharing (Teams/Zoom) ONLY
- **Can:**
  - View only what customer shows them
  - Guide customers through troubleshooting
  - Document issues for development team
- **Cannot:**
  - Login to customer accounts
  - View data without customer present
  - Reset passwords
- **Use Case:** Troubleshooting, training, bug reporting

#### 4. **Developer/Engineer**
- **Who:** Development team
- **Access:** Code, anonymized logs, test environments
- **Can:**
  - Access source code
  - View anonymized/sanitized logs
  - Work in development/staging environments
  - Fix bugs, develop features
- **Cannot:**
  - Access production customer data
  - Login to customer accounts
- **Use Case:** Development, bug fixes, feature implementation

---

### Firm-Level Roles (Customer Law Firm Employees)

These roles are for the law firm's employees - YOUR CUSTOMERS.

#### 1. **Firm Administrator** ⭐ REQUIRED: Minimum 2 per firm
- **Who:** Managing partners, office managers
- **Access:** Full access to THEIR firm's data
- **Permissions:**
  - ✅ Manage firm settings
  - ✅ Create/edit/delete firm users
  - ✅ Manage all clients and cases
  - ✅ Manage all transactions
  - ✅ Access all reports
  - ✅ Manage bank accounts
  - ✅ Configure firm preferences
  - ✅ Export all firm data
  - ✅ Reset passwords for firm users
- **Cannot:**
  - See other firms' data
  - Access platform administration
- **Requirement:** Each firm MUST have minimum 2 admins (backup/recovery)
- **Use Case:** Overall firm management

#### 2. **Attorney (Full Access)**
- **Who:** Partners, associates
- **Access:** Full operational access to their firm
- **Permissions:**
  - ✅ Create/edit/delete clients and cases
  - ✅ Create/edit/delete transactions
  - ✅ Access all reports
  - ✅ View all bank accounts
  - ❌ Cannot manage users or firm settings
- **Use Case:** Handling client matters, trust accounts

#### 3. **Paralegal/Assistant (Limited Access)**
- **Who:** Paralegals, legal assistants
- **Access:** Limited operational access
- **Permissions:**
  - ✅ Create/edit clients and cases
  - ✅ Create/edit transactions
  - ✅ View reports
  - ✅ View bank accounts (read-only)
  - ❌ Cannot delete or void transactions
  - ❌ Cannot manage users
- **Use Case:** Day-to-day case management

#### 4. **Bookkeeper (Financial Focus)**
- **Who:** Accountants, bookkeepers
- **Access:** Financial/accounting access
- **Permissions:**
  - ✅ View all clients and cases (read-only)
  - ✅ Create/edit/delete transactions
  - ✅ Access all financial reports
  - ✅ Manage bank accounts
  - ❌ Cannot manage clients/cases
  - ❌ Cannot manage users
- **Use Case:** Financial management, reconciliation

#### 5. **Auditor (Read-Only)**
- **Who:** Compliance officers, external auditors
- **Access:** Read-only for compliance
- **Permissions:**
  - ✅ View all clients, cases, transactions
  - ✅ Access all reports
  - ✅ Export data
  - ❌ Cannot create, edit, or delete anything
- **Use Case:** Compliance review, audits

---

## 🔐 Registration Workflow

### Level 1: Firm Registration (Self-Registration)

Law firms sign up for the SaaS platform.

**Flow:**
```
1. Law firm visits www.ioltaguard.com
2. Clicks "Start Free Trial" or "Sign Up"
3. Fills out FIRM registration form:
   - Firm Name
   - Primary Contact Name
   - Primary Contact Email
   - Phone Number
   - Address (Street, City, State, Zip)
   - Firm Size (dropdown: 1-5, 6-10, 11-25, 26-50, 51+)
   - State Bar Number (verification)
   - Plan Selection (Basic, Professional, Enterprise)

4. System validates:
   - Email verification (send 6-digit code)
   - CAPTCHA (prevent bots)
   - Check if firm already exists
   - Validate bar number format

5. Firm account created:
   - Unique tenant ID assigned
   - Database isolation configured
   - Firm status: "Trial" (30 days)

6. Primary contact automatically becomes FIRST Firm Administrator:
   - Receives welcome email with setup link
   - Sets password (must meet requirements)
   - Sets up 2FA (MANDATORY)

7. Firm Admin can now:
   - Access the system
   - Add additional Firm Admins (REQUIRED - min 2)
   - Add users (attorneys, paralegals, etc.)
   - Configure firm settings
   - Add bank accounts, clients, cases
```

**What Gets Created:**
- ✅ Firm record (tenant)
- ✅ First Firm Administrator user
- ✅ Default settings for the firm
- ✅ Isolated data space
- ✅ Trial subscription (30 days)

**Email Verification:**
```
Subject: Verify Your Email - IOLTA Guard

Hi [Name],

Welcome to IOLTA Guard! Please verify your email to complete registration.

Your verification code: 123456

Or click this link: https://ioltaguard.com/verify?token=abc123

This code expires in 15 minutes.

Best regards,
IOLTA Guard Team
```

**Implementation:**
```python
# apps/firms/api/views.py
class FirmRegistrationView(APIView):
    permission_classes = []  # Public endpoint

    def post(self, request):
        # Step 1: Validate input
        serializer = FirmRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        # Step 2: Check if firm already exists
        if LawFirm.objects.filter(email=request.data['email']).exists():
            return Response({
                'error': 'A firm with this email already exists'
            }, status=400)

        # Step 3: Create firm (tenant)
        firm = LawFirm.objects.create(
            firm_name=request.data['firm_name'],
            firm_number=generate_firm_number(),  # FIRM-00001
            email=request.data['email'],
            phone=request.data['phone'],
            address=request.data['address'],
            city=request.data['city'],
            state=request.data['state'],
            zip_code=request.data['zip_code'],
            bar_number=request.data['bar_number'],
            subscription_plan='trial',
            trial_ends_at=timezone.now() + timedelta(days=30)
        )

        # Step 4: Create first Firm Admin user
        user = User.objects.create_user(
            username=request.data['email'],
            email=request.data['email'],
            first_name=request.data['first_name'],
            last_name=request.data['last_name']
        )

        # Step 5: Create user profile
        UserProfile.objects.create(
            user=user,
            firm=firm,
            role='firm_admin',
            must_change_password=False,  # They set password during signup
            two_factor_required=True  # Force 2FA setup
        )

        # Step 6: Send welcome email with setup link
        send_welcome_email(user, firm)

        # Step 7: Log registration
        AuditLog.objects.create(
            firm=firm,
            action='FIRM_REGISTERED',
            object_repr=firm.firm_name,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        return Response({
            'success': True,
            'firm_id': firm.id,
            'message': 'Firm registered successfully. Check your email to complete setup.'
        })
```

---

### Level 2: User Registration (Within Firm - Admin-Only)

Firm Administrators create user accounts for their employees.

**Flow:**
```
1. Firm Admin logs into their firm's account
2. Goes to "Settings" → "User Management"
3. Clicks "Add New User"
4. Fills out form:
   - First Name, Last Name
   - Email (must be unique across system)
   - Role (Attorney, Paralegal, Bookkeeper, Auditor, Firm Admin)
   - Permissions (based on role, can customize)

5. System creates user account
6. User receives welcome email with setup link
7. User clicks link → Sets password → Sets up 2FA (MANDATORY)
8. User can now access the firm's data
```

**Important:** Users are ALWAYS tied to their specific firm. They can only see their firm's data.

**Implementation:**
```python
# apps/users/api/views.py
class UserCreateView(APIView):
    permission_classes = [IsAuthenticated, IsFirmAdmin]

    def post(self, request):
        # Validate admin permissions
        if request.user.profile.role not in ['firm_admin']:
            return Response({
                'error': 'Only Firm Administrators can create users'
            }, status=403)

        # Check if email already exists
        if User.objects.filter(email=request.data['email']).exists():
            return Response({
                'error': 'User with this email already exists'
            }, status=400)

        # Create user
        user = User.objects.create_user(
            username=request.data['email'],
            email=request.data['email'],
            first_name=request.data['first_name'],
            last_name=request.data['last_name']
        )

        # Create profile - automatically assign to admin's firm
        UserProfile.objects.create(
            user=user,
            firm=request.user.profile.firm,  # Same firm as admin
            role=request.data['role'],
            two_factor_required=True  # MANDATORY
        )

        # Generate setup token
        setup_token = generate_setup_token(user)

        # Send welcome email
        send_user_welcome_email(user, setup_token)

        # Log action
        AuditLog.objects.create(
            user=request.user,
            firm=request.user.profile.firm,
            action='USER_CREATED',
            object_repr=user.get_full_name(),
            ip_address=get_client_ip(request)
        )

        return Response({
            'success': True,
            'user_id': user.id,
            'message': f'User created. Welcome email sent to {user.email}'
        })
```

---

## 🛡️ Authentication & Authorization

### Session-Based Authentication

**Current Settings:**
```python
# settings.py
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_COOKIE_AGE = 1800  # 30 minutes
SESSION_SAVE_EVERY_REQUEST = True  # Refresh on activity
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SECURE = True
```

### Multi-Tenant Data Isolation

**Automatic Firm Filtering:**

Every database query automatically filters by the user's firm:

```python
# Middleware: apps/core/middleware.py
class TenantMiddleware:
    """Ensure all queries filter by user's firm"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Set current firm on request
            request.firm = request.user.profile.firm

        return self.get_response(request)


# Model Manager: apps/clients/models.py
class ClientManager(models.Manager):
    def get_queryset(self):
        """Always filter by current firm"""
        qs = super().get_queryset()

        # Get current request from thread-local storage
        firm = get_current_firm()
        if firm:
            qs = qs.filter(firm=firm)

        return qs

class Client(models.Model):
    firm = models.ForeignKey(
        'firms.LawFirm',
        on_delete=models.PROTECT,
        related_name='clients'
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    # ... other fields

    objects = ClientManager()

    class Meta:
        indexes = [
            models.Index(fields=['firm', 'last_name']),  # Optimize firm queries
        ]
```

### Role-Based Permissions

**Custom Permission Classes:**

```python
# apps/core/permissions.py
from rest_framework import permissions

class IsFirmAdmin(permissions.BasePermission):
    """Allow access only to Firm Administrators"""
    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                request.user.profile.role == 'firm_admin')

class IsAttorneyOrAbove(permissions.BasePermission):
    """Allow access to Attorney level and above"""
    def has_permission(self, request, view):
        allowed_roles = ['firm_admin', 'attorney']
        return (request.user.is_authenticated and
                request.user.profile.role in allowed_roles)

class CanManageTransactions(permissions.BasePermission):
    """Transaction management based on role"""
    def has_permission(self, request, view):
        allowed_roles = ['firm_admin', 'attorney', 'paralegal', 'bookkeeper']
        return (request.user.is_authenticated and
                request.user.profile.role in allowed_roles)

    def has_object_permission(self, request, view, obj):
        # Auditors: read-only
        if request.user.profile.role == 'auditor':
            return request.method in permissions.SAFE_METHODS

        # Paralegals: cannot delete/void
        if request.user.profile.role == 'paralegal':
            return request.method != 'DELETE'

        return True

class SameFirmOnly(permissions.BasePermission):
    """Ensure user can only access their firm's data"""
    def has_object_permission(self, request, view, obj):
        # Check if object belongs to user's firm
        return obj.firm == request.user.profile.firm
```

---

## 🏢 Multi-tenant Implementation

### Database Models

**Law Firm Model:**

```python
# apps/firms/models.py
class LawFirm(models.Model):
    """Law firm (tenant) model"""

    # Basic Info
    firm_name = models.CharField(max_length=200)
    firm_number = models.CharField(max_length=50, unique=True)  # FIRM-00001
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)

    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)

    # Verification
    bar_number = models.CharField(max_length=100, blank=True)
    bar_association = models.CharField(max_length=100, blank=True)

    # Subscription
    subscription_plan = models.CharField(
        max_length=50,
        choices=[
            ('trial', 'Trial'),
            ('basic', 'Basic'),
            ('professional', 'Professional'),
            ('enterprise', 'Enterprise'),
        ],
        default='trial'
    )
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    subscription_start = models.DateTimeField(null=True, blank=True)

    # Limits
    max_users = models.IntegerField(default=5)
    max_storage_gb = models.IntegerField(default=10)

    # Settings
    is_active = models.BooleanField(default=True)
    timezone = models.CharField(max_length=50, default='America/New_York')
    logo = models.ImageField(upload_to='firm_logos/', null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['firm_name']
        indexes = [
            models.Index(fields=['firm_number']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return self.firm_name

    @property
    def is_trial(self):
        return self.subscription_plan == 'trial'

    @property
    def trial_days_remaining(self):
        if self.trial_ends_at:
            delta = self.trial_ends_at - timezone.now()
            return max(0, delta.days)
        return 0
```

**User Profile Model:**

```python
# apps/users/models.py
class UserProfile(models.Model):
    """User profile with firm association and role"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    firm = models.ForeignKey(
        'firms.LawFirm',
        on_delete=models.CASCADE,
        related_name='users'
    )
    role = models.CharField(
        max_length=50,
        choices=[
            ('firm_admin', 'Firm Administrator'),
            ('attorney', 'Attorney'),
            ('paralegal', 'Paralegal/Assistant'),
            ('bookkeeper', 'Bookkeeper'),
            ('auditor', 'Auditor (Read-Only)'),
        ],
        default='attorney'
    )

    # Additional Info
    bar_number = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)

    # Security
    is_active = models.BooleanField(default=True)
    must_change_password = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)

    # 2FA (MANDATORY)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True)
    two_factor_backup_codes = models.JSONField(default=list)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__last_name', 'user__first_name']
        indexes = [
            models.Index(fields=['firm', 'role']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()} ({self.firm.firm_name})"
```

---

## 👨‍💼 Platform Team Roles

### Customer Success Manager Dashboard

**What They Can See:**

```python
# apps/platform/api/views.py
class CustomerSuccessDashboardView(APIView):
    """Customer Success dashboard - metrics only, no data"""
    permission_classes = [IsAuthenticated, IsCustomerSuccess]

    def get(self, request, firm_id):
        firm = LawFirm.objects.get(id=firm_id)

        # Billing info
        billing_info = {
            'firm_name': firm.firm_name,
            'contact_email': firm.email,
            'contact_phone': firm.phone,
            'plan': firm.get_subscription_plan_display(),
            'status': 'Active' if firm.is_active else 'Inactive',
            'trial_ends': firm.trial_ends_at,
            'next_billing': firm.subscription_start,
            'registered': firm.created_at,
        }

        # Usage metrics (counts only, no details)
        usage_metrics = {
            'total_users': firm.users.filter(is_active=True).count(),
            'users_by_role': {
                'attorneys': firm.users.filter(role='attorney').count(),
                'paralegals': firm.users.filter(role='paralegal').count(),
                'bookkeepers': firm.users.filter(role='bookkeeper').count(),
                'auditors': firm.users.filter(role='auditor').count(),
            },
            'active_users_30d': firm.users.filter(
                user__last_login__gte=timezone.now() - timedelta(days=30)
            ).count(),
            'total_clients': Client.objects.filter(firm=firm).count(),
            'total_cases': Case.objects.filter(firm=firm).count(),
            'total_transactions': Transaction.objects.filter(
                case__firm=firm
            ).count(),
            'transactions_this_month': Transaction.objects.filter(
                case__firm=firm,
                transaction_date__gte=timezone.now().replace(day=1)
            ).count(),
            'storage_used_gb': calculate_storage_usage(firm),
        }

        # Feature adoption (boolean flags only)
        feature_adoption = {
            'bank_reconciliation': BankReconciliation.objects.filter(
                account__firm=firm
            ).exists(),
            'reports_generated': Report.objects.filter(
                firm=firm
            ).count(),
        }

        # Health score (calculated)
        health_score = calculate_health_score(firm)

        # Log this access
        AuditLog.objects.create(
            user=request.user,
            action='CS_VIEWED_DASHBOARD',
            object_repr=firm.firm_name,
            ip_address=get_client_ip(request)
        )

        return Response({
            'billing_info': billing_info,
            'usage_metrics': usage_metrics,
            'feature_adoption': feature_adoption,
            'health_score': health_score,
        })
```

**Customer Success Permissions:**

```python
# apps/platform/models.py
class CustomerSuccessAction(models.Model):
    """Track all Customer Success actions"""

    cs_user = models.ForeignKey(User, on_delete=models.CASCADE)
    firm = models.ForeignKey('firms.LawFirm', on_delete=models.CASCADE)
    action_type = models.CharField(
        max_length=50,
        choices=[
            ('viewed_dashboard', 'Viewed Dashboard'),
            ('sent_message', 'Sent Message'),
            ('extended_trial', 'Extended Trial'),
            ('scheduled_checkin', 'Scheduled Check-in'),
        ]
    )
    details = models.JSONField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()

    class Meta:
        ordering = ['-timestamp']


# Trial extension logic
class TrialExtensionView(APIView):
    """Extend trial period - ONE TIME only"""
    permission_classes = [IsAuthenticated, IsCustomerSuccess]

    def post(self, request, firm_id):
        firm = LawFirm.objects.get(id=firm_id)

        # Check if already extended
        previous_extensions = CustomerSuccessAction.objects.filter(
            firm=firm,
            action_type='extended_trial'
        ).count()

        if previous_extensions >= 1:
            return Response({
                'error': 'Trial already extended once. Cannot extend again.'
            }, status=400)

        # Extend trial by 14 or 30 days
        extension_days = request.data.get('days', 14)
        if extension_days not in [14, 30]:
            return Response({
                'error': 'Extension must be 14 or 30 days'
            }, status=400)

        # Update trial end date
        firm.trial_ends_at = firm.trial_ends_at + timedelta(days=extension_days)
        firm.save()

        # Log action
        CustomerSuccessAction.objects.create(
            cs_user=request.user,
            firm=firm,
            action_type='extended_trial',
            details={
                'days': extension_days,
                'new_end_date': firm.trial_ends_at.isoformat()
            },
            ip_address=get_client_ip(request)
        )

        # Send email to firm admin
        send_trial_extension_email(firm, extension_days)

        return Response({
            'success': True,
            'message': f'Trial extended by {extension_days} days',
            'new_end_date': firm.trial_ends_at
        })
```

---

## 🆘 Support & Password Recovery

### Support Model (Screen Sharing Only)

**No Direct Access:**

Platform team (Support Specialists) cannot access customer firm data. All support is via screen sharing.

**Support Process:**
```
1. Customer submits support ticket
2. Support Specialist reviews ticket
3. Support schedules Zoom/Teams call with customer
4. Customer shares their screen
5. Support guides customer through issue
6. Customer controls what is visible
7. Issue resolved or escalated to development
```

**Advantages:**
- ✅ Zero data exposure risk
- ✅ Customer maintains full control
- ✅ Better customer relationship (human interaction)
- ✅ Compliance with privacy regulations
- ✅ Major selling point for security

**Disadvantages:**
- ❌ Slower than direct access
- ❌ Requires customer availability
- ❌ Cannot fix issues after-hours

---

### Firm Admin Password Recovery

**Prevention: Require Multiple Admins**

```python
# Validation when deleting/deactivating Firm Admin
class UserDeleteView(APIView):
    def delete(self, request, user_id):
        user = User.objects.get(id=user_id)

        if user.profile.role == 'firm_admin':
            # Count active firm admins
            admin_count = UserProfile.objects.filter(
                firm=user.profile.firm,
                role='firm_admin',
                is_active=True
            ).count()

            if admin_count <= 2:
                return Response({
                    'error': 'Cannot delete. Firm must have at least 2 active administrators.'
                }, status=400)

        # Proceed with deletion
        user.profile.is_active = False
        user.profile.save()

        return Response({'success': True})
```

**Recovery: Identity Verification + One-Time Code**

If ALL Firm Admins are locked out (lost password + 2FA):

```python
# apps/users/models.py
class EmergencyRecoveryRequest(models.Model):
    """Emergency access recovery for locked-out Firm Admins"""

    firm = models.ForeignKey('firms.LawFirm', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Verification Info
    requested_by_email = models.EmailField()
    phone_verified = models.BooleanField(default=False)
    id_verified = models.BooleanField(default=False)
    bar_number_verified = models.BooleanField(default=False)

    # Support Ticket
    support_ticket_id = models.CharField(max_length=50)
    support_agent = models.CharField(max_length=100)

    # Recovery Code
    recovery_code = models.CharField(max_length=64, unique=True)
    code_expires_at = models.DateTimeField()
    code_used = models.BooleanField(default=False)

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField()

    class Meta:
        ordering = ['-created_at']


# Emergency recovery flow
class EmergencyRecoveryView(APIView):
    """Generate one-time recovery code after identity verification"""
    permission_classes = []  # Support team access

    def post(self, request):
        # Support agent has verified identity offline:
        # - Photo ID checked
        # - Firm bar number verified
        # - Business license reviewed
        # - Phone call to firm's registered number

        user = User.objects.get(email=request.data['email'])

        # Generate one-time recovery code
        recovery_code = get_random_string(64)
        expires_at = timezone.now() + timedelta(hours=1)

        recovery = EmergencyRecoveryRequest.objects.create(
            firm=user.profile.firm,
            user=user,
            requested_by_email=request.data['email'],
            phone_verified=True,
            id_verified=True,
            bar_number_verified=True,
            support_ticket_id=request.data['ticket_id'],
            support_agent=request.data['agent_name'],
            recovery_code=recovery_code,
            code_expires_at=expires_at,
            ip_address=get_client_ip(request)
        )

        # Send recovery code to verified email
        send_recovery_code_email(user, recovery_code)

        # Alert all firm contacts
        send_emergency_access_alert(user.profile.firm, user)

        return Response({
            'success': True,
            'message': 'Recovery code sent',
            'expires_in_minutes': 60
        })


# Use recovery code to login
class UseRecoveryCodeView(APIView):
    """Login with emergency recovery code"""
    permission_classes = []

    def post(self, request):
        code = request.data.get('recovery_code')

        try:
            recovery = EmergencyRecoveryRequest.objects.get(
                recovery_code=code,
                code_used=False
            )

            # Check expiration
            if timezone.now() > recovery.code_expires_at:
                return Response({
                    'error': 'Recovery code expired'
                }, status=400)

            # Mark as used
            recovery.code_used = True
            recovery.resolved_at = timezone.now()
            recovery.save()

            # Login user (bypass 2FA ONCE)
            login(request, recovery.user)

            # Force password reset and 2FA setup
            recovery.user.profile.must_change_password = True
            recovery.user.profile.two_factor_enabled = False  # Force re-setup
            recovery.user.profile.save()

            # Log the emergency access
            AuditLog.objects.create(
                user=recovery.user,
                firm=recovery.firm,
                action='EMERGENCY_RECOVERY_USED',
                details={
                    'support_ticket': recovery.support_ticket_id,
                    'support_agent': recovery.support_agent
                },
                ip_address=get_client_ip(request)
            )

            return Response({
                'success': True,
                'message': 'Emergency access granted. You must reset password and setup 2FA now.',
                'requires_password_reset': True,
                'requires_2fa_setup': True
            })

        except EmergencyRecoveryRequest.DoesNotExist:
            return Response({
                'error': 'Invalid recovery code'
            }, status=404)
```

**Email Alert to All Firm Contacts:**

```
Subject: SECURITY ALERT - Emergency Access Used

IMPORTANT SECURITY NOTICE

Emergency account recovery was used for:
- User: Jane Smith (jane@smithlaw.com)
- Firm: Smith & Associates Law
- Date/Time: Nov 9, 2025 at 2:30 PM EST
- IP Address: 192.168.1.100
- Support Ticket: #12345
- Support Agent: John Doe

This emergency access was granted after identity verification including:
- Photo ID verification
- State bar number confirmation
- Phone verification
- Business license review

The user has been required to:
1. Reset their password immediately
2. Set up 2FA again
3. Review all security settings

If you did not request this access, contact support IMMEDIATELY.

All actions have been logged for security audit.

IOLTA Guard Security Team
```

---

### Self-Service Data Export (GDPR Compliance)

**Firm Admin Can Export All Data:**

```python
# apps/firms/api/views.py
class DataExportView(APIView):
    """Self-service data export for GDPR compliance"""
    permission_classes = [IsAuthenticated, IsFirmAdmin]

    def post(self, request):
        firm = request.user.profile.firm
        export_format = request.data.get('format', 'csv')  # csv, json, pdf

        # Create export job
        export_job = DataExportJob.objects.create(
            firm=firm,
            requested_by=request.user,
            export_format=export_format,
            status='processing'
        )

        # Queue background task
        export_all_data.delay(export_job.id)

        return Response({
            'success': True,
            'job_id': export_job.id,
            'message': 'Export job created. You will be notified when ready.',
            'estimated_time_minutes': 15
        })

    def get(self, request, job_id):
        """Check export status"""
        export_job = DataExportJob.objects.get(
            id=job_id,
            firm=request.user.profile.firm
        )

        if export_job.status == 'completed':
            # Generate download link (expires in 48 hours)
            download_url = export_job.get_download_url()

            return Response({
                'status': 'completed',
                'download_url': download_url,
                'expires_in_hours': 48,
                'file_size_mb': export_job.file_size_mb
            })
        else:
            return Response({
                'status': export_job.status,
                'progress_percent': export_job.progress
            })


# Background task
@shared_task
def export_all_data(job_id):
    """Export all firm data"""
    job = DataExportJob.objects.get(id=job_id)
    firm = job.firm

    try:
        # Collect all data
        data = {
            'firm_info': serialize_firm(firm),
            'users': serialize_users(firm.users.all()),
            'clients': serialize_clients(Client.objects.filter(firm=firm)),
            'cases': serialize_cases(Case.objects.filter(firm=firm)),
            'transactions': serialize_transactions(
                Transaction.objects.filter(case__firm=firm)
            ),
            'bank_accounts': serialize_bank_accounts(
                BankAccount.objects.filter(firm=firm)
            ),
            'reports': serialize_reports(Report.objects.filter(firm=firm)),
        }

        # Generate file
        if job.export_format == 'csv':
            file_path = generate_csv_export(data, job)
        elif job.export_format == 'json':
            file_path = generate_json_export(data, job)
        elif job.export_format == 'pdf':
            file_path = generate_pdf_export(data, job)

        # Update job
        job.status = 'completed'
        job.file_path = file_path
        job.file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        job.completed_at = timezone.now()
        job.save()

        # Send notification
        send_export_ready_email(job)

    except Exception as e:
        job.status = 'failed'
        job.error_message = str(e)
        job.save()
```

---

## 🔒 Security Best Practices

### 1. Two-Factor Authentication (MANDATORY)

**All users must enable 2FA on first login:**

```python
# Login flow with mandatory 2FA
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        two_fa_code = request.data.get('two_fa_code')

        # Step 1: Authenticate username/password
        user = authenticate(username=username, password=password)

        if not user:
            return Response({'error': 'Invalid credentials'}, status=401)

        # Step 2: Check if 2FA is set up
        if not user.profile.two_factor_enabled:
            # First login - must set up 2FA
            return Response({
                'requires_2fa_setup': True,
                'user_id': user.id,
                'message': '2FA setup required. Redirecting to setup page.'
            })

        # Step 3: Verify 2FA code
        if not two_fa_code:
            return Response({
                'requires_2fa': True,
                'message': 'Enter your 6-digit 2FA code'
            })

        if verify_2fa_code(user, two_fa_code):
            login(request, user)
            return Response({'success': True})
        else:
            return Response({'error': 'Invalid 2FA code'}, status=401)


# 2FA Setup
from pyotp import TOTP, random_base32
import qrcode

def generate_2fa_secret(user):
    """Generate new 2FA secret"""
    secret = random_base32()
    user.profile.two_factor_secret = secret
    user.profile.save()
    return secret

def generate_qr_code(user):
    """Generate QR code for authenticator app"""
    totp = TOTP(user.profile.two_factor_secret)
    uri = totp.provisioning_uri(
        name=user.email,
        issuer_name='IOLTA Guard'
    )

    qr = qrcode.make(uri)
    # Return as base64 image
    return qr

def verify_2fa_code(user, code):
    """Verify 2FA code"""
    totp = TOTP(user.profile.two_factor_secret)
    return totp.verify(code, valid_window=1)

def generate_backup_codes(user, count=10):
    """Generate backup recovery codes"""
    import secrets
    codes = [secrets.token_hex(4).upper() for _ in range(count)]
    user.profile.two_factor_backup_codes = codes
    user.profile.save()
    return codes
```

### 2. Password Reset (From Login Screen)

**Secure password reset without disabling 2FA:**

```python
# Password Reset Token Model
class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField()

    def is_valid(self):
        return not self.used and timezone.now() < self.expires_at


# Request password reset
class RequestPasswordResetView(APIView):
    permission_classes = []  # Public endpoint

    def post(self, request):
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)

            # Generate token
            token = get_random_string(64)
            expires_at = timezone.now() + timedelta(hours=1)

            PasswordResetToken.objects.create(
                user=user,
                token=token,
                expires_at=expires_at,
                ip_address=get_client_ip(request)
            )

            # Send email
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{token}"
            send_password_reset_email(user, reset_url)

            # Always return success (prevent user enumeration)
            return Response({
                'success': True,
                'message': 'If account exists, reset link sent.'
            })

        except User.DoesNotExist:
            # Don't reveal user doesn't exist
            return Response({
                'success': True,
                'message': 'If account exists, reset link sent.'
            })


# Reset password
class ResetPasswordView(APIView):
    permission_classes = []

    def post(self, request, token):
        new_password = request.data.get('new_password')

        try:
            reset_token = PasswordResetToken.objects.get(token=token)

            if not reset_token.is_valid():
                return Response({
                    'error': 'Token expired or already used'
                }, status=400)

            # Update password
            user = reset_token.user
            user.set_password(new_password)
            user.save()

            # Mark token as used
            reset_token.used = True
            reset_token.save()

            # IMPORTANT: Do NOT disable 2FA
            # User still needs 2FA code to login

            # Clear failed login attempts
            user.profile.failed_login_attempts = 0
            user.profile.locked_until = None
            user.profile.save()

            return Response({
                'success': True,
                'message': 'Password reset. Login with new password and 2FA.'
            })

        except PasswordResetToken.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=404)
```

### 3. Account Lockout

**Prevent brute force attacks:**

```python
# After 5 failed attempts, lock for 30 minutes
class LoginView(APIView):
    def post(self, request):
        user = User.objects.get(username=username)
        profile = user.profile

        # Check if locked
        if profile.locked_until and profile.locked_until > timezone.now():
            return Response({
                'error': f'Account locked until {profile.locked_until}'
            }, status=403)

        # Authenticate
        if authenticate(username=username, password=password):
            # Reset failed attempts
            profile.failed_login_attempts = 0
            profile.locked_until = None
            profile.save()
        else:
            # Increment failed attempts
            profile.failed_login_attempts += 1

            if profile.failed_login_attempts >= 5:
                # Lock for 30 minutes
                profile.locked_until = timezone.now() + timedelta(minutes=30)

            profile.save()
```

### 4. Complete Activity Logging

**Log all actions for audit trail:**

```python
# Audit Log Model
class AuditLog(models.Model):
    """Comprehensive audit logging"""

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    firm = models.ForeignKey('firms.LawFirm', on_delete=models.CASCADE)

    action = models.CharField(max_length=50)  # LOGIN, CREATE, UPDATE, DELETE
    model_name = models.CharField(max_length=100, blank=True)
    object_id = models.IntegerField(null=True)
    object_repr = models.CharField(max_length=200)

    changes = models.JSONField(null=True)  # Before/after values

    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['firm', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action']),
        ]


# Auto-log all model changes
from django.db.models.signals import post_save, post_delete

@receiver(post_save, sender=Client)
def log_client_change(sender, instance, created, **kwargs):
    action = 'CREATE' if created else 'UPDATE'

    AuditLog.objects.create(
        user=get_current_user(),
        firm=instance.firm,
        action=action,
        model_name='Client',
        object_id=instance.id,
        object_repr=str(instance),
        ip_address=get_current_ip(),
        user_agent=get_current_user_agent()
    )
```

### 5. Session Security

**Secure session configuration:**

```python
# settings.py

# Session timeout: 30 minutes
SESSION_COOKIE_AGE = 1800
SESSION_SAVE_EVERY_REQUEST = True  # Refresh on activity

# Security flags
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF protection

# CSRF protection
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_USE_SESSIONS = True

# Password hashing (use Argon2 - most secure)
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'apps.users.validators.PasswordStrengthValidator',
    },
]
```

---

## 📊 Permission Matrix

| Feature | Customer Success | Firm Admin | Attorney | Paralegal | Bookkeeper | Auditor |
|---------|-----------------|------------|----------|-----------|------------|---------|
| **Platform Access** |
| View Billing | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| View Metrics | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Send Messages | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Extend Trial | ✅ (once) | ❌ | ❌ | ❌ | ❌ | ❌ |
| View Customer Data | ❌ | - | - | - | - | - |
| **Firm Management** |
| Manage Firm Settings | - | ✅ | ❌ | ❌ | ❌ | ❌ |
| Create Users | - | ✅ | ❌ | ❌ | ❌ | ❌ |
| Edit Users | - | ✅ | ❌ | ❌ | ❌ | ❌ |
| Delete Users | - | ✅ | ❌ | ❌ | ❌ | ❌ |
| Reset User Passwords | - | ✅ | ❌ | ❌ | ❌ | ❌ |
| Export All Data | - | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Clients** |
| Create Client | - | ✅ | ✅ | ✅ | ❌ | ❌ |
| Edit Client | - | ✅ | ✅ | ✅ | ❌ | ❌ |
| Delete Client | - | ✅ | ✅ | ❌ | ❌ | ❌ |
| View Client | - | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Cases** |
| Create Case | - | ✅ | ✅ | ✅ | ❌ | ❌ |
| Edit Case | - | ✅ | ✅ | ✅ | ❌ | ❌ |
| Delete Case | - | ✅ | ✅ | ❌ | ❌ | ❌ |
| View Case | - | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Transactions** |
| Create Transaction | - | ✅ | ✅ | ✅ | ✅ | ❌ |
| Edit Transaction | - | ✅ | ✅ | ✅ | ✅ | ❌ |
| Delete Transaction | - | ✅ | ✅ | ❌ | ✅ | ❌ |
| Void Transaction | - | ✅ | ✅ | ❌ | ✅ | ❌ |
| View Transaction | - | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Reports** |
| All Reports | - | ✅ | ✅ | ✅ | ✅ | ✅ |
| Export Reports | - | ✅ | ✅ | ❌ | ✅ | ✅ |

---

## 📝 Implementation Plan

### Phase 1: Multi-tenant Database Schema (Week 1-2)

**Tasks:**
1. Create `LawFirm` model with subscription fields
2. Create `UserProfile` model with firm association
3. Add 2FA fields to UserProfile
4. Create migration strategy for existing data
5. Add firm foreign keys to all models (Client, Case, Transaction, etc.)
6. Create database indexes for performance

**Deliverables:**
- ✅ Firms table created
- ✅ User profiles with firm association
- ✅ All models have firm foreign key
- ✅ Database optimized with indexes

### Phase 2: Firm Registration & Onboarding (Week 3)

**Tasks:**
1. Create firm registration API endpoint
2. Create firm registration frontend form
3. Implement email verification
4. Create welcome email templates
5. Build first-time firm admin setup flow
6. Add trial tracking logic

**Deliverables:**
- ✅ Firm registration working
- ✅ Email verification functional
- ✅ Trial period tracking

### Phase 3: 2FA Implementation (Week 4) - MANDATORY

**Tasks:**
1. Install pyotp and qrcode libraries
2. Create 2FA setup API endpoints
3. Build 2FA setup UI (QR code display)
4. Implement 2FA verification in login
5. Generate and display backup codes
6. Force 2FA setup on first login

**Deliverables:**
- ✅ 2FA mandatory for all users
- ✅ QR code generation working
- ✅ Backup codes provided
- ✅ Login requires 2FA

### Phase 4: Password Reset Workflow (Week 5)

**Tasks:**
1. Create PasswordResetToken model
2. Create password reset API endpoints
3. Build "Forgot Password" UI
4. Create password reset email templates
5. Implement token validation
6. Add password strength validation

**Deliverables:**
- ✅ Password reset from login screen
- ✅ Email with reset links
- ✅ Token expiration (1 hour)
- ✅ 2FA preserved after reset

### Phase 5: Role-Based Permissions (Week 6-7)

**Tasks:**
1. Create custom permission classes
2. Apply permissions to all API endpoints
3. Implement multi-tenant data filtering
4. Add middleware for firm isolation
5. Test all permission combinations
6. Update frontend to hide features based on role

**Deliverables:**
- ✅ Permissions enforced on backend
- ✅ Data isolation working
- ✅ Frontend respects roles

### Phase 6: Customer Success Portal (Week 8)

**Tasks:**
1. Create Customer Success dashboard API
2. Build CS frontend dashboard
3. Implement messaging system
4. Add trial extension logic
5. Create usage metrics calculations
6. Add health score algorithm

**Deliverables:**
- ✅ CS can view metrics (no data)
- ✅ Trial extension working
- ✅ Messaging functional

### Phase 7: Audit Logging (Week 9)

**Tasks:**
1. Create AuditLog model
2. Add signals to log all changes
3. Log authentication events
4. Create audit log viewer UI
5. Add export audit logs feature
6. Implement log retention policy

**Deliverables:**
- ✅ All actions logged
- ✅ Customers can view their logs
- ✅ CS actions logged

### Phase 8: Emergency Recovery (Week 10)

**Tasks:**
1. Create EmergencyRecoveryRequest model
2. Build identity verification workflow
3. Implement recovery code generation
4. Create recovery email templates
5. Add security alerts
6. Test emergency scenarios

**Deliverables:**
- ✅ Emergency recovery working
- ✅ Full audit trail
- ✅ Security alerts sent

### Phase 9: Data Export (Week 11)

**Tasks:**
1. Create DataExportJob model
2. Build export functionality (CSV, JSON, PDF)
3. Implement background job processing
4. Create download link generation
5. Add email notifications
6. Test large exports

**Deliverables:**
- ✅ Self-service export working
- ✅ Multiple formats supported
- ✅ GDPR compliant

### Phase 10: Testing & Launch (Week 12)

**Tasks:**
1. Complete security audit
2. Penetration testing
3. Load testing
4. User acceptance testing
5. Documentation
6. Launch

---

## 📞 OPEN QUESTIONS & DECISIONS NEEDED

### 1. "Break Glass" Emergency Access

**Question:** Should platform team have emergency "break glass" access to customer data in critical situations?

**Context:** Sometimes critical bugs or data corruption requires direct database access to fix.

**Options:**

**A) No Break Glass (Maximum Privacy)**
- Platform team NEVER has access under any circumstance
- All issues resolved via screen sharing only
- **Pros:** Maximum privacy, major selling point
- **Cons:** Slower support, can't fix critical issues after-hours

**B) Break Glass with Customer Consent (Balanced)**
- Available ONLY if customer explicitly approves
- Customer must click "Approve Emergency Access" button
- Access granted for specific time period (1-4 hours)
- Full transparency and audit trail
- **Pros:** Balance between support quality and privacy
- **Cons:** Requires customer approval (may not be available)

**C) Break Glass in Contract (Rare Use)**
- Mentioned in Terms of Service
- Used only for critical emergencies
- Customer notified immediately
- Very rare usage (like fire alarm - exists but rarely used)
- **Pros:** Can fix critical issues quickly
- **Cons:** Platform team CAN see data (temporary)

**YOUR DECISION NEEDED:**
- [ ] Option A: No break glass
- [ ] Option B: Only with customer approval
- [ ] Option C: Allowed in emergencies (in TOS)

---

### 2. Firm Registration Billing

**Question:** How should billing work for new firm registrations?

**Options:**

**A) No Credit Card for Trial (Recommended)**
- 30-day free trial
- No credit card required upfront
- At end of trial: Prompt to add payment method
- **Pros:** Lower barrier to entry, more signups
- **Cons:** Some trial users may not convert

**B) Credit Card Required for Trial**
- Credit card required to start trial
- Not charged during trial
- Auto-charges at end of trial (can cancel before)
- **Pros:** Higher conversion rate, fewer tire-kickers
- **Cons:** Higher barrier to entry, fewer signups

**YOUR DECISION NEEDED:**
- [ ] Option A: No credit card for trial
- [ ] Option B: Credit card required

**Trial Expiration:**
- What happens when trial expires?
  - [ ] Account paused (read-only access, can't add data)
  - [ ] Account locked (no access until subscription)
  - [ ] Grace period (3-7 days before pause)

---

### 3. User Limits & Pricing

**Question:** How should user limits and pricing work?

**Options:**

**A) Per-User Pricing**
- $X per user per month
- Unlimited users (pay as you grow)
- Example: $25/user/month
- **Pros:** Scales with firm size, fair pricing
- **Cons:** More expensive for large firms

**B) Tiered Plans (Flat Rate)**
- Basic: Up to 5 users - $99/month
- Professional: Up to 25 users - $299/month
- Enterprise: Unlimited users - $599/month
- **Pros:** Predictable pricing, encourages upgrades
- **Cons:** May limit small firms

**C) Hybrid Model**
- Base plan includes X users
- Additional users: $Y each
- Example: $199/month (includes 10 users) + $15/each additional
- **Pros:** Predictable base, flexible growth
- **Cons:** More complex pricing

**YOUR DECISION NEEDED:**
- [ ] Option A: Per-user pricing
- [ ] Option B: Tiered flat rate
- [ ] Option C: Hybrid model

**Other Limits:**
- Max transactions per month? (or unlimited?)
- Max storage per firm? (10GB, 50GB, unlimited?)
- Max bank accounts per firm?

---

### 4. Password Expiration Policy

**Question:** Should passwords expire periodically?

**Context:** Some compliance standards require password expiration (e.g., every 90 days).

**Options:**

**A) Password Expiration (90 days)**
- Passwords expire every 90 days
- User must change password
- Cannot reuse last 5 passwords
- **Pros:** Meets compliance requirements
- **Cons:** Annoying for users, may lead to weaker passwords

**B) No Expiration (Modern Approach)**
- Passwords never expire
- Focus on 2FA and strong passwords
- **Pros:** Better user experience, modern security practice
- **Cons:** May not meet some compliance requirements

**C) Optional (Firm Choice)**
- Each firm can choose their policy
- Firm Admin configures expiration rules
- **Pros:** Flexibility
- **Cons:** More complex to implement

**YOUR DECISION NEEDED:**
- [ ] Option A: Required expiration (90 days)
- [ ] Option B: No expiration
- [ ] Option C: Firm choice

**Password History:**
- [ ] Prevent reusing last 5 passwords
- [ ] No password history tracking

---

### 5. Session & Concurrent Login Policy

**Question:** How should sessions and concurrent logins be handled?

**Session Timeout:**
- Current: 30 minutes of inactivity
- [ ] Keep 30 minutes
- [ ] Change to: ___ minutes
- [ ] Make it configurable per firm

**Concurrent Logins:**
- [ ] Allow multiple concurrent sessions (user can login from laptop + phone)
- [ ] Only one session at a time (logging in elsewhere logs out first session)
- [ ] Limit to X devices (e.g., max 3 concurrent sessions)

**"Remember Me" Option:**
- [ ] Allow "Remember Me" checkbox (extends session to 30 days)
- [ ] No "Remember Me" (security-focused)

---

### 6. Customer Success Permissions

**Question:** Should Customer Success be able to modify billing plans?

**Current Decision:** Customer Success CANNOT modify billing/plans

**Clarification Needed:**
- Who CAN modify billing plans?
  - [ ] Only Firm Admin (self-service)
  - [ ] Sales team (separate role)
  - [ ] Platform Administrator

**Automatic Billing:**
- [ ] Auto-upgrade if user limit exceeded (e.g., add 6th user → auto-upgrade to Pro plan)
- [ ] Block adding users if plan limit reached (must upgrade first)

---

### 7. Multi-Firm User Access

**Question:** Can one user belong to multiple law firms?

**Context:** Some attorneys work for multiple firms (part-time, consultant, etc.)

**Options:**

**A) One Firm Per User (Simpler)**
- Each email can only belong to one firm
- User must use different emails for different firms
- **Pros:** Simpler data isolation, clearer audit trail
- **Cons:** Inconvenient for multi-firm users

**B) Multiple Firms Per User (Complex)**
- One email can belong to multiple firms
- User selects which firm to access on login
- **Pros:** Better user experience for consultants
- **Cons:** More complex data isolation, potential security issues

**YOUR DECISION NEEDED:**
- [ ] Option A: One firm per user (one email = one firm)
- [ ] Option B: Multiple firms per user (allow switching)

---

### 8. Firm Deactivation / Cancellation

**Question:** What happens when a firm cancels their subscription?

**Options:**

**A) Immediate Deactivation**
- Account locked immediately upon cancellation
- Data retained for 30 days (can reactivate)
- After 30 days: Data permanently deleted
- **Pros:** Clean, clear policy
- **Cons:** Harsh, may lose customers

**B) End of Billing Cycle**
- Account remains active until end of billing period
- Then same as Option A
- **Pros:** Customer gets what they paid for
- **Cons:** Must track billing cycles

**C) Read-Only Grace Period**
- Account becomes read-only on cancellation
- Can view/export data but not add new data
- 60-day grace period before deletion
- **Pros:** Customer-friendly, encourages exports
- **Cons:** More complex to implement

**YOUR DECISION NEEDED:**
- [ ] Option A: Immediate lock + 30 day deletion
- [ ] Option B: Active until billing cycle end
- [ ] Option C: Read-only grace period

**Data Deletion:**
- After grace period, should data be:
  - [ ] Permanently deleted (cannot recover)
  - [ ] Soft deleted (can recover if customer pays recovery fee)
  - [ ] Archived (retained for compliance, anonymized)

---

### 9. Support Ticket System

**Question:** Should there be an in-app support ticket system?

**Options:**

**A) Email-Only Support**
- Users email support@ioltaguard.com
- Support team tracks in external system (Zendesk, etc.)
- **Pros:** Simple
- **Cons:** Less integrated

**B) In-App Ticketing**
- "Help" button in application
- Users submit tickets in-app
- Support team responds in-app
- **Pros:** Better UX, can attach context automatically
- **Cons:** More development work

**YOUR DECISION NEEDED:**
- [ ] Option A: Email-only
- [ ] Option B: In-app ticketing

---

### 10. Legal & Compliance

**Questions for Legal Review:**

- [ ] Where will customer data be stored? (Region/country)
- [ ] SOC 2 compliance timeline?
- [ ] GDPR compliance needed? (if serving EU firms)
- [ ] Cyber insurance required?
- [ ] Data breach notification procedure?
- [ ] Subpoena response procedure?
- [ ] Attorney-client privilege protections?
- [ ] IOLTA regulation compliance by state?

---

## 📝 Next Steps

1. **Review this document** with stakeholders
2. **Make decisions** on all open questions above
3. **Prioritize features** for MVP vs later phases
4. **Create implementation tickets** in Jira
5. **Begin Phase 1** (Multi-tenant database schema)

---

**Document Version:** 2.0
**Last Updated:** November 9, 2025
**Status:** Awaiting Decisions on Open Questions
**Author:** Development Team

**For questions or clarifications, please contact the development team.**
