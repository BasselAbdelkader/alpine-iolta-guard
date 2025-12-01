from django.urls import path
from . import views

app_name = 'bank_accounts'

urlpatterns = [
    # Bank Account URLs
    path('', views.IndexView.as_view(), name='index'),
    path('create/', views.BankAccountCreateView.as_view(), name='create'),
    # path('<int:pk>/', views.BankAccountDetailView.as_view(), name='detail'),  # Hidden for future use
    path('<int:pk>/edit/', views.BankAccountUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.BankAccountDeleteView.as_view(), name='delete'),
    
    # Bank Transaction URLs
    path('transactions/', views.BankTransactionIndexView.as_view(), name='bank_transactions'),
    path('transactions/create/', views.BankTransactionCreateView.as_view(), name='bank_transaction_create'),
    path('transactions/<int:pk>/', views.BankTransactionDetailView.as_view(), name='bank_transaction_detail'),
    path('transactions/<int:pk>/edit/', views.BankTransactionUpdateView.as_view(), name='bank_transaction_edit'),
    path('transactions/<int:pk>/delete/', views.BankTransactionDeleteView.as_view(), name='bank_transaction_delete'),
    path('transactions/<int:pk>/void/', views.void_bank_transaction, name='bank_transaction_void'),

    # API URLs
    path('api/balance/<int:account_id>/', views.get_bank_account_balance, name='api_bank_balance'),

    # Transaction Audit URLs
    path('transactions/<int:transaction_id>/audit-history/', views.transaction_audit_history, name='transaction_audit_history'),
    path('transactions/<int:transaction_id>/audit-report/xml/', views.transaction_audit_report_xml, name='transaction_audit_report_xml'),
]
