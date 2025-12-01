"""
TAMS Enhanced Form Base Classes
Provides security-enhanced form validation and sanitization
"""

from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
import re
import html

class SecureFormMixin:
    """
    Mixin to add enhanced security validation to any Django form
    """
    
    # Dangerous patterns to detect and prevent
    DANGEROUS_PATTERNS = [
        (r'<script[^>]*>.*?</script>', 'Script tags are not allowed'),
        (r'javascript:', 'JavaScript protocols are not allowed'),
        (r'vbscript:', 'VBScript protocols are not allowed'),
        (r'on\w+\s*=', 'Event handlers are not allowed'),
        (r'<iframe[^>]*>', 'Iframe tags are not allowed'),
        (r'<object[^>]*>', 'Object tags are not allowed'),
        (r'<embed[^>]*>', 'Embed tags are not allowed'),
        (r'eval\s*\(', 'Eval functions are not allowed'),
        (r'alert\s*\(', 'Alert functions are not allowed'),
        (r'confirm\s*\(', 'Confirm functions are not allowed'),
        (r'prompt\s*\(', 'Prompt functions are not allowed'),
    ]
    
    SQL_INJECTION_PATTERNS = [
        (r'union\s+select', 'SQL injection attempts are not allowed'),
        (r'drop\s+table', 'Database modification attempts are not allowed'),
        (r'delete\s+from', 'Database deletion attempts are not allowed'),
        (r'insert\s+into', 'Database insertion attempts are not allowed'),
        (r'update\s+.*set', 'Database update attempts are not allowed'),
        (r'--\s*$', 'SQL comments are not allowed'),
        (r'/\*.*\*/', 'SQL block comments are not allowed'),
        (r"'\s*or\s*'", 'SQL injection patterns are not allowed'),
        (r"1\s*=\s*1", 'SQL tautologies are not allowed'),
    ]
    
    def clean(self):
        """Enhanced clean method with security validation"""
        cleaned_data = super().clean()
        
        # Perform security validation on all text fields
        self.validate_security(cleaned_data)
        
        # Perform sanitization if enabled
        if getattr(settings, 'ENABLE_INPUT_SANITIZATION', True):
            cleaned_data = self.sanitize_data(cleaned_data)
        
        return cleaned_data
    
    def validate_security(self, data):
        """Validate data for security threats"""
        violations = []
        
        for field_name, value in data.items():
            if isinstance(value, str) and value:
                field_violations = self.validate_field_security(field_name, value)
                violations.extend(field_violations)
        
        if violations:
            # Log security violation attempt
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"SECURITY: Form validation blocked potentially dangerous input: {violations}")
            
            # Raise validation error
            raise ValidationError("Invalid input detected. Please check your data and try again.")
    
    def validate_field_security(self, field_name, value):
        """Validate individual field for security issues"""
        violations = []
        value_lower = value.lower()
        
        # Check for dangerous patterns
        for pattern, message in self.DANGEROUS_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE | re.DOTALL):
                violations.append(f"{field_name}: {message}")
        
        # Check for SQL injection patterns
        for pattern, message in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                violations.append(f"{field_name}: {message}")
        
        # Check field length limits
        max_length = getattr(settings, 'MAX_INPUT_LENGTH', 10000)
        if len(value) > max_length:
            violations.append(f"{field_name}: Input too long (maximum {max_length} characters)")
        
        # Check for null bytes
        if '\x00' in value:
            violations.append(f"{field_name}: Null bytes are not allowed")
        
        return violations
    
    def sanitize_data(self, data):
        """Sanitize form data"""
        sanitized_data = {}
        
        for field_name, value in data.items():
            if isinstance(value, str):
                sanitized_data[field_name] = self.sanitize_string(value)
            else:
                sanitized_data[field_name] = value
        
        return sanitized_data
    
    def sanitize_string(self, text):
        """Sanitize individual string value"""
        if not text:
            return text
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Trim excessive whitespace while preserving intentional formatting
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Strip trailing whitespace but preserve leading whitespace for formatting
            cleaned_line = line.rstrip()
            cleaned_lines.append(cleaned_line)
        
        text = '\n'.join(cleaned_lines)
        
        # Limit length
        max_length = getattr(settings, 'MAX_INPUT_LENGTH', 10000)
        if len(text) > max_length:
            text = text[:max_length]
        
        return text


class SecureModelForm(SecureFormMixin, forms.ModelForm):
    """
    Enhanced ModelForm with built-in security validation
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add security-enhanced widgets where appropriate
        for field_name, field in self.fields.items():
            if isinstance(field, forms.CharField):
                # Add maxlength attribute to prevent excessively long inputs
                max_length = getattr(settings, 'MAX_INPUT_LENGTH', 10000)
                current_maxlength = field.widget.attrs.get('maxlength', max_length)
                # Convert to int if it's a string, otherwise use default
                try:
                    current_maxlength = int(current_maxlength)
                except (ValueError, TypeError):
                    current_maxlength = max_length
                
                if current_maxlength > max_length:
                    field.widget.attrs['maxlength'] = max_length
                
                # Add input validation attributes
                field.widget.attrs.update({
                    'data-security-validated': 'true',
                    'autocomplete': 'off' if 'password' in field_name.lower() else field.widget.attrs.get('autocomplete'),
                })


class SecureForm(SecureFormMixin, forms.Form):
    """
    Enhanced Form with built-in security validation
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add security-enhanced widgets where appropriate
        for field_name, field in self.fields.items():
            if isinstance(field, forms.CharField):
                # Add maxlength attribute
                max_length = getattr(settings, 'MAX_INPUT_LENGTH', 10000)
                if hasattr(field.widget.attrs, 'get'):
                    current_maxlength = field.widget.attrs.get('maxlength', max_length)
                    # Convert to int if it's a string, otherwise use default
                    try:
                        current_maxlength = int(current_maxlength)
                    except (ValueError, TypeError):
                        current_maxlength = max_length
                    
                    if current_maxlength > max_length:
                        field.widget.attrs['maxlength'] = max_length
                
                # Add security attributes
                field.widget.attrs.update({
                    'data-security-validated': 'true',
                })


# CSRF Token Validation Decorator for Views
def require_csrf_token(view_func):
    """
    Decorator to ensure CSRF token validation for views
    Can be used on class-based views with method_decorator
    """
    from django.views.decorators.csrf import csrf_protect
    from django.utils.decorators import method_decorator
    
    if hasattr(view_func, 'dispatch'):
        # Class-based view
        return method_decorator(csrf_protect, name='dispatch')(view_func)
    else:
        # Function-based view
        return csrf_protect(view_func)
        

# Enhanced CSRF Protection Mixin for Class-Based Views
class CSRFProtectedMixin:
    """
    Mixin to ensure CSRF protection is properly applied to class-based views
    """
    
    def dispatch(self, request, *args, **kwargs):
        """Ensure CSRF protection is active"""
        from django.middleware.csrf import get_token
        
        # Ensure CSRF token is generated for this request
        get_token(request)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """Add CSRF token to context"""
        context = super().get_context_data(**kwargs)
        context['csrf_token'] = self.request.META.get('CSRF_COOKIE')
        return context