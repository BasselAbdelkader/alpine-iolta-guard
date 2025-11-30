from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import BankAccount, BankReconciliation, BankTransaction
from .forms import BankAccountForm, BankTransactionForm, BankTransactionSearchForm

class IndexView(LoginRequiredMixin, ListView):
    model = BankAccount
    template_name = 'bank_accounts/index.html'
    context_object_name = 'bank_accounts'
    
    def get_queryset(self):
        return BankAccount.objects.all().order_by('bank_name', 'account_name')

class BankAccountDetailView(LoginRequiredMixin, DetailView):
    model = BankAccount
    template_name = 'bank_accounts/detail.html'
    context_object_name = 'bank_account'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reconciliations'] = self.object.bankreconciliation_set.all().order_by('-reconciliation_date')[:10]
        return context

class BankAccountCreateView(LoginRequiredMixin, CreateView):
    model = BankAccount
    form_class = BankAccountForm
    template_name = 'bank_accounts/form.html'
    success_url = reverse_lazy('bank_accounts:index')
    
    def form_valid(self, form):
        messages.success(self.request, 'Bank account created successfully.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Add New Bank Account'
        return context

class BankAccountUpdateView(LoginRequiredMixin, UpdateView):
    model = BankAccount
    form_class = BankAccountForm
    template_name = 'bank_accounts/form.html'
    success_url = reverse_lazy('bank_accounts:index')
    
    def get(self, request, *args, **kwargs):
        # Prevent editing of bank accounts
        messages.error(request, 'Bank accounts cannot be modified after creation. Please contact administrator to delete and recreate if changes are needed.')
        return redirect('bank_accounts:index')
    
    def post(self, request, *args, **kwargs):
        # Prevent editing of bank accounts
        messages.error(request, 'Bank accounts cannot be modified after creation. Please contact administrator to delete and recreate if changes are needed.')
        return redirect('bank_accounts:index')
    
    def form_valid(self, form):
        messages.error(self.request, 'Bank accounts cannot be modified after creation.')
        return redirect('bank_accounts:index')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit Bank Account: {self.object.account_name}'
        return context

class BankAccountDeleteView(LoginRequiredMixin, DeleteView):
    model = BankAccount
    success_url = reverse_lazy('bank_accounts:index')
    
    def delete(self, request, *args, **kwargs):
        bank_account = self.get_object()
        messages.success(request, f'Bank account "{bank_account.account_name}" deleted successfully.')
        return super().delete(request, *args, **kwargs)


# Bank Transaction Views
class BankTransactionIndexView(LoginRequiredMixin, ListView):
    model = BankTransaction
    template_name = 'bank_accounts/bank_transactions/index.html'
    context_object_name = 'bank_transactions'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = BankTransaction.objects.select_related('bank_account', 'client', 'case', 'vendor').order_by('-transaction_date', '-created_at')
        
        # Apply search filters
        search_query = self.request.GET.get('search', '')
        transaction_type = self.request.GET.get('transaction_type', '')
        status = self.request.GET.get('status', '')
        date_from = self.request.GET.get('date_from', '')
        date_to = self.request.GET.get('date_to', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(description__icontains=search_query) |
                Q(reference_number__icontains=search_query) |
                Q(reference_number__icontains=search_query) |
                Q(bank_reference__icontains=search_query) |
                Q(bank_category__icontains=search_query)
            )
        
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        if status:
            queryset = queryset.filter(status=status)
        
        if date_from:
            queryset = queryset.filter(transaction_date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(transaction_date__lte=date_to)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = BankTransactionSearchForm(self.request.GET)
        
        # Calculate summary statistics
        queryset = self.get_queryset()
        deposit_transactions = queryset.filter(transaction_type__in=['DEPOSIT', 'TRANSFER_IN', 'INTEREST'])
        withdrawal_transactions = queryset.filter(transaction_type__in=['WITHDRAWAL', 'TRANSFER_OUT', 'FEE'])
        
        context['deposits_count'] = deposit_transactions.count()
        context['total_deposits'] = sum(bt.amount for bt in deposit_transactions)
        context['withdrawals_count'] = withdrawal_transactions.count()
        context['total_withdrawals'] = sum(bt.amount for bt in withdrawal_transactions)
        
        # Unmatched statistics
        unmatched_transactions = queryset.filter(status='UNMATCHED')
        context['unmatched_count'] = unmatched_transactions.count()
        context['unmatched_amount'] = sum(bt.amount for bt in unmatched_transactions)
        
        # Matched statistics
        matched_transactions = queryset.filter(status='MATCHED')
        context['matched_count'] = matched_transactions.count()
        context['matched_amount'] = sum(bt.amount for bt in matched_transactions)
        
        # Since tables are now consolidated, all transactions are in bank_transactions
        # No need for missing transactions logic
        missing_transactions = []
        
        context['missing_checks_count'] = len(missing_transactions)
        context['missing_checks_amount'] = sum(txn.amount for txn in missing_transactions)
        context['missing_checks'] = missing_transactions[:10]  # Limit to 10 items for display
        
        return context


class BankTransactionDetailView(LoginRequiredMixin, DetailView):
    model = BankTransaction
    template_name = 'bank_accounts/bank_transactions/detail.html'
    context_object_name = 'bank_transaction'


class BankTransactionCreateView(LoginRequiredMixin, CreateView):
    model = BankTransaction
    form_class = BankTransactionForm
    template_name = 'bank_accounts/bank_transactions/form.html'
    success_url = reverse_lazy('bank_accounts:bank_transactions')
    
    def get(self, request, *args, **kwargs):
        """Handle GET request - return form HTML for AJAX requests"""
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form = self.form_class()

            # Check if client_id and case_id are provided (from case detail page)
            client_id = request.GET.get('client_id')
            case_id = request.GET.get('case_id')

            context = {
                'form': form,
                'form_title': 'Add New Bank Transaction',
                'mode': 'dynamic'  # Default to dynamic mode
            }

            # Debug logging to see what parameters are being received
            print(f"DEBUG: client_id = {client_id}, case_id = {case_id}")

            # If called from case detail page, provide client/case context
            if client_id and case_id:
                try:
                    from ..clients.models import Client, Case
                    client = Client.objects.get(id=client_id)
                    case = Case.objects.get(id=case_id)

                    # Calculate available funds (case balance)
                    available_funds = case.get_current_balance()

                    # Get the first active bank account as default
                    default_bank_account = BankAccount.objects.filter(is_active=True).first()

                    # Add context for locked fields and pre-populated values
                    context.update({
                        'client': client,
                        'case': case,
                        'available_funds': available_funds,
                        'default_bank_account': default_bank_account,
                        'is_case_context': True,  # Flag to indicate locked fields
                        'form_title': f'Add Transaction - {case.case_title}',
                        'mode': 'case_context'  # Explicit mode indicator
                    })

                    # Pre-populate form fields for case context mode only
                    if default_bank_account:
                        form.fields['bank_account'].initial = default_bank_account
                    form.fields['client'].initial = client
                    form.fields['case'].initial = case

                except (Client.DoesNotExist, Case.DoesNotExist):
                    # If client/case don't exist, fall back to regular form
                    pass

            html = render_to_string('bank_accounts/bank_transactions/modal_form.html', context, request=request)
            return JsonResponse({'form_html': html})
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Set the user who created this record
        form.instance.created_by = self.request.user.get_full_name() or self.request.user.username

        # Handle payee - auto-create vendor if doesn't exist
        payee_name = form.cleaned_data.get('payee')
        if payee_name and payee_name.strip():
            from ..vendors.models import Vendor
            vendor, created = Vendor.objects.get_or_create(
                vendor_name=payee_name.strip(),
                defaults={'is_active': True}
            )
            form.instance.vendor = vendor

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX request - return JSON response
            form.save()
            return JsonResponse({'success': True, 'message': 'Bank transaction created successfully.'})
        else:
            # Regular request - use default behavior
            messages.success(self.request, 'Bank transaction created successfully.')
            return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors - preserve mode but don't auto-lock based on selected values"""
        # DEBUG: Print form errors
        print(f"DEBUG: Form validation failed!")
        print(f"DEBUG: Form errors: {form.errors}")
        print(f"DEBUG: Form non-field errors: {form.non_field_errors()}")

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX request - return form with errors

            # Get the original mode from the request (passed as hidden field or GET param)
            # This tells us if form was opened in dynamic mode or case_context mode
            original_mode = self.request.POST.get('original_mode') or self.request.GET.get('mode', 'dynamic')

            print(f"DEBUG: Original mode from request: {original_mode}")

            # Preserve the original context from POST data
            context = {
                'form': form,
                'form_title': 'Add New Bank Transaction',
                'mode': original_mode  # Preserve the original mode
            }

            # ONLY restore case context if original mode was 'case_context'
            # Don't lock fields just because user selected a client/case in dynamic mode
            client_id = self.request.POST.get('client')
            case_id = self.request.POST.get('case')

            # If original mode was case_context AND both client and case are present
            if original_mode == 'case_context' and client_id and case_id:
                try:
                    from ..clients.models import Client, Case
                    client = Client.objects.get(id=client_id)
                    case = Case.objects.get(id=case_id)

                    # Calculate available funds
                    available_funds = case.get_current_balance()

                    # Get bank account from form data
                    bank_account_id = self.request.POST.get('bank_account')
                    default_bank_account = None
                    if bank_account_id:
                        try:
                            default_bank_account = BankAccount.objects.get(id=bank_account_id)
                        except BankAccount.DoesNotExist:
                            default_bank_account = BankAccount.objects.filter(is_active=True).first()
                    else:
                        default_bank_account = BankAccount.objects.filter(is_active=True).first()

                    # Restore case context to keep fields locked
                    context.update({
                        'client': client,
                        'case': case,
                        'available_funds': available_funds,
                        'default_bank_account': default_bank_account,
                        'is_case_context': True,  # Keep fields locked
                        'form_title': f'Add Transaction - {case.case_title}',
                        'mode': 'case_context'  # Preserve locked mode
                    })

                except (Client.DoesNotExist, Case.DoesNotExist):
                    # If client/case lookup fails, use dynamic mode
                    pass

            html = render_to_string('bank_accounts/bank_transactions/modal_form.html', context, request=self.request)
            return JsonResponse({'success': False, 'form_html': html})
        else:
            # Regular request - use default behavior
            return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Add New Bank Transaction'
        return context


class BankTransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = BankTransaction
    form_class = BankTransactionForm
    template_name = 'bank_accounts/bank_transactions/form.html'
    success_url = reverse_lazy('bank_accounts:bank_transactions')

    def get(self, request, *args, **kwargs):
        """Handle GET request - return form HTML for AJAX requests"""
        self.object = self.get_object()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form = self.form_class(instance=self.object)

            # Build context with client/case info from the transaction being edited
            context = {
                'form': form,
                'form_title': f'Edit Transaction: {self.object.transaction_number}',
                'is_editing': True,
                'editing_transaction_id': self.object.id,
                'mode': 'editing'  # Force editing mode to lock client/case fields
            }

            # Add client and case context from the existing transaction
            if self.object.client:
                context['current_client_id'] = self.object.client.id
                context['client'] = self.object.client  # Add client object for template
            if self.object.case:
                context['current_case_id'] = self.object.case.id
                context['case'] = self.object.case  # Add case object for template

            html = render_to_string('bank_accounts/bank_transactions/modal_form.html', context, request=request)
            return JsonResponse({'form_html': html})
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX request - return JSON response
            form.save()
            return JsonResponse({'success': True, 'message': 'Transaction updated successfully.'})
        else:
            # Regular request - use default behavior
            messages.success(self.request, 'Bank transaction updated successfully.')
            return super().form_valid(form)

    def form_invalid(self, form):
        """Handle form validation errors for AJAX requests"""
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX request - return form with errors
            html = render_to_string('bank_accounts/bank_transactions/modal_form.html', {
                'form': form,
                'form_title': f'Edit Transaction: {self.object.transaction_number}'
            }, request=self.request)
            return JsonResponse({'success': False, 'form_html': html})
        else:
            # Regular request - use default behavior
            return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit Bank Transaction: {self.object.bank_reference}'
        return context


class BankTransactionDeleteView(LoginRequiredMixin, UpdateView):
    """
    Handle transaction voiding (not actual deletion for audit trail)
    """
    model = BankTransaction
    fields = []  # No form fields needed
    success_url = reverse_lazy('bank_accounts:bank_transactions')

    def post(self, request, *args, **kwargs):
        """Handle voiding transaction"""
        try:
            transaction = self.get_object()
            void_reason = request.POST.get('void_reason', 'No reason provided')

            # Void the transaction instead of deleting
            transaction.void_transaction(
                voided_by=request.user.get_full_name() or request.user.username,
                void_reason=void_reason
            )

            transaction_ref = transaction.transaction_number or f'ID {transaction.id}'

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # AJAX request
                return JsonResponse({
                    'success': True,
                    'message': f'Transaction {transaction_ref} has been voided successfully.'
                })
            else:
                # Regular request
                messages.success(request, f'Transaction {transaction_ref} has been voided successfully.')
                return redirect(self.success_url)

        except ValueError as e:
            # Handle specific voiding errors (already voided, cleared transaction, etc.)
            error_message = str(e)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': error_message
                })
            else:
                messages.error(request, f'Error voiding transaction: {error_message}')
                return redirect(self.success_url)

        except Exception as e:
            # Handle unexpected errors
            error_message = f'Internal error: {str(e)}'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': error_message
                })
            else:
                messages.error(request, f'Error voiding transaction: {error_message}')
                return redirect(self.success_url)

    def get(self, request, *args, **kwargs):
        """Handle GET request for void confirmation"""
        transaction = self.get_object()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'confirm': True,
                'message': f'Are you sure you want to void transaction {transaction.transaction_number}?',
                'transaction_id': transaction.id
            })
        return redirect(self.success_url)


