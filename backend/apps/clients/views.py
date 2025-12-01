from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, render
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from trust_account_project.csrf_protection import EnhancedCSRFMixin, enhanced_csrf_protect, api_csrf_protect
from .models import Client, Case
from .forms import ClientForm, CaseForm
from ..bank_accounts.models import BankTransaction
from datetime import datetime

class IndexView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'clients/index.html'
    context_object_name = 'clients'
    
    def get_queryset(self):
        queryset = Client.objects.all().prefetch_related('cases')
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(client_name__icontains=search_query) |
                
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(client_number__icontains=search_query)
            )
        
        # Client type filter
        client_type = self.request.GET.get('client_type', '')
        if client_type:
            queryset = queryset.filter(client_type=client_type)
        
        # Balance filter with default to 'non_zero'
        balance_filter = self.request.GET.get('balance_filter', 'non_zero')
        
        if balance_filter == 'zero':
            # Filter clients with zero balance
            
            zero_balance_clients = []
            for client in queryset:
                if client.get_current_balance() == 0:
                    zero_balance_clients.append(client.id)
            queryset = queryset.filter(id__in=zero_balance_clients)
        elif balance_filter == 'non_zero':
            # Filter clients with non-zero balance (default)
            
            non_zero_balance_clients = []
            for client in queryset:
                if client.get_current_balance() != 0:
                    non_zero_balance_clients.append(client.id)
            queryset = queryset.filter(id__in=non_zero_balance_clients)
        # If balance_filter is empty string (All Balances), show all clients
        
        # Status filter with default to 'active'
        status_filter = self.request.GET.get('status_filter', 'active')
        
        if status_filter == 'active':
            # Show only active clients (default)
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'inactive':
            # Show only inactive clients
            queryset = queryset.filter(is_active=False)
        # If status_filter is 'all', show all clients regardless of active status
        
        # Sorting functionality
        sort_field = self.request.GET.get('sort', '')
        sort_direction = self.request.GET.get('direction', 'asc')
        
        if sort_field == 'name':
            if sort_direction == 'desc':
                queryset = queryset.order_by('-client_name')
            else:
                queryset = queryset.order_by('client_name')
        elif sort_field == 'balance':
            # For balance sorting, we need to convert clients to list and sort by calculated balance
            client_list = list(queryset)
            if sort_direction == 'desc':
                client_list.sort(key=lambda x: x.get_current_balance(), reverse=True)
            else:
                client_list.sort(key=lambda x: x.get_current_balance())
            # Convert back to queryset-like object by getting IDs in order
            client_ids = [client.id for client in client_list]
            # Preserve the order using CASE WHEN
            from django.db.models import Case as DjangoCase, When, IntegerField
            preserved = DjangoCase(*[When(pk=pk, then=pos) for pos, pk in enumerate(client_ids)], output_field=IntegerField())
            queryset = queryset.filter(id__in=client_ids).order_by(preserved)
        else:
            queryset = queryset.order_by('-created_at')
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Removed client_type_choices - clients don't have types in trust account system
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_client_type'] = self.request.GET.get('client_type', '')
        context['selected_balance_filter'] = self.request.GET.get('balance_filter', 'non_zero')
        context['selected_status_filter'] = self.request.GET.get('status_filter', 'active')
        
        # Calculate total trust balance across all clients
        from decimal import Decimal
        total_balance = Decimal('0.00')
        for client in self.get_queryset():
            total_balance += client.get_current_balance()
        context['total_trust_balance'] = total_balance
        
        return context

class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'clients/detail.html'
    context_object_name = 'client'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Default to showing only active cases unless filter specified
        case_filter = self.request.GET.get('case_filter', 'active')
        if case_filter == 'active':
            context['cases'] = self.object.cases.filter(is_active=True).order_by('-created_at')
        elif case_filter == 'inactive':
            context['cases'] = self.object.cases.filter(is_active=False).order_by('-created_at')
        else:  # 'all'
            context['cases'] = self.object.cases.all().order_by('-created_at')
        context['current_balance'] = self.object.get_current_balance()
        context['selected_case_filter'] = case_filter
        return context

