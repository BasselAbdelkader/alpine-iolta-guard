from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('print/', views.print_clients_report, name='print_clients'),
    path('print-with-cases/', views.print_clients_with_cases, name='print_clients_with_cases'),
    path('print-case-ledger/', views.print_case_ledger_by_query, name='print_case_ledger_query'),
    path('cases/<int:case_id>/print/', views.print_case_ledger, name='print_case_ledger'),
    path('create/', views.ClientCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ClientDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ClientUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.ClientDeleteView.as_view(), name='delete'),
    path('<int:client_id>/smart-delete/', views.smart_delete_client, name='smart_delete'),
    
    # Case URLs
    path('cases/', views.CaseIndexView.as_view(), name='case_index'),
    path('cases/create/', views.CaseCreateView.as_view(), name='case_create'),
    path('<int:client_id>/cases/create/', views.CaseCreateView.as_view(), name='client_case_create'),
    path('cases/<int:pk>/', views.CaseDetailView.as_view(), name='case_detail'),
    path('cases/<int:pk>/edit/', views.CaseUpdateView.as_view(), name='case_edit'),
    path('cases/<int:pk>/delete/', views.CaseDeleteView.as_view(), name='case_delete'),
    path('cases/<int:case_id>/deactivate/', views.case_deactivate, name='case_deactivate'),
    path('cases/<int:case_id>/delete/', views.case_delete_permanent, name='case_delete_permanent'),
    
    # AJAX Search URLs
    path('ajax/search/', views.ajax_search_clients, name='ajax_search_clients'),
    path('ajax/cases-for-client/', views.ajax_cases_for_client, name='ajax_cases_for_client'),
    path('ajax/client-balance/', views.ajax_client_balance, name='ajax_client_balance'),
    path('cases/ajax/search/', views.ajax_search_cases, name='ajax_search_cases'),
    path('cases/<int:case_id>/transactions/', views.case_transactions, name='case_transactions'),
    path('cases/<int:case_id>/balance/', views.case_balance_api, name='case_balance_api'),
]
