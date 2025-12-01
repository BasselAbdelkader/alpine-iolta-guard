from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime, date, timedelta
import calendar
from apps.bank_accounts.models import BankAccount
from apps.clients.models import Client
from apps.bank_accounts.models import BankTransaction
from apps.settings.models import LawFirm
from django.db.models import Sum, Q, Max, Case, When, F, DecimalField, Value
from decimal import Decimal


def get_all_client_balances():
    # PERFORMANCE OPTIMIZATION: Calculate all client balances in a single query
    # Instead of 194 clients * 2 queries = 388 queries, this does 1 query
    
    # Single aggregated query using CASE WHEN to calculate deposits - withdrawals
    balances = BankTransaction.objects.exclude(
        status='voided'
    ).values('client_id').annotate(
        deposits=Sum(
            Case(
                When(transaction_type='DEPOSIT', then=F('amount')),
                default=Value(0, output_field=DecimalField(max_digits=15, decimal_places=2)),
                output_field=DecimalField(max_digits=15, decimal_places=2)
            )
        ),
        withdrawals=Sum(
            Case(
                When(transaction_type='WITHDRAWAL', then=F('amount')),
                default=Value(0, output_field=DecimalField(max_digits=15, decimal_places=2)),
                output_field=DecimalField(max_digits=15, decimal_places=2)
            )
        )
    ).annotate(
        balance=F('deposits') - F('withdrawals')
    )

    # Convert to dict for fast lookup: {client_id: balance}
    balance_dict = {b['client_id']: b['balance'] for b in balances if b['client_id']}
    return balance_dict


def get_last_activities():
    # Get last transaction date for all clients in one query
    activities = BankTransaction.objects.exclude(
        status='voided'
    ).values('client_id').annotate(
        last_date=Max('transaction_date')
    )
    return {a['client_id']: a['last_date'] for a in activities if a['client_id']}