class ClientCreateView(EnhancedCSRFMixin, LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/form.html'
    success_url = reverse_lazy('clients:index')
    
    # Enhanced security settings
    max_transaction_amount = 1000000.00
    sensitive_fields = ['email', 'phone', 'address']
    
    def get(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form = self.form_class()
            form_html = render_to_string('clients/modal_form.html', {
                'form': form,
                'form_title': 'Add New Client'
            }, request=request)
            return HttpResponse(form_html)
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form.save()
            return JsonResponse({'success': True})
        messages.success(self.request, 'Client created successfully.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form_html = render_to_string('clients/modal_form.html', {
                'form': form,
                'form_title': 'Add New Client'
            }, request=self.request)
            return JsonResponse({'success': False, 'form_html': form_html})
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Add New Client'
        return context

class ClientUpdateView(EnhancedCSRFMixin, LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/form.html'
    success_url = reverse_lazy('clients:index')
    
    # Enhanced security settings
    sensitive_fields = ['email', 'phone', 'address']
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form = self.form_class(instance=self.object)
            form_html = render_to_string('clients/modal_form.html', {
                'form': form,
                'form_title': f'Edit Client: {self.object.full_name}',
                'client_id': self.object.pk
            }, request=request)
            return JsonResponse({'form_html': form_html})
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form.save()
            return JsonResponse({'success': True})
        messages.success(self.request, 'Client updated successfully.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form_html = render_to_string('clients/modal_form.html', {
                'form': form,
                'form_title': f'Edit Client: {self.object.full_name}',
                'client_id': self.object.pk
            }, request=self.request)
            return JsonResponse({'success': False, 'form_html': form_html})
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit Client: {self.object.full_name}'
        return context

class ClientDeleteView(EnhancedCSRFMixin, LoginRequiredMixin, DeleteView):
    model = Client
    success_url = reverse_lazy('clients:index')
    
    # Enhanced security settings
    require_confirmation_delete = True
    
    def delete(self, request, *args, **kwargs):
        client = self.get_object()
        messages.success(request, f'Client "{client.full_name}" deleted successfully.')
        return super().delete(request, *args, **kwargs)

@require_http_methods(["POST"])
@login_required
@api_csrf_protect
def smart_delete_client(request, client_id):
    """
    AJAX endpoint to smart delete a client with these rules:
    1. If Balance > 0: Cannot Delete, Cannot be Inactive (ERROR)
    2. If Balance == 0 but has transactions: Cannot Delete, Can be Inactive (mark inactive)
    3. If Balance == 0 AND No transactions: Can Delete (permanent delete)
    """
    try:
        client = get_object_or_404(Client, id=client_id)

        # Check if client has any records (transactions, cases, etc.)
        has_transactions = client.bank_transactions.exists()
        has_cases = client.cases.exists()
        current_balance = client.get_current_balance()

        client_name = client.full_name

        # RULE 1: If balance > 0, REJECT - cannot delete or mark inactive
        if current_balance > 0:
            return JsonResponse({
                'success': False,
                'message': f'Cannot delete or deactivate client "{client_name}" with a balance of ${current_balance:,.2f}. Please zero out the balance first.'
            }, status=400)

        # RULE 2: If balance == 0 but has transactions/cases, mark as INACTIVE
        elif has_transactions or has_cases:
            client.is_active = False
            client.trust_account_status = 'CLOSED'
            client.save()

            return JsonResponse({
                'success': True,
                'action': 'deactivated',
                'message': f'Client "{client_name}" has been marked as inactive (balance: $0, has transaction history).',
                'client_id': client_id
            })

        # RULE 3: If balance == 0 AND no transactions/cases, PERMANENTLY DELETE
        else:
            client.delete()

            return JsonResponse({
                'success': True,
                'action': 'deleted',
                'message': f'Client "{client_name}" has been permanently deleted (no transaction history).',
                'client_id': client_id
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error processing delete request: {str(e)}'
        }, status=500)


# Case Views
class CaseIndexView(LoginRequiredMixin, ListView):
    model = Case
    template_name = 'clients/cases/index.html'
    context_object_name = 'cases'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Case.objects.select_related('client').order_by('-created_at')
        
        # Filter by search query
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(case_number__icontains=search) |
                Q(client__client_name__icontains=search)
            )
        
        # Filter by client
        client_id = self.request.GET.get('client')
        if client_id:
            queryset = queryset.filter(client_id=client_id)
            
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(case_status=status)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clients'] = Client.objects.filter(is_active=True).order_by('client_name')
        context['status_choices'] = Case.CASE_STATUS_CHOICES
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_client'] = self.request.GET.get('client', '')
        context['selected_status'] = self.request.GET.get('status', '')
        return context


