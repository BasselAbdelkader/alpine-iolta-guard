from django.urls import path
from . import views

app_name = 'vendors'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('create/', views.VendorCreateView.as_view(), name='create'),
    path('<int:pk>/', views.VendorDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.VendorUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.VendorDeleteView.as_view(), name='delete'),
    path('<int:pk>/export/', views.VendorPaymentExportView.as_view(), name='export_payments'),
    path('create-quick/', views.create_quick_vendor, name='create_quick'),
    path('create-modal/', views.create_vendor_modal, name='create_modal'),
    path('search/', views.search_vendors, name='search'),
    path('api/list/', views.vendor_list_api, name='api_list'),
]