def get_bank_account_balance(request, account_id):
    """API endpoint to get bank account balance"""
    try:
        bank_account = BankAccount.objects.get(id=account_id, is_active=True)
        balance = bank_account.get_current_balance()
        return JsonResponse({
            'success': True,
            'balance': float(balance),
            'account_name': bank_account.account_name
        })
    except BankAccount.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Bank account not found',
            'balance': 0
        })


@require_http_methods(["POST"])
def void_bank_transaction(request, pk):
    """AJAX endpoint to void a bank transaction"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        transaction = get_object_or_404(BankTransaction, pk=pk)

        # Check if already voided
        if transaction.status == 'voided':
            return JsonResponse({
                'success': False,
                'message': 'Transaction is already voided.'
            })

        # Check if cleared (optional - you may want to allow voiding cleared transactions)
        if transaction.status == 'cleared':
            return JsonResponse({
                'success': False,
                'message': 'Cannot void cleared transactions.'
            })

        # Get void reason from request
        void_reason = request.POST.get('void_reason', '').strip()
        if not void_reason:
            return JsonResponse({
                'success': False,
                'message': 'Void reason is required.'
            })

        # Get client IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')

        # Void the transaction using the model method
        transaction.void_transaction(
            void_reason=void_reason,
            voided_by=request.user.username,
            ip_address=ip_address
        )

        return JsonResponse({
            'success': True,
            'message': f'Transaction {transaction.transaction_number} has been voided successfully.'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error voiding transaction: {str(e)}'
        })


@require_http_methods(["GET"])
def transaction_audit_history(request, transaction_id):
    """
    Get audit history for a specific transaction (AJAX endpoint).
    Returns JSON with all audit logs for the transaction.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        transaction = BankTransaction.objects.get(id=transaction_id)
    except BankTransaction.DoesNotExist:
        return JsonResponse({'error': 'Transaction not found'}, status=404)

    # Import here to avoid circular import
    from .models import BankTransactionAudit

    # Get all audit logs for this transaction
    audit_logs = BankTransactionAudit.objects.filter(
        transaction=transaction
    ).order_by('-action_date')

    logs_data = []
    for log in audit_logs:
        logs_data.append({
            'id': log.id,
            'action': log.action,
            'action_display': log.get_action_display(),
            'action_date': log.action_date.strftime('%m/%d/%Y %I:%M %p'),
            'action_date_iso': log.action_date.isoformat(),
            'action_by': log.action_by,
            'old_amount': str(log.old_amount) if log.old_amount else None,
            'new_amount': str(log.new_amount) if log.new_amount else None,
            'old_status': log.old_status,
            'new_status': log.new_status,
            'change_reason': log.change_reason,
            'changes_summary': log.get_changes_summary(),
            'ip_address': log.ip_address,
            'badge_class': log.get_action_badge_class(),
            'old_values': log.old_values,
            'new_values': log.new_values,
        })

    return JsonResponse({
        'success': True,
        'transaction': {
            'id': transaction.id,
            'transaction_number': transaction.transaction_number,
            'transaction_date': transaction.transaction_date.strftime('%m/%d/%Y'),
            'amount': str(transaction.amount),
            'status': transaction.status,
            'payee': transaction.payee or '-',
        },
        'audit_logs': logs_data,
        'count': len(logs_data)
    })