class CaseDetailView(LoginRequiredMixin, DetailView):
    model = Case
    template_name = 'clients/cases/detail.html'
    context_object_name = 'case'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get related transactions and settlements for this case
        
        from ..settlements.models import Settlement
        
        # Get transactions for this specific case from consolidated table (including voided for audit trail)
        from ..bank_accounts.models import BankTransaction
        transactions = BankTransaction.objects.filter(
            case=self.object
        ).select_related('bank_account', 'client', 'vendor').order_by('-transaction_date', '-created_at')
        
        # Build transaction register for this case
        transaction_register = []
        running_balance = 0
        
        # Process transactions in chronological order for balance calculation
        all_transactions = list(transactions.order_by('transaction_date', 'id'))

        for transaction in all_transactions:
            # Determine transaction type and display
            if transaction.transaction_type == 'DEPOSIT':
                entry_type = 'Deposit'
                amount_display = f'+{transaction.amount:,.2f}'
                amount_class = 'text-success'
                display_amount = transaction.amount
                # Only include non-voided transactions in balance calculation
                if transaction.status != 'voided':
                    running_balance += transaction.amount
            else:  # WITHDRAWAL or TRANSFER
                entry_type = 'Withdrawal'
                amount_display = f'-{transaction.amount:,.2f}'
                amount_class = 'text-danger'
                display_amount = transaction.amount
                # Only include non-voided transactions in balance calculation
                if transaction.status != 'voided':
                    running_balance -= transaction.amount

            # Determine payee - use payee field or vendor name
            if transaction.payee:
                payee = transaction.payee
            elif transaction.vendor:
                payee = transaction.vendor.vendor_name
            else:
                payee = "-"

            # Determine client
            client_name = transaction.client.client_name if transaction.client else "-"

            transaction_register.append({
                'id': transaction.id,  # Add transaction ID for JavaScript functions
                'date': transaction.transaction_date,
                'type': entry_type,
                'amount': display_amount,
                'amount_display': amount_display,
                'amount_class': amount_class,
                'balance': running_balance,
                'description': transaction.description,
                'reference': transaction.reference_number,
                'payee': payee,
                'client': client_name,
                'status': transaction.status,  # Use status field directly
                'void_reason': transaction.void_reason,
                'voided_date': transaction.voided_date,
                'voided_by': transaction.voided_by,
                'transaction': transaction,
                'case': transaction.case
            })
        
        # Keep chronological order (oldest first)
        context['transaction_register'] = transaction_register
        context['case_balance'] = running_balance
        context['transactions'] = transactions
        context['transaction_items'] = transactions  # For template compatibility
        
        context['settlements'] = Settlement.objects.filter(
            case=self.object
        ).order_by('-settlement_date')
        
        return context


