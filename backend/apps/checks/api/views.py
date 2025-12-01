from rest_framework.permissions import AllowAny
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from apps.bank_accounts.models import BankTransaction
from .serializers import CheckSerializer


class CheckViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for check printing queue"""

    serializer_class = CheckSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['reference_number', 'payee', 'client__first_name', 'client__last_name']
    ordering = ['-transaction_date', '-id']

    def get_queryset(self):
        """Get all checks that need to be printed (no check number assigned yet)"""
        from django.db.models import Q
        queryset = BankTransaction.objects.filter(
            transaction_type='WITHDRAWAL',
            status='pending',
            reference_number='TO PRINT'
        ).exclude(
            status='voided'
        ).select_related('client', 'case', 'vendor', 'bank_account')

        # Apply filters
        reference_number = self.request.query_params.get('reference_number')
        payee = self.request.query_params.get('payee')
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')

        if reference_number:
            queryset = queryset.filter(reference_number__icontains=reference_number)
        if payee:
            queryset = queryset.filter(
                Q(payee__icontains=payee) |
                Q(vendor__vendor_name__icontains=payee) |
                Q(client__first_name__icontains=payee) |
                Q(client__last_name__icontains=payee)
            )
        if from_date:
            queryset = queryset.filter(transaction_date__gte=from_date)
        if to_date:
            queryset = queryset.filter(transaction_date__lte=to_date)

        return queryset

    def list(self, request, *args, **kwargs):
        """List all checks with count"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'checks': serializer.data,
            'count': queryset.count()
        })

    @action(detail=False, methods=['GET'], url_path='print-queue')
    def print_queue(self, request):
        """Alias for list - get all checks to print"""
        return self.list(request)

    @action(detail=False, methods=['GET'], url_path='print-batch-pdf')
    def print_batch_pdf(self, request):
        """Generate PDF for batch printing checks"""
        import sys
        import traceback
        from django.http import HttpResponse
        from django.template.loader import render_to_string
        from weasyprint import HTML
        from apps.settings.models import LawFirm

        try:
            # Get check_ids from query parameter (comma-separated)
            check_ids_param = request.query_params.get('check_ids', '')
            if check_ids_param:
                check_ids = [id.strip() for id in check_ids_param.split(',') if id.strip()]
            else:
                return HttpResponse("No checks specified", status=400)

            print(f"[PDF GENERATE] Received check_ids: {check_ids}", file=sys.stderr, flush=True)

            checks = BankTransaction.objects.filter(id__in=check_ids).select_related(
                'client', 'vendor', 'case', 'bank_account'
            ).order_by('id')

            print(f"[PDF GENERATE] Found {checks.count()} checks with reference_numbers: {list(checks.values_list('reference_number', 'id'))}", file=sys.stderr, flush=True)

            if not checks.exists():
                return HttpResponse("No checks found with the provided IDs", status=404)

            # Render all checks to single PDF
            print(f"[PDF GENERATE] Rendering template...", file=sys.stderr, flush=True)
            html_string = render_to_string('checks/batch_print_layout.html', {
                'checks': checks,
                'law_firm': LawFirm.get_active_firm(),
            })
            print(f"[PDF GENERATE] Template rendered, HTML length: {len(html_string)}", file=sys.stderr, flush=True)

            print(f"[PDF GENERATE] Generating PDF...", file=sys.stderr, flush=True)
            pdf = HTML(string=html_string).write_pdf()
            print(f"[PDF GENERATE] PDF generated, size: {len(pdf)} bytes", file=sys.stderr, flush=True)

            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="checks_batch.pdf"'

            return response

        except Exception as e:
            print(f"[PDF GENERATE ERROR] {type(e).__name__}: {str(e)}", file=sys.stderr, flush=True)
            traceback.print_exc(file=sys.stderr)
            return HttpResponse(f"Error generating PDF: {str(e)}", status=500)

    @action(detail=False, methods=['GET'], url_path='next-check-number')
    def next_check_number(self, request):
        """Get the next available check number - uses same logic as get_next_numbers()"""
        from apps.settings.models import CheckSequence
        from apps.bank_accounts.models import BankAccount

        # Get the primary trust account (or first bank account)
        bank_account = BankAccount.objects.filter(account_type='Trust Account').first()
        if not bank_account:
            bank_account = BankAccount.objects.first()

        if not bank_account:
            return Response({'error': 'No bank account found'}, status=404)

        # Get or create the check sequence
        sequence, created = CheckSequence.objects.get_or_create(
            bank_account=bank_account,
            defaults={'next_check_number': bank_account.next_check_number or 1001}
        )

        # BUGFIX: Use same logic as get_next_numbers() to determine actual next number
        # This ensures preview and print show the same check numbers
        bank_account.refresh_from_db()
        if bank_account.next_check_number and bank_account.next_check_number > sequence.next_check_number:
            actual_next = bank_account.next_check_number
        else:
            actual_next = sequence.next_check_number

        print(f"[NEXT CHECK NUMBER] Bank account: {bank_account.account_name}, Sequence: {sequence.next_check_number}, BankAccount: {bank_account.next_check_number}, Returning: {actual_next}")

        return Response({
            'next_check_number': actual_next,
            'bank_account': bank_account.account_name
        })

    @action(detail=False, methods=['POST'], url_path='update-next-check-number')
    def update_next_check_number(self, request):
        """Update the next check number - syncs both CheckSequence and BankAccount"""
        from apps.settings.models import CheckSequence
        from apps.bank_accounts.models import BankAccount

        new_reference_number = request.data.get('next_check_number')
        if not new_reference_number:
            return Response({'error': 'next_check_number is required'}, status=400)

        try:
            new_reference_number = int(new_reference_number)
            if new_reference_number < 1:
                return Response({'error': 'Check number must be 1 or greater'}, status=400)
        except ValueError:
            return Response({'error': 'Invalid check number format'}, status=400)

        # Get the primary trust account (or first bank account)
        bank_account = BankAccount.objects.filter(account_type='Trust Account').first()
        if not bank_account:
            bank_account = BankAccount.objects.first()

        if not bank_account:
            return Response({'error': 'No bank account found'}, status=404)

        # Get or create the check sequence
        sequence, created = CheckSequence.objects.get_or_create(
            bank_account=bank_account,
            defaults={'next_check_number': new_reference_number}
        )

        # BUGFIX: Update BOTH CheckSequence and BankAccount to keep them in sync
        sequence.next_check_number = new_reference_number
        sequence.save()
        
        bank_account.next_check_number = new_reference_number
        bank_account.save(update_fields=['next_check_number', 'updated_at'])

        print(f"[UPDATE CHECK NUMBER] Updated next check number to {new_reference_number} for account {bank_account.account_name} (synced both sequence and bank_account)")

        return Response({
            'success': True,
            'next_check_number': new_reference_number,
            'bank_account': bank_account.account_name,
            'message': f'Next check number updated to {new_reference_number}'
        })

    @action(detail=False, methods=['POST'], url_path='assign-check-numbers')
    def assign_reference_numbers(self, request):
        """
        Assign sequential check numbers to transactions.
        Expected POST data: {check_ids: [252, 246, ...]}
        """
        from apps.settings.models import CheckSequence
        from apps.bank_accounts.models import BankAccount
        from django.db import transaction as db_transaction

        check_ids = request.data.get('check_ids', [])
        if not check_ids:
            return Response({'error': 'No check IDs provided'}, status=400)

        import sys
        print(f"[CHECK ASSIGN] Received check_ids: {check_ids}", file=sys.stderr, flush=True)

        # Get the transactions
        transactions = BankTransaction.objects.filter(
            id__in=check_ids
        ).select_related('bank_account').order_by('id')

        print(f"[CHECK ASSIGN] Found {transactions.count()} transactions: {list(transactions.values_list('id', flat=True))}", file=sys.stderr, flush=True)

        if not transactions.exists():
            return Response({'error': 'No transactions found'}, status=404)

        # Get the bank account (assuming all checks are from same account)
        bank_account = transactions.first().bank_account
        if not bank_account:
            return Response({'error': 'No bank account found for these checks'}, status=400)

        # Get sequential check numbers
        try:
            with db_transaction.atomic():
                reference_numbers = CheckSequence.get_next_numbers(bank_account, len(check_ids))

                # Assign check numbers to transactions
                results = []
                for txn, check_num in zip(transactions, reference_numbers):
                    print(f"[CHECK ASSIGN] Assigning check #{check_num} to transaction ID {txn.id}", file=sys.stderr, flush=True)
                    # Update reference_number (was "TO PRINT", now becomes actual check number)
                    txn.reference_number = str(check_num)
                    txn.save()
                    results.append({
                        'transaction_id': txn.id,
                        'reference_number': str(check_num),
                        'payee': txn.payee or (txn.vendor.vendor_name if txn.vendor else None),
                        'amount': str(txn.amount)
                    })

                print(f"[CHECK ASSIGN] Successfully assigned check numbers: {[r['reference_number'] for r in results]}", file=sys.stderr, flush=True)

                return Response({
                    'success': True,
                    'message': f'Assigned check numbers {reference_numbers[0]} to {reference_numbers[-1]}',
                    'checks': results,
                    'next_check_number': reference_numbers[-1] + 1
                })

        except Exception as e:
            return Response({'error': str(e)}, status=500)
