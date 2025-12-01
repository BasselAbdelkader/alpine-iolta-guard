from rest_framework.permissions import AllowAny
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count
from datetime import datetime, date

from ..bank_accounts.models import BankTransaction
from .serializers import (
    BankTransactionSerializer, BankTransactionListSerializer,
    BankTransactionItemSerializer, BankTransactionItemListSerializer
)
from apps.api.permissions import IsTrustAccountUser
from apps.api.pagination import StandardResultsSetPagination


class TransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Transaction CRUD operations with advanced filtering
    """
    queryset = BankTransaction.objects.all()
    serializer_class = BankTransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Search fields for ?search= parameter
    search_fields = ['transaction_number', 'description', 'reference_number']
    
    # Filter fields for ?field=value parameters
    filterset_fields = ['transaction_type', 'status', 'bank_account']
    
    # Ordering fields for ?ordering= parameter
    ordering_fields = ['transaction_date', 'amount', 'transaction_number', 'created_at']
    ordering = ['-transaction_date', '-created_at']  # Default ordering
    
    def get_queryset(self):
        """Customize queryset with optimizations and filters"""
        queryset = BankTransaction.objects.select_related('bank_account', 'client', 'case', 'vendor')
        
        # Date range filters
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(transaction_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(transaction_date__lte=end_date)
        
        # Amount range filters
        min_amount = self.request.query_params.get('min_amount', None)
        max_amount = self.request.query_params.get('max_amount', None)
        
        if min_amount:
            queryset = queryset.filter(amount__gte=min_amount)
        if max_amount:
            queryset = queryset.filter(amount__lte=max_amount)
        
        # Client filter
        client_id = self.request.query_params.get('client', None)
        if client_id:
            queryset = queryset.filter(client_id=client_id)

        # Case filter
        case_id = self.request.query_params.get('case', None)
        if case_id:
            queryset = queryset.filter(case_id=case_id)
        
        return queryset.order_by('-transaction_date', '-created_at')
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return BankTransactionListSerializer
        return BankTransactionSerializer
    
    def list(self, request, *args, **kwargs):
        """Enhanced list view with transaction summary metadata"""
        response = super().list(request, *args, **kwargs)
        
        # Add metadata to response
        if hasattr(response, 'data') and 'results' in response.data:
            # Calculate summary statistics for current filtered queryset
            current_queryset = self.filter_queryset(self.get_queryset())
            
            summary = current_queryset.aggregate(
                total_amount=Sum('amount'),
                total_transactions=Count('id'),
                deposits_amount=Sum('amount', filter=Q(transaction_type='DEPOSIT')),
                withdrawals_amount=Sum('amount', filter=Q(transaction_type='WITHDRAWAL')),
                transfers_amount=Sum('amount', filter=Q(transaction_type='TRANSFER')),
                cleared_amount=Sum('amount', filter=Q(status='cleared')),
                uncleared_amount=Sum('amount', filter=Q(status='pending'))
            )
            
            response.data['summary'] = {
                'total_transactions': summary['total_transactions'] or 0,
                'total_amount': str(summary['total_amount'] or 0),
                'deposits_amount': str(summary['deposits_amount'] or 0),
                'withdrawals_amount': str(summary['withdrawals_amount'] or 0),
                'transfers_amount': str(summary['transfers_amount'] or 0),
                'cleared_amount': str(summary['cleared_amount'] or 0),
                'uncleared_amount': str(summary['uncleared_amount'] or 0)
            }
        
        return response
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Enhanced search endpoint for transactions"""
        query = request.query_params.get('q', '')
        limit = int(request.query_params.get('limit', 50))
        
        if len(query) < 2:
            return Response({
                'transactions': [],
                'count': 0,
                'query': query,
                'message': 'Search query must be at least 2 characters'
            })
        
        # Search across multiple fields
        transactions = BankTransaction.objects.select_related('bank_account', 'client', 'case').filter(
            Q(transaction_number__icontains=query) |
            Q(description__icontains=query) |
            Q(reference_number__icontains=query) |
            Q(client__first_name__icontains=query) |
            Q(client__last_name__icontains=query) |
            Q(case__case_title__icontains=query) |
            Q(case__case_number__icontains=query)
        ).distinct().order_by('-transaction_date')[:limit]

        serializer = BankTransactionListSerializer(transactions, many=True)
        return Response({
            'transactions': serializer.data,
            'count': transactions.count(),
            'query': query,
            'limit': limit
        })
    
    @action(detail=False, methods=['get'])
    def unbalanced(self, request):
        """Get transactions that are marked as unbalanced or have validation issues"""
        transactions = []
        unbalanced_transactions = BankTransaction.objects.filter(
            # Add any specific unbalanced criteria here if needed
            # For now, we'll return transactions without proper client/case linkage
        ).filter(
            Q(client__isnull=True) | Q(case__isnull=True)
        )

        for transaction in unbalanced_transactions:
            transactions.append({
                'id': transaction.id,
                'transaction_number': transaction.transaction_number,
                'transaction_date': transaction.transaction_date,
                'amount': str(transaction.amount),
                'issue': 'Missing client or case linkage',
                'client': transaction.client.full_name if transaction.client else 'Missing',
                'case': transaction.case.case_title if transaction.case else 'Missing'
            })
        
        return Response({
            'unbalanced_transactions': transactions,
            'count': len(transactions)
        })
    
    @action(detail=False, methods=['get'])
    def monthly_summary(self, request):
        """Get monthly transaction summary"""
        year = int(request.query_params.get('year', datetime.now().year))
        
        monthly_data = []
        for month in range(1, 13):
            month_transactions = BankTransaction.objects.filter(
                transaction_date__year=year,
                transaction_date__month=month
            ).aggregate(
                total_amount=Sum('amount'),
                total_count=Count('id'),
                deposits=Sum('amount', filter=Q(transaction_type='DEPOSIT')),
                withdrawals=Sum('amount', filter=Q(transaction_type='WITHDRAWAL'))
            )
            
            monthly_data.append({
                'month': month,
                'month_name': date(year, month, 1).strftime('%B'),
                'total_amount': str(month_transactions['total_amount'] or 0),
                'total_count': month_transactions['total_count'] or 0,
                'deposits': str(month_transactions['deposits'] or 0),
                'withdrawals': str(month_transactions['withdrawals'] or 0)
            })
        
        return Response({
            'year': year,
            'monthly_summary': monthly_data
        })
    
    @action(detail=True, methods=['post'])
    def void(self, request, pk=None):
        """Void a transaction"""
        transaction = self.get_object()

        if transaction.status == 'voided':
            return Response(
                {'error': 'Transaction is already voided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        void_reason = request.data.get('void_reason', '')
        voided_by = request.data.get('voided_by', request.user.username if request.user else '')

        # Use the void_transaction method which sets status='voided'
        transaction.void_transaction(voided_by=voided_by, void_reason=void_reason)

        return Response({
            'message': f'Transaction {transaction.transaction_number} has been voided',
            'voided_date': transaction.voided_date,
            'voided_by': transaction.voided_by
        })
    
    @action(detail=True, methods=['post'])
    def clear(self, request, pk=None):
        """Mark transaction as cleared"""
        transaction = self.get_object()
        
        if transaction.status == 'cleared':
            return Response(
                {'error': 'Transaction is already cleared'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transaction.status = 'cleared'
        transaction.cleared_date = date.today()
        transaction.save()
        
        return Response({
            'message': f'Transaction {transaction.transaction_number} has been marked as cleared',
            'cleared_date': transaction.cleared_date
        })


class BankTransactionItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for BankTransaction CRUD operations (individual transaction items)
    """
    queryset = BankTransaction.objects.all()
    serializer_class = BankTransactionItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    search_fields = ['description', 'client__first_name', 'client__last_name', 'case__case_title']
    filterset_fields = ['item_type', 'client', 'case', 'vendor']
    ordering_fields = ['amount', 'created_at', 'transaction_date']
    ordering = ['-transaction_date', '-created_at']
    
    def get_queryset(self):
        """Optimize queryset with select_related"""
        return BankTransaction.objects.select_related(
            'bank_account', 'client', 'case', 'vendor'
        ).all()
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return BankTransactionItemListSerializer
        return BankTransactionItemSerializer
    
    @action(detail=False, methods=['get'])
    def by_client(self, request):
        """Get transaction items for a specific client"""
        client_id = request.query_params.get('client_id')
        if not client_id:
            return Response({'error': 'client_id parameter is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        items = BankTransaction.objects.filter(client_id=client_id).select_related(
            'bank_account', 'case', 'vendor'
        ).order_by('-transaction_date')

        serializer = BankTransactionItemListSerializer(items, many=True)
        return Response({
            'client_id': client_id,
            'items': serializer.data,
            'count': items.count()
        })
    
    @action(detail=False, methods=['get'])
    def by_case(self, request):
        """Get transaction items for a specific case"""
        case_id = request.query_params.get('case_id')
        if not case_id:
            return Response({'error': 'case_id parameter is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        items = BankTransaction.objects.filter(case_id=case_id).select_related(
            'bank_account', 'client', 'vendor'
        ).order_by('-transaction_date')

        serializer = BankTransactionItemListSerializer(items, many=True)
        return Response({
            'case_id': case_id,
            'items': serializer.data,
            'count': items.count()
        })