class CaseCreateView(EnhancedCSRFMixin, LoginRequiredMixin, CreateView):
    model = Case
    form_class = CaseForm
    template_name = 'clients/cases/form.html'
    
    # Enhanced security settings
    max_transaction_amount = 10000000.00  # Higher limit for case amounts
    sensitive_fields = ['case_amount', 'case_description']
    
    def get_success_url(self):
        return reverse_lazy('clients:case_detail', kwargs={'pk': self.object.pk})
    
    def get_initial(self):
        initial = super().get_initial()
        client_id = self.kwargs.get('client_id') or self.request.GET.get('client_id')
        if client_id:
            try:
                client = Client.objects.get(id=client_id, is_active=True)
                initial['client'] = client
            except Client.DoesNotExist:
                pass
        return initial
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        client_id = self.kwargs.get('client_id') or self.request.GET.get('client_id')
        if client_id:
            try:
                # Restrict client field to only show the current client
                form.fields['client'].queryset = Client.objects.filter(id=client_id, is_active=True)
            except:
                pass
        return form
    
    def get(self, request, *args, **kwargs):
        client_id = kwargs.get('client_id') or request.GET.get('client_id')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Use get_form to get the properly configured form
            form = self.get_form()
            
            form_html = render_to_string('clients/cases/modal_form.html', {
                'form': form,
                'form_title': 'Create New Case',
                'client_id': client_id
            }, request=request)
            return JsonResponse({'form_html': form_html})
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                case = form.save()
                return JsonResponse({
                    'success': True, 
                    'message': f'Case "{case.case_number}" created successfully!',
                    'case_id': case.id,
                    'case_number': case.case_number
                })
            except Exception as e:
                return JsonResponse({
                    'success': False, 
                    'message': f'Error creating case: {str(e)}'
                })
        messages.success(self.request, 'Case created successfully.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            client_id = self.kwargs.get('client_id') or self.request.GET.get('client_id')
            form_html = render_to_string('clients/cases/modal_form.html', {
                'form': form,
                'form_title': 'Create New Case',
                'client_id': client_id
            }, request=self.request)
            return JsonResponse({'success': False, 'form_html': form_html})
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Create New Case'
        
        # If client_id is provided in URL, pre-select the client
        client_id = self.request.GET.get('client_id')
        if client_id:
            try:
                client = Client.objects.get(id=client_id, is_active=True)
                context['form'].fields['client'].initial = client
                context['pre_selected_client'] = client
            except Client.DoesNotExist:
                pass
                
        return context


class CaseUpdateView(EnhancedCSRFMixin, LoginRequiredMixin, UpdateView):
    model = Case
    form_class = CaseForm
    template_name = 'clients/cases/form.html'
    
    # Enhanced security settings
    max_transaction_amount = 10000000.00  # Higher limit for case amounts
    sensitive_fields = ['case_amount', 'case_description']
    
    def get_success_url(self):
        return reverse_lazy('clients:case_detail', kwargs={'pk': self.object.pk})
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form = self.form_class(instance=self.object)
            form_html = render_to_string('clients/cases/modal_form.html', {
                'form': form,
                'form_title': f'Edit Case: {self.object.case_number}',
                'case_id': self.object.pk
            }, request=request)
            return JsonResponse({'form_html': form_html})
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                case = form.save()
                return JsonResponse({
                    'success': True, 
                    'message': f'Case "{case.case_number}" updated successfully!',
                    'case_id': case.id,
                    'case_number': case.case_number
                })
            except Exception as e:
                return JsonResponse({
                    'success': False, 
                    'message': f'Error updating case: {str(e)}'
                })
        messages.success(self.request, 'Case updated successfully.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form_html = render_to_string('clients/cases/modal_form.html', {
                'form': form,
                'form_title': f'Edit Case: {self.object.case_number}',
                'case_id': self.object.pk
            }, request=self.request)
            return JsonResponse({'success': False, 'form_html': form_html})
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit Case: {self.object.case_number}'
        return context


class CaseDeleteView(EnhancedCSRFMixin, LoginRequiredMixin, DeleteView):
    model = Case
    
    # Enhanced security settings
    require_confirmation_delete = True
    
    def get_success_url(self):
        return reverse_lazy('clients:detail', kwargs={'pk': self.object.client.pk})
    
    def delete(self, request, *args, **kwargs):
        case = self.get_object()
        client = case.client
        messages.success(request, f'Case "{case.case_number}" deleted successfully.')
        return super().delete(request, *args, **kwargs)