@require_http_methods(["GET"])
def transaction_audit_report_xml(request, transaction_id):
    """
    Generate HTML report of transaction audit history.
    Opens in new tab and can be printed.
    """
    from django.http import HttpResponse

    if not request.user.is_authenticated:
        return HttpResponse('Unauthorized', status=401)

    try:
        transaction = BankTransaction.objects.get(id=transaction_id)
    except BankTransaction.DoesNotExist:
        return HttpResponse('Transaction not found', status=404)

    # Import here to avoid circular import
    from .models import BankTransactionAudit

    audit_logs = BankTransactionAudit.objects.filter(
        transaction=transaction
    ).order_by('action_date')

    # Build HTML report - clean and professional like case ledger
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Transaction Audit Report - {transaction.transaction_number or transaction.id}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                background: white;
                color: #000;
            }}

            .print-button {{
                position: fixed;
                top: 20px;
                right: 20px;
                background: #333;
                color: white;
                border: 1px solid #000;
                padding: 10px 20px;
                cursor: pointer;
                font-size: 14px;
            }}

            .print-button:hover {{
                background: #000;
            }}

            .header {{
                text-align: center;
                border-bottom: 2px solid #000;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}

            .header h1 {{
                font-size: 24px;
                font-weight: bold;
                margin: 0 0 10px 0;
                text-transform: uppercase;
            }}

            .header .subtitle {{
                font-size: 14px;
                color: #333;
                margin: 5px 0;
            }}

            .info-section {{
                margin-bottom: 30px;
            }}

            .info-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 10px;
            }}

            .info-table td {{
                padding: 8px;
                border: 1px solid #000;
                font-size: 14px;
            }}

            .info-table td:first-child {{
                font-weight: bold;
                background: #f0f0f0;
                width: 200px;
            }}

            h2 {{
                font-size: 18px;
                font-weight: bold;
                text-transform: uppercase;
                border-bottom: 2px solid #000;
                padding-bottom: 5px;
                margin: 30px 0 15px 0;
            }}

            .audit-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }}

            .audit-table th {{
                background: #333;
                color: white;
                padding: 10px;
                text-align: left;
                font-weight: bold;
                font-size: 13px;
                border: 1px solid #000;
            }}

            .audit-table td {{
                padding: 10px;
                border: 1px solid #ccc;
                font-size: 13px;
            }}

            .audit-table tbody tr:nth-child(even) {{
                background: #f9f9f9;
            }}

            .reason-row {{
                background: #fff9e6 !important;
                font-style: italic;
            }}

            .footer {{
                text-align: center;
                margin-top: 50px;
                padding-top: 20px;
                border-top: 2px solid #000;
                font-size: 12px;
                color: #666;
            }}

            @media print {{
                body {{
                    margin: 20px;
                }}
                .print-button {{
                    display: none;
                }}
            }}
        </style>
    </head>
    <body>
        <button class="print-button" onclick="window.print()">Print Report</button>

        <div class="header">
            <h1>Transaction Audit Report</h1>
            <div class="subtitle">Generated: {timezone.now().strftime('%m/%d/%Y %I:%M %p')}</div>
            <div class="subtitle">Prepared by: {request.user.username}</div>
        </div>

        <div class="info-section">
            <table class="info-table">
                <tr>
                    <td>Transaction Number:</td>
                    <td>{transaction.transaction_number or 'N/A'}</td>
                </tr>
                <tr>
                    <td>Transaction Date:</td>
                    <td>{transaction.transaction_date.strftime('%m/%d/%Y')}</td>
                </tr>
                <tr>
                    <td>Type:</td>
                    <td>{transaction.get_transaction_type_display()}</td>
                </tr>
                <tr>
                    <td>Amount:</td>
                    <td>${transaction.amount:,.2f}</td>
                </tr>
                <tr>
                    <td>Current Status:</td>
                    <td>{transaction.status.upper()}</td>
                </tr>
                <tr>
                    <td>Payee:</td>
                    <td>{transaction.payee or 'N/A'}</td>
                </tr>
                <tr>
                    <td>Reference:</td>
                    <td>{transaction.reference_number or 'N/A'}</td>
                </tr>
    """

    if transaction.client:
        html += f"""
                <tr>
                    <td>Client:</td>
                    <td>{transaction.client.full_name}</td>
                </tr>
        """

    if transaction.case:
        html += f"""
                <tr>
                    <td>Case:</td>
                    <td>{transaction.case.case_title}</td>
                </tr>
        """

    html += """
            </table>
        </div>

        <h2>Audit Trail</h2>
        <table class="audit-table">
            <thead>
                <tr>
                    <th>Date/Time</th>
                    <th>Action</th>
                    <th>User</th>
                    <th>Changes</th>
                    <th>Old Amount</th>
                    <th>New Amount</th>
                    <th>Old Status</th>
                    <th>New Status</th>
                    <th>IP Address</th>
                </tr>
            </thead>
            <tbody>
    """

    for log in audit_logs:
        # Format amounts - show $0.00 for zero, not dash
        old_amount_display = f'${log.old_amount:,.2f}' if log.old_amount is not None else '-'
        new_amount_display = f'${log.new_amount:,.2f}' if log.new_amount is not None else '-'

        html += f"""
                <tr>
                    <td>{log.action_date.strftime('%m/%d/%Y %I:%M %p')}</td>
                    <td>{log.get_action_display()}</td>
                    <td>{log.action_by}</td>
                    <td>{log.get_changes_summary()}</td>
                    <td>{old_amount_display}</td>
                    <td>{new_amount_display}</td>
                    <td>{log.old_status or '-'}</td>
                    <td>{log.new_status or '-'}</td>
                    <td>{log.ip_address or '-'}</td>
                </tr>
        """

        if log.change_reason:
            html += f"""
                <tr class="reason-row">
                    <td colspan="9"><strong>Reason:</strong> {log.change_reason}</td>
                </tr>
            """

    html += """
            </tbody>
        </table>

        <div class="footer">
            <p><strong>IOLTA Guard Trust Account Management System</strong></p>
            <p>Official audit report for compliance and record-keeping</p>
        </div>
    </body>
    </html>
    """

    return HttpResponse(html, content_type='text/html')
