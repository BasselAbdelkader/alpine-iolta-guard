from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='index'),
    path('uncleared-transactions/', views.UnclearedTransactionsView.as_view(), name='uncleared_transactions'),
]