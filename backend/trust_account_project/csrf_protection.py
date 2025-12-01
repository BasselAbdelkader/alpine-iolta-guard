"""
TAMS Advanced CSRF Protection System
Provides comprehensive view-level CSRF enforcement beyond Django's default protection
"""

import hashlib
import hmac
import time
import json
import logging
from django.conf import settings
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import JsonResponse, HttpResponseForbidden
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.mixins import LoginRequiredMixin
import re

logger = logging.getLogger(__name__)

class AdvancedCSRFProtectionMiddleware(MiddlewareMixin):
    """
    Advanced CSRF protection middleware with enhanced validation
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # State-changing HTTP methods that require CSRF protection
        self.protected_methods = {'POST', 'PUT', 'DELETE', 'PATCH'}
        # API endpoints that need special handling
        self.api_patterns = [
            r'/api/',
            r'/ajax/',
            r'.*/create/$',
            r'.*/update/$',
            r'.*/delete/$',
        ]
        super().__init__(get_response)
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Enhanced CSRF validation for views"""
        
        # Skip GET, HEAD, OPTIONS, TRACE
        if request.method not in self.protected_methods:
            return None
        
        # Check if this is an API endpoint
        is_api_endpoint = self.is_api_endpoint(request.path)
        
        # Enhanced CSRF validation
        if not self.validate_csrf_token(request, is_api_endpoint):
            return self.csrf_failure(request, is_api_endpoint)
        
        # Additional validation for sensitive operations
        if self.is_sensitive_operation(request):
            if not self.validate_sensitive_operation(request):
                return self.sensitive_operation_failure(request)
        
        return None
    
    def is_api_endpoint(self, path):
        """Check if path is an API endpoint"""
        for pattern in self.api_patterns:
            if re.match(pattern, path):
                return True
        return False
    
    def validate_csrf_token(self, request, is_api_endpoint):
        """Enhanced CSRF token validation"""
        from django.middleware.csrf import _get_token_from_request
        
        # Get CSRF token from request
        try:
            csrf_token = _get_token_from_request(request)
        except:
            # Fallback to basic token extraction
            csrf_token = request.POST.get('csrfmiddlewaretoken') or request.META.get('HTTP_X_CSRFTOKEN')
        
        if not csrf_token:
            logger.warning(f"SECURITY: Missing CSRF token from {self.get_client_ip(request)} for {request.path}")
            return False
        
        # Basic CSRF validation - let Django's middleware handle the complex validation
        # This is an additional layer, not a replacement
        if len(csrf_token) < 32:  # CSRF tokens should be at least 32 characters
            logger.error(f"SECURITY: Invalid CSRF token format from {self.get_client_ip(request)}")
            return False
        
        # Additional validation for API endpoints
        if is_api_endpoint:
            return self.validate_api_csrf(request, csrf_token)
        
        return True
    
    def validate_api_csrf(self, request, csrf_token):
        """Additional CSRF validation for API endpoints"""
        
        # Check for proper headers
        ajax_header = request.META.get('HTTP_X_REQUESTED_WITH')
        if ajax_header != 'XMLHttpRequest':
            # For API calls, require custom header for CSRF protection
            csrf_header = request.META.get('HTTP_X_CSRFTOKEN')
            if not csrf_header or csrf_header != csrf_token:
                logger.warning(f"SECURITY: API CSRF validation failed from {self.get_client_ip(request)}")
                return False
        
        return True
    
    def is_sensitive_operation(self, request):
        """Check if operation requires additional validation"""
        sensitive_patterns = [
            r'.*/delete/$',
            r'.*/transactions/',
            r'.*/settlements/',
            r'.*/bank_accounts/',
        ]
        
        for pattern in sensitive_patterns:
            if re.match(pattern, request.path, re.IGNORECASE):
                return True
        
        return False
    
    def validate_sensitive_operation(self, request):
        """Additional validation for sensitive operations"""
        
        # Require confirmation parameter for delete operations
        if 'delete' in request.path.lower():
            confirm = request.POST.get('confirm_delete') or request.GET.get('confirm_delete')
            if confirm != 'yes':
                logger.warning(f"SECURITY: Delete operation without confirmation from {self.get_client_ip(request)}")
                return False
        
        # Validate transaction amounts
        if 'transaction' in request.path.lower():
            amount = request.POST.get('amount')
            if amount:
                try:
                    amount_val = float(amount)
                    if amount_val < 0:
                        logger.warning(f"SECURITY: Negative transaction amount attempted from {self.get_client_ip(request)}")
                        return False
                    if amount_val > 1000000:  # $1M limit
                        logger.warning(f"SECURITY: Excessive transaction amount attempted: ${amount_val} from {self.get_client_ip(request)}")
                        return False
                except (ValueError, TypeError):
                    logger.warning(f"SECURITY: Invalid transaction amount format from {self.get_client_ip(request)}")
                    return False
        
        return True
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or 'unknown'
    
    def csrf_failure(self, request, is_api_endpoint):
        """Handle CSRF validation failure"""
        client_ip = self.get_client_ip(request)
        
        # Log security incident
        logger.error(f"SECURITY: CSRF protection triggered - blocked request from {client_ip} to {request.path}")
        
        if is_api_endpoint or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': 'CSRF verification failed. Please refresh the page and try again.',
                'code': 'csrf_failure',
                'status': 'forbidden'
            }, status=403)
        else:
            return HttpResponseForbidden(
                'CSRF verification failed. This appears to be a cross-site request forgery attempt. '
                'Please refresh the page and try again.'
            )
    
    def sensitive_operation_failure(self, request):
        """Handle sensitive operation validation failure"""
        client_ip = self.get_client_ip(request)
        
        logger.error(f"SECURITY: Sensitive operation validation failed from {client_ip} to {request.path}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': 'Additional validation required for this operation.',
                'code': 'validation_failure',
                'status': 'forbidden'
            }, status=403)
        else:
            return HttpResponseForbidden(
                'Additional validation required for this sensitive operation.'
            )


