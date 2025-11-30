from django.urls import path, include
from .auth_views import LoginAPIView, LogoutAPIView, CheckAuthAPIView
from .health import health_check, readiness, liveness

urlpatterns = [
    # Health check endpoints (public - no auth required)
    path('health/', health_check, name='api_health_check'),
    path('health/ready/', readiness, name='api_readiness'),
    path('health/live/', liveness, name='api_liveness'),

    # Session-based authentication endpoints
    path('auth/login/', LoginAPIView.as_view(), name='api_login'),
    path('auth/logout/', LogoutAPIView.as_view(), name='api_logout'),
    path('auth/check/', CheckAuthAPIView.as_view(), name='api_check_auth'),

    # API v1 endpoints
    path('v1/dashboard/', include('apps.dashboard.api.urls')),
    path('v1/', include('apps.clients.api.urls')),  # Clients router includes both clients/ and cases/
    # path('v1/transactions/', include('apps.transactions.api.urls')),
    path('v1/bank-accounts/', include('apps.bank_accounts.api.urls')),
    path('v1/vendors/', include('apps.vendors.api.urls')),
    path('v1/settlements/', include('apps.settlements.api.urls')),
    path('v1/checks/', include('apps.checks.api.urls')),
    path('v1/settings/', include('apps.settings.api.urls')),
    path('v1/imports/', include('apps.imports.api.urls')),  # Two-stage import approval
]