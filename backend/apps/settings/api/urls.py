from django.urls import path
from . import views

app_name = 'settings_api'

urlpatterns = [
    # CSV Import endpoints
    path('csv/preview/', views.csv_preview, name='csv-preview'),
    path('csv/import/', views.csv_import_confirm, name='csv-import-confirm'),

    # Import Audit endpoints
    path('import-audits/', views.import_audit_list, name='import-audit-list'),
    path('import-audits/<int:pk>/delete/', views.import_audit_delete, name='import-audit-delete'),

    # User Management endpoints
    path('users/', views.list_users, name='list-users'),
    path('users/create/', views.create_user, name='create-user'),
    path('users/me/', views.get_current_user, name='get-current-user'),
    path('users/<int:user_id>/', views.get_user, name='get-user'),
    path('users/<int:user_id>/update/', views.update_user, name='update-user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete-user'),
]
