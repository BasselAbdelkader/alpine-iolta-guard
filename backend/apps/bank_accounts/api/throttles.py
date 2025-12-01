"""
Financial Transaction Rate Limiting (OWASP A01 - Access Control)

Security Controls:
1. Prevent automated fraud via rate limiting
2. Throttle high-risk operations more strictly
3. Protect against DoS attacks via bulk operations
4. Comply with ABA trust account security requirements

Rate Limits:
- General financial operations: 10/hour
- Withdrawals: 5/hour (stricter due to fraud risk)
- CSV bulk imports: 3/hour (resource intensive)
- Approval operations: 20/hour
"""

from rest_framework.throttling import UserRateThrottle
import logging

logger = logging.getLogger(__name__)


class FinancialTransactionThrottle(UserRateThrottle):
    """
    General rate limit for financial transactions

    Limit: 10 transactions per hour per user
    Applies to: All financial transaction creation/modification
    Rationale: Prevents automated fraud scripts
    """
    rate = '10/hour'
    scope = 'financial_transaction'

    def allow_request(self, request, view):
        """Override to add security logging"""
        allowed = super().allow_request(request, view)

        if not allowed:
            logger.warning(
                f"SECURITY: Rate limit exceeded for financial transactions. "
                f"User: {request.user.username if request.user.is_authenticated else 'Anonymous'}, "
                f"IP: {self.get_ident(request)}, "
                f"Path: {request.path}"
            )

        return allowed


class WithdrawalThrottle(UserRateThrottle):
    """
    Strict rate limit for withdrawal operations

    Limit: 5 withdrawals per hour per user
    Applies to: WITHDRAWAL and TRANSFER_OUT transactions
    Rationale: Higher fraud risk requires stricter limits
    """
    rate = '5/hour'
    scope = 'withdrawal'

    def allow_request(self, request, view):
        """Only throttle withdrawal transactions"""
        # Check if this is a withdrawal operation
        if request.method in ['POST', 'PUT', 'PATCH']:
            transaction_type = request.data.get('transaction_type', '').upper()

            if transaction_type in ['WITHDRAWAL', 'TRANSFER_OUT']:
                allowed = super().allow_request(request, view)

                if not allowed:
                    logger.error(
                        f"SECURITY: Withdrawal rate limit exceeded! "
                        f"User: {request.user.username if request.user.is_authenticated else 'Anonymous'}, "
                        f"IP: {self.get_ident(request)}, "
                        f"Amount: {request.data.get('amount', 'Unknown')}, "
                        f"This may indicate automated fraud attempt."
                    )

                return allowed

        # Not a withdrawal, allow without throttling
        return True


class BulkOperationThrottle(UserRateThrottle):
    """
    Rate limit for CSV bulk import operations

    Limit: 3 imports per hour per user
    Applies to: CSV file uploads and bulk data imports
    Rationale: Resource-intensive operations need strict limits
    """
    rate = '3/hour'
    scope = 'bulk_operation'

    def allow_request(self, request, view):
        """Override to add security logging"""
        allowed = super().allow_request(request, view)

        if not allowed:
            logger.warning(
                f"SECURITY: Bulk operation rate limit exceeded. "
                f"User: {request.user.username if request.user.is_authenticated else 'Anonymous'}, "
                f"IP: {self.get_ident(request)}, "
                f"This may indicate DoS attempt via resource exhaustion."
            )

        return allowed


class TransactionApprovalThrottle(UserRateThrottle):
    """
    Rate limit for transaction approval operations

    Limit: 20 approvals per hour per user
    Applies to: Approval/rejection of pending transactions
    Rationale: Prevent rapid-fire approval attacks
    """
    rate = '20/hour'
    scope = 'transaction_approval'

    def allow_request(self, request, view):
        """Override to add security logging"""
        allowed = super().allow_request(request, view)

        if not allowed:
            logger.warning(
                f"SECURITY: Transaction approval rate limit exceeded. "
                f"User: {request.user.username if request.user.is_authenticated else 'Anonymous'}, "
                f"IP: {self.get_ident(request)}, "
                f"This may indicate unauthorized mass-approval attempt."
            )

        return allowed


class CheckPrintingThrottle(UserRateThrottle):
    """
    Rate limit for check printing operations

    Limit: 10 checks per hour per user
    Applies to: Check generation and printing
    Rationale: Prevent automated check fraud
    """
    rate = '10/hour'
    scope = 'check_printing'

    def allow_request(self, request, view):
        """Override to add security logging"""
        allowed = super().allow_request(request, view)

        if not allowed:
            logger.error(
                f"SECURITY: Check printing rate limit exceeded! "
                f"User: {request.user.username if request.user.is_authenticated else 'Anonymous'}, "
                f"IP: {self.get_ident(request)}, "
                f"This may indicate check fraud attempt."
            )

        return allowed


# Throttle class mapping for easy import
THROTTLE_CLASSES = {
    'financial': FinancialTransactionThrottle,
    'withdrawal': WithdrawalThrottle,
    'bulk': BulkOperationThrottle,
    'approval': TransactionApprovalThrottle,
    'check': CheckPrintingThrottle,
}
