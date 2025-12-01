"""
Import Approval API URLs
"""

from django.urls import path
from .views import approve_import, reject_import, get_pending_imports

urlpatterns = [
    path('pending/', get_pending_imports, name='get_pending_imports'),
    path('<int:import_batch_id>/approve/', approve_import, name='approve_import'),
    path('<int:import_batch_id>/reject/', reject_import, name='reject_import'),
]