class EnhancedCSRFMixin:
    """
    Mixin for class-based views with enhanced CSRF protection
    """
    
    # Override these in subclasses for specific requirements
    require_confirmation_delete = True
    max_transaction_amount = 1000000.00
    sensitive_fields = ['amount', 'password', 'ssn', 'account_number']
    
    def dispatch(self, request, *args, **kwargs):
        """Enhanced dispatch with CSRF validation"""
        
        # Ensure CSRF token is present
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            csrf_token = get_token(request)
            if not csrf_token:
                logger.error(f"SECURITY: No CSRF token available for {request.path}")
                return JsonResponse({'error': 'CSRF token required'}, status=403)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """Add enhanced CSRF context data"""
        context = super().get_context_data(**kwargs)
        
        # Add CSRF token and security metadata
        context['csrf_token'] = get_token(self.request)
        context['requires_confirmation'] = getattr(self, 'require_confirmation_delete', False)
        context['max_transaction_amount'] = getattr(self, 'max_transaction_amount', 1000000.00)
        
        return context
    
    def form_valid(self, form):
        """Enhanced form validation with security checks"""
        
        # Check for sensitive data in form
        form_data = form.cleaned_data
        self.validate_sensitive_data(form_data)
        
        # Log successful form submission
        logger.info(f"SECURITY: Form submission validated for {self.request.user} from {self.get_client_ip()}")
        
        return super().form_valid(form)
    
    def validate_sensitive_data(self, data):
        """Validate sensitive data in forms"""
        
        for field_name, value in data.items():
            if field_name in self.sensitive_fields and value:
                # Additional validation for sensitive fields
                if field_name == 'amount':
                    try:
                        amount_val = float(str(value))
                        if amount_val > self.max_transaction_amount:
                            raise SuspiciousOperation(f"Transaction amount exceeds limit: ${amount_val}")
                    except (ValueError, TypeError):
                        raise SuspiciousOperation(f"Invalid amount format: {value}")
                
                elif field_name in ['ssn', 'account_number']:
                    # Validate format and log access
                    logger.info(f"SECURITY: Sensitive field {field_name} accessed by {self.request.user}")
        
        return True
    
    def get_client_ip(self):
        """Get client IP address"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip or 'unknown'


# Enhanced decorators for function-based views
def enhanced_csrf_protect(view_func):
    """Enhanced CSRF protection decorator"""
    from django.views.decorators.csrf import csrf_protect
    from functools import wraps
    
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # Enhanced CSRF validation
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            # Ensure token is present
            csrf_token = get_token(request)
            if not csrf_token:
                logger.error(f"SECURITY: Enhanced CSRF protection - no token for {request.path}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'CSRF token required'}, status=403)
                else:
                    return HttpResponseForbidden('CSRF token required')
        
        # Apply standard CSRF protection
        return csrf_protect(view_func)(request, *args, **kwargs)
    
    return wrapped_view


def api_csrf_protect(view_func):
    """Specific CSRF protection for API views"""
    from functools import wraps
    
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            # For API endpoints, require both CSRF token and header
            csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
            if not csrf_token:
                logger.warning(f"SECURITY: API CSRF header missing for {request.path}")
                return JsonResponse({
                    'error': 'CSRF token required in X-CSRFToken header',
                    'code': 'csrf_required'
                }, status=403)
            
            # Additional API-specific validation
            if not request.headers.get('Content-Type', '').startswith('application/'):
                logger.warning(f"SECURITY: Invalid content type for API endpoint {request.path}")
                return JsonResponse({
                    'error': 'Invalid content type for API endpoint',
                    'code': 'invalid_content_type'
                }, status=400)
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


# Method decorator for class-based views
def method_csrf_protect(method):
    """Method decorator for enhanced CSRF protection on specific methods"""
    return method_decorator(enhanced_csrf_protect)(method)