# AJAX Search Endpoints for Dynamic Search Implementation
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@require_http_methods(["GET"])
@ensure_csrf_cookie
def ajax_search_clients(request):
    """AJAX endpoint for dynamic client search"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    query = request.GET.get('q', '').strip()
    limit = min(int(request.GET.get('limit', 50)), 100)  # Max 100 results
    
    if len(query) < 2:  # Require at least 2 characters
        return JsonResponse({'clients': [], 'count': 0})
    
    # Search clients
    clients = Client.objects.filter(
        Q(client_name__icontains=query) |
        
        Q(email__icontains=query) |
        Q(phone__icontains=query) |
        Q(client_number__icontains=query)
    ).select_related()[:limit]
    
    # Format results for JSON response
    client_data = []
    for client in clients:
        # Calculate current balance dynamically
        
        balance = client.get_current_balance()
        
        client_data.append({
            'id': client.id,
            'full_name': client.full_name,
            'email': client.email or '',
            'phone': client.phone or '',
            'address': client.address or '',
            'city': client.city or '',
            'state': client.state or '',
            'current_balance': f"{balance:,.2f}",
            'balance_class': 'text-success' if balance >= 0 else 'text-danger',
            'is_active': client.is_active,
            'created_at': client.created_at.strftime('%m/%d/%Y'),
        })
    
    return JsonResponse({
        'clients': client_data,
        'count': len(client_data),
        'query': query,
    })


@require_http_methods(["GET"])
def ajax_search_cases(request):
    """AJAX endpoint for dynamic case search"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    query = request.GET.get('q', '').strip()
    client_filter = request.GET.get('client', '')
    status_filter = request.GET.get('status', '')
    limit = min(int(request.GET.get('limit', 50)), 100)  # Max 100 results
    
    if len(query) < 2 and not client_filter and not status_filter:
        return JsonResponse({'cases': [], 'count': 0})
    
    # Build queryset
    cases = Case.objects.select_related('client')
    
    if query and len(query) >= 2:
        cases = cases.filter(
            Q(case_number__icontains=query) |
            Q(client__client_name__icontains=query)
        )
    
    if client_filter:
        cases = cases.filter(client_id=client_filter)
    
    if status_filter:
        cases = cases.filter(case_status=status_filter)
    
    cases = cases.order_by('-created_at')[:limit]
    
    # Format results for JSON response
    case_data = []
    for case in cases:
        case_data.append({
            'id': case.id,
            'case_number': case.case_number or '',
            'case_title': case.case_title or '',
            'client_name': case.client.full_name,
            'client_id': case.client.id,
            'case_amount': f"{case.case_amount:,.2f}" if case.case_amount else "0.00",
            'case_status': case.case_status,
            'case_status_display': case.get_case_status_display(),
            'opened_date': case.opened_date.strftime('%M %d, %Y') if case.opened_date else '',
            'status_class': {
                'Open': 'bg-primary',
                'Pending Settlement': 'bg-warning',
                'Settled': 'bg-success',
                'Closed': 'bg-secondary',
            }.get(case.case_status, 'bg-dark'),
        })
    
    return JsonResponse({
        'cases': case_data,
        'count': len(case_data),
        'query': query,
    })


