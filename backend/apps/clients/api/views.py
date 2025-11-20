from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from ..models import Client, Case
from .serializers import ClientSerializer, ClientListSerializer, CaseSerializer, CaseListSerializer
from apps.api.permissions import IsTrustAccountUser
from apps.api.pagination import StandardResultsSetPagination
from trust_account_project.api_hardening import (
    SecureAPIPermission, APIRateLimitThrottle, api_security_required,
    sensitive_api_endpoint, SecureSessionAuthentication
)


class ClientViewSet(viewsets.ModelViewSet):
    """
    Enhanced ViewSet for Client CRUD operations with security hardening
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]  # PRODUCTION: Require authentication
    throttle_classes = [APIRateLimitThrottle]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Search fields for ?search= parameter
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'client_number', 'address', 'city']
    
    # Filter fields for ?field=value parameters  
    filterset_fields = ['is_active', 'trust_account_status', 'state']
    
    # Ordering fields for ?ordering= parameter
    ordering_fields = ['last_name', 'first_name', 'client_number', 'created_at', 'trust_account_status']
    ordering = ['-created_at']  # Default ordering
    
    def get_queryset(self):
        """Customize queryset with optimizations"""
        queryset = Client.objects.all().order_by('-created_at')
        
        # Add custom filters
        trust_status = self.request.query_params.get('trust_status', None)
        if trust_status:
            queryset = queryset.filter(trust_account_status=trust_status)
        
        # Filter by balance range (if provided)
        min_balance = self.request.query_params.get('min_balance', None)
        max_balance = self.request.query_params.get('max_balance', None)
        
        if min_balance or max_balance:
            # Note: This is not ideal for performance as it requires calculating balances
            # In a production system, you'd want a cached balance field
            filtered_clients = []
            for client in queryset:
                balance = client.get_current_balance()
                if min_balance and balance < float(min_balance):
                    continue
                if max_balance and balance > float(max_balance):
                    continue
                filtered_clients.append(client.pk)
            queryset = queryset.filter(pk__in=filtered_clients)
        
        return queryset
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return ClientListSerializer
        return ClientSerializer
    
    def list(self, request, *args, **kwargs):
        """Enhanced list view with metadata"""
        response = super().list(request, *args, **kwargs)
        
        # Add metadata to response
        if hasattr(response, 'data') and 'results' in response.data:
            total_clients = Client.objects.count()
            active_clients = Client.objects.filter(is_active=True).count()
            
            response.data['metadata'] = {
                'total_clients': total_clients,
                'active_clients': active_clients,
                'inactive_clients': total_clients - active_clients,
            }
        
        return response
    
    @action(detail=True, methods=['get'])
    def cases(self, request, pk=None):
        """Get all cases for a specific client"""
        client = self.get_object()
        cases = client.cases.all().order_by('-created_at')
        
        # Apply search to cases if provided
        search = request.query_params.get('search', None)
        if search:
            cases = cases.filter(
                Q(case_title__icontains=search) |
                Q(case_number__icontains=search) |
                Q(case_description__icontains=search)
            )
        
        # Apply case status filter
        case_status = request.query_params.get('status', None)
        if case_status:
            cases = cases.filter(case_status=case_status)
        
        serializer = CaseListSerializer(cases, many=True)
        return Response({
            'client_id': client.id,
            'client_name': client.full_name,
            'client_number': client.client_number,
            'cases': serializer.data,
            'count': cases.count()
        })
    
    @action(detail=True, methods=['get'])
    def balance_history(self, request, pk=None):
        """Get balance calculation breakdown for a client"""
        client = self.get_object()

        # Get transactions for balance calculation (exclude voided)
        from apps.bank_accounts.models import BankTransaction
        transactions = BankTransaction.objects.filter(
            client=client
        ).exclude(
            status='voided'
        ).order_by('-transaction_date')

        balance_history = []
        running_balance = 0

        for txn in transactions:
            if txn.transaction_type == 'DEPOSIT':
                running_balance += txn.amount
                transaction_type = 'DEPOSIT'
            else:
                running_balance -= txn.amount
                transaction_type = 'WITHDRAWAL'

            balance_history.append({
                'date': txn.transaction_date,
                'transaction_number': txn.transaction_number,
                'type': transaction_type,
                'amount': str(txn.amount),
                'running_balance': str(running_balance),
                'description': txn.description,
                'case_title': txn.case.case_title if txn.case else None,
                'status': txn.status,  # Include status field
                'status_display': txn.get_status_display(),  # Human-readable status
            })
        
        return Response({
            'client_id': client.id,
            'client_name': client.full_name,
            'current_balance': str(client.get_current_balance()),
            'balance_history': list(reversed(balance_history)),  # Chronological order
        })
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """BUG #7 FIX: Enhanced search endpoint with full name support"""
        from django.db.models import Value
        from django.db.models.functions import Concat

        query = request.query_params.get('q', '')
        # BUG #8 FIX: Support both 'limit' and 'page_size' parameters
        limit = int(request.query_params.get('page_size') or request.query_params.get('limit', 50))

        if len(query) < 2:
            return Response({
                'clients': [],
                'count': 0,
                'query': query,
                'message': 'Search query must be at least 2 characters'
            })

        # BUG #7 FIX: Search across multiple fields including full name
        clients = Client.objects.annotate(
            full_name_search=Concat('first_name', Value(' '), 'last_name')
        ).filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(full_name_search__icontains=query) |  # BUG #7 FIX: Search full name
            Q(email__icontains=query) |
            Q(phone__icontains=query) |
            Q(client_number__icontains=query) |
            Q(address__icontains=query) |
            Q(city__icontains=query)
        )

        # REQUIREMENT: Search includes ALL clients (both active and inactive)
        # Do not apply is_active filter to search results

        clients = clients.order_by('last_name', 'first_name')[:limit]

        serializer = ClientListSerializer(clients, many=True)
        return Response({
            'clients': serializer.data,
            'count': clients.count(),
            'query': query,
            'limit': limit
        })
    
    @action(detail=False, methods=['get'])
    def trust_summary(self, request):
        """Get trust account status summary with optional historical date filter"""
        from django.db.models import Count
        from datetime import datetime

        # REQUIREMENT: Date filter for historical trust balance
        as_of_date = request.query_params.get('as_of_date', None)

        status_counts = Client.objects.values('trust_account_status').annotate(
            count=Count('id')
        ).order_by('trust_account_status')

        # Calculate total trust balance (with optional date filter)
        if as_of_date:
            try:
                # Parse date
                filter_date = datetime.strptime(as_of_date, '%Y-%m-%d').date()

                # Calculate historical balance for each client as of that date
                from apps.bank_accounts.models import BankTransaction
                from django.db.models import Sum, Q

                # Get all non-voided transactions up to and including the filter date
                total_balance = 0
                for client in Client.objects.all():
                    deposits = BankTransaction.objects.filter(
                        client=client,
                        transaction_type='DEPOSIT',
                        transaction_date__lte=filter_date
                    ).exclude(status='voided').aggregate(total=Sum('amount'))['total'] or 0

                    withdrawals = BankTransaction.objects.filter(
                        client=client,
                        transaction_type__in=['WITHDRAWAL', 'TRANSFER_OUT'],
                        transaction_date__lte=filter_date
                    ).exclude(status='voided').aggregate(total=Sum('amount'))['total'] or 0

                    client_balance = deposits - withdrawals
                    total_balance += client_balance

            except ValueError:
                return Response({
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }, status=400)
        else:
            # Current balance (no date filter)
            total_balance = sum(client.get_current_balance() for client in Client.objects.all())

        return Response({
            'total_clients': Client.objects.count(),
            'active_clients': Client.objects.filter(is_active=True).count(),
            'status_breakdown': list(status_counts),
            'total_trust_balance': str(total_balance),
            'as_of_date': as_of_date if as_of_date else 'current',
        })

    def destroy(self, request, *args, **kwargs):
        """
        Smart Delete Logic:
        1. If client has balance (amount ≠ 0): REJECT - Cannot delete or set inactive
        2. If client has transactions BUT balance = 0: SOFT DELETE (set inactive)
        3. If client has no transactions: HARD DELETE (permanent removal)
        """
        from apps.bank_accounts.models import BankTransaction
        from django.db import models
        from decimal import Decimal

        instance = self.get_object()

        # Get client's current balance
        client_balance = Decimal(str(instance.get_current_balance() or 0))

        # Check if client has ANY transactions (including voided ones for audit trail)
        has_transactions = BankTransaction.objects.filter(
            models.Q(client=instance) | models.Q(case__client=instance)
        ).exists()

        # Check for non-voided transactions specifically
        has_active_transactions = BankTransaction.objects.filter(
            models.Q(client=instance) | models.Q(case__client=instance)
        ).exclude(status='voided').exists()

        # RULE 1: If client has balance (≠ 0), REJECT deletion
        if client_balance != Decimal('0'):
            return Response({
                'success': False,
                'error': f'Cannot delete client with balance of ${client_balance:,.2f}',
                'balance': float(client_balance)
            }, status=status.HTTP_400_BAD_REQUEST)

        # RULE 2: If client has transactions but balance = 0, SOFT DELETE (set inactive)
        if has_transactions:
            instance.is_active = False
            instance.save()

            return Response({
                'success': True,
                'message': f'Client {instance.full_name} has been set to Inactive (has transaction history with zero balance).',
                'soft_delete': True
            }, status=status.HTTP_200_OK)

        # RULE 3: No transactions and balance = 0, HARD DELETE (permanent)
        else:
            instance.delete()
            return Response({
                'success': True,
                'message': f'Client {instance.full_name} deleted successfully.',
                'soft_delete': False
            }, status=status.HTTP_204_NO_CONTENT)


