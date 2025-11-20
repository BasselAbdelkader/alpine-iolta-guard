from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def format_amount_accounting(value):
    """
    Format amounts using professional accounting standards (no currency symbol):
    - Positive amounts: 1,234.56
    - Negative amounts: (1,234.56)
    - Zero amounts: 0.00
    """
    if value is None:
        return "0.00"
    
    try:
        amount = Decimal(str(value))
        if amount < 0:
            return f"({abs(amount):,.2f})"  # Professional accounting standard
        return f"{amount:,.2f}"
    except (ValueError, TypeError):
        return "0.00"

@register.filter
def format_deposit(value):
    """
    Format deposit amounts (money in):
    - Always positive: 1,000.00 (Green color via CSS)
    """
    if value is None:
        return "0.00"
    
    try:
        amount = abs(Decimal(str(value)))  # Always positive for deposits
        return f"{amount:,.2f}"
    except (ValueError, TypeError):
        return "0.00"

@register.filter
def format_withdrawal(value):
    """
    Format withdrawal amounts (money out):
    - Always in parentheses: (500.00) (Black color via CSS)
    """
    if value is None:
        return "(0.00)"
    
    try:
        amount = abs(Decimal(str(value)))  # Always positive, then wrapped in parentheses
        return f"({amount:,.2f})"
    except (ValueError, TypeError):
        return "(0.00)"

@register.filter
def balance_status_class(value):
    """
    Return CSS class for balance status (professional accounting color coding):
    - Negative: text-danger fw-bold (RED + BOLD - critical alert)
    - Zero: text-muted (gray)
    - Positive: text-success (green)
    """
    if value is None:
        return "text-muted"
    
    try:
        amount = Decimal(str(value))
        if amount < 0:
            return "text-danger fw-bold"  # RED + BOLD for negative balances (critical alert)
        elif amount == 0:
            return "text-muted"           # Gray for zero balances
        else:
            return "text-success"         # Green for positive balances
    except (ValueError, TypeError):
        return "text-muted"

@register.filter
def deposit_class(value):
    """Return CSS class for deposits (green for money in)"""
    return "text-success"

@register.filter
def withdrawal_class(value):
    """Return CSS class for withdrawals (black for money out)"""
    return "text-dark"

@register.filter
def format_phone(value, vendor=None):
    """
    Format phone numbers to (123) 456-7890 format with dynamic area code detection
    """
    if not value:
        return "-"
    
    # Remove all non-digit characters  
    digits = ''.join(filter(str.isdigit, str(value)))
    
    # Handle different digit lengths
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    elif len(digits) == 7:
        # For 7-digit numbers, try to get area code dynamically
        area_code = "555"  # Default fallback
        
        # If vendor has a linked client, use client's area code
        if hasattr(vendor, 'client') and vendor and vendor.client and vendor.client.phone:
            client_digits = ''.join(filter(str.isdigit, str(vendor.client.phone)))
            if len(client_digits) >= 10:
                area_code = client_digits[:3]
        
        return f"({area_code}) {digits[:3]}-{digits[3:]}"
    else:
        return value  # Return original if can't format

@register.simple_tag
def accounting_total(queryset, field_name):
    """
    Calculate total for a queryset field using professional accounting format
    Usage: {% accounting_total clients 'current_balance' %}
    """
    try:
        total = sum(getattr(obj, field_name, 0) for obj in queryset)
        if total < 0:
            return f"({abs(total):,.2f})"
        return f"{total:,.2f}"
    except (ValueError, TypeError, AttributeError):
        return "0.00"