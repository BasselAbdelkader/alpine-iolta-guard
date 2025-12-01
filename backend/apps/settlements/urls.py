from django.urls import path
from . import views

app_name = 'settlements'

urlpatterns = [
    # Settlement URLs
    path('', views.SettlementIndexView.as_view(), name='index'),
    path('create/', views.SettlementCreateView.as_view(), name='create'),
    path('<int:pk>/', views.SettlementDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.SettlementUpdateView.as_view(), name='edit'),
    path('<int:pk>/reconciliation/', views.SettlementReconciliationView.as_view(), name='reconciliation'),
    
    # Distribution URLs
    path('<int:settlement_pk>/distributions/create/', views.SettlementDistributionCreateView.as_view(), name='distribution_create'),
    path('distributions/<int:pk>/edit/', views.SettlementDistributionUpdateView.as_view(), name='distribution_edit'),
    
    # AJAX URLs
    path('<int:pk>/balance-check/', views.settlement_balance_check, name='balance_check'),
    path('distributions/<int:pk>/mark-paid/', views.mark_distribution_paid, name='mark_paid'),
]