from django.views.generic import TemplateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.template.loader import render_to_string
from weasyprint import HTML
from apps.bank_accounts.models import BankTransaction
from apps.settings.models import LawFirm


class CheckPrintQueueView(LoginRequiredMixin, TemplateView):
    """View for displaying check printing queue"""
    template_name = 'checks/print_queue.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Base queryset - all checks ready to print
        # Include: reference="TO PRINT", reference_number="TO PRINT", or has an actual check number
        from django.db.models import Q
        ready_to_print = BankTransaction.objects.filter(
            transaction_type='WITHDRAWAL',
            check_is_printed=False
        ).filter(
            Q(reference_number='TO PRINT') |  # Reference is "TO PRINT"
            Q(reference_number='TO PRINT') |      # Check number is "TO PRINT"
            Q(reference_number__isnull=True) |    # No check number yet
            Q(reference_number='') |              # Empty check number
            (Q(reference_number__isnull=False) & ~Q(reference_number=''))  # Has actual check number
        ).exclude(status='voided').select_related(
            'client', 'vendor', 'case', 'bank_account'
        )

        # Apply search filters
        reference_number = self.request.GET.get('reference_number', '').strip()
        payee = self.request.GET.get('payee', '').strip()
        from_date = self.request.GET.get('from_date', '').strip()
        to_date = self.request.GET.get('to_date', '').strip()

        if reference_number:
            ready_to_print = ready_to_print.filter(reference_number__icontains=reference_number)

        if payee:
            from django.db.models import Q
            ready_to_print = ready_to_print.filter(
                Q(payee__icontains=payee) |
                Q(vendor__vendor_name__icontains=payee) |
                Q(client__first_name__icontains=payee) |
                Q(client__last_name__icontains=payee)
            )

        if from_date:
            ready_to_print = ready_to_print.filter(transaction_date__gte=from_date)

        if to_date:
            ready_to_print = ready_to_print.filter(transaction_date__lte=to_date)

        # Order by date and check number
        ready_to_print = ready_to_print.order_by('transaction_date', 'reference_number')

        context['ready_to_print'] = ready_to_print
        context['ready_count'] = ready_to_print.count()
        context['total_amount'] = sum(c.amount for c in ready_to_print)

        return context


class CheckPreviewView(LoginRequiredMixin, DetailView):
    """View for previewing a single check"""
    model = BankTransaction
    template_name = 'checks/check_preview.html'
    slug_field = 'transaction_number'
    slug_url_kwarg = 'transaction_number'
    context_object_name = 'check'

    def get_queryset(self):
        return BankTransaction.objects.filter(
            transaction_type='WITHDRAWAL',
            reference_number__isnull=False
        ).exclude(reference_number='')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['law_firm'] = LawFirm.get_active_firm()
        return context


class PrintCheckView(LoginRequiredMixin, View):
    """Generate PDF for single check"""
    def get(self, request, transaction_number):
        check = BankTransaction.objects.get(transaction_number=transaction_number)

        # Assign check number if not already assigned (for "TO PRINT" checks)
        if not check.reference_number or check.reference_number == 'TO PRINT':
            check.reference_number = check.bank_account.get_next_reference_number()
            check.save(update_fields=['reference_number'])

        # Render check template to HTML
        html_string = render_to_string('checks/check_print_layout.html', {
            'check': check,
            'law_firm': LawFirm.get_active_firm(),
        })

        # Convert to PDF
        pdf = HTML(string=html_string).write_pdf()

        # Return PDF response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="check_{check.reference_number}.pdf"'

        return response


class MarkAsPrintedView(LoginRequiredMixin, View):
    """Mark selected checks as printed"""
    def post(self, request):
        check_ids = request.POST.getlist('check_ids')

        updated = BankTransaction.objects.filter(
            id__in=check_ids,
            check_is_printed=False
        ).update(check_is_printed=True)

        messages.success(request, f'{updated} check(s) marked as printed')
        return redirect('checks:print_queue')


class BatchPrintView(LoginRequiredMixin, View):
    """Generate PDF for multiple checks"""

    def get(self, request):
        """Handle GET request with check_ids query parameter"""
        # Get check_ids from query parameter (comma-separated)
        check_ids_param = request.GET.get('check_ids', '')
        if check_ids_param:
            check_ids = [id.strip() for id in check_ids_param.split(',') if id.strip()]
        else:
            check_ids = []

        return self._generate_pdf(check_ids)

    def post(self, request):
        """Handle POST request with check_ids array"""
        check_ids = request.POST.getlist('check_ids')
        return self._generate_pdf(check_ids)

    def _generate_pdf(self, check_ids):
        """Generate PDF for the given check IDs"""
        if not check_ids:
            return HttpResponse("No checks specified", status=400)

        checks = BankTransaction.objects.filter(id__in=check_ids).select_related(
            'client', 'vendor', 'case', 'bank_account'
        ).order_by('reference_number')

        if not checks.exists():
            return HttpResponse("No checks found with the provided IDs", status=404)

        # Assign check numbers to any checks that don't have them yet (for "TO PRINT" checks)
        for check in checks:
            if not check.reference_number or check.reference_number == 'TO PRINT':
                check.reference_number = check.bank_account.get_next_reference_number()
                check.save(update_fields=['reference_number'])

        # Render all checks to single PDF
        html_string = render_to_string('checks/batch_print_layout.html', {
            'checks': checks,
            'law_firm': LawFirm.get_active_firm(),
        })

        pdf = HTML(string=html_string).write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="checks_batch.pdf"'

        return response


class UnmarkAsPrintedView(LoginRequiredMixin, View):
    """Unmark a check as printed (move it back to ready to print)"""
    def post(self, request):
        check_id = request.POST.get('check_id')

        if check_id:
            updated = BankTransaction.objects.filter(
                id=check_id,
                check_is_printed=True
            ).update(check_is_printed=False)

            if updated:
                messages.success(request, 'Check unmarked and moved to ready to print queue')
            else:
                messages.warning(request, 'Check not found or already in print queue')
        else:
            messages.error(request, 'No check selected')

        return redirect('checks:print_queue')
