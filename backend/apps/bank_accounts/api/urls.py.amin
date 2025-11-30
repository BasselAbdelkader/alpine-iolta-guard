from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    BankAccountViewSet,
    BankTransactionViewSet,
    BankReconciliationViewSet,
    TransactionApprovalViewSet
)

# Create router and register ViewSets
router = DefaultRouter()
router.register(r'accounts', BankAccountViewSet, basename='bankaccount')
router.register(r'bank-transactions', BankTransactionViewSet, basename='banktransaction')
router.register(r'reconciliations', BankReconciliationViewSet, basename='bankreconciliation')
router.register(r'approvals', TransactionApprovalViewSet, basename='transactionapproval')

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

    # COMPLIANCE CONTROL #3: Two-Person Approval Workflow Endpoints
    # /api/v1/bank-accounts/approvals/ - GET (list all approvals)
    # /api/v1/bank-accounts/approvals/{id}/ - GET (approval details)
    # /api/v1/bank-accounts/approvals/pending/ - GET (pending approvals)
    # /api/v1/bank-accounts/approvals/pending-count/ - GET (count for badge)
    # /api/v1/bank-accounts/approvals/my-requests/ - GET (user's requests)
    # /api/v1/bank-accounts/approvals/history/ - GET (approved/rejected)
    # /api/v1/bank-accounts/approvals/{id}/approve/ - POST (approve transaction)
    # /api/v1/bank-accounts/approvals/{id}/reject/ - POST (reject transaction)
]
