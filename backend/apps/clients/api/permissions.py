"""
SECURITY FIX C2: IDOR Vulnerability Protection
Per-object permissions for client access based on user roles

This module prevents Insecure Direct Object Reference (IDOR) attacks by ensuring
users can only access clients they are authorized to see based on their role.
"""

import logging
from rest_framework.permissions import BasePermission

logger = logging.getLogger(__name__)


class CanAccessClient(BasePermission):
    """
    Per-object permission to check if user can access specific client
    
    Implements Role-Based Access Control (RBAC) for client data:
    
    **Access Rules:**
    - **Superusers:** Full access to all clients
    - **Managing Attorneys:** Full access to all clients
    - **Bookkeepers:** Read-only access to all clients
    - **Staff Attorneys:** Access to clients via assigned_users field
    - **Paralegals:** Access to clients via assigned_users field  
    - **System Admins:** No financial data access (denied)
    
    **Security:**
    - Logs all unauthorized access attempts
    - Prevents IDOR attacks (ID enumeration)
    - Enforces attorney-client privilege
    - Compliance with trust account rules
    """
    
    def has_permission(self, request, view):
        """
        Check if user has general permission to access client endpoints
        This is called before has_object_permission
        """
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            logger.warning(f"Unauthenticated access attempt to client API from {request.META.get('REMOTE_ADDR')}")
            return False
        
        # System admins cannot access financial data
        if hasattr(request.user, 'profile') and request.user.profile.role == 'system_admin':
            logger.warning(f"System admin {request.user} attempted client access - denied (no financial access)")
            return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user can access this specific client object
        
        Args:
            request: HTTP request
            view: ViewSet handling the request
            obj: Client object being accessed
            
        Returns:
            bool: True if access allowed, False otherwise
        """
        user = request.user
        
        # Superusers: full access
        if user.is_superuser:
            logger.debug(f"Superuser {user} accessing client {obj.id}")
            return True
        
        # Check if user has profile
        if not hasattr(user, 'profile'):
            logger.error(f"User {user} has no profile - denying access to client {obj.id}")
            return False
        
        role = user.profile.role
        
        # Managing attorneys: full access
        if role == 'managing_attorney':
            logger.debug(f"Managing attorney {user} accessing client {obj.id}")
            return True
        
        # Bookkeepers: read-only access to all
        if role == 'bookkeeper':
            if request.method in ['GET', 'HEAD', 'OPTIONS']:
                logger.debug(f"Bookkeeper {user} viewing client {obj.id}")
                return True
            else:
                logger.warning(
                    f"SECURITY: Bookkeeper {user} attempted write operation ({request.method}) "
                    f"on client {obj.id} - denied (read-only role)"
                )
                return False
        
        # Staff attorneys and paralegals: access via assigned_users
        if role in ['staff_attorney', 'paralegal']:
            # Check if user is assigned to this client
            has_access = obj.assigned_users.filter(id=user.id).exists()
            
            if has_access:
                logger.debug(f"{role.title()} {user} accessing assigned client {obj.id}")
                return True
            else:
                logger.warning(
                    f"SECURITY: {role.title()} {user} attempted access to unassigned "
                    f"client {obj.id} ({obj.full_name}) - denied (IDOR attempt blocked)"
                )
                return False
        
        # System admins: no financial access (already blocked in has_permission)
        if role == 'system_admin':
            logger.warning(f"SECURITY: System admin {user} attempted client {obj.id} access - denied")
            return False
        
        # Unknown role: deny and log error
        logger.error(
            f"SECURITY: Unknown role '{role}' for user {user} - "
            f"denying access to client {obj.id} (configuration error)"
        )
        return False
