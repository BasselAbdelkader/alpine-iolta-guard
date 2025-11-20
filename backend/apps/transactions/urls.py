from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('create/', views.TransactionCreateView.as_view(), name='create'),
    path('<int:pk>/', views.TransactionDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.TransactionUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='delete'),
    path('ajax/get-client-cases/', views.get_client_cases, name='get_client_cases'),
    path('ajax/search/', views.ajax_search_transactions, name='ajax_search_transactions'),
    path('<int:pk>/void/', views.void_transaction, name='void'),
]