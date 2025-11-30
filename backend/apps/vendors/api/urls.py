from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import VendorViewSet, VendorTypeViewSet

# Create router and register ViewSets
router = DefaultRouter()
router.register(r'', VendorViewSet, basename='vendor')
router.register(r'types', VendorTypeViewSet, basename='vendortype')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),

    # Available endpoints:
    # /api/v1/vendors/ - GET (list), POST (create)
    # /api/v1/vendors/{id}/ - GET (detail), PUT (update), PATCH (partial_update), DELETE (delete)
    # /api/v1/vendors/search/ - GET (search vendors)
    # /api/v1/vendors/{id}/payments/ - GET (vendor payment history)

    # /api/v1/vendors/types/ - GET (list), POST (create)
    # /api/v1/vendors/types/{id}/ - GET (detail), PUT (update), PATCH (partial_update), DELETE (delete)
]
