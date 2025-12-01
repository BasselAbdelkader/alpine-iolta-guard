from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from apps.dashboard.views import DashboardView, UnclearedTransactionsView
from apps.settings.models import LawFirm
from datetime import date


class LawFirmAPIView(APIView):
    """
    Lightweight API that returns ONLY law firm info
    Used by all pages for sidebar/header - STATIC VALUES
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Return static hardcoded law firm info
        return Response({
            'firm_name': 'IOLTA Guard Insurance Law',
            'address': '',
            'address_line2': '',
            'city': 'San Francisco',
            'state': 'CA',
            'zip_code': '',
            'phone': '(415) 555-0100',
            'email': 'info@ioltaguard.com',
        })


class DashboardAPIView(APIView):
    """
    Dashboard API that reuses existing DashboardView logic
    Returns all dashboard data as JSON for frontend consumption
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Create an instance of the existing DashboardView
        dashboard_view = DashboardView()
        dashboard_view.request = request

        # Get all the context data (reuses existing business logic!)
        try:
            context = dashboard_view.get_context_data(**{})
        except Exception as e:
            # Log the error and return a proper response
            import traceback
            traceback.print_exc()
            return Response({
                'error': str(e),
                'detail': 'Error loading dashboard data'
            }, status=500)

        # Convert to JSON-serializable format
        data = {
            'law_firm': self._serialize_law_firm(context.get('law_firm')),
            'next_reconciliation': context.get('next_reconciliation'),
            'bank_register_balance': str(context.get('bank_register_balance', 0)),
            'trust_balance': str(context.get('trust_balance', 0)),
            'balances_match': context.get('balances_match', True),
            'balance_difference': str(context.get('balance_difference', 0)),
            'pending_transactions_count': context.get('pending_transactions_count', 0),
            'active_clients_count': context.get('active_clients_count', 0),
            'clients_with_balances': self._serialize_clients_with_balances(context.get('clients_with_balances', [])),
            'trust_status_counts': context.get('trust_status_counts', {}),
            'stale_clients': self._serialize_stale_clients(context.get('stale_clients', [])),
            'stale_clients_count': context.get('stale_clients_count', 0),
            'outstanding_checks': self._serialize_outstanding_checks(context.get('outstanding_checks', [])),
            'outstanding_checks_count': context.get('outstanding_checks_count', 0),
            'trust_health': {
                'score': context.get('trust_health_score', 0),
                'status': context.get('trust_health_status', 'UNKNOWN'),
                'color': context.get('trust_health_color', 'secondary'),
                'issues': context.get('health_issues', []),
                'warnings': context.get('health_warnings', []),
            },
            'health_details': {
                'uncleared_transactions': self._serialize_uncleared_transactions(
                    context.get('uncleared_transactions_list', [])
                ),
                'outstanding_checks_list': self._serialize_outstanding_checks_details(
                    context.get('outstanding_checks_list', [])
                ),
                'negative_balance_clients': context.get('negative_balance_clients', []),
            },
            'total_client_balance': str(context.get('total_client_balance', 0)),
            'unallocated_funds': str(context.get('unallocated_funds', 0)),
            'total_health_issues': context.get('total_health_issues', 0),
        }

        return Response(data)

    def _serialize_law_firm(self, law_firm):
        """Convert law firm object to JSON"""
        if not law_firm:
            return None

        return {
            'firm_name': law_firm.firm_name,
            'address': law_firm.address_line1,
            'address_line2': law_firm.address_line2 or '',
            'city': law_firm.city,
            'state': law_firm.state,
            'zip_code': law_firm.zip_code,
            'phone': law_firm.phone,
            'email': law_firm.email,
        }

    def _serialize_clients_with_balances(self, clients_list):
        """Convert clients with balances to JSON"""
        result = []
        for item in clients_list:
            client = item.get('client')
            if client:
                result.append({
                    'id': client.id,
                    'full_name': client.full_name,
                    'email': client.email,
                    'phone': client.phone,
                    'balance': str(item.get('balance', 0)),
                    'last_activity': item.get('last_activity').strftime('%m/%d/%Y') if item.get('last_activity') else None,
                    'cases': item.get('cases', []),
                    'trust_status': item.get('trust_status', 'UNKNOWN'),
                })
        return result

    def _serialize_stale_clients(self, stale_list):
        """Convert stale clients to JSON"""
        result = []
        for item in stale_list:
            client = item.get('client')
            if client:
                result.append({
                    'id': client.id,
                    'full_name': client.full_name,
                    'balance': str(item.get('balance', 0)),
                    'last_deposit': item.get('last_deposit').strftime('%m/%d/%Y') if item.get('last_deposit') else None,
                })
        return result

    def _serialize_outstanding_checks(self, checks_list):
        """Convert outstanding checks to JSON"""
        result = []
        for item in checks_list:
            check = item.get('check')
            if check:
                result.append({
                    'id': check.id,
                    'bank_account_id': check.bank_account_id,
                    'reference_number': item.get('reference_number'),
                    'date_issued': check.transaction_date.strftime('%m/%d/%Y'),
                    'payee': item.get('payee', 'Unknown'),
                    'client_name': check.client.full_name if check.client else 'N/A',
                    'case_number': check.case.case_number if check.case else 'N/A',
                    'description': check.description or '',
                    'amount': str(check.amount),
                    'days_outstanding': item.get('days_outstanding', 0),
                    'status': check.status,
                })
        return result

    def _serialize_uncleared_transactions(self, transactions_list):
        """Convert uncleared transactions to JSON"""
        result = []
        for item in transactions_list:
            txn = item.get('transaction')
            if txn:
                # Get client/vendor name
                client_name = txn.client.full_name if txn.client else None
                vendor_name = txn.vendor.vendor_name if txn.vendor else None
                payee_name = txn.payee if txn.payee else (client_name or vendor_name or 'Unknown')

                result.append({
                    'id': txn.id,
                    'transaction_number': txn.transaction_number,
                    'date': txn.transaction_date.strftime('%m/%d/%Y'),
                    'type': txn.transaction_type,
                    'amount': str(txn.amount),
                    'description': txn.description or '',
                    'status': txn.status,  # FIX: Include actual status field
                    'client': client_name,
                    'payee': payee_name,
                    'days_pending': item.get('days_old', 0),
                })
        return result

    def _serialize_outstanding_checks_details(self, checks_list):
        """Convert outstanding checks details to JSON"""
        result = []
        for item in checks_list:
            result.append({
                'reference_number': item.get('number'),
                'reference': item.get('reference'),
                'date': item.get('date').strftime('%m/%d/%Y') if item.get('date') else None,
                'amount': str(item.get('amount', 0)),
                'payee': item.get('payee', 'Unknown'),
                'days_outstanding': item.get('days_outstanding', 0),
            })
        return result


