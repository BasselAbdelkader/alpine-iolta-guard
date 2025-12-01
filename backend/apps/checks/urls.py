from django.urls import path
from . import views

app_name = 'checks'

urlpatterns = [
    path('print-queue/', views.CheckPrintQueueView.as_view(), name='print_queue'),
    path('preview/<str:transaction_number>/', views.CheckPreviewView.as_view(), name='preview'),
    path('print/<str:transaction_number>/', views.PrintCheckView.as_view(), name='print_single'),
    path('print-batch/', views.BatchPrintView.as_view(), name='print_batch'),
    path('mark-printed/', views.MarkAsPrintedView.as_view(), name='mark_printed'),
    path('unmark-printed/', views.UnmarkAsPrintedView.as_view(), name='unmark_printed'),
]
