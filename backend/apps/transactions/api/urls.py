from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import TransactionViewSet, BankTransactionItemViewSet

# Create router and register ViewSets
router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'transaction-items', BankTransactionItemViewSet, basename='banktransactionitem')

# URL patterns include both router URLs and custom endpoints
urlpatterns = [
    # Include router URLs (provides all CRUD operations)
    path('', include(router.urls)),
    
    # Custom endpoints handled by router actions:
    # /api/v1/transactions/ - GET (list with summary), POST (create)
    # /api/v1/transactions/{id}/ - GET (detail), PUT (update), PATCH (partial_update), DELETE (delete)
    # /api/v1/transactions/search/ - GET (search transactions)
    # /api/v1/transactions/unbalanced/ - GET (unbalanced transactions)
    # /api/v1/transactions/monthly_summary/ - GET (monthly summary)
    # /api/v1/transactions/{id}/void/ - POST (void transaction)
    # /api/v1/transactions/{id}/clear/ - POST (clear transaction)
    
    # /api/v1/transaction-items/ - GET (list), POST (create)
    # /api/v1/transaction-items/{id}/ - GET (detail), PUT (update), PATCH (partial_update), DELETE (delete)
    # /api/v1/transaction-items/by_client/ - GET (items by client)
    # /api/v1/transaction-items/by_case/ - GET (items by case)
]
