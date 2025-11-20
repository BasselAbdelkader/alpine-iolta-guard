"""
TAMS Advanced API Endpoint Hardening System
Provides comprehensive security for REST API endpoints
"""

import time
import json
import logging
import hashlib
import hmac
from datetime import datetime, timedelta
from django.conf import settings
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import JsonResponse
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from rest_framework.permissions import BasePermission
from rest_framework.throttling import BaseThrottle
from rest_framework.exceptions import Throttled
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from functools import wraps
import re

logger = logging.getLogger(__name__)

class APISecurityMiddleware(MiddlewareMixin):
    """
    Comprehensive API security middleware
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # API security configuration
        self.api_prefixes = ['/api/', '/ajax/']
        self.sensitive_endpoints = [
            r'/api/v1/transactions/',
            r'/api/v1/bank-accounts/',
            r'/api/v1/settlements/',
        ]
        self.max_request_size = 10 * 1024 * 1024  # 10MB
        self.max_params_count = 100
        super().__init__(get_response)
    
    def process_request(self, request):
        """Process API requests with enhanced security"""
        
        if not self.is_api_request(request):
            return None
        
        # Size validation
        if not self.validate_request_size(request):
            return self.security_response('Request size exceeds limit', 413)
        
        # Parameter count validation
        if not self.validate_parameter_count(request):
            return self.security_response('Too many parameters', 400)
        
        # Content type validation
        if not self.validate_content_type(request):
            return self.security_response('Invalid content type', 400)
        
        # Rate limit validation per IP/user
        if not self.validate_rate_limits(request):
            return self.security_response('Rate limit exceeded', 429)
        
        # SQL injection pattern detection
        if not self.validate_sql_injection(request):
            return self.security_response('Invalid request pattern detected', 400)
        
        # Sensitive endpoint validation
        if self.is_sensitive_endpoint(request) and not self.validate_sensitive_access(request):
            return self.security_response('Additional authentication required', 403)
        
        return None
    
    def is_api_request(self, path):
        """Check if request is to API endpoint"""
        return any(path.startswith(prefix) for prefix in self.api_prefixes)
    
    def validate_request_size(self, request):
        """Validate request size limits"""
        content_length = int(request.META.get('CONTENT_LENGTH', 0))
        if content_length > self.max_request_size:
            logger.warning(f"SECURITY: Oversized API request from {self.get_client_ip(request)}: {content_length} bytes")
            return False
        return True
    
    def validate_parameter_count(self, request):
        """Validate parameter count limits"""
        param_count = len(request.GET) + len(request.POST)
        if param_count > self.max_params_count:
            logger.warning(f"SECURITY: Too many parameters from {self.get_client_ip(request)}: {param_count}")
            return False
        return True
    
    def validate_content_type(self, request):
        """Validate content type for API requests"""
        if request.method in ['POST', 'PUT', 'PATCH']:
            content_type = request.content_type.lower()
            allowed_types = [
                'application/json',
                'application/x-www-form-urlencoded',
                'multipart/form-data'
            ]
            if not any(content_type.startswith(ct) for ct in allowed_types):
                logger.warning(f"SECURITY: Invalid content type from {self.get_client_ip(request)}: {content_type}")
                return False
        return True
    
    def validate_rate_limits(self, request):
        """Validate rate limits per IP and user"""
        client_ip = self.get_client_ip(request)
        
        # IP-based rate limiting
        ip_key = f"api_rate_ip_{client_ip}"
        ip_requests = cache.get(ip_key, 0)
        if ip_requests > 1000:  # 1000 requests per hour per IP
            logger.warning(f"SECURITY: IP rate limit exceeded: {client_ip}")
            return False
        
        cache.set(ip_key, ip_requests + 1, 3600)  # 1 hour timeout
        
        # User-based rate limiting
        if request.user.is_authenticated:
            user_key = f"api_rate_user_{request.user.id}"
            user_requests = cache.get(user_key, 0)
            if user_requests > 2000:  # 2000 requests per hour per user
                logger.warning(f"SECURITY: User rate limit exceeded: {request.user}")
                return False
            
            cache.set(user_key, user_requests + 1, 3600)
        
        return True
    
    def validate_sql_injection(self, request):
        """Detect potential SQL injection patterns"""
        suspicious_patterns = [
            r'union\s+select',
            r'drop\s+table',
            r'delete\s+from',
            r'insert\s+into',
            r'update\s+.*set',
            r'--\s*$',
            r'/\*.*\*/',
            r"'\s*or\s*'",
            r'1\s*=\s*1',
            r'admin\'\s*--',
            r'or\s+1\s*=\s*1',
        ]
        
        # Check all input sources
        all_params = {}
        all_params.update(request.GET.dict())
        all_params.update(request.POST.dict())
        
        # Check request body for JSON
        if hasattr(request, 'body') and request.body:
            try:
                if request.content_type.startswith('application/json'):
                    body_data = json.loads(request.body.decode('utf-8'))
                    if isinstance(body_data, dict):
                        all_params.update(body_data)
            except:
                pass
        
        for key, value in all_params.items():
            if isinstance(value, str):
                value_lower = value.lower()
                for pattern in suspicious_patterns:
                    if re.search(pattern, value_lower, re.IGNORECASE):
                        logger.error(f"SECURITY: SQL injection pattern detected from {self.get_client_ip(request)}: {pattern}")
                        return False
        
        return True
    
    def is_sensitive_endpoint(self, request):
        """Check if endpoint is sensitive"""
        path = request.path
        for pattern in self.sensitive_endpoints:
            if re.match(pattern, path):
                return True
        return False
    
    def validate_sensitive_access(self, request):
        """Additional validation for sensitive endpoints"""
        
        # Require authentication
        if not request.user.is_authenticated:
            return False
        
        # Check for additional headers
        required_headers = ['X-Requested-With', 'X-CSRFToken']
        for header in required_headers:
            if header not in request.META.get(f'HTTP_{header.upper().replace("-", "_")}', ''):
                if header == 'X-Requested-With' and request.META.get('HTTP_X_REQUESTED_WITH') != 'XMLHttpRequest':
                    logger.warning(f"SECURITY: Missing required header {header} from {self.get_client_ip(request)}")
                    return False
        
        # Time-based validation (business hours check - optional)
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:  # Outside 6 AM - 10 PM
            # Allow but log suspicious activity
            logger.info(f"SECURITY: After-hours API access by {request.user} from {self.get_client_ip(request)}")
        
        return True
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or 'unknown'
    
    def security_response(self, message, status_code):
        """Create security response"""
        return JsonResponse({
            'error': message,
            'code': 'security_validation_failed',
            'status': status_code
        }, status=status_code)


class SecureAPIPermission(BasePermission):
    """
    Enhanced API permission class with additional security checks
    """
    
    def has_permission(self, request, view):
        """Enhanced permission check"""
        
        # Check basic authentication
        if not request.user.is_authenticated:
            return False
        
        # Check for suspended or inactive users
        if not request.user.is_active:
            logger.warning(f"SECURITY: Inactive user API access attempt: {request.user}")
            return False
        
        # Additional checks for specific HTTP methods
        if request.method in ['DELETE']:
            # DELETE operations require admin permission
            if not request.user.is_staff:
                logger.warning(f"SECURITY: Non-staff DELETE attempt by {request.user}")
                return False
        
        # Check session age for sensitive operations
        if hasattr(request, 'session'):
            session_age = time.time() - request.session.get('_session_init_timestamp_', time.time())
            if session_age > 28800:  # 8 hours
                logger.warning(f"SECURITY: Stale session API access by {request.user}")
                return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        """Enhanced object-level permission check"""
        
        # Basic permission check
        if not self.has_permission(request, view):
            return False
        
        # Log object access for audit purposes
        logger.info(f"SECURITY: Object access - User: {request.user}, Object: {obj.__class__.__name__}:{obj.pk}")
        
        # Additional object-level security can be added here
        # For example, checking if user has permission to access specific client data
        
        return True


class APIRateLimitThrottle(BaseThrottle):
    """
    Custom rate limiting for API endpoints
    """
    
    def __init__(self):
        self.rates = {
            'authenticated': 2000,  # 2000 requests per hour for authenticated users
            'anonymous': 100,       # 100 requests per hour for anonymous users
            'sensitive': 500,       # 500 requests per hour for sensitive endpoints
        }
    
    def allow_request(self, request, view):
        """Check if request should be allowed"""
        
        # Determine rate limit category
        if self.is_sensitive_endpoint(request):
            rate_key = 'sensitive'
        elif request.user.is_authenticated:
            rate_key = 'authenticated'
        else:
            rate_key = 'anonymous'
        
        # Get rate limit for this category
        rate_limit = self.rates[rate_key]
        
        # Create cache key
        cache_key = self.get_cache_key(request, rate_key)
        
        # Get current request count
        current_requests = cache.get(cache_key, 0)
        
        if current_requests >= rate_limit:
            # Rate limit exceeded
            self.wait_time = 3600  # 1 hour wait time
            return False
        
        # Increment counter
        cache.set(cache_key, current_requests + 1, 3600)  # 1 hour timeout
        
        return True
    
    def wait(self):
        """Return wait time when throttled"""
        return getattr(self, 'wait_time', 3600)
    
    def get_cache_key(self, request, rate_key):
        """Generate cache key for rate limiting"""
        if request.user.is_authenticated:
            identifier = f"user_{request.user.id}"
        else:
            identifier = f"ip_{self.get_client_ip(request)}"
        
        return f"api_throttle_{rate_key}_{identifier}"
    
    def is_sensitive_endpoint(self, request):
        """Check if endpoint is sensitive"""
        sensitive_patterns = [
            r'/api/v1/transactions/',
            r'/api/v1/bank-accounts/',
            r'/api/v1/settlements/',
        ]
        
        path = request.path
        return any(re.match(pattern, path) for pattern in sensitive_patterns)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or 'unknown'


# API Security Decorators
def api_security_required(view_func):
    """Decorator for enhanced API security"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # Additional security checks
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        # Check for required headers
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
            if not csrf_token:
                return JsonResponse({'error': 'CSRF token required'}, status=403)
        
        # Log API access
        logger.info(f"API Access: {request.user} -> {request.path} ({request.method})")
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


