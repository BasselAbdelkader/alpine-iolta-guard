from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q

from ..models import BankAccount, BankTransaction, BankReconciliation
from .serializers import (
    BankAccountSerializer, BankAccountListSerializer,
    BankTransactionSerializer, BankReconciliationSerializer
)
from apps.api.permissions import IsTrustAccountUser
from apps.api.pagination import StandardResultsSetPagination


class BankAccountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for BankAccount CRUD operations with balance calculations
    """
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated]  # Require authentication
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    search_fields = ['account_name', 'account_number', 'bank_name', 'routing_number']
    filterset_fields = ['account_type', 'is_active']
    ordering_fields = ['bank_name', 'account_name', 'created_at']
    ordering = ['bank_name', 'account_name']
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return BankAccountListSerializer
        return BankAccountSerializer
    
    def list(self, request, *args, **kwargs):
        """Enhanced list view with summary statistics"""
        response = super().list(request, *args, **kwargs)
        
        # Add summary metadata
        if hasattr(response, 'data') and 'results' in response.data:
            accounts = BankAccount.objects.all()
            
            # Calculate totals (trust balance = register balance = ALL non-voided transactions)
            total_trust_balance = sum(account.get_current_balance() for account in accounts)
            active_accounts = accounts.filter(is_active=True).count()

            # Group by account type
            type_summary = {}
            for account in accounts:
                acc_type = account.account_type
                if acc_type not in type_summary:
                    type_summary[acc_type] = {
                        'count': 0,
                        'trust_balance': 0,
                        'pending_count': 0
                    }
                type_summary[acc_type]['count'] += 1
                type_summary[acc_type]['trust_balance'] += account.get_current_balance()
                type_summary[acc_type]['pending_count'] += account.get_pending_transactions_count()

            response.data['summary'] = {
                'total_accounts': accounts.count(),
                'active_accounts': active_accounts,
                'inactive_accounts': accounts.count() - active_accounts,
                'total_trust_balance': str(total_trust_balance),
                'account_types': {
                    acc_type: {
                        'count': data['count'],
                        'trust_balance': str(data['trust_balance']),
                        'pending_count': data['pending_count']
                    }
                    for acc_type, data in type_summary.items()
                }
            }
        
        return response

    def update(self, request, *args, **kwargs):
        """Override update to allow next_check_number updates"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Special handling for next_check_number updates
        if 'next_check_number' in request.data:
            # Update next_check_number directly bypassing serializer
            new_check_number = request.data.get('next_check_number')
            instance.next_check_number = new_check_number
            instance.save(update_fields=['next_check_number', 'updated_at'])

            # Return updated serializer data
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        # For all other updates, use default behavior (will raise ValueError)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        """Default perform_update for non-check_number updates"""
        serializer.save()

    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """Get all transactions for a specific bank account"""
        account = self.get_object()
        
        # Get transaction parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        transaction_type = request.query_params.get('type')
        
        # Build queryset using consolidated bank_transactions table
        transactions = BankTransaction.objects.filter(
            bank_account=account
        ).exclude(status='voided').order_by('-transaction_date')

        if start_date:
            transactions = transactions.filter(transaction_date__gte=start_date)
        if end_date:
            transactions = transactions.filter(transaction_date__lte=end_date)
        if transaction_type:
            transactions = transactions.filter(transaction_type=transaction_type)

        # Calculate summary
        summary = transactions.aggregate(
            total_amount=Sum('amount'),
            total_count=Count('id'),
            deposits=Sum('amount', filter=Q(transaction_type='DEPOSIT')),
            withdrawals=Sum('amount', filter=Q(transaction_type='WITHDRAWAL')),
            cleared_amount=Sum('amount', filter=Q(status='cleared'))
        )

        # Serialize transactions using bank transaction serializer
        serializer = BankTransactionSerializer(transactions[:50], many=True)  # Limit to 50 for performance
        
        return Response({
            'account_id': account.id,
            'account_name': account.account_name,
            'account_number': account.account_number,
            'current_balance': str(account.get_current_balance()),
            'transactions': serializer.data,
            'summary': {
                'total_count': summary['total_count'] or 0,
                'total_amount': str(summary['total_amount'] or 0),
                'deposits': str(summary['deposits'] or 0),
                'withdrawals': str(summary['withdrawals'] or 0),
                'cleared_amount': str(summary['cleared_amount'] or 0)
            }
        })
    
    @action(detail=True, methods=['get'])
    def balance_history(self, request, pk=None):
        """Get balance history for a bank account"""
        account = self.get_object()
        
        transactions = BankTransaction.objects.filter(
            bank_account=account
        ).exclude(status='voided').order_by('transaction_date', 'id')
        
        balance_history = []
        running_balance = account.opening_balance
        
        # Add opening balance entry
        balance_history.append({
            'date': account.created_at.date(),
            'description': 'Opening Balance',
            'type': 'OPENING',
            'amount': str(account.opening_balance),
            'running_balance': str(running_balance)
        })
        
        # Add each transaction
        for transaction in transactions:
            if transaction.transaction_type == 'DEPOSIT':
                running_balance += transaction.amount
            else:
                running_balance -= transaction.amount
            
            balance_history.append({
                'date': transaction.transaction_date,
                'description': transaction.description,
                'transaction_number': transaction.transaction_number,
                'type': transaction.transaction_type,
                'amount': str(transaction.amount),
                'running_balance': str(running_balance),
                'status': transaction.status == 'cleared'
            })
        
        return Response({
            'account_id': account.id,
            'account_name': account.account_name,
            'opening_balance': str(account.opening_balance),
            'current_balance': str(account.get_current_balance()),
            'balance_history': balance_history
        })
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get comprehensive summary of all bank accounts"""
        accounts = BankAccount.objects.all()
        
        summary = {
            'total_accounts': accounts.count(),
            'active_accounts': accounts.filter(is_active=True).count(),
            'account_details': []
        }
        
        total_system_balance = 0
        
        for account in accounts:
            current_balance = account.get_current_balance()
            total_system_balance += current_balance
            
            summary['account_details'].append({
                'id': account.id,
                'account_name': account.account_name,
                'account_number': account.account_number,
                'account_type': account.account_type,
                'bank_name': account.bank_name,
                'opening_balance': str(account.opening_balance),
                'current_balance': str(current_balance),
                'balance_difference': str(current_balance - account.opening_balance),
                'is_active': account.is_active
            })
        
        summary['total_system_balance'] = str(total_system_balance)
        return Response(summary)


class BankTransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for BankTransaction operations (for reconciliation)
    """
    queryset = BankTransaction.objects.all()
    serializer_class = BankTransactionSerializer
    permission_classes = [IsAuthenticated]  # Require authentication
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    search_fields = [
        'description', 'reference_number', 'check_number', 'bank_reference', 'payee',
        'client__first_name', 'client__last_name',  # Search by client name
        'case__case_title',  # Search by case title
        'vendor__vendor_name',  # Search by vendor name
    ]
    filterset_fields = ['bank_account', 'transaction_type', 'status']
    ordering_fields = ['transaction_date', 'post_date', 'amount']
    ordering = ['-transaction_date', '-created_at']

    def get_queryset(self):
        """Optimize queryset and add filters"""
        queryset = BankTransaction.objects.select_related('bank_account', 'client', 'case', 'vendor')

        # Date filters
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(transaction_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(transaction_date__lte=end_date)

        return queryset

    def create(self, request, *args, **kwargs):
        """Override create to pass audit parameters"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')

        # Save with audit parameters
        # Get username from authenticated user
        username = request.user.username if request.user and request.user.is_authenticated else 'system'

        instance = serializer.save(
            audit_user=username,
            audit_reason='Transaction created via API',
            audit_ip=ip_address
        )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """Override update to pass audit parameters"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Get IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')

        # Save with audit parameters
        # Get username from authenticated user
        username = request.user.username if request.user and request.user.is_authenticated else 'system'

        # Special handling for BankAccount updates - only allow next_check_number
        if isinstance(instance, BankAccount) and 'next_check_number' in serializer.validated_data:
            instance.next_check_number = serializer.validated_data['next_check_number']
            instance.save(update_fields=['next_check_number', 'updated_at'])
            serializer = self.get_serializer(instance)
        else:
            instance = serializer.save(
                audit_user=username,
                audit_reason='Transaction updated via API',
                audit_ip=ip_address
            )

        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """Handle PATCH requests with partial updates"""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def unmatched(self, request):
        """Get unmatched bank transactions for reconciliation"""
        unmatched = BankTransaction.objects.filter(status='UNMATCHED').select_related('bank_account')
        serializer = self.get_serializer(unmatched, many=True)

        return Response({
            'unmatched_transactions': serializer.data,
            'count': unmatched.count()
        })

    @action(detail=True, methods=['post'])
    def void(self, request, pk=None):
        """Void a bank transaction"""
        transaction = self.get_object()

        # Check if already voided
        if transaction.status == 'voided':
            return Response({
                'success': False,
                'message': 'Transaction is already voided.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if cleared
        if transaction.status == 'cleared':
            return Response({
                'success': False,
                'message': 'Cannot void cleared transactions.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get void reason
        void_reason = request.data.get('void_reason', '').strip()
        if not void_reason:
            return Response({
                'success': False,
                'message': 'Void reason is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')

        # Void the transaction
        # Get username from authenticated user
        username = request.user.username if request.user and request.user.is_authenticated else 'system'

        try:
            transaction.void_transaction(
                void_reason=void_reason,
                voided_by=username,
                ip_address=ip_address
            )

            return Response({
                'success': True,
                'message': f'Transaction {transaction.transaction_number} has been voided successfully.'
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error voiding transaction: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def reissue(self, request, pk=None):
        """
        REQUIREMENT: Reissue a check (for checks that are not cleared and not reconciled)

        3-TRANSACTION LOGIC:
        1. VOID the original transaction (removes from balance, preserves audit trail with original date)
        2. Create reversal deposit (CLEARED status - dated today, reverses the voided withdrawal)
        3. Create new check transaction (PENDING status - dated today, until printed)

        Original transaction keeps its original date. New transactions dated today (reissue date).
        """
        from datetime import date
        from django.db import transaction as db_transaction

        original_txn = self.get_object()

        # REQUIREMENT: Cannot reissue if status is Cleared or Reconciled
        if original_txn.status in ['cleared', 'reconciled']:
            return Response({
                'success': False,
                'message': f'Cannot reissue {original_txn.get_status_display()} transactions.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Only allow reissuing withdrawals (checks)
        if original_txn.transaction_type != 'WITHDRAWAL':
            return Response({
                'success': False,
                'message': 'Only withdrawal transactions (checks) can be reissued.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')

        username = request.user.username if request.user and request.user.is_authenticated else 'system'
        reissue_date = date.today()  # Use today's date for all reissue operations

        try:
            with db_transaction.atomic():
                # Store original check info for reference
                original_check_number = original_txn.reference_number or original_txn.check_number
                original_description = original_txn.description
                original_amount = original_txn.amount

                # REQUIREMENT: Reference number logic
                # If original reference was "TO PRINT":
                #   - Reversal deposit gets blank reference
                #   - New withdrawal gets "TO PRINT" (so it can be printed with new check number)
                # If original reference was actual check number, keep it for all transactions
                if original_txn.reference_number == 'TO PRINT':
                    reference_for_reversal = ''
                    check_number_for_reversal = ''
                    reference_for_new_check = 'TO PRINT'
                    check_number_for_new_check = ''
                else:
                    reference_for_reversal = original_txn.reference_number
                    check_number_for_reversal = original_txn.check_number
                    reference_for_new_check = original_txn.reference_number
                    check_number_for_new_check = original_txn.check_number

                # STEP 1: VOID the original transaction
                # This removes it from balance calculation but keeps it for audit trail
                # IMPORTANT: Keep original transaction_date - do NOT update it
                original_txn.status = 'voided'
                original_txn.description = f"VOIDED - Reissued on {reissue_date.strftime('%Y-%m-%d')}: {original_description}"
                # NOTE: transaction_date is NOT updated - keeps original date for audit trail
                original_txn.save(
                    audit_user=username,
                    audit_reason=f'Check reissued by {username} - original voided',
                    audit_ip=ip_address
                )

                # STEP 2: Create reversal deposit (CLEARED)
                # This reverses the voided withdrawal - deposit of same amount
                reversal_txn = BankTransaction.objects.create(
                    bank_account=original_txn.bank_account,
                    transaction_date=reissue_date,  # Today's date
                    transaction_type='DEPOSIT',
                    amount=original_amount,  # Same amount as original
                    description=f"Reversal - Reissue of check #{original_check_number}: {original_description}",
                    client=original_txn.client,
                    case=original_txn.case,
                    reference_number=reference_for_reversal,  # Blank if original was TO PRINT
                    check_number=check_number_for_reversal,  # Blank if original was TO PRINT
                    status='cleared',  # CLEARED status
                )

                # STEP 3: Create new check transaction (PENDING)
                new_check = BankTransaction.objects.create(
                    bank_account=original_txn.bank_account,
                    transaction_date=reissue_date,  # Today's date
                    transaction_type='WITHDRAWAL',
                    amount=original_amount,  # Same amount as original
                    description=f"Reissue of check #{original_check_number}: {original_description}",
                    client=original_txn.client,
                    case=original_txn.case,
                    vendor=original_txn.vendor,
                    payee=original_txn.payee,
                    reference_number=reference_for_new_check,  # "TO PRINT" if original was TO PRINT
                    check_number=check_number_for_new_check,  # Blank if original was TO PRINT
                    check_memo=original_txn.check_memo,
                    item_type=original_txn.item_type,
                    status='pending',  # PENDING until printed and cleared by bank
                )

                return Response({
                    'success': True,
                    'message': f'Check {original_check_number} reissued successfully.',
                    'original_transaction_id': original_txn.id,
                    'reversal_transaction_id': reversal_txn.id,
                    'new_check_transaction_id': new_check.id,
                    'original_transaction_number': original_txn.transaction_number,
                    'reversal_transaction_number': reversal_txn.transaction_number,
                    'new_check_transaction_number': new_check.transaction_number,
                    'reissue_date': reissue_date.isoformat()
                })

        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error reissuing check: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def audit_history(self, request, pk=None):
        """Get audit history for a transaction"""
        transaction = self.get_object()

        from ..models import BankTransactionAudit

        # Get all audit logs for this transaction
        audit_logs = BankTransactionAudit.objects.filter(
            transaction=transaction
        ).order_by('-action_date')

        logs_data = []
        for log in audit_logs:
            logs_data.append({
                'id': log.id,
                'action': log.action,
                'action_date': log.action_date.strftime('%m/%d/%Y %I:%M %p'),
                'action_by': log.action_by,
                'old_amount': str(log.old_amount) if log.old_amount is not None else None,
                'new_amount': str(log.new_amount) if log.new_amount is not None else None,
                'old_status': log.old_status,
                'new_status': log.new_status,
                'change_reason': log.change_reason,
                'changes_summary': log.get_changes_summary(),
                'ip_address': str(log.ip_address) if log.ip_address else None,
            })

        return Response({
            'success': True,
            'transaction': {
                'id': transaction.id,
                'transaction_number': transaction.transaction_number,
                'transaction_date': transaction.transaction_date.strftime('%m/%d/%Y'),
                'transaction_type': transaction.transaction_type,
                'transaction_type_display': transaction.get_transaction_type_display(),
                'amount': str(transaction.amount),
                'description': transaction.description or '',
                'status': transaction.status,
                'status_display': transaction.get_status_display(),
                'payee': transaction.payee or '-',
                'client_name': transaction.client.full_name if transaction.client else None,
                'case_number': transaction.case.case_number if transaction.case else None,
                'case_title': transaction.case.case_title if transaction.case else None,
                'vendor_name': transaction.vendor.vendor_name if transaction.vendor else None,
                'reference_number': transaction.reference_number or '',
            },
            'audit_logs': logs_data,
            'count': len(logs_data)
        })

    @action(detail=True, methods=['get'], url_path='audit_history_pdf')
    def audit_history_pdf(self, request, pk=None):
        """Generate PDF of audit history"""
        from django.http import HttpResponse
        from django.template.loader import render_to_string
        from weasyprint import HTML
        import tempfile

        transaction = self.get_object()
        from ..models import BankTransactionAudit
        from apps.settings.models import LawFirm

        # Get audit logs
        audit_logs = BankTransactionAudit.objects.filter(
            transaction=transaction
        ).order_by('-action_date')

        # Get law firm info
        law_firm = LawFirm.objects.first()

        # Prepare context
        context = {
            'transaction': transaction,
            'audit_logs': audit_logs,
            'law_firm': law_firm,
        }

        # Render HTML template
        html_string = render_to_string('audit_trail_pdf.html', context)

        # Generate PDF
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
        pdf_file = html.write_pdf()

        # Return PDF response
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="audit_trail_{transaction.transaction_number}.pdf"'

        return response

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary statistics for all transactions"""
        transactions = self.get_queryset()

        summary = transactions.aggregate(
            total_deposits=Sum('amount', filter=Q(transaction_type='DEPOSIT') & ~Q(status='voided')),
            total_withdrawals=Sum('amount', filter=Q(transaction_type='WITHDRAWAL') & ~Q(status='voided')),
            deposits_count=Count('id', filter=Q(transaction_type='DEPOSIT') & ~Q(status='voided')),
            withdrawals_count=Count('id', filter=Q(transaction_type='WITHDRAWAL') & ~Q(status='voided')),
            matched_count=Count('id', filter=Q(status='cleared')),
            matched_amount=Sum('amount', filter=Q(status='cleared')),
            unmatched_count=Count('id', filter=Q(status='pending')),
            unmatched_amount=Sum('amount', filter=Q(status='pending'))
        )

        return Response({
            'deposits': {
                'count': summary['deposits_count'] or 0,
                'total': str(summary['total_deposits'] or 0)
            },
            'withdrawals': {
                'count': summary['withdrawals_count'] or 0,
                'total': str(summary['total_withdrawals'] or 0)
            },
            'matched': {
                'count': summary['matched_count'] or 0,
                'amount': str(summary['matched_amount'] or 0)
            },
            'unmatched': {
                'count': summary['unmatched_count'] or 0,
                'amount': str(summary['unmatched_amount'] or 0)
            }
        })

    @action(detail=False, methods=['get'])
    def missing(self, request):
        """Get missing/outstanding transactions (reference_number='TO PRINT' or status='pending')"""
        missing_transactions = BankTransaction.objects.filter(
            Q(reference_number='TO PRINT') | Q(status='pending')
        ).exclude(status='voided').select_related('bank_account', 'client', 'case', 'vendor').order_by('-transaction_date')

        serializer = self.get_serializer(missing_transactions, many=True)

        total_amount = missing_transactions.aggregate(total=Sum('amount'))['total'] or 0

        return Response({
            'missing_checks': serializer.data,
            'missing_checks_count': missing_transactions.count(),
            'missing_checks_amount': str(total_amount)
        })


class BankReconciliationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for BankReconciliation operations
    """
    queryset = BankReconciliation.objects.all()
    serializer_class = BankReconciliationSerializer
    permission_classes = [IsAuthenticated]  # Require authentication
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    
    filterset_fields = ['bank_account', 'is_reconciled']
    ordering_fields = ['reconciliation_date', 'created_at']
    ordering = ['-reconciliation_date']
    
    def get_queryset(self):
        return BankReconciliation.objects.select_related('bank_account')
