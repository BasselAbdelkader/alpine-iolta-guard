"""
TAMS Security Middleware and Authentication Enhancements
Implements brute force protection and enhanced security features
"""

import logging
import time
from datetime import datetime, timedelta
from django.contrib.auth import authenticate
from django.contrib.auth.backends import ModelBackend
from django.core.cache import cache
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
import json

logger = logging.getLogger(__name__)

class BruteForceProtectionMiddleware(MiddlewareMixin):
    """
    Middleware to implement brute force protection for authentication attempts
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Configuration - can be moved to settings.py
        self.max_attempts = getattr(settings, 'BRUTE_FORCE_MAX_ATTEMPTS', 5)
        self.lockout_duration = getattr(settings, 'BRUTE_FORCE_LOCKOUT_DURATION', 900)  # 15 minutes
        self.cooldown_period = getattr(settings, 'BRUTE_FORCE_COOLDOWN', 60)  # 1 minute
        super().__init__(get_response)
    
    def process_request(self, request):
        """Check if IP is blocked before processing login attempts"""
        if self.is_login_request(request):
            client_ip = self.get_client_ip(request)
            
            # Check if IP is currently blocked
            if self.is_ip_blocked(client_ip):
                logger.warning(f"Blocked login attempt from IP: {client_ip}")
                return self.create_blocked_response(request)
            
            # Check if too many rapid attempts
            if self.is_too_many_rapid_attempts(client_ip):
                self.block_ip(client_ip, duration=self.cooldown_period)
                logger.warning(f"IP {client_ip} blocked due to rapid successive attempts")
                return self.create_rate_limit_response(request)
        
        return None
    
    def process_response(self, request, response):
        """Process response to track failed login attempts"""
        if self.is_login_request(request) and request.method == 'POST':
            client_ip = self.get_client_ip(request)
            
            # Check if login was successful (redirect or successful status)
            if response.status_code in [200, 302] and not self.has_form_errors(response):
                # Successful login - reset failed attempts
                self.reset_failed_attempts(client_ip)
                logger.info(f"Successful login from IP: {client_ip}")
            elif request.method == 'POST':
                # Failed login - increment counter
                self.record_failed_attempt(client_ip)
                
                # Check if we should block the IP
                failed_attempts = self.get_failed_attempts(client_ip)
                if failed_attempts >= self.max_attempts:
                    self.block_ip(client_ip, duration=self.lockout_duration)
                    logger.warning(f"IP {client_ip} blocked after {failed_attempts} failed attempts")
                    
                    # Return blocked response for this attempt
                    return self.create_blocked_response(request)
                else:
                    remaining = self.max_attempts - failed_attempts
                    logger.warning(f"Failed login from IP: {client_ip} ({remaining} attempts remaining)")
        
        return response
    
    def is_login_request(self, request):
        """Check if request is a login attempt"""
        login_urls = ['/admin/login/', '/auth/login/', '/accounts/login/']
        return any(request.path.startswith(url) for url in login_urls)
    
    def get_client_ip(self, request):
        """Get client IP address, handling proxies"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or 'unknown'
    
    def get_cache_key(self, ip, key_type):
        """Generate cache key for IP tracking"""
        return f"brute_force_{key_type}_{ip}"
    
    def record_failed_attempt(self, ip):
        """Record a failed login attempt"""
        cache_key = self.get_cache_key(ip, 'attempts')
        
        # Get current attempts and increment
        attempts = cache.get(cache_key, [])
        current_time = time.time()
        
        # Add current attempt
        attempts.append(current_time)
        
        # Clean up old attempts (older than lockout duration)
        cutoff_time = current_time - self.lockout_duration
        attempts = [attempt for attempt in attempts if attempt > cutoff_time]
        
        # Store updated attempts list
        cache.set(cache_key, attempts, self.lockout_duration)
        
        # Also track rapid attempts (for rate limiting)
        rapid_key = self.get_cache_key(ip, 'rapid')
        rapid_attempts = cache.get(rapid_key, [])
        rapid_attempts.append(current_time)
        
        # Keep only attempts from last minute
        rapid_cutoff = current_time - self.cooldown_period
        rapid_attempts = [attempt for attempt in rapid_attempts if attempt > rapid_cutoff]
        cache.set(rapid_key, rapid_attempts, self.cooldown_period)
        
        return len(attempts)
    
    def get_failed_attempts(self, ip):
        """Get count of failed attempts for IP"""
        cache_key = self.get_cache_key(ip, 'attempts')
        attempts = cache.get(cache_key, [])
        
        # Clean up old attempts
        current_time = time.time()
        cutoff_time = current_time - self.lockout_duration
        recent_attempts = [attempt for attempt in attempts if attempt > cutoff_time]
        
        if len(recent_attempts) != len(attempts):
            # Update cache with cleaned list
            cache.set(cache_key, recent_attempts, self.lockout_duration)
        
        return len(recent_attempts)
    
    def is_too_many_rapid_attempts(self, ip):
        """Check if IP has too many rapid attempts"""
        rapid_key = self.get_cache_key(ip, 'rapid')
        rapid_attempts = cache.get(rapid_key, [])
        
        # More than 3 attempts in the last minute is considered rapid
        return len(rapid_attempts) > 3
    
    def block_ip(self, ip, duration):
        """Block IP for specified duration"""
        cache_key = self.get_cache_key(ip, 'blocked')
        block_until = time.time() + duration
        cache.set(cache_key, block_until, duration)
        
        # Log security event
        logger.error(f"SECURITY: IP {ip} blocked for {duration} seconds due to brute force attempts")
    
    def is_ip_blocked(self, ip):
        """Check if IP is currently blocked"""
        cache_key = self.get_cache_key(ip, 'blocked')
        block_until = cache.get(cache_key)
        
        if block_until and time.time() < block_until:
            return True
        elif block_until:
            # Block expired, clean up
            cache.delete(cache_key)
        
        return False
    
    def reset_failed_attempts(self, ip):
        """Reset failed attempts counter for IP"""
        attempt_key = self.get_cache_key(ip, 'attempts')
        rapid_key = self.get_cache_key(ip, 'rapid')
        cache.delete(attempt_key)
        cache.delete(rapid_key)
    
    def has_form_errors(self, response):
        """Check if response contains form errors (indicating failed login)"""
        if hasattr(response, 'context_data') and response.context_data:
            form = response.context_data.get('form')
            if form and hasattr(form, 'errors') and form.errors:
                return True
        
        # For admin login, check content for error indicators
        if hasattr(response, 'content'):
            content_str = response.content.decode('utf-8', errors='ignore').lower()
            error_indicators = [
                'please enter the correct username and password',
                'invalid username or password', 
                'authentication failed',
                'login failed'
            ]
            return any(indicator in content_str for indicator in error_indicators)
        
        return False
    
    def create_blocked_response(self, request):
        """Create response for blocked IP"""
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX request
            return JsonResponse({
                'error': 'Too many failed login attempts. Please try again later.',
                'blocked': True,
                'retry_after': self.lockout_duration
            }, status=429)
        else:
            # Regular request
            context = {
                'error_message': 'Too many failed login attempts from your IP address. Please try again later.',
                'retry_after_minutes': self.lockout_duration // 60,
            }
            return render(request, 'registration/login_blocked.html', context, status=429)
    
    def create_rate_limit_response(self, request):
        """Create response for rate limiting"""
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': 'Please wait before attempting to login again.',
                'rate_limited': True,
                'retry_after': self.cooldown_period
            }, status=429)
        else:
            context = {
                'error_message': 'Please wait a moment before attempting to login again.',
                'retry_after_seconds': self.cooldown_period,
            }
            return render(request, 'registration/login_rate_limited.html', context, status=429)


