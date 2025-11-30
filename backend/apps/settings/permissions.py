"""
COMPLIANCE CONTROL #2: ROLE-BASED ACCESS CONTROL (RBAC)

This module provides two types of permission enforcement:
1. Class-based permissions (for DRF ViewSets)
2. Decorator-based permissions (for function-based views and additional control)

Usage:
    # Class-based (existing):
    class MyViewSet(viewsets.ModelViewSet):
        permission_classes = [HasFinancialAccess, CanApproveTransactions]

    # Decorator-based (new):
    from apps.settings.permissions import require_role, require_permission

    @require_role(['managing_attorney', 'bookkeeper'])
    def my_view(request):
        pass
"""
from rest_framework import permissions
from functools import wraps
from rest_framework.response import Response
from rest_framework import status


class HasFinancialAccess(permissions.BasePermission):
    """
    Permission class that blocks System Administrators from accessing financial data.

    Allows access to:
    - Managing Attorney
    - Staff Attorney
    - Paralegal
    - Bookkeeper

    Blocks access to:
    - System Administrator
    """

    message = "System Administrators do not have access to client or financial data."

    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers always have access (backward compatibility)
        if request.user.is_superuser:
            return True

        # Check if user has profile
        try:
            profile = request.user.profile
        except Exception:
            # No profile = allow access (backward compatibility for existing users)
            return True

        # Block System Administrators
        if profile.role == 'system_admin':
            return False

        # Allow all other roles
        return True


class CanApproveTransactions(permissions.BasePermission):
    """
    Permission for approving transactions.
    Only Managing Attorneys can approve transactions.
    """

    message = "Only Managing Attorneys can approve transactions."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        try:
            profile = request.user.profile
            return profile.can_approve_transactions
        except Exception:
            return False


class CanReconcileAccounts(permissions.BasePermission):
    """
    Permission for reconciling bank accounts.
    Managing Attorneys and Bookkeepers can reconcile.
    """

    message = "Only Managing Attorneys and Bookkeepers can reconcile accounts."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        try:
            profile = request.user.profile
            return profile.can_reconcile
        except Exception:
            return False


class CanPrintChecks(permissions.BasePermission):
    """
    Permission for printing checks.
    Managing Attorneys and Bookkeepers can print checks.
    """

    message = "Only Managing Attorneys and Bookkeepers can print checks."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        try:
            profile = request.user.profile
            return profile.can_print_checks
        except Exception:
            return False


class CanManageUsers(permissions.BasePermission):
    """
    Permission for managing users.
    Managing Attorneys and System Administrators can manage users.
    """

    message = "Only Managing Attorneys and System Administrators can manage users."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        try:
            profile = request.user.profile
            return profile.can_manage_users
        except Exception:
            return False


# ============================================================================
# DECORATOR-BASED PERMISSIONS (Compliance Control #2)
# ============================================================================

