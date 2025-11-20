from rest_framework import permissions


class IsTrustAccountUser(permissions.BasePermission):
    """
    Custom permission for trust account users.
    Ensures user is authenticated and has access to trust account data.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # For now, authenticated users can access all trust account data
        # This can be enhanced with role-based permissions later
        return request.user and request.user.is_authenticated


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for owner (if object has user field)
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # If no user field, allow authenticated users
        return request.user and request.user.is_authenticated