def get_last_deposits():
    # Get last deposit date for all clients in one query
    deposits = BankTransaction.objects.filter(
        transaction_type='DEPOSIT'
    ).exclude(
        status='voided'
    ).values('client_id').annotate(
        last_date=Max('transaction_date')
    )
    return {d['client_id']: d['last_date'] for d in deposits if d['client_id']}


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Dashboard'

        # Law Firm Information
        context['law_firm'] = LawFirm.get_active_firm()

        # Calculate next reconciliation date (last day of current month)
        today = date.today()
        last_day = calendar.monthrange(today.year, today.month)[1]
        next_reconciliation = date(today.year, today.month, last_day)
        context['next_reconciliation'] = next_reconciliation.strftime('%m/%d/%Y')

        # Get all client balances in a single query
        client_balance_dict = get_all_client_balances()
        
        # Get all last activity dates in a single query
        last_activity_dict = get_last_activities()

        # Bank Register Balance
        bank_account = BankAccount.objects.first()
        context['bank_register_balance'] = bank_account.get_current_balance() if bank_account else 0

        # Trust Balance = Sum of ALL client balances (using cached dict)
        total_client_balance = sum(client_balance_dict.values())
        context['trust_balance'] = total_client_balance

        # Verify they match
        if bank_account:
            difference = abs(context['bank_register_balance'] - total_client_balance)
            context['balances_match'] = difference < 0.01
            context['balance_difference'] = difference
        else:
            context['balances_match'] = True
            context['balance_difference'] = 0

        # Count pending transactions
        context['pending_transactions_count'] = BankTransaction.objects.filter(
            status__iexact='pending'
        ).exclude(status='voided').count() if bank_account else 0

        # Trust Account Clients by Status
        clients_with_balances = []
        trust_status_counts = {
            'ACTIVE_WITH_FUNDS': 0,
            'ACTIVE_ZERO_BALANCE': 0,
            'NEGATIVE_BALANCE': 0,
            'DORMANT': 0,
            'CLOSED': 0
        }

        # Prefetch clients to avoid querying them one by one if we iterate
        # But we need to iterate to check statuses
        # Let's iterate over Client.objects.all() but avoid DB calls inside
        all_clients = Client.objects.all().prefetch_related('cases')
        
        for client in all_clients:
            balance = client_balance_dict.get(client.id, Decimal('0'))
            last_activity = last_activity_dict.get(client.id)

            # Determine trust status
            if balance != 0:
                trust_status = 'ACTIVE_WITH_FUNDS'
            elif balance == 0:
                # Check dormancy logic
                if last_activity:
                    two_years_ago = today - timedelta(days=730)
                    if last_activity >= two_years_ago:
                        trust_status = 'ACTIVE_ZERO_BALANCE'
                    else:
                        trust_status = 'DORMANT'
                else:
                    trust_status = 'ACTIVE_ZERO_BALANCE'
            else:
                trust_status = 'NEGATIVE_BALANCE' # Should be caught by != 0 but covering logic gaps
            
            if balance < 0:
                 trust_status = 'NEGATIVE_BALANCE'

            trust_status_counts[trust_status] += 1

            if balance != 0:
                # Use prefetched cases
                # We need to be careful not to trigger new query. 
                # .all() on a prefetched relation is fine.
                cases = client.cases.all()
                case_titles = [case.case_title for case in cases if case.is_active]

                clients_with_balances.append({
                    'client': client,
                    'balance': balance,
                    'last_activity': last_activity,
                    'cases': case_titles,
                    'trust_status': trust_status
                })

        # Active Clients
        context['active_clients_count'] = trust_status_counts['ACTIVE_WITH_FUNDS']
        context['clients_with_balances'] = sorted(clients_with_balances, key=lambda x: x['balance'], reverse=True)[:5]
        context['trust_status_counts'] = trust_status_counts

        # Stale Clients (No recent deposits 2+ years)
        # Optimize: use pre-calculated last deposits
        last_deposits_dict = get_last_deposits()
        two_years_ago = today - timedelta(days=730)
        stale_clients = []

        for client in all_clients:
            balance = client_balance_dict.get(client.id, Decimal('0'))
            if balance != 0:
                last_deposit = last_deposits_dict.get(client.id)
                if last_deposit and last_deposit < two_years_ago:
                    stale_clients.append({
                        'client': client,
                        'balance': balance,
                        'last_deposit': last_deposit
                    })
        
        context['stale_clients'] = sorted(stale_clients, key=lambda x: x['balance'], reverse=True)[:3]
        context['stale_clients_count'] = len(stale_clients)

        # Outstanding checks
        ninety_days_ago = today - timedelta(days=90)
        outstanding_checks = []
        
        # Optimize: select_related for vendor/client to avoid N+1
        old_checks = BankTransaction.objects.filter(
            reference_number__isnull=False,
            transaction_type='WITHDRAWAL',
            transaction_date__lt=ninety_days_ago,
            status__iexact='pending'
        ).exclude(reference_number='').select_related('client', 'vendor')

        for check in old_checks:
            if True:  # Already filtered for pending status in query
                days_outstanding = (today - check.transaction_date).days
                
                payee = 'Unknown'
                if check.payee:
                    payee = check.payee
                elif check.vendor:
                    payee = check.vendor.vendor_name
                elif check.client:
                    payee = check.client.full_name
                
                outstanding_checks.append({
                    'check': check,
                    'reference_number': check.reference_number,
                    'days_outstanding': days_outstanding,
                    'payee': payee
                })
        
        context['outstanding_checks'] = sorted(outstanding_checks, key=lambda x: x['check'].amount, reverse=True)[:25]
        context['outstanding_checks_count'] = len(outstanding_checks)

        # Pass pre-calculated data to health methods
        trust_health = self._calculate_trust_health(
            bank_account, 
            context['bank_register_balance'], 
            total_client_balance,
            client_balance_dict
        )
        context.update(trust_health)

        context.update(self._get_health_details(client_balance_dict, all_clients))

        context['total_client_balance'] = total_client_balance
        if bank_account:
            context['unallocated_funds'] = context['bank_register_balance'] - total_client_balance
        else:
            context['unallocated_funds'] = 0
            
        context['total_health_issues'] = len(trust_health.get('health_issues', [])) + len(trust_health.get('health_warnings', []))

        return context

    def _get_health_details(self, client_balance_dict, all_clients):
        """Get detailed data for each health metric using pre-fetched data"""
        details = {}

        # Uncleared transactions details
        uncleared_transactions = BankTransaction.objects.filter(status__iexact='pending').select_related('bank_account', 'client', 'vendor').order_by('-transaction_date')
        
        # Consolidated list for both 'uncleared_transactions_list' and details
        txn_list = []
        for txn in uncleared_transactions:
            days_old = (date.today() - txn.transaction_date).days
            
            # Logic for serializer compatibility (DashboardAPIView expects this structure)
            txn_data = {
                'transaction': txn,
                'number': txn.transaction_number,
                'type': txn.transaction_type,
                'date': txn.transaction_date,
                'amount': txn.amount,
                'description': txn.description,
                'reference': txn.reference_number,
                'days_old': days_old
            }
            txn_list.append(txn_data)
            
        details['uncleared_transactions_list'] = txn_list

        # Outstanding checks details (reuse query logic if possible, but for now separate is okay as it's filtered)
        ninety_days_ago = date.today() - timedelta(days=90)
        old_check_transactions = BankTransaction.objects.filter(
            reference_number__isnull=False,
            transaction_type='WITHDRAWAL',
            transaction_date__lt=ninety_days_ago,
            status__iexact='pending'
        ).exclude(reference_number='').select_related('client', 'vendor')

        details['outstanding_checks_list'] = []
        for check in old_check_transactions:
            if True:  # Already filtered for pending status in query
                payee = 'Unknown'
                if check.payee:
                    payee = check.payee
                elif check.vendor:
                    payee = check.vendor.vendor_name
                elif check.client:
                    payee = check.client.full_name

                details['outstanding_checks_list'].append({
                    'number': check.reference_number,
                    'reference': check.reference_number,
                    'date': check.transaction_date,
                    'amount': check.amount,
                    'payee': payee,
                    'days_outstanding': (date.today() - check.transaction_date).days
                })

        # Negative balance clients details - OPTIMIZED to use dict
        details['negative_balance_clients'] = []
        for client in all_clients:
            balance = client_balance_dict.get(client.id, Decimal('0'))
            if balance < 0:
                details['negative_balance_clients'].append({
                    'name': client.full_name,
                    'id': client.id,
                    'balance': balance,
                    'email': client.email,
                    'phone': client.phone
                })

        # Recent transactions (last 10 uncleared) - taken from main list
        details['recent_uncleared'] = uncleared_transactions[:10]

        return details

    def _calculate_trust_health(self, bank_account, bank_register_balance, total_client_balance, client_balance_dict):
        """Calculate comprehensive trust account health metrics using passed data"""
        
        health_data = {
            'trust_health_score': 100,
            'trust_health_status': 'EXCELLENT',
            'trust_health_color': 'success',
            'health_issues': [],
            'health_warnings': []
        }

        if not bank_account:
            health_data.update({
                'trust_health_score': 0,
                'trust_health_status': 'CRITICAL',
                'trust_health_color': 'danger',
                'health_issues': ['No trust account configured']
            })
            return health_data

        # 1. Balance Reconciliation Health
        balance_difference = abs(bank_register_balance - total_client_balance)
        reconciliation_ratio = balance_difference / max(bank_register_balance, 1) if bank_register_balance > 0 else 0

        if reconciliation_ratio < 0.001:
            reconciliation_score = 40
        elif reconciliation_ratio < 0.01:
            reconciliation_score = 30
            health_data['health_warnings'].append(
                f'Minor balance variance: ${balance_difference:,.2f}'
            )
        elif reconciliation_ratio < 0.05:
            reconciliation_score = 20
            health_data['health_issues'].append(
                f'Balance reconciliation issue: ${balance_difference:,.2f}'
            )
        else:
            reconciliation_score = 0
            health_data['health_issues'].append(
                f'CRITICAL balance variance: ${balance_difference:,.2f}'
            )

        # 2. Negative Client Balances - OPTIMIZED to use dict
        # Count negative balances from the dictionary directly
        negative_clients_balances = [b for b in client_balance_dict.values() if b < 0]
        negative_count = len(negative_clients_balances)
        negative_balance_total = sum(abs(b) for b in negative_clients_balances)

        if negative_count == 0:
            negative_score = 25
        elif negative_count <= 2 and negative_balance_total < 10000:
            negative_score = 15
            health_data['health_issues'].append(f'{negative_count} client(s) with negative balance')
        elif negative_count <= 5:
            negative_score = 10
            health_data['health_issues'].append(f'{negative_count} clients with negative balances')
        else:
            negative_score = 0
            health_data['health_issues'].append(f'{negative_count} clients with negative balances ({negative_balance_total:,.2f})')

        # 3. Uncleared Transactions Health
        total_transactions = BankTransaction.objects.count()
        uncleared_transactions = BankTransaction.objects.filter(status__iexact='pending').exclude(status='voided').count()
        uncleared_ratio = uncleared_transactions / max(total_transactions, 1)

        if uncleared_transactions == 0:
            uncleared_score = 20
        elif uncleared_ratio < 0.1:
            uncleared_score = 18
            health_data['health_warnings'].append(f'{uncleared_transactions} uncleared transactions')
        elif uncleared_ratio < 0.25:
            uncleared_score = 15
            health_data['health_warnings'].append(f'{uncleared_transactions} uncleared transactions')
        elif uncleared_ratio < 0.5:
            uncleared_score = 10
            health_data['health_warnings'].append(f'{uncleared_transactions} uncleared transactions')
        else:
            uncleared_score = 0
            health_data['health_warnings'].append(f'{uncleared_transactions} uncleared transactions')

        # 4. Unallocated Funds
        unallocated_amount = bank_register_balance - total_client_balance
        unallocated_ratio = unallocated_amount / max(bank_register_balance, 1) if bank_register_balance > 0 else 0

        if 0 <= unallocated_ratio <= 0.05:
            surplus_score = 10
        elif 0.05 < unallocated_ratio <= 0.15:
            surplus_score = 7
            health_data['health_warnings'].append(f'Moderate unallocated funds: {unallocated_amount:,.2f}')
        elif unallocated_ratio > 0.15:
            surplus_score = 5
            health_data['health_issues'].append(f'Large unallocated funds: {unallocated_amount:,.2f}')
        else:
            surplus_score = 0
            health_data['health_issues'].append(f'Trust account deficit: {abs(unallocated_amount):,.2f}')

        # 5. Outstanding Checks
        # Optimize: We can just count them efficiently
        ninety_days_ago = date.today() - timedelta(days=90)
        outstanding_count = BankTransaction.objects.filter(
            reference_number__isnull=False,
            transaction_type='WITHDRAWAL',
            transaction_date__lt=ninety_days_ago,
            status__iexact='pending'
        ).exclude(reference_number='').count()

        if outstanding_count == 0:
            checks_score = 5
        elif outstanding_count <= 3:
            checks_score = 3
            health_data['health_warnings'].append(f'{outstanding_count} checks outstanding >90 days')
        else:
            checks_score = 0
            health_data['health_issues'].append(f'{outstanding_count} checks outstanding >90 days')

        total_score = reconciliation_score + negative_score + uncleared_score + surplus_score + checks_score

        if total_score >= 95:
            status, color = 'EXCELLENT', 'success'
        elif total_score >= 85:
            status, color = 'GOOD', 'success'
        elif total_score >= 70:
            status, color = 'FAIR', 'warning'
        elif total_score >= 50:
            status, color = 'POOR', 'warning'
        else:
            status, color = 'CRITICAL', 'danger'

        health_data.update({
            'trust_health_score': total_score,
            'trust_health_status': status,
            'trust_health_color': color,
            'reconciliation_score': reconciliation_score,
            'negative_balance_score': negative_score,
            'uncleared_score': uncleared_score,
            'surplus_score': surplus_score,
            'checks_score': checks_score,
            'balance_difference': balance_difference,
            'negative_clients_count': negative_count,
            'uncleared_transactions_count': uncleared_transactions,
            'surplus_amount': unallocated_amount,
            'total_client_balance': total_client_balance,
        })

        return health_data