@require_http_methods(["GET"])
def case_transactions(request, case_id):
    """AJAX endpoint to get transactions for a specific case"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        case = Case.objects.get(id=case_id, is_active=True)
    except Case.DoesNotExist:
        return JsonResponse({'error': 'Case not found'}, status=404)
    
    # Get transactions for this case (INCLUDING VOIDED for audit trail)
    transaction_items = BankTransaction.objects.filter(
        case=case
    ).select_related('client', 'vendor').order_by('transaction_date', 'id')

    # Build transaction data with running balance
    transactions = []
    running_balance = 0

    for item in transaction_items:
        if item.transaction_type == 'DEPOSIT':
            # Only include non-voided transactions in balance
            if item.status != 'voided':
                running_balance += item.amount
            transaction_type = 'Deposit'
            amount_display = f'{item.amount:,.2f}'
            amount_class = 'text-success'
            type_class = 'bg-success'
        else:  # WITHDRAWAL or TRANSFER
            # Only include non-voided transactions in balance
            if item.status != 'voided':
                running_balance -= item.amount
            transaction_type = 'Withdrawal'
            amount_display = f'({item.amount:,.2f})'
            amount_class = 'text-danger'
            type_class = 'bg-danger'

        # Format balance
        if running_balance < 0:
            balance_display = f"({abs(running_balance):,.2f})"
        else:
            balance_display = f"{running_balance:,.2f}"

        # Determine payee - use payee field or vendor name
        if item.payee:
            payee = item.payee
        elif item.vendor:
            payee = item.vendor.vendor_name
        else:
            payee = "-"

        # Status badge
        if item.status == 'pending':
            status_display = 'Pending'
            status_class = 'bg-warning text-dark'
        elif item.status == 'cleared':
            status_display = 'Cleared'
            status_class = 'bg-success'
        elif item.status == 'voided':
            status_display = 'Voided'
            status_class = 'bg-danger'
        else:
            status_display = item.get_status_display()
            status_class = 'bg-secondary'

        transactions.append({
            'date': item.transaction_date.strftime('%m/%d/%Y'),
            'type': transaction_type,
            'type_class': type_class,
            'payee': payee,
            'description': item.description or '-',
            'amount_display': amount_display,
            'amount_class': amount_class,
            'balance_display': balance_display,
            'balance': running_balance,
            'status': status_display,
            'status_class': status_class
        })
    
    return JsonResponse({
        'transactions': transactions,
        'count': len(transactions),
        'case_balance': balance_display if transactions else '0.00'
    })


@require_http_methods(["GET"])
def ajax_cases_for_client(request):
    """AJAX endpoint to get cases for a specific client"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    client_id = request.GET.get('client_id')
    if not client_id:
        return JsonResponse({'error': 'Client ID required'}, status=400)
    
    try:
        # Verify client exists
        client = Client.objects.get(id=client_id, is_active=True)
    except Client.DoesNotExist:
        return JsonResponse({'error': 'Client not found'}, status=404)
    
    # Get active cases for this client
    cases = Case.objects.filter(
        client_id=client_id,
        is_active=True
    ).order_by('-opened_date')
    
    # Format results for JSON response
    case_data = []
    for case in cases:
        case_data.append({
            'id': case.id,
            'case_number': case.case_number or '',
            'case_title': case.case_title or '',
            'case_status': case.case_status,
            'case_status_display': case.get_case_status_display(),
        })
    
    return JsonResponse({
        'cases': case_data,
        'count': len(case_data),
        'client_id': client_id,
        'client_name': client.full_name
    })


@require_http_methods(["POST"])
def case_deactivate(request, case_id):
    """AJAX endpoint to deactivate a case (make inactive)"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        case = Case.objects.get(id=case_id)
    except Case.DoesNotExist:
        return JsonResponse({'error': 'Case not found'}, status=404)
    
    # Make case inactive
    case.is_active = False
    case.save()
    
    return JsonResponse({
        'success': True,
        'message': f'Case "{case.case_title}" has been made inactive'
    })


@require_http_methods(["POST"])
def case_delete_permanent(request, case_id):
    """AJAX endpoint to permanently delete a case"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        case = Case.objects.get(id=case_id)
    except Case.DoesNotExist:
        return JsonResponse({'error': 'Case not found'}, status=404)
    
    # Check if case has transactions/balance
    current_balance = case.get_current_balance()
    if abs(current_balance) > 0.01:
        return JsonResponse({
            'success': False,
            'message': f'Cannot delete case with balance of ${abs(current_balance):,.2f}. Use deactivate instead.'
        })
    
    case_title = case.case_title
    client_id = case.client.pk
    case.delete()
    
    return JsonResponse({
        'success': True,
        'message': f'Case "{case_title}" has been permanently deleted'
    })


