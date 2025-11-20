from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def format_phone_us(phone_number):
    """
    Format phone number to US format (xxx) xxx-xxxx
    """
    if not phone_number:
        return phone_number
    
    # Remove all non-digits
    digits = re.sub(r'\D', '', str(phone_number))
    
    # Handle different lengths
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        # Remove leading 1 for US numbers
        digits = digits[1:]
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    else:
        # Return original if not standard US format
        return phone_number

@register.filter
def format_currency(amount):
    """Format balances using professional accounting standards - Red+Bold ONLY for negative balances"""
    if amount is None:
        return "0.00"
    
    amount = float(amount)
    formatted_amount = intcomma(f"{abs(amount):.2f}")
    
    if amount < 0:
        # Red + Bold ONLY for negative balances (critical alerts)
        return mark_safe(f'<span style="color: red; font-weight: bold;">({formatted_amount})</span>')
    elif amount > 0:
        # Green for positive balances
        return mark_safe(f'<span style="color: green;">{formatted_amount}</span>')
    else:
        # Standard black for zero
        return formatted_amount

@register.filter
def negate(value):
    """Convert a positive number to negative"""
    try:
        return -float(value)
    except (ValueError, TypeError):
        return value