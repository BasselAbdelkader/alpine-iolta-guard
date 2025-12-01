from django import template
from decimal import Decimal

register = template.Library()


@register.filter
def amount_in_words(value):
    """Convert dollar amount to words: 10000 -> 'Ten Thousand'"""
    try:
        # Convert to integer (dollar part only)
        value = int(Decimal(str(value)))
    except (ValueError, TypeError):
        return "Zero"

    if value == 0:
        return "Zero"

    # Define number words
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
    teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen",
             "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    thousands = ["", "Thousand", "Million", "Billion"]

    def convert_hundreds(num):
        """Convert a number under 1000 to words"""
        if num == 0:
            return ""
        elif num < 10:
            return ones[num]
        elif num < 20:
            return teens[num - 10]
        elif num < 100:
            return tens[num // 10] + ("-" + ones[num % 10] if num % 10 != 0 else "")
        else:
            hundred_part = ones[num // 100] + " Hundred"
            remainder = num % 100
            if remainder == 0:
                return hundred_part
            else:
                return hundred_part + " " + convert_hundreds(remainder)

    # Handle negative numbers
    if value < 0:
        return "Negative " + amount_in_words(-value)

    # Split into groups of three digits
    groups = []
    while value > 0:
        groups.append(value % 1000)
        value //= 1000

    # Convert each group to words
    result = []
    for i, group in enumerate(groups):
        if group != 0:
            group_words = convert_hundreds(group)
            if i > 0:
                group_words += " " + thousands[i]
            result.append(group_words)

    # Reverse and join
    return " ".join(reversed(result))


@register.filter
def cents_part(value):
    """Get cents portion: 10000.50 -> '50'"""
    try:
        cents = int((Decimal(str(value)) % 1) * 100)
        return f"{cents:02d}"
    except (ValueError, TypeError):
        return "00"