@login_required
def print_clients_report(request):
    """Generate printable PDF report of clients with non-zero balances"""

    # Get clients with non-zero balances
    clients_with_balances = []
    total_balance = 0

    for client in Client.objects.filter(is_active=True).order_by('client_name'):
        balance = client.get_current_balance()
        if balance != 0:  # Only include clients with non-zero balances
            # Get all cases for this client with their balances
            cases = []
            for case in Case.objects.filter(client=client, is_active=True):
                case_balance = case.get_current_balance()
                cases.append({
                    'case_number': case.case_number,
                    'case_title': case.case_title,
                    'balance': case_balance
                })

            clients_with_balances.append({
                'client': client,
                'balance': balance,
                'cases': cases
            })
            total_balance += balance

    # Get law firm information for header
    from ..settings.models import LawFirm
    law_firm = LawFirm.get_active_firm()

    context = {
        'clients_with_balances': clients_with_balances,
        'total_balance': total_balance,
        'law_firm': law_firm,
        'report_date': datetime.now().strftime('%B %d, %Y'),
        'report_time': datetime.now().strftime('%I:%M %p'),
        'client_count': len(clients_with_balances),
        'report_title': 'Client Trust Account Balances - Non-Zero Balances Only'
    }

    # Check if WeasyPrint is available for PDF generation
    try:
        from weasyprint import HTML
        # Generate PDF
        template = get_template('clients/print_clients_report.html')
        html_string = template.render(context)

        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf_file = html.write_pdf()

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="clients_balances_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        return response

    except ImportError:
        # Fallback to HTML if WeasyPrint is not available
        return render(request, 'clients/print_clients_report.html', context)


