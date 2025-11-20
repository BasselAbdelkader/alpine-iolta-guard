from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Sum, Q
from django.utils import timezone
from django.template.loader import render_to_string
from datetime import datetime, timedelta
from decimal import Decimal
import csv
import io

from apps.clients.models import Client, Case
from apps.bank_accounts.models import BankTransaction
from apps.settlements.models import Settlement


@login_required
def reports_index(request):
    """Reports dashboard with links to all available reports"""
    return render(request, 'reports/index.html')


@login_required
def client_ledger_report(request):
    """Generate client ledger report showing all transactions for selected client(s)"""
    
    # Get filter parameters
    client_id = request.GET.get('client_id')
    case_id = request.GET.get('case_id')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    export_format = request.GET.get('export', 'html')
    
    # Initialize empty values
    transaction_items = BankTransaction.objects.none()
    items_with_balance = []
    current_balance = Decimal('0.00')
    total_deposits = Decimal('0.00')
    total_withdrawals = Decimal('0.00')
    
    # Only load data if client is selected
    if client_id:
        # Default date range (last 12 months if not specified)
        if not date_from:
            date_from = (timezone.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not date_to:
            date_to = timezone.now().strftime('%Y-%m-%d')
        
        # Build base queryset - EXCLUDE voided transactions for accurate balances
        transaction_items = BankTransaction.objects.select_related(
            'client', 'case', 'vendor'
        ).filter(
            client_id=client_id,
            transaction_date__range=[date_from, date_to]
        ).exclude(
            status='voided'  # Critical: Don't include voided transactions in balance calculations
        ).order_by('-transaction_date', '-created_at')
        
        # Apply case filter if specified
        if case_id:
            transaction_items = transaction_items.filter(case_id=case_id)
        
        # Calculate running balances and totals
        # Process transactions chronologically for running balance
        for item in transaction_items.order_by('transaction_date', 'id'):
            if item.transaction_type == 'DEPOSIT':
                current_balance += item.amount
                total_deposits += item.amount
            else:
                current_balance -= item.amount
                total_withdrawals += item.amount

            # Add running balance to the item (for display)
            item.running_balance = current_balance
            items_with_balance.append(item)
    
    # Keep chronological order (oldest first) as requested by customer
    
    # Get client and case info for display
    selected_client = None
    selected_case = None
    if client_id:
        selected_client = get_object_or_404(Client, id=client_id)
    if case_id:
        selected_case = get_object_or_404(Case, id=case_id)
    
    context = {
        'transaction_items': items_with_balance,
        'clients': Client.objects.filter(is_active=True).order_by('first_name', 'last_name'),
        'cases': Case.objects.filter(is_active=True).order_by('-opened_date'),
        'selected_client': selected_client,
        'selected_case': selected_case,
        'date_from': date_from,
        'date_to': date_to,
        'current_balance': current_balance,
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'net_change': total_deposits - total_withdrawals,
        'transaction_count': len(items_with_balance),
        'report_generated': timezone.now(),
    }
    
    # Handle export formats
    if export_format == 'pdf':
        return render_client_ledger_pdf(request, context)
    elif export_format == 'excel':
        return render_client_ledger_excel(request, context)
    
    return render(request, 'reports/client_ledger.html', context)


def render_client_ledger_pdf(request, context):
    """Render client ledger as PDF using HTML to PDF conversion"""
    try:
        from weasyprint import HTML, CSS
        from django.template.loader import render_to_string
        
        # Render HTML template for PDF
        html_content = render_to_string('reports/client_ledger_pdf.html', context)
        
        # Generate PDF
        pdf_file = HTML(string=html_content).write_pdf()
        
        # Create response
        response = HttpResponse(pdf_file, content_type='application/pdf')
        
        # Set filename
        client_name = context['selected_client'].full_name if context['selected_client'] else 'All_Clients'
        filename = f"Client_Ledger_{client_name}_{context['date_from']}_to_{context['date_to']}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except ImportError:
        # Fallback to simple HTML response if weasyprint not available
        response = HttpResponse(
            "PDF export requires weasyprint library. Contact administrator to install dependencies.",
            content_type='text/plain'
        )
        return response


def render_client_ledger_excel(request, context):
    """Render client ledger as Excel using CSV format"""
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    
    # Set filename
    client_name = context['selected_client'].full_name if context['selected_client'] else 'All_Clients'
    filename = f"Client_Ledger_{client_name}_{context['date_from']}_to_{context['date_to']}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    
    # Write header information
    writer.writerow(['Trust Account Client Ledger Report'])
    writer.writerow([''])
    
    if context['selected_client']:
        writer.writerow(['Client:', context['selected_client'].full_name])
        if context['selected_case']:
            writer.writerow(['Case:', context['selected_case'].case_number])
    else:
        writer.writerow(['Client:', 'All Clients'])
    
    # Parse date strings to datetime objects if needed
    try:
        if isinstance(context['date_from'], str):
            date_from_formatted = datetime.strptime(context['date_from'], '%Y-%m-%d').strftime('%m/%d/%Y')
        else:
            date_from_formatted = context['date_from'].strftime('%m/%d/%Y')
            
        if isinstance(context['date_to'], str):
            date_to_formatted = datetime.strptime(context['date_to'], '%Y-%m-%d').strftime('%m/%d/%Y')
        else:
            date_to_formatted = context['date_to'].strftime('%m/%d/%Y')
    except:
        # Fallback to original string if parsing fails
        date_from_formatted = context['date_from']
        date_to_formatted = context['date_to']
    
    writer.writerow(['Report Period:', f"{date_from_formatted} to {date_to_formatted}"])
    writer.writerow(['Generated:', context['report_generated'].strftime('%m/%d/%Y %I:%M:%S %p')])
    writer.writerow([''])
    
    # Write summary
    writer.writerow(['SUMMARY'])
    writer.writerow(['Total Deposits:', f"{context['total_deposits']:.2f}"])
    writer.writerow(['Total Withdrawals:', f"({context['total_withdrawals']:.2f})"])
    writer.writerow(['Current Balance:', f"{context['current_balance']:.2f}"])
    writer.writerow([''])
    
    # Write column headers
    writer.writerow([
        'Date', 'Type', 'Ref', 'Payee', 'Description', 
        'Amount', 'Balance'
    ])
    
    # Write transaction data
    for item in context['transaction_items']:
        # Single Amount column - deposits positive, withdrawals with parentheses
        if item.transaction_type == 'DEPOSIT':
            amount = f"{item.amount:.2f}"
        else:
            amount = f"({item.amount:.2f})"
        
        # Format balance with parentheses for negatives
        if item.running_balance < 0:
            balance = f"({abs(item.running_balance):.2f})"
        else:
            balance = f"{item.running_balance:.2f}"
        
        # Get vendor/payee name
        vendor_payee = ''
        if hasattr(item, 'vendor') and item.vendor:
            vendor_payee = item.vendor.vendor_name
        
        writer.writerow([
            item.transaction_date.strftime('%m/%d/%Y'),
            item.get_transaction_type_display(),
            item.case.case_number if item.case else '',
            vendor_payee,
            item.description,
            amount,
            balance
        ])
    
    return response