def sensitive_api_endpoint(view_func):
    """Decorator for sensitive API endpoints requiring additional validation"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # Enhanced validation for sensitive endpoints
        
        # Check authentication
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        # Check staff status for sensitive operations
        if request.method in ['DELETE'] and not request.user.is_staff:
            return JsonResponse({'error': 'Administrative privileges required'}, status=403)
        
        # Validate request timing
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:
            logger.warning(f"SECURITY: Sensitive API access outside business hours by {request.user}")
        
        # Additional validation for transaction amounts
        if 'amount' in request.POST or 'amount' in request.GET:
            try:
                amount = float(request.POST.get('amount', request.GET.get('amount', 0)))
                if amount > 1000000:  # $1M limit
                    logger.error(f"SECURITY: Large transaction attempt: ${amount} by {request.user}")
                    return JsonResponse({'error': 'Transaction amount exceeds limit'}, status=400)
            except (ValueError, TypeError):
                return JsonResponse({'error': 'Invalid amount format'}, status=400)
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


class SecureSessionAuthentication(SessionAuthentication):
    """
    Enhanced session authentication with additional security
    """
    
    def authenticate(self, request):
        """Enhanced authentication with session validation"""
        
        # Standard session authentication
        user_auth = super().authenticate(request)
        
        if user_auth:
            user, auth = user_auth
            
            # Additional session security checks
            if hasattr(request, 'session'):
                # Check session age
                session_start = request.session.get('_session_init_timestamp_')
                if not session_start:
                    request.session['_session_init_timestamp_'] = time.time()
                else:
                    session_age = time.time() - session_start
                    if session_age > 28800:  # 8 hours
                        logger.warning(f"SECURITY: Session expired for {user}")
                        return None
                
                # Check for session hijacking indicators
                if not self.validate_session_security(request, user):
                    return None
            
            return user_auth
        
        return None
    
    def validate_session_security(self, request, user):
        """Validate session security indicators"""
        
        # Check IP consistency (basic check)
        current_ip = self.get_client_ip(request)
        session_ip = request.session.get('_session_ip')
        
        if not session_ip:
            request.session['_session_ip'] = current_ip
        elif session_ip != current_ip:
            # IP changed - potential session hijacking
            logger.warning(f"SECURITY: Session IP change for {user}: {session_ip} -> {current_ip}")
            # In production, you might want to force re-authentication
            # For now, just log the incident
        
        # Check user agent consistency
        current_ua = request.META.get('HTTP_USER_AGENT', '')
        session_ua = request.session.get('_session_user_agent')
        
        if not session_ua:
            request.session['_session_user_agent'] = current_ua
        elif session_ua != current_ua:
            logger.warning(f"SECURITY: Session User-Agent change for {user}")
        
        return True
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or 'unknown'