class UnclearedTransactionsView(LoginRequiredMixin, TemplateView):
    """View for displaying uncleared transactions organized by age groups"""
    template_name = 'dashboard/uncleared_transactions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all uncleared transactions (pending/not cleared)
        uncleared = BankTransaction.objects.filter(
            status__iexact='pending'
        ).exclude(
            status='voided'
        ).select_related('client', 'case', 'vendor', 'bank_account').order_by('-transaction_date')

        # Calculate age groups based on days old
        today = date.today()
        age_groups = {
            'recent': [],      # 0-7 days
            'moderate': [],    # 8-30 days
            'old': [],         # 31-90 days
            'very_old': []     # 90+ days
        }

        total_deposits = 0
        total_withdrawals = 0

        for txn in uncleared:
            days_old = (today - txn.transaction_date).days

            # Add to appropriate age group
            if days_old <= 7:
                age_groups['recent'].append(txn)
            elif days_old <= 30:
                age_groups['moderate'].append(txn)
            elif days_old <= 90:
                age_groups['old'].append(txn)
            else:
                age_groups['very_old'].append(txn)

            # Calculate totals
            if txn.transaction_type == 'DEPOSIT':
                total_deposits += txn.amount
            elif txn.transaction_type == 'WITHDRAWAL':
                total_withdrawals += txn.amount

        # Add to context
        context['age_groups'] = age_groups
        context['recent_count'] = len(age_groups['recent'])
        context['moderate_count'] = len(age_groups['moderate'])
        context['old_count'] = len(age_groups['old'])
        context['very_old_count'] = len(age_groups['very_old'])
        context['total_count'] = uncleared.count()
        context['total_deposits'] = total_deposits
        context['total_withdrawals'] = total_withdrawals
        context['net_amount'] = total_deposits - total_withdrawals

        return context
