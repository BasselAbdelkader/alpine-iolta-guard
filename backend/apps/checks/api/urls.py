from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CheckViewSet

router = DefaultRouter()
router.register(r'', CheckViewSet, basename='check')

urlpatterns = [
    path('', include(router.urls)),
]