def print_clients_with_cases(request):
    """Generate printable PDF report of clients with their cases and balances in professional table format"""

    # Get clients with non-zero balances
    clients_with_balances = []
    total_balance = 0

    for client in Client.objects.filter(is_active=True).order_by('client_name'):
        balance = client.get_current_balance()
        if balance != 0:  # Only include clients with non-zero balances
            # Get all cases for this client with their balances
            cases = []
            for case in Case.objects.filter(client=client, is_active=True):
                case_balance = case.get_current_balance()
                cases.append({
                    'case_number': case.case_number,
                    'case_title': case.case_title,
                    'balance': case_balance
                })

            clients_with_balances.append({
                'client': client,
                'balance': balance,
                'cases': cases
            })
            total_balance += balance

    # Get law firm information for header
    from ..settings.models import LawFirm
    law_firm = LawFirm.get_active_firm()

    context = {
        'clients_with_balances': clients_with_balances,
        'total_balance': total_balance,
        'law_firm': law_firm,
        'report_date': datetime.now().strftime('%B %d, %Y'),
        'report_time': datetime.now().strftime('%I:%M %p'),
        'client_count': len(clients_with_balances),
        'report_title': 'Client Trust Balances - With Cases'
    }

    # Check if WeasyPrint is available for PDF generation
    try:
        from weasyprint import HTML
        # Generate PDF
        template = get_template('clients/print_clients_with_cases.html')
        html_string = template.render(context)

        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf_file = html.write_pdf()

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="clients_with_cases_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        return response

    except ImportError as e:
        import sys
        print(f"[CLIENTS PDF] WeasyPrint ImportError: {e}", file=sys.stderr, flush=True)
        # Fallback to HTML if WeasyPrint is not available
        return render(request, 'clients/print_clients_with_cases.html', context)
    except Exception as e:
        import sys
        print(f"[CLIENTS PDF] Error generating PDF: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc()
        # Fallback to HTML on any error
        return render(request, 'clients/print_clients_with_cases.html', context)


def print_case_ledger_by_query(request):
    """Wrapper view that accepts case_id as query parameter"""
    case_id = request.GET.get('case_id')
    if not case_id:
        return HttpResponse("Missing case_id parameter", status=400)
    return print_case_ledger(request, int(case_id))

def print_case_ledger(request, case_id):
    """Generate printable PDF report of case ledger transactions"""

    # Get the case
    case = get_object_or_404(Case, id=case_id)
    
    # Get transactions for this specific case from consolidated table
    transactions = BankTransaction.objects.filter(
        case=case
    ).select_related('bank_account', 'client', 'vendor').order_by('-transaction_date', '-created_at')
    
    # Build transaction register for this case
    transaction_register = []
    running_balance = 0
    
    # Process transactions in chronological order for balance calculation
    all_transactions = list(transactions.order_by('transaction_date', 'id'))
    
    for transaction in all_transactions:
        if transaction.status == 'voided':
            # Voided transactions appear in ledger but don't affect balance
            entry_type = f'VOIDED - {transaction.transaction_type.title()}'
            amount_display = f'(VOID) {transaction.amount:,.2f}'
            amount_class = 'text-muted'
            display_amount = transaction.amount
        elif transaction.transaction_type == 'DEPOSIT':
            running_balance += transaction.amount
            entry_type = 'Deposit'
            amount_display = f'+{transaction.amount:,.2f}'
            amount_class = 'text-success'
            display_amount = transaction.amount
        else:  # WITHDRAWAL or TRANSFER
            running_balance -= transaction.amount
            entry_type = 'Withdrawal'
            amount_display = f'-{transaction.amount:,.2f}'
            amount_class = 'text-danger'
            display_amount = transaction.amount

        # Determine payee - use payee field or vendor name
        if transaction.payee:
            payee = transaction.payee
        elif transaction.vendor:
            payee = transaction.vendor.vendor_name
        else:
            payee = "-"

        transaction_register.append({
            'date': transaction.transaction_date,
            'type': entry_type,
            'amount': display_amount,
            'amount_display': amount_display,
            'amount_class': amount_class,
            'balance': running_balance,
            'description': transaction.description,
            'reference': transaction.reference_number,
            'payee': payee,
            'status': transaction.status,  # Use status field directly
            'void_reason': transaction.void_reason,
            'voided_date': transaction.voided_date,
            'voided_by': transaction.voided_by,
            'transaction': transaction,
            'check_memo': transaction.check_memo,
        })
    
    # Keep chronological order (oldest first) for display
    
    # Get law firm information for header
    from ..settings.models import LawFirm
    law_firm = LawFirm.get_active_firm()
    
    context = {
        'case': case,
        'transaction_register': transaction_register,
        'case_balance': running_balance,
        'law_firm': law_firm,
        'report_date': datetime.now().strftime('%B %d, %Y'),
        'report_time': datetime.now().strftime('%I:%M %p'),
        'transaction_count': len(transaction_register),
        'report_title': f'Case Ledger Report - {case.case_title or case.case_number}'
    }

    # Check if WeasyPrint is available for PDF generation
    try:
        from weasyprint import HTML
        # Generate PDF
        template = get_template('clients/print_case_ledger.html')
        html_string = template.render(context)

        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf_file = html.write_pdf()

        case_identifier = case.case_number or f"case_{case.id}"
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="case_ledger_{case_identifier}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        return response

    except ImportError as e:
        import sys
        print(f"[CASE LEDGER PDF] WeasyPrint ImportError: {e}", file=sys.stderr, flush=True)
        # Fallback to HTML if WeasyPrint is not available
        return render(request, 'clients/print_case_ledger.html', context)
    except Exception as e:
        import sys
        print(f"[CASE LEDGER PDF] Error generating PDF: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc()
        # Fallback to HTML on any error
        return render(request, 'clients/print_case_ledger.html', context)


@require_http_methods(["GET"])
def case_balance_api(request, case_id):
    """AJAX endpoint to get current balance for a specific case"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        case = Case.objects.get(id=case_id, is_active=True)
    except Case.DoesNotExist:
        return JsonResponse({'error': 'Case not found'}, status=404)

    # Get current balance for the case
    balance = case.get_current_balance()

    # If balance is negative, show as zero for available funds
    available_balance = max(balance, 0)

    return JsonResponse({
        'balance': float(available_balance),
        'raw_balance': float(balance),
        'case_id': case_id,
        'case_number': case.case_number or ''
    })


@require_http_methods(["GET"])
def ajax_client_balance(request):
    """AJAX endpoint to get current balance for a specific client"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    client_id = request.GET.get('client_id')
    if not client_id:
        return JsonResponse({'error': 'Client ID required'}, status=400)

    try:
        client = Client.objects.get(id=client_id, is_active=True)
    except Client.DoesNotExist:
        return JsonResponse({'error': 'Client not found'}, status=404)

    # Get current balance for the client
    balance = client.get_current_balance()

    # If balance is negative, show as zero for available funds
    available_balance = max(balance, 0)

    return JsonResponse({
        'balance': float(available_balance),
        'raw_balance': float(balance),
        'client_id': client_id,
        'client_name': client.full_name
    })
