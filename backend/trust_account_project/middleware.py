from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages


class NoCacheAfterLogoutMiddleware:
    """
    Middleware to prevent caching of authenticated pages and redirect 
    users to login if they try to access protected pages after logout
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Define protected URLs that require authentication
        protected_paths = [
            '/dashboard/',
            '/clients/',
            '/vendors/',
            '/transactions/',
            '/bank_accounts/',
            '/settlements/',
            '/reports/',
            '/settings/',
        ]
        
        # Check if current path needs protection
        needs_auth = any(request.path.startswith(path) for path in protected_paths)
        
        if needs_auth:
            # If user is not authenticated, redirect to login
            if not request.user.is_authenticated:
                messages.warning(request, 'Please log in to access this page.')
                return redirect('/auth/login/')
            
            # Add cache control headers to prevent browser caching
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            
        return response


class SecurityHeadersMiddleware:
    """
    Middleware to add security headers
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response