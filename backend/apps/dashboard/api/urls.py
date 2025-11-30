from django.urls import path
from .views import DashboardAPIView, LawFirmAPIView, UnclearedTransactionsAPIView

urlpatterns = [
    path('', DashboardAPIView.as_view(), name='dashboard-api'),
    path('law-firm/', LawFirmAPIView.as_view(), name='law-firm-api'),
    path('uncleared-transactions/', UnclearedTransactionsAPIView.as_view(), name='uncleared-transactions-api'),
]
