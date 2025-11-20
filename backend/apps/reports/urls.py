from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_index, name='index'),
    path('client-ledger/', views.client_ledger_report, name='client_ledger'),
]