def require_role(allowed_roles):
    """
    Decorator to restrict API access based on user role.

    Supports both Django views and DRF ViewSet actions.

    Args:
        allowed_roles (list): List of role strings that are allowed access

    Returns:
        Decorated function that checks role before allowing access

    Example:
        # For regular views:
        @require_role(['managing_attorney', 'staff_attorney'])
        def create_transaction(request):
            pass

        # For ViewSet actions:
        @require_role(['managing_attorney', 'staff_attorney'])
        @action(detail=True, methods=['post'])
        def void(self, request, pk=None):
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(first_arg, *args, **kwargs):
            # Detect if this is a ViewSet method or regular view function
            # ViewSet: first_arg is 'self', second arg is 'request'
            # Regular view: first_arg is 'request'
            from rest_framework.viewsets import ViewSetMixin

            if isinstance(first_arg, ViewSetMixin):
                # This is a ViewSet action method: wrapper(self, request, ...)
                viewset_instance = first_arg
                request = args[0] if args else kwargs.get('request')
                remaining_args = args[1:] if len(args) > 1 else ()
            else:
                # This is a regular view function: wrapper(request, ...)
                request = first_arg
                remaining_args = args
                viewset_instance = None

            # Check if user is authenticated
            if not request.user or not request.user.is_authenticated:
                return Response(
                    {
                        'error': 'Authentication required',
                        'detail': 'You must be logged in to access this resource.'
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Get user profile
            try:
                profile = request.user.userprofile
            except Exception:
                # Try alternate attribute name
                try:
                    profile = request.user.profile
                except Exception:
                    return Response(
                        {
                            'error': 'No user profile',
                            'detail': 'Your user account does not have a role assigned. Please contact your administrator.'
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )

            # Superusers bypass role checks
            if request.user.is_superuser:
                # Call original function with correct arguments based on type
                if viewset_instance is not None:
                    return view_func(viewset_instance, request, *remaining_args, **kwargs)
                else:
                    return view_func(request, *remaining_args, **kwargs)

            # Check if user's role is in allowed roles
            if profile.role not in allowed_roles:
                return Response(
                    {
                        'error': 'Insufficient permissions',
                        'detail': f'Your role ({profile.get_role_display()}) does not have permission to perform this action. Required role: {", ".join([r.replace("_", " ").title() for r in allowed_roles])}',
                        'user_role': profile.role,
                        'required_roles': allowed_roles
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            # Role check passed, execute view with correct arguments
            if viewset_instance is not None:
                return view_func(viewset_instance, request, *remaining_args, **kwargs)
            else:
                return view_func(request, *remaining_args, **kwargs)

        return wrapper
    return decorator


def require_permission(permission_name):
    """
    Decorator to restrict API access based on specific permission flag.

    Args:
        permission_name (str): Name of permission flag to check
            - 'can_approve_transactions'
            - 'can_reconcile'
            - 'can_print_checks'
            - 'can_manage_users'

    Returns:
        Decorated function that checks permission before allowing access

    Example:
        @require_permission('can_approve_transactions')
        def approve_transaction(request):
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check if user is authenticated
            if not request.user or not request.user.is_authenticated:
                return Response(
                    {
                        'error': 'Authentication required',
                        'detail': 'You must be logged in to access this resource.'
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Get user profile
            try:
                profile = request.user.userprofile
            except Exception:
                # Try alternate attribute name
                try:
                    profile = request.user.profile
                except Exception:
                    return Response(
                        {
                            'error': 'No user profile',
                            'detail': 'Your user account does not have a role assigned. Please contact your administrator.'
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )

            # Superusers bypass permission checks
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Check if user has the required permission
            has_permission = getattr(profile, permission_name, False)

            if not has_permission:
                # Get human-readable permission name
                permission_display = permission_name.replace('can_', '').replace('_', ' ').title()

                return Response(
                    {
                        'error': 'Insufficient permissions',
                        'detail': f'You do not have permission to perform this action. Required permission: {permission_display}',
                        'user_role': profile.role,
                        'required_permission': permission_name
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            # Permission check passed, execute view
            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator


def require_any_role(allowed_roles):
    """
    Alias for require_role for clarity.
    Same as require_role - checks if user has ANY of the specified roles.
    """
    return require_role(allowed_roles)


def require_all_permissions(*permission_names):
    """
    Decorator to require multiple permissions (user must have ALL).

    Args:
        *permission_names: Variable number of permission flag names

    Example:
        @require_all_permissions('can_approve_transactions', 'can_reconcile')
        def reconcile_and_approve(request):
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check if user is authenticated
            if not request.user or not request.user.is_authenticated:
                return Response(
                    {
                        'error': 'Authentication required',
                        'detail': 'You must be logged in to access this resource.'
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Get user profile
            try:
                profile = request.user.userprofile
            except Exception:
                # Try alternate attribute name
                try:
                    profile = request.user.profile
                except Exception:
                    return Response(
                        {
                            'error': 'No user profile',
                            'detail': 'Your user account does not have a role assigned. Please contact your administrator.'
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )

            # Superusers bypass permission checks
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Check all permissions
            missing_permissions = []
            for permission_name in permission_names:
                if not getattr(profile, permission_name, False):
                    missing_permissions.append(permission_name.replace('can_', '').replace('_', ' ').title())

            if missing_permissions:
                return Response(
                    {
                        'error': 'Insufficient permissions',
                        'detail': f'You are missing required permissions: {", ".join(missing_permissions)}',
                        'user_role': profile.role,
                        'required_permissions': list(permission_names)
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            # All permissions check passed, execute view
            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator


def get_user_permissions(user):
    """
    Get all permissions for a user as a dictionary.

    Args:
        user: Django User object

    Returns:
        dict with role and permission flags, or None if no profile
    """
    try:
        profile = user.userprofile
    except Exception:
        try:
            profile = user.profile
        except Exception:
            return None

    return {
        'role': profile.role,
        'role_display': profile.get_role_display(),
        'can_approve_transactions': profile.can_approve_transactions,
        'can_reconcile': profile.can_reconcile,
        'can_print_checks': profile.can_print_checks,
        'can_manage_users': profile.can_manage_users,
    }
