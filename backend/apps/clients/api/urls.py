from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ClientViewSet, CaseViewSet, QuickBooksValidateView, QuickBooksImportView

# Create router and register ViewSets
router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='client')

# URL patterns include both router URLs and custom endpoints
urlpatterns = [
    # Include router URLs (provides all CRUD operations)
    path('', include(router.urls)),
    path('cases/', include([
        path('', CaseViewSet.as_view({'get': 'list', 'post': 'create'})),
        path('<int:pk>/', CaseViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
        path('<int:pk>/balance/', CaseViewSet.as_view({'get': 'balance'})),
        path('<int:pk>/transactions/', CaseViewSet.as_view({'get': 'transactions'})),
        path('by_client/', CaseViewSet.as_view({'get': 'by_client'})),
    ])),

    # QuickBooks Import endpoints
    path('quickbooks/validate/', QuickBooksValidateView.as_view(), name='quickbooks-validate'),
    path('quickbooks/import/', QuickBooksImportView.as_view(), name='quickbooks-import'),

    # Custom endpoints are handled by the router actions:
    # /api/v1/clients/ - GET (list), POST (create)
    # /api/v1/clients/{id}/ - GET (detail), PUT (update), PATCH (partial_update), DELETE (delete)
    # /api/v1/clients/{id}/cases/ - GET (client's cases)
    # /api/v1/clients/{id}/balance_history/ - GET (balance breakdown)
    # /api/v1/clients/search/ - GET (search clients)
    # /api/v1/clients/trust_summary/ - GET (trust account summary)

    # /api/v1/clients/cases/ - GET (list), POST (create)
    # /api/v1/clients/cases/{id}/ - GET (detail), PUT (update), PATCH (partial_update), DELETE (delete)
    # /api/v1/clients/cases/{id}/balance/ - GET (case balance)
    # /api/v1/clients/cases/{id}/transactions/ - GET (case transactions)
    # /api/v1/clients/cases/by_client/ - GET (cases by client)
]