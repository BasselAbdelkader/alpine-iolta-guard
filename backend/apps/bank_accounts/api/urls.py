from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import BankAccountViewSet, BankTransactionViewSet, BankReconciliationViewSet

# Create router and register ViewSets
router = DefaultRouter()
router.register(r'accounts', BankAccountViewSet, basename='bankaccount')
router.register(r'bank-transactions', BankTransactionViewSet, basename='banktransaction')
router.register(r'reconciliations', BankReconciliationViewSet, basename='bankreconciliation')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
    
    # Available endpoints:
    # /api/v1/bank-accounts/accounts/ - GET (list), POST (create)
    # /api/v1/bank-accounts/accounts/{id}/ - GET (detail), PUT (update), PATCH (partial_update), DELETE (delete)
    # /api/v1/bank-accounts/accounts/{id}/transactions/ - GET (account transactions)
    # /api/v1/bank-accounts/accounts/{id}/balance_history/ - GET (balance history)
    # /api/v1/bank-accounts/accounts/summary/ - GET (all accounts summary)
    
    # /api/v1/bank-accounts/bank-transactions/ - GET (list), POST (create)
    # /api/v1/bank-accounts/bank-transactions/unmatched/ - GET (unmatched for reconciliation)
    
    # /api/v1/bank-accounts/reconciliations/ - GET (list), POST (create)
]
