from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Session authentication that doesn't enforce CSRF for API endpoints.
    This allows the frontend and backend to work as one system without CSRF tokens.
    """
    def enforce_csrf(self, request):
        # Skip CSRF check for API endpoints
        return