class UnclearedTransactionsAPIView(APIView):
    """
    Uncleared Transactions API that reuses existing UnclearedTransactionsView logic
    Returns all uncleared transactions grouped by age for frontend consumption
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Create an instance of the existing UnclearedTransactionsView
        uncleared_view = UnclearedTransactionsView()
        uncleared_view.request = request

        # Get all the context data (reuses existing business logic!)
        try:
            context = uncleared_view.get_context_data(**{})
        except Exception as e:
            # Log the error and return a proper response
            import traceback
            traceback.print_exc()
            return Response({
                'error': str(e),
                'detail': 'Error loading uncleared transactions data'
            }, status=500)

        # Convert to JSON-serializable format
        data = {
            'total_count': context.get('total_count', 0),
            'total_deposits': str(context.get('total_deposits', 0)),
            'total_withdrawals': str(context.get('total_withdrawals', 0)),
            'net_amount': str(context.get('net_amount', 0)),
            'recent_count': context.get('recent_count', 0),
            'moderate_count': context.get('moderate_count', 0),
            'old_count': context.get('old_count', 0),
            'very_old_count': context.get('very_old_count', 0),
            'age_groups': {
                'recent': self._serialize_transactions(context.get('age_groups', {}).get('recent', [])),
                'moderate': self._serialize_transactions(context.get('age_groups', {}).get('moderate', [])),
                'old': self._serialize_transactions(context.get('age_groups', {}).get('old', [])),
                'very_old': self._serialize_transactions(context.get('age_groups', {}).get('very_old', [])),
            }
        }

        return Response(data)

    def _serialize_transactions(self, transactions_list):
        """Convert transactions to JSON"""
        result = []
        today = date.today()

        for txn in transactions_list:
            # Calculate days old
            days_old = (today - txn.transaction_date).days

            # Get client/vendor/payee name
            client_name = txn.client.full_name if txn.client else None
            vendor_name = txn.vendor.vendor_name if txn.vendor else None
            case_number = txn.case.case_number if txn.case else None
            payee_name = txn.payee if txn.payee else (client_name or vendor_name)

            result.append({
                'id': txn.id,
                'transaction_number': txn.transaction_number,
                'transaction_date': txn.transaction_date.strftime('%m/%d/%Y'),
                'transaction_type': txn.transaction_type,
                'amount': str(txn.amount),
                'description': txn.description or '',
                'reference_number': txn.reference_number or '',
                'client': client_name,
                'case': case_number,
                'vendor': vendor_name,
                'payee': payee_name,
                'days_old': days_old,
                'status': txn.status,
            })

        return result
