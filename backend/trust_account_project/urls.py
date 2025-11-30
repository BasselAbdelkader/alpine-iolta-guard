"""trust_account_project URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('dashboard:index'), name='home'),
    path('auth/', include('django.contrib.auth.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('clients/', include('apps.clients.urls')),
    path('vendors/', include('apps.vendors.urls')),
    path('transactions/', include('apps.transactions.urls')),
    path('bank/', lambda request: redirect('/bank-accounts/')),
    path('bank-accounts/', include('apps.bank_accounts.urls')),
    path('settlements/', include('apps.settlements.urls')),
    path('reports/', include('apps.reports.urls')),
    path('settings/', include('apps.settings.urls')),
    path('checks/', include('apps.checks.urls')),
    # API Routes
    path('api/', include('apps.api.urls')),
]

# Media files are served via WhiteNoise, but add media files for development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)