class CaseViewSet(viewsets.ModelViewSet):
    """
    Enhanced ViewSet for Case CRUD operations with security hardening
    """
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    permission_classes = [IsAuthenticated]  # Temporarily allow any for frontend development
    throttle_classes = [APIRateLimitThrottle]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    search_fields = ['case_title', 'case_number', 'case_description', 'client__first_name', 'client__last_name']
    filterset_fields = ['case_status', 'is_active', 'client']
    ordering_fields = ['case_number', 'case_title', 'opened_date', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Optimize queryset with select_related"""
        queryset = Case.objects.select_related('client').all()
        
        # Custom filters
        client_id = self.request.query_params.get('client', None)
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(case_status=status)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return CaseListSerializer
        return CaseSerializer
    
    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None):
        """Get the current balance for a specific case"""
        case = self.get_object()
        balance = case.get_current_balance()

        return Response({
            'case_id': case.id,
            'case_number': case.case_number,
            'case_title': case.case_title,
            'balance': str(balance),
            'formatted_balance': f'${balance:,.2f}' if balance >= 0 else f'(${abs(balance):,.2f})'
        })

    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """Get all transactions for a specific case"""
        case = self.get_object()

        from apps.bank_accounts.models import BankTransaction
        transactions_data = BankTransaction.objects.filter(case=case).order_by('-transaction_date')

        transactions = []
        for txn in transactions_data:
            # When voided, amount should be 0
            amount = '0.00' if txn.status == 'voided' else str(txn.amount)

            # Get payee from multiple sources (priority: payee field, vendor, client)
            payee = txn.payee
            if not payee and txn.vendor:
                payee = txn.vendor.vendor_name
            elif not payee and txn.client:
                payee = txn.client.full_name

            transactions.append({
                'id': txn.id,
                'transaction_number': txn.transaction_number,
                'date': txn.transaction_date,
                'type': txn.transaction_type,
                'amount': amount,
                'description': txn.description,
                'status': txn.status,  # FIX: Return actual status string (cleared/pending/voided)
                'payee': payee or '',
                'reference_number': txn.reference_number,
                'void_reason': txn.void_reason or '',
                'voided_by': txn.voided_by or '',
                'voided_date': str(txn.voided_date) if txn.voided_date else None,
            })

        return Response({
            'case_id': case.id,
            'case_number': case.case_number,
            'case_title': case.case_title,
            'current_balance': str(case.get_current_balance()),
            'transactions': transactions,
            'count': len(transactions)
        })
    
    @action(detail=False, methods=['get'])
    def by_client(self, request):
        """Get cases grouped by client"""
        client_id = request.query_params.get('client_id')
        if not client_id:
            return Response({'error': 'client_id parameter is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            client = Client.objects.get(pk=client_id)
        except Client.DoesNotExist:
            return Response({'error': 'Client not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        cases = Case.objects.filter(client=client).order_by('-created_at')
        serializer = CaseListSerializer(cases, many=True)
        
        return Response({
            'client_id': client.id,
            'client_name': client.full_name,
            'client_number': client.client_number,
            'cases': serializer.data,
            'count': cases.count()
        })

    @action(detail=True, methods=['get'], url_path='ledger-pdf', permission_classes=[])
    def ledger_pdf(self, request, pk=None):
        """Generate case ledger PDF"""
        from apps.clients.views import print_case_ledger
        return print_case_ledger(request, pk)


from rest_framework.views import APIView
from apps.clients.utils import QuickBooksParser, QuickBooksImporter


class QuickBooksValidateView(APIView):
    """
    Validate QuickBooks CSV file before import.

    POST /api/clients/quickbooks/validate/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Validate uploaded QuickBooks CSV file."""
        # Check if file was uploaded
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file uploaded'},
                status=status.HTTP_400_BAD_REQUEST
            )

        uploaded_file = request.FILES['file']

        # Read file content
        try:
            file_content = uploaded_file.read()
        except Exception as e:
            return Response(
                {'error': f'Could not read file: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Parse and validate
        parser = QuickBooksParser(file_content)
        success, valid_data, errors, warnings = parser.parse()

        if not success:
            return Response({
                'valid': False,
                'errors': errors,
                'warnings': warnings
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get summary
        summary = parser.get_summary(valid_data)

        return Response({
            'valid': True,
            'summary': summary,
            'errors': errors,
            'warnings': warnings
        })


class QuickBooksImportView(APIView):
    """
    Import validated QuickBooks CSV file.

    POST /api/clients/quickbooks/import/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Import QuickBooks CSV file."""
        # Check if file was uploaded
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file uploaded'},
                status=status.HTTP_400_BAD_REQUEST
            )

        uploaded_file = request.FILES['file']

        # Get options
        skip_errors = request.POST.get('skip_errors', 'true').lower() == 'true'

        # Read file content
        try:
            file_content = uploaded_file.read()
        except Exception as e:
            return Response(
                {'error': f'Could not read file: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Parse and validate
        parser = QuickBooksParser(file_content)
        success, valid_data, errors, warnings = parser.parse()

        if not success:
            return Response({
                'success': False,
                'error': 'File validation failed',
                'errors': errors,
                'warnings': warnings
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if there are errors and skip_errors is False
        if errors and not skip_errors:
            return Response({
                'success': False,
                'error': 'File has validation errors. Set skip_errors=true to import valid rows only.',
                'errors': errors,
                'warnings': warnings
            }, status=status.HTTP_400_BAD_REQUEST)

        # Import data
        try:
            # Pass filename to importer for logging
            filename = uploaded_file.name if hasattr(uploaded_file, 'name') else 'unknown.csv'
            importer = QuickBooksImporter(request.user, filename=filename)
            result = importer.import_data(valid_data)

            return Response(result)
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Import failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
