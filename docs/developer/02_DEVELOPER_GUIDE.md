# IOLTA Guard - Developer Guide

**Document Version:** 1.0
**Last Updated:** November 13, 2025
**Target Audience:** Software Developers, DevOps Engineers
**Classification:** Technical Documentation

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Environment Setup](#development-environment-setup)
3. [Project Structure](#project-structure)
4. [Development Workflow](#development-workflow)
5. [Backend Development](#backend-development)
6. [Frontend Development](#frontend-development)
7. [Database Development](#database-development)
8. [Testing Guidelines](#testing-guidelines)
9. [Debugging](#debugging)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites

**Required Software:**
- Docker 24+ ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose 2+ (included with Docker Desktop)
- Git 2.30+
- Code Editor (VS Code recommended)

**Recommended Tools:**
- PostgreSQL client (psql, pgAdmin, DBeaver)
- Postman or Insomnia (API testing)
- Chrome/Firefox Developer Tools

**Knowledge Requirements:**
- Python 3.12+ and Django 5.1+
- PostgreSQL and SQL
- HTML/CSS/JavaScript
- RESTful API design
- Docker containerization
- Git version control

### System Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4GB
- Disk: 10GB free space
- OS: Linux, macOS, or Windows with WSL2

**Recommended:**
- CPU: 4 cores
- RAM: 8GB+
- Disk: 20GB+ SSD
- OS: Linux or macOS

---

## Development Environment Setup

### 1. Clone Repository

```bash
# Clone the repository
git clone <repository-url> ve_demo
cd ve_demo

# Verify project structure
ls -la
```

### 2. Environment Configuration

Create `account.json` in project root:

```json
{
  "application": {
    "secret_key": "your-development-secret-key-here",
    "allowed_hosts": ["localhost", "127.0.0.1", "0.0.0.0", "host.docker.internal"],
    "debug": true
  },
  "database": {
    "name": "iolta_guard_db",
    "user": "iolta_user",
    "password": "your-secure-password",
    "host": "db",
    "port": "5432"
  }
}
```

**Security Note:** Never commit `account.json` to version control.

### 3. Start Development Environment

```bash
# Start all containers
docker-compose up -d

# Verify containers are running
docker ps

# Expected output:
# - iolta_backend_alpine
# - iolta_frontend_alpine
# - iolta_db_alpine

# Check logs
docker-compose logs -f
```

### 4. Initialize Database

```bash
# Run migrations
docker exec iolta_backend_alpine python manage.py migrate

# Create superuser
docker exec -it iolta_backend_alpine python manage.py createsuperuser

# Load test data (optional)
docker exec iolta_backend_alpine python manage.py loaddata fixtures/test_data.json
```

### 5. Access Application

- **Frontend:** http://localhost/
- **Django Admin:** http://localhost/admin/
- **API Root:** http://localhost/api/

**Default Credentials:**
- Username: (created in step 4)
- Password: (created in step 4)

### 6. IDE Setup (VS Code)

**Recommended Extensions:**
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-azuretools.vscode-docker",
    "batisteo.vscode-django",
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint"
  ]
}
```

**Python Settings:**
```json
{
  "python.defaultInterpreterPath": "docker exec iolta_backend_alpine python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black"
}
```

---

## Project Structure

```
ve_demo/
├── backend/                      # Django backend application
│   ├── apps/                     # Django apps (modules)
│   │   ├── api/                  # API routing
│   │   ├── bank_accounts/        # Bank account management
│   │   ├── checks/               # Check printing
│   │   ├── clients/              # Client & case management
│   │   ├── dashboard/            # Dashboard views
│   │   ├── reports/              # Report generation
│   │   ├── settings/             # System settings
│   │   ├── settlements/          # Settlements
│   │   ├── transactions/         # (legacy)
│   │   └── vendors/              # Vendor management
│   ├── trust_account_project/    # Django project settings
│   │   ├── settings.py           # Main settings
│   │   ├── urls.py               # URL routing
│   │   ├── wsgi.py               # WSGI config
│   │   └── security.py           # Security middleware
│   ├── manage.py                 # Django management script
│   ├── requirements.txt          # Python dependencies
│   └── Dockerfile                # Backend container config
│
├── frontend/                     # Frontend static files
│   ├── html/                     # HTML pages
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── clients.html
│   │   ├── client-detail.html
│   │   ├── case-detail.html
│   │   └── ...
│   ├── js/                       # JavaScript files
│   │   ├── api.js                # API client
│   │   ├── auth.js               # Authentication
│   │   ├── dashboard.js
│   │   ├── clients.js
│   │   └── ...
│   ├── css/                      # Stylesheets
│   │   └── styles.css
│   └── nginx.conf                # Nginx configuration
│
├── docs/                         # Documentation
│   ├── developer/                # Technical documentation
│   ├── userguide/                # End-user documentation
│   └── compliance/               # Audit & compliance docs
│
├── tests/                        # Test scripts
├── scripts/                      # Utility scripts
├── docker-compose.yml            # Container orchestration
├── account.json                  # Configuration (gitignored)
├── CLAUDE.md                     # Project guide for AI
├── SESSION_LOG_*.md              # Development session logs
└── README.md                     # Project README

```

### Django App Structure

Each Django app follows this structure:

```
apps/{app_name}/
├── __init__.py
├── models.py               # Data models
├── views.py                # Template views (if any)
├── urls.py                 # URL routing
├── admin.py                # Django admin configuration
├── apps.py                 # App configuration
├── api/                    # API components
│   ├── __init__.py
│   ├── serializers.py      # DRF serializers
│   ├── views.py            # API views/viewsets
│   └── permissions.py      # Custom permissions
└── migrations/             # Database migrations
    └── 0001_initial.py
```

---

## Development Workflow

### Git Workflow

```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make changes and commit
git add .
git commit -m "feat: add description"

# 3. Push to remote
git push origin feature/your-feature-name

# 4. Create pull request
# (via GitHub/GitLab interface)

# 5. After review, merge to main
# (via pull request)
```

**Commit Message Convention:**
```
feat: Add new feature
fix: Fix bug
docs: Update documentation
style: Code formatting
refactor: Code refactoring
test: Add tests
chore: Maintenance tasks
```

### Development Cycle

```
1. Pull latest code
   ↓
2. Create feature branch
   ↓
3. Develop & test locally
   ↓
4. Run tests
   ↓
5. Commit changes
   ↓
6. Push to remote
   ↓
7. Create pull request
   ↓
8. Code review
   ↓
9. Merge to main
   ↓
10. Deploy to staging
```

### Hot Reload / Auto-Restart

**Backend (Django):**
```bash
# Django auto-reloads on code changes
# No restart needed for Python files

# If changes don't appear:
docker restart iolta_backend_alpine
```

**Frontend (Nginx):**
```bash
# Static files served directly
# Refresh browser to see changes

# If changes don't appear:
docker exec iolta_frontend_alpine nginx -s reload
```

---

## Backend Development

### Creating a New Django App

```bash
# 1. Create app structure
docker exec iolta_backend_alpine python manage.py startapp newapp

# 2. Move app to apps/ directory
docker exec iolta_backend_alpine mv newapp /app/apps/

# 3. Add to INSTALLED_APPS in settings.py
# 'apps.newapp',

# 4. Create API structure
docker exec iolta_backend_alpine mkdir -p /app/apps/newapp/api
docker exec iolta_backend_alpine touch /app/apps/newapp/api/__init__.py
docker exec iolta_backend_alpine touch /app/apps/newapp/api/serializers.py
docker exec iolta_backend_alpine touch /app/apps/newapp/api/views.py
```

### Creating a Model

```python
# apps/newapp/models.py
from django.db import models

class NewModel(models.Model):
    """Description of model"""

    # Fields
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField()

    # Relationships
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.PROTECT,  # NEVER use CASCADE for financial data
        related_name='related_objects'
    )

    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'newmodel'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['client', 'date']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} - {self.date}"

    def get_formatted_amount(self):
        """Format amount for display"""
        if self.amount < 0:
            return f"({abs(self.amount):,.2f})"
        return f"{self.amount:,.2f}"
```

### Creating Database Migration

```bash
# 1. Generate migration
docker exec iolta_backend_alpine python manage.py makemigrations

# 2. Review migration file
# apps/newapp/migrations/0001_initial.py

# 3. Apply migration
docker exec iolta_backend_alpine python manage.py migrate

# 4. Verify migration
docker exec iolta_backend_alpine python manage.py showmigrations
```

### Creating an API Endpoint

**Step 1: Create Serializer**

```python
# apps/newapp/api/serializers.py
from rest_framework import serializers
from ..models import NewModel

class NewModelSerializer(serializers.ModelSerializer):
    # Computed fields
    formatted_amount = serializers.CharField(
        source='get_formatted_amount',
        read_only=True
    )

    # Nested serializers
    client_name = serializers.CharField(
        source='client.full_name',
        read_only=True
    )

    class Meta:
        model = NewModel
        fields = '__all__'
        # OR specify fields explicitly:
        # fields = ['id', 'name', 'amount', 'client', 'client_name']

    def validate(self, data):
        """Custom validation"""
        if data.get('amount', 0) < 0:
            raise serializers.ValidationError({
                'amount': 'Amount cannot be negative'
            })
        return data

    def validate_name(self, value):
        """Field-specific validation"""
        if len(value) < 3:
            raise serializers.ValidationError(
                'Name must be at least 3 characters'
            )
        return value
```

**Step 2: Create ViewSet**

```python
# apps/newapp/api/views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from ..models import NewModel
from .serializers import NewModelSerializer

class NewModelViewSet(viewsets.ModelViewSet):
    """
    API endpoint for NewModel management

    list:       GET    /api/newmodels/
    create:     POST   /api/newmodels/
    retrieve:   GET    /api/newmodels/{id}/
    update:     PUT    /api/newmodels/{id}/
    partial:    PATCH  /api/newmodels/{id}/
    destroy:    DELETE /api/newmodels/{id}/
    """
    queryset = NewModel.objects.all()
    serializer_class = NewModelSerializer
    permission_classes = [IsAuthenticated]

    # Filtering
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = ['is_active', 'client']
    search_fields = ['name', 'description']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Customize queryset"""
        queryset = super().get_queryset()

        # Optimize queries
        queryset = queryset.select_related('client')

        # Filter by query params
        client_id = self.request.query_params.get('client_id')
        if client_id:
            queryset = queryset.filter(client_id=client_id)

        return queryset

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Custom endpoint: /api/newmodels/summary/"""
        from django.db.models import Sum, Count

        stats = self.get_queryset().aggregate(
            total=Sum('amount'),
            count=Count('id')
        )

        return Response(stats)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Custom endpoint: /api/newmodels/{id}/archive/"""
        obj = self.get_object()
        obj.is_active = False
        obj.save()

        return Response({
            'status': 'archived',
            'id': obj.id
        })
```

**Step 3: Register URLs**

```python
# apps/newapp/api/urls.py
from rest_framework.routers import DefaultRouter
from .views import NewModelViewSet

router = DefaultRouter()
router.register(r'newmodels', NewModelViewSet, basename='newmodel')

urlpatterns = router.urls
```

```python
# apps/api/urls.py
from django.urls import path, include

urlpatterns = [
    # ... existing patterns
    path('', include('apps.newapp.api.urls')),
]
```

### Common Backend Tasks

#### Query Database

```python
# Get all objects
all_clients = Client.objects.all()

# Filter
active_clients = Client.objects.filter(is_active=True)

# Get one object
client = Client.objects.get(id=1)

# Get or None
client = Client.objects.filter(id=1).first()

# Aggregation
from django.db.models import Sum, Count
total_balance = BankTransaction.objects.filter(
    transaction_type='DEPOSIT'
).aggregate(total=Sum('amount'))['total']

# Complex queries
clients_with_balance = Client.objects.annotate(
    balance=Sum('cases__transactions__amount')
).filter(balance__gt=0)

# Optimize queries
clients = Client.objects.select_related('case').prefetch_related('transactions')
```

#### Handle Transactions

```python
from django.db import transaction

@transaction.atomic
def transfer_funds(from_case, to_case, amount):
    """Transfer funds between cases"""

    # Create withdrawal
    BankTransaction.objects.create(
        case=from_case,
        client=from_case.client,
        transaction_type='WITHDRAWAL',
        amount=amount,
        description=f'Transfer to {to_case.case_number}'
    )

    # Create deposit
    BankTransaction.objects.create(
        case=to_case,
        client=to_case.client,
        transaction_type='DEPOSIT',
        amount=amount,
        description=f'Transfer from {from_case.case_number}'
    )

    # If any error occurs, both transactions will be rolled back
```

#### Custom Management Command

```python
# apps/newapp/management/commands/custom_command.py
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Description of command'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        self.stdout.write('Starting...')

        # Command logic here

        self.stdout.write(self.style.SUCCESS('Done!'))
```

```bash
# Run command
docker exec iolta_backend_alpine python manage.py custom_command --dry-run
```

---

## Frontend Development

### HTML Page Structure

```html
<!-- html/new-page.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Title - IOLTA Guard</title>

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- Custom CSS -->
    <link rel="stylesheet" href="/css/styles.css">
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <!-- Navigation content -->
    </nav>

    <!-- Main Content -->
    <div class="container mt-4">
        <h1>Page Title</h1>

        <div class="card">
            <div class="card-body">
                <!-- Content here -->
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

    <!-- Custom JS -->
    <script src="/js/api.js"></script>
    <script src="/js/new-page.js"></script>
</body>
</html>
```

### JavaScript Module Pattern

```javascript
// js/new-page.js
(function() {
    'use strict';

    // Module-level variables
    let currentData = [];

    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        initializePage();
        attachEventListeners();
        loadData();
    });

    function initializePage() {
        console.log('Page initialized');
        // Setup code here
    }

    function attachEventListeners() {
        // Button clicks
        document.getElementById('btnSave')
            .addEventListener('click', handleSave);

        // Form submission
        document.getElementById('myForm')
            .addEventListener('submit', handleFormSubmit);
    }

    async function loadData() {
        try {
            showLoading();

            const response = await api.get('/api/endpoint/');
            currentData = response;

            renderData(currentData);

        } catch (error) {
            showError('Failed to load data: ' + error.message);
        } finally {
            hideLoading();
        }
    }

    function renderData(data) {
        const container = document.getElementById('dataContainer');
        container.innerHTML = '';

        data.forEach(item => {
            const html = createItemHTML(item);
            container.insertAdjacentHTML('beforeend', html);
        });
    }

    function createItemHTML(item) {
        return `
            <div class="card mb-3">
                <div class="card-body">
                    <h5 class="card-title">${item.name}</h5>
                    <p class="card-text">${item.description}</p>
                    <button class="btn btn-primary" onclick="editItem(${item.id})">
                        Edit
                    </button>
                </div>
            </div>
        `;
    }

    async function handleSave(event) {
        event.preventDefault();

        const data = {
            name: document.getElementById('name').value,
            amount: parseFloat(document.getElementById('amount').value)
        };

        try {
            const response = await api.post('/api/endpoint/', data);
            showSuccess('Saved successfully');
            loadData(); // Refresh data
        } catch (error) {
            showError('Failed to save: ' + error.message);
        }
    }

    function showLoading() {
        document.getElementById('loading').classList.remove('d-none');
    }

    function hideLoading() {
        document.getElementById('loading').classList.add('d-none');
    }

    function showError(message) {
        const alert = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        document.getElementById('alerts').insertAdjacentHTML('beforeend', alert);
    }

    function showSuccess(message) {
        const alert = `
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        document.getElementById('alerts').insertAdjacentHTML('beforeend', alert);
    }

    // Public API (if needed)
    window.newPageModule = {
        reload: loadData
    };

})();
```

### API Communication

```javascript
// js/api.js - Common API client
const api = {
    baseURL: '/api',

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;

        const defaultOptions = {
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            }
        };

        const config = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, config);

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Request failed');
            }

            return await response.json();

        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },

    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    },

    getCSRFToken() {
        const name = 'csrftoken';
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                return decodeURIComponent(cookie.substring(name.length + 1));
            }
        }
        return '';
    }
};
```

### Common UI Patterns

**Loading Spinner:**
```html
<div id="loading" class="d-none">
    <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
    </div>
</div>
```

**Modal Form:**
```html
<div class="modal fade" id="editModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Edit Item</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="editForm">
                    <div class="mb-3">
                        <label for="name" class="form-label">Name</label>
                        <input type="text" class="form-control" id="name" required>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" onclick="saveForm()">Save</button>
            </div>
        </div>
    </div>
</div>
```

**Data Table:**
```html
<table class="table table-striped table-hover">
    <thead>
        <tr>
            <th>Name</th>
            <th>Amount</th>
            <th>Date</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody id="tableBody">
        <!-- Populated by JavaScript -->
    </tbody>
</table>
```

---

## Database Development

### Accessing Database

```bash
# PostgreSQL client
docker exec -it iolta_db_alpine psql -U iolta_user -d iolta_guard_db

# Django shell
docker exec -it iolta_backend_alpine python manage.py shell

# Database shell (Django)
docker exec -it iolta_backend_alpine python manage.py dbshell
```

### Common SQL Queries

```sql
-- List all tables
\dt

-- Describe table
\d clients;

-- Get current balance for client
SELECT
    c.first_name,
    c.last_name,
    COALESCE(SUM(CASE WHEN bt.transaction_type = 'DEPOSIT' THEN bt.amount ELSE 0 END), 0) -
    COALESCE(SUM(CASE WHEN bt.transaction_type IN ('WITHDRAWAL', 'TRANSFER_OUT') THEN bt.amount ELSE 0 END), 0) as balance
FROM clients c
LEFT JOIN bank_transactions bt ON bt.client_id = c.id
WHERE bt.status != 'voided' OR bt.status IS NULL
GROUP BY c.id, c.first_name, c.last_name;

-- Find transactions for case
SELECT
    bt.id,
    bt.transaction_date,
    bt.transaction_type,
    bt.amount,
    bt.description
FROM bank_transactions bt
WHERE bt.case_id = 1
ORDER BY bt.transaction_date, bt.id;

-- Audit trail
SELECT
    c.first_name || ' ' || c.last_name as client,
    ca.case_number,
    bt.transaction_date,
    bt.transaction_type,
    bt.amount,
    bt.created_at,
    bt.updated_at
FROM bank_transactions bt
JOIN clients c ON c.id = bt.client_id
JOIN cases ca ON ca.id = bt.case_id
ORDER BY bt.created_at DESC
LIMIT 100;
```

### Backup and Restore

```bash
# Backup database
docker exec iolta_db_alpine pg_dump -U iolta_user iolta_guard_db > backup_$(date +%Y%m%d).sql

# Restore database
cat backup_20251113.sql | docker exec -i iolta_db_alpine psql -U iolta_user -d iolta_guard_db

# Django fixtures
docker exec iolta_backend_alpine python manage.py dumpdata > fixtures/backup.json
docker exec iolta_backend_alpine python manage.py loaddata fixtures/backup.json
```

---

## Testing Guidelines

### Manual Testing

**Test Checklist:**
- [ ] Create client
- [ ] Create case for client
- [ ] Add deposit transaction
- [ ] Add withdrawal transaction
- [ ] Verify balance calculation
- [ ] Close case
- [ ] Attempt transaction on closed case (should fail)
- [ ] Generate report
- [ ] Print check

### API Testing with cURL

```bash
# Get CSRF token
CSRF=$(docker exec iolta_backend_alpine python manage.py shell -c "from django.middleware.csrf import get_token; from django.test import RequestFactory; print(get_token(RequestFactory().get('/')))")

# Login
curl -X POST http://localhost/api/auth/login/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF" \
  -d '{"username":"admin","password":"password"}' \
  -c cookies.txt

# Get clients
curl -X GET http://localhost/api/clients/ \
  -b cookies.txt

# Create client
curl -X POST http://localhost/api/clients/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF" \
  -b cookies.txt \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "(555) 123-4567"
  }'
```

---

## Debugging

### Django Debug Toolbar

```python
# settings.py
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1', 'host.docker.internal']
```

### Logging

```python
# View logs
docker-compose logs -f backend

# Django logging
import logging
logger = logging.getLogger(__name__)

def my_view(request):
    logger.info('View accessed')
    logger.debug('Debug information')
    logger.error('Error occurred')
```

### Common Issues

**Issue: Changes not appearing**
```bash
# Restart backend
docker restart iolta_backend_alpine

# Clear browser cache
# Ctrl+Shift+R (hard refresh)
```

**Issue: Database connection error**
```bash
# Check database is running
docker ps | grep db

# Check database logs
docker logs iolta_db_alpine

# Restart database
docker restart iolta_db_alpine
```

---

## Best Practices

### Code Style

**Python:**
- Follow PEP 8
- Use meaningful variable names
- Add docstrings to functions/classes
- Keep functions small (<50 lines)
- Use type hints

**JavaScript:**
- Use const/let (not var)
- Use arrow functions
- Use template literals
- Add comments for complex logic
- Use async/await

### Security

- Never commit secrets
- Validate all inputs
- Use parameterized queries
- Enable CSRF protection
- Use HTTPS in production
- Keep dependencies updated

### Performance

- Use select_related/prefetch_related
- Add database indexes
- Paginate large datasets
- Cache calculated values
- Optimize images
- Minify CSS/JS in production

---

## Troubleshooting

See [03_TROUBLESHOOTING_GUIDE.md](./03_TROUBLESHOOTING_GUIDE.md) for comprehensive troubleshooting guide.

---

**Document Control:**
- **Version:** 1.0
- **Last Updated:** November 13, 2025
- **Next Review:** Quarterly

---

*This document is confidential. Unauthorized distribution prohibited.*
