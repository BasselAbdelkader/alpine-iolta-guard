from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.db import transaction, models
from django.utils import timezone
from .models import Settlement, SettlementDistribution, SettlementReconciliation
from .forms import SettlementForm, SettlementDistributionForm
from apps.clients.models import Client
from apps.vendors.models import Vendor
from apps.bank_accounts.models import BankAccount


class SettlementIndexView(LoginRequiredMixin, ListView):
    model = Settlement
    template_name = 'settlements/index.html'
    context_object_name = 'settlements'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Settlement.objects.select_related('client', 'case', 'bank_account').order_by('-settlement_date')
        
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by client if provided
        client_id = self.request.GET.get('client')
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Settlement.SETTLEMENT_STATUS_CHOICES
        context['clients'] = Client.objects.filter(is_active=True)
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_client'] = self.request.GET.get('client', '')
        return context


class SettlementDetailView(LoginRequiredMixin, DetailView):
    model = Settlement
    template_name = 'settlements/detail.html'
    context_object_name = 'settlement'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['distributions'] = self.object.distributions.select_related('vendor', 'client').order_by('distribution_type')
        
        # Check if reconciliation exists
        try:
            context['reconciliation'] = self.object.reconciliation
        except SettlementReconciliation.DoesNotExist:
            context['reconciliation'] = None
        
        return context


class SettlementCreateView(LoginRequiredMixin, CreateView):
    model = Settlement
    form_class = SettlementForm
    template_name = 'settlements/form.html'
    success_url = reverse_lazy('settlements:index')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user.get_full_name() or self.request.user.username
        messages.success(self.request, 'Settlement created successfully.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Create New Settlement'
        return context


class SettlementUpdateView(LoginRequiredMixin, UpdateView):
    model = Settlement
    form_class = SettlementForm
    template_name = 'settlements/form.html'
    success_url = reverse_lazy('settlements:index')
    
    def form_valid(self, form):
        messages.success(self.request, 'Settlement updated successfully.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit Settlement: {self.object.settlement_number}'
        return context


class SettlementDistributionCreateView(LoginRequiredMixin, CreateView):
    model = SettlementDistribution
    form_class = SettlementDistributionForm
    template_name = 'settlements/distribution_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.settlement = get_object_or_404(Settlement, pk=kwargs['settlement_pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.settlement = self.settlement
        messages.success(self.request, 'Distribution added successfully.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('settlements:detail', kwargs={'pk': self.settlement.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['settlement'] = self.settlement
        context['form_title'] = f'Add Distribution to {self.settlement.settlement_number}'
        return context


class SettlementDistributionUpdateView(LoginRequiredMixin, UpdateView):
    model = SettlementDistribution
    form_class = SettlementDistributionForm
    template_name = 'settlements/distribution_form.html'
    
    def get_success_url(self):
        return reverse_lazy('settlements:detail', kwargs={'pk': self.object.settlement.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Distribution updated successfully.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['settlement'] = self.object.settlement
        context['form_title'] = f'Edit Distribution'
        return context


class SettlementReconciliationView(LoginRequiredMixin, DetailView):
    model = Settlement
    template_name = 'settlements/reconciliation.html'
    context_object_name = 'settlement'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get or create reconciliation record
        reconciliation, created = SettlementReconciliation.objects.get_or_create(
            settlement=self.object,
            defaults={
                'bank_balance_before': self.object.bank_account.get_current_balance(),
                'client_balance_before': self.object.client.get_current_balance(),
                'total_distributions': self.object.distributions.aggregate(
                    total=models.Sum('amount')
                )['total'] or 0,
            }
        )
        
        context['reconciliation'] = reconciliation
        context['distributions'] = self.object.distributions.select_related('vendor', 'client')
        
        return context
    
    def post(self, request, *args, **kwargs):
        settlement = self.get_object()
        
        try:
            with transaction.atomic():
                # Update reconciliation with current balances
                reconciliation = settlement.reconciliation
                reconciliation.bank_balance_after = settlement.bank_account.get_current_balance()
                reconciliation.client_balance_after = settlement.client.get_current_balance()
                reconciliation.reconciled_by = request.user.get_full_name() or request.user.username
                reconciliation.perform_reconciliation()
                
                # Update settlement status based on reconciliation
                if reconciliation.is_balanced:
                    settlement.status = 'COMPLETED'
                    messages.success(request, 'Settlement reconciled successfully and marked as completed.')
                else:
                    settlement.status = 'IN_PROGRESS'
                    messages.warning(request, f'Settlement reconciliation shows imbalance of ${reconciliation.balance_difference}. Please review.')
                
                settlement.save()
                
        except Exception as e:
            messages.error(request, f'Error performing reconciliation: {str(e)}')
        
        return redirect('settlements:reconciliation', pk=settlement.pk)


def settlement_balance_check(request, pk):
    """AJAX endpoint to check settlement balance"""
    settlement = get_object_or_404(Settlement, pk=pk)
    
    data = {
        'is_balanced': settlement.is_balanced,
        'total_amount': float(settlement.total_amount),
        'remaining_balance': float(settlement.remaining_balance),
        'distributions_count': settlement.distributions.count(),
    }
    
    return JsonResponse(data)


def mark_distribution_paid(request, pk):
    """AJAX endpoint to mark a distribution as paid"""
    if request.method == 'POST':
        distribution = get_object_or_404(SettlementDistribution, pk=pk)
        distribution.is_paid = True
        distribution.paid_date = timezone.now().date()
        distribution.save()
        
        messages.success(request, f'Distribution marked as paid.')
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})