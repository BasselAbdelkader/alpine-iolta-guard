from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db import transaction as db_transaction
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.db.models import Q
# from .models import Transaction, TransactionItem  # OLD MODELS - COMMENTED OUT
from ..bank_accounts.models import BankTransaction
from .forms import TransactionForm
from ..clients.models import Case

class IndexView(LoginRequiredMixin, ListView):
    model = BankTransaction
    template_name = 'transactions/index.html'
    context_object_name = 'transactions'
    paginate_by = 10
    
    def get_queryset(self):
        # BankTransaction is consolidated - no items to prefetch
        return BankTransaction.objects.select_related('bank_account', 'client', 'vendor', 'case').order_by('-transaction_date', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transactions = context['transactions']
        
        # Calculate running balance for each transaction
        # Get the current bank account balance
        from ..bank_accounts.models import BankAccount
        from django.db.models import Sum, Count
        
        bank_account = BankAccount.objects.first()  # Assuming single bank account
        
        if bank_account:
            # Get all transactions in chronological order to calculate running balance
            all_transactions_ordered = BankTransaction.objects.order_by('transaction_date', 'id')
            
            # Calculate running balance chronologically starting from 0
            # (opening balance transaction is now included in the transactions)
            running_balance = 0  # Start from 0 since opening balance is now a transaction
            balance_dict = {}
            
            for transaction in all_transactions_ordered:
                if transaction.transaction_type == 'DEPOSIT':
                    running_balance += transaction.amount
                else:  # WITHDRAWAL or TRANSFER
                    running_balance -= transaction.amount
                balance_dict[transaction.id] = running_balance
            
            # Now assign running balances to the current page transactions
            transactions_list = list(transactions)
            for transaction in transactions_list:
                transaction.running_balance = balance_dict.get(transaction.id, 0)
        
        # Calculate summary statistics from all transactions (not just current page)
        all_transactions = BankTransaction.objects.all()
        
        # Total deposits
        total_deposits = all_transactions.filter(transaction_type='DEPOSIT').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Total withdrawals
        total_withdrawals = all_transactions.filter(transaction_type='WITHDRAWAL').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Total transfers
        total_transfers = all_transactions.filter(transaction_type='TRANSFER').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Uncleared transactions count
        uncleared_count = all_transactions.filter(status='pending').count()
        
        # Current account balance - use the final running balance
        current_balance = running_balance if bank_account else 0
        
        context.update({
            'total_deposits': total_deposits,
            'total_withdrawals': total_withdrawals,
            'total_transfers': total_transfers,
            'uncleared_count': uncleared_count,
            'current_balance': current_balance,
        })
        
        return context

class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = BankTransaction
    template_name = 'transactions/detail.html'
    context_object_name = 'transaction'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # BankTransaction is consolidated - no separate items
        context['transaction_items'] = [self.object] if self.object else []
        return context

class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = BankTransaction
    form_class = TransactionForm
    template_name = 'transactions/form.html'
    success_url = reverse_lazy('transactions:index')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass client_id and case_id from GET/POST parameters to form
        client_id = self.request.GET.get('client_id') or self.request.POST.get('client_id')
        case_id = self.request.GET.get('case_id') or self.request.POST.get('case_id')
        
        if client_id:
            kwargs['client_id'] = client_id
        if case_id:
            kwargs['case_id'] = case_id
            
        return kwargs
    
    def get(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Get parameters from URL
            client_id = request.GET.get('client_id')
            vendor_id = request.GET.get('vendor_id') 
            case_id = request.GET.get('case_id')
            
            # Pass client_id and case_id to form
            form_kwargs = {}
            if client_id:
                form_kwargs['client_id'] = client_id
            if case_id:
                form_kwargs['case_id'] = case_id
                
            form = self.form_class(**form_kwargs)
            
            # Set payee name if vendor provided
            if vendor_id:
                try:
                    from ..vendors.models import Vendor
                    vendor = Vendor.objects.get(id=vendor_id)
                    form.fields['payee_name'].initial = vendor.vendor_name
                except Vendor.DoesNotExist:
                    pass
                
            form_html = render_to_string('transactions/modal_form.html', {
                'form': form,
                'form_title': 'Add New Transaction',
                'request': request  # Pass request to template for access to GET parameters
            }, request=request)
            return JsonResponse({'form_html': form_html})
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Add New Transaction'
        return context
    
    @db_transaction.atomic
    def form_valid(self, form):
        # Save the transaction first
        transaction = form.save()
        
        # Create the single transaction item
        client = form.cleaned_data.get('client')
        case = form.cleaned_data.get('case')
        payee_name = form.cleaned_data.get('payee_name')

        # Find or create vendor based on payee_name
        vendor = None
        if payee_name and payee_name.strip():
            from ..vendors.models import Vendor
            vendor, created = Vendor.objects.get_or_create(
                vendor_name=payee_name.strip(),
                defaults={'is_active': True}
            )
        
        # Automatically determine item_type based on transaction_type and context
        transaction_type = transaction.transaction_type
        if transaction_type == 'DEPOSIT':
            item_type = 'CLIENT_DEPOSIT'
        elif vendor:
            item_type = 'VENDOR_PAYMENT'
        else:
            item_type = 'CASE_SETTLEMENT'
        
        # Update the transaction with client/case/vendor details
        # BankTransaction is consolidated - no separate transaction items needed
        transaction.client = client
        transaction.case = case
        transaction.vendor = vendor
        transaction.item_type = item_type
        transaction.save()
        
        messages.success(self.request, 'Transaction created successfully.')
        
        # Handle AJAX requests
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Transaction created successfully.'})
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form_html = render_to_string('transactions/modal_form.html', {
                'form': form,
                'form_title': 'Add New Transaction',
                'request': self.request  # Pass request to template for access to GET/POST parameters
            }, request=self.request)
            return JsonResponse({'success': False, 'form_html': form_html})
        return super().form_invalid(form)

class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = BankTransaction
    form_class = TransactionForm
    template_name = 'transactions/form.html'
    success_url = reverse_lazy('transactions:index')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass client_id and case_id from GET/POST parameters to form
        client_id = self.request.GET.get('client_id') or self.request.POST.get('client_id')
        case_id = self.request.GET.get('case_id') or self.request.POST.get('case_id')
        
        if client_id:
            kwargs['client_id'] = client_id
        if case_id:
            kwargs['case_id'] = case_id
            
        return kwargs
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form = self.get_form()
            
            form_html = render_to_string('transactions/modal_form.html', {
                'form': form,
                'form_title': f'Edit Transaction: {self.object.transaction_number}',
                'request': request  # Pass request to template
            }, request=request)
            return JsonResponse({'form_html': form_html})
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit Transaction: {self.object.transaction_number}'
        return context
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Pre-populate the form with existing transaction data
        # BankTransaction is consolidated - use the transaction directly
        if self.object:
            form.initial['client'] = self.object.client
            form.initial['case'] = self.object.case
            form.initial['payee_name'] = self.object.vendor.vendor_name if self.object.vendor else ''

            # When client is specified, populate case dropdown with that client's cases
            if self.object.client:
                try:
                    form.fields['case'].queryset = Case.objects.filter(
                        client=self.object.client, is_active=True
                    ).order_by('-opened_date', 'case_number')
                except:
                    pass
        return form
    
    @db_transaction.atomic
    def form_valid(self, form):
        # Save the transaction
        transaction = form.save()
        
        # Update or create the single transaction item
        client = form.cleaned_data.get('client')
        case = form.cleaned_data.get('case')
        payee_name = form.cleaned_data.get('payee_name')

        # Find or create vendor based on payee_name
        vendor = None
        if payee_name and payee_name.strip():
            from ..vendors.models import Vendor
            vendor, created = Vendor.objects.get_or_create(
                vendor_name=payee_name.strip(),
                defaults={'is_active': True}
            )
        
        # Automatically determine item_type based on transaction_type and context
        transaction_type = transaction.transaction_type
        if transaction_type == 'DEPOSIT':
            item_type = 'CLIENT_DEPOSIT'
        elif vendor:
            item_type = 'VENDOR_PAYMENT'
        else:
            item_type = 'CASE_SETTLEMENT'
            
        # Update the consolidated transaction with client/case/vendor details
        # BankTransaction is consolidated - no separate items needed
        transaction.client = client
        transaction.case = case
        transaction.vendor = vendor
        transaction.item_type = item_type
        transaction.save()
        
        messages.success(self.request, 'Transaction updated successfully.')
        
        # Handle AJAX requests
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Transaction updated successfully.'})
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form_html = render_to_string('transactions/modal_form.html', {
                'form': form,
                'form_title': f'Edit Transaction: {self.object.transaction_number}',
                'request': self.request  # Pass request to template
            }, request=self.request)
            return JsonResponse({'success': False, 'form_html': form_html})
        return super().form_invalid(form)

class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = BankTransaction
    success_url = reverse_lazy('transactions:index')
    
    def delete(self, request, *args, **kwargs):
        transaction = self.get_object()
        messages.success(request, f'Transaction "{transaction.transaction_number}" deleted successfully.')
        return super().delete(request, *args, **kwargs)


@require_http_methods(["GET"])
def get_client_cases(request):
    """AJAX view to get cases for a specific client"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    client_id = request.GET.get('client_id')
    
    if client_id:
        cases = Case.objects.filter(
            client_id=client_id, 
            is_active=True
        ).order_by('-opened_date').values('id', 'case_number')
        
        cases_list = list(cases)
    else:
        cases_list = []
    
    return JsonResponse({'cases': cases_list})


# AJAX Search Endpoint for Dynamic Transaction Search

@require_http_methods(["GET"])
def ajax_search_transactions(request):
    """AJAX endpoint for dynamic transaction search"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    query = request.GET.get('q', '').strip()
    limit = min(int(request.GET.get('limit', 50)), 100)  # Max 100 results
    
    if len(query) < 2:  # Require at least 2 characters
        return JsonResponse({'transactions': [], 'count': 0})
    
    # Search transactions and related data
    # BankTransaction is consolidated - no items to prefetch
    transactions = BankTransaction.objects.select_related(
        'bank_account', 'client', 'vendor', 'case'
    ).filter(
        Q(transaction_number__icontains=query) |
        Q(reference_number__icontains=query) |
        Q(description__icontains=query) |
        Q(client__first_name__icontains=query) |
        Q(client__last_name__icontains=query) |
        Q(vendor__vendor_name__icontains=query) |
        Q(case__case_number__icontains=query)
    ).distinct().order_by('-transaction_date', '-created_at')[:limit]
    
    # Format results for JSON response
    transaction_data = []
    running_balance = 0  # This would need to be calculated properly in a real implementation
    
    for transaction in transactions:
        # Get clients and vendors for this transaction
        # BankTransaction is consolidated - get directly from transaction
        clients = []
        vendors = []
        if transaction.client and transaction.client.full_name not in clients:
            clients.append(transaction.client.full_name)
        if transaction.vendor and transaction.vendor.vendor_name not in vendors:
            vendors.append(transaction.vendor.vendor_name)
        
        # Calculate display balance (simplified - in production you'd calculate properly)
        if transaction.transaction_type == 'DEPOSIT':
            running_balance += transaction.amount
        else:
            running_balance -= transaction.amount
        
        transaction_data.append({
            'id': transaction.id,
            'transaction_date': transaction.transaction_date.strftime('%m/%d/%Y'),
            'transaction_type': transaction.transaction_type,
            'transaction_type_display': transaction.get_transaction_type_display(),
            'transaction_type_class': {
                'DEPOSIT': 'bg-success',
                'WITHDRAWAL': 'bg-danger',
                'TRANSFER': 'bg-info',
            }.get(transaction.transaction_type, 'bg-secondary'),
            'reference_number': transaction.reference_number or '',
            'description': transaction.description or 'No description provided',
            'amount': f"{transaction.amount:,.2f}",
            'amount_class': 'text-success' if transaction.transaction_type == 'DEPOSIT' else 'text-dark',
            'formatted_amount': f"+{transaction.amount:,.2f}" if transaction.transaction_type == 'DEPOSIT' else f"-{transaction.amount:,.2f}",
            'running_balance': f"{running_balance:,.2f}",
            'balance_class': 'text-success' if running_balance >= 0 else 'text-danger',
            'clients': ', '.join(clients) if clients else '-',
            'vendors': ', '.join(vendors) if vendors else '-',
            'status': transaction.status == 'cleared',
            'status_display': 'Cleared' if transaction.status == 'cleared' else 'Pending',
            'status_class': 'bg-success' if transaction.status == 'cleared' else 'bg-warning',
        })
    
    return JsonResponse({
        'transactions': transaction_data,
        'count': len(transaction_data),
        'query': query,
    })


@require_http_methods(["POST"])
def void_transaction(request, pk):
    """AJAX endpoint to void a transaction"""
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

        # Get void reason from POST data
        void_reason = request.POST.get('void_reason', '').strip()
        if not void_reason:
            return JsonResponse({
                'success': False,
                'message': 'Void reason is required.'
            })

        # Use the void_transaction method which sets status='voided'
        voided_by = request.user.username if hasattr(request.user, 'username') else 'system'
        transaction.void_transaction(voided_by=voided_by, void_reason=void_reason)
        
        return JsonResponse({
            'success': True, 
            'message': 'Transaction voided successfully.'
        })
        
    except BankTransaction.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Transaction not found.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Error voiding transaction: {str(e)}'
        })