class EnhancedInputValidationMixin:
    """
    Mixin for enhanced input validation and sanitization
    """
    
    # Common dangerous patterns to check for
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',                # JavaScript protocol
        r'vbscript:',                 # VBScript protocol
        r'onload=',                   # Event handlers
        r'onerror=',
        r'onclick=',
        r'onmouseover=',
        r'<iframe[^>]*>',             # Iframe tags
        r'<object[^>]*>',             # Object tags
        r'<embed[^>]*>',              # Embed tags
        r'eval\s*\(',                 # JavaScript eval
        r'alert\s*\(',                # JavaScript alert
        r'confirm\s*\(',              # JavaScript confirm
        r'prompt\s*\(',               # JavaScript prompt
    ]
    
    def validate_input_security(self, data):
        """
        Validate input data for security threats
        Returns (is_safe, violations_found)
        """
        import re
        violations = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    violations.extend(self._check_string_security(value, key))
        elif isinstance(data, str):
            violations.extend(self._check_string_security(data, 'input'))
        
        return len(violations) == 0, violations
    
    def _check_string_security(self, text, field_name):
        """Check individual string for security violations"""
        import re
        violations = []
        
        text_lower = text.lower()
        
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                violations.append(f"Potentially dangerous content in {field_name}: {pattern}")
        
        # Check for SQL injection patterns
        sql_patterns = [
            r'union\s+select',
            r'drop\s+table',
            r'delete\s+from',
            r'insert\s+into',
            r'update\s+.*set',
            r'--\s*$',
            r'/\*.*\*/',
            r"'\s*or\s*'",
            r'1\s*=\s*1',
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, text_lower):
                violations.append(f"Potential SQL injection in {field_name}: {pattern}")
        
        return violations
    
    def sanitize_input(self, text):
        """Basic input sanitization"""
        if not isinstance(text, str):
            return text
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Limit length (can be customized per field)
        max_length = getattr(self, 'max_input_length', 10000)
        if len(text) > max_length:
            text = text[:max_length]
        
        # Basic HTML entity encoding for display
        import html
        return html.escape(text)


# Enhanced Authentication Backend with Security Logging
class SecureAuthenticationBackend(ModelBackend):
    """
    Enhanced authentication backend with security logging
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """Enhanced authentication with security logging"""
        
        # Get client IP for logging
        client_ip = 'unknown'
        if request:
            client_ip = request.META.get('HTTP_X_FORWARDED_FOR', 
                                       request.META.get('REMOTE_ADDR', 'unknown'))
        
        try:
            # Attempt normal authentication
            result = super().authenticate(request, username, password, **kwargs)
            
            if result:
                logger.info(f"SECURITY: Successful authentication for user '{username}' from IP {client_ip}")
            else:
                logger.warning(f"SECURITY: Failed authentication attempt for user '{username}' from IP {client_ip}")
            
            return result
            
        except Exception as e:
            logger.error(f"SECURITY: Authentication error for user '{username}' from IP {client_ip}: {str(e)}")
            return None


# Signal handlers for security logging
@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """Log failed login attempts"""
    username = credentials.get('username', 'unknown')
    client_ip = 'unknown'
    
    if request:
        client_ip = request.META.get('HTTP_X_FORWARDED_FOR',
                                   request.META.get('REMOTE_ADDR', 'unknown'))
    
    logger.warning(f"SECURITY: Failed login attempt - Username: '{username}', IP: {client_ip}")