from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime, date, timedelta
import calendar
from apps.bank_accounts.models import BankAccount
from apps.clients.models import Client
from apps.bank_accounts.models import BankTransaction
from apps.settings.models import LawFirm
from django.db.models import Sum, Q, Max


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
        
        # Two balance calculations that MUST match:
        # 1. Trust Balance = Sum of all client balances
        # 2. Bank Register = Sum of all transactions in system
        bank_account = BankAccount.objects.first()

        # Bank Register Balance = ALL transactions in system (pending + cleared, exclude voided)
        context['bank_register_balance'] = bank_account.get_current_balance() if bank_account else 0

        # Trust Balance = Sum of ALL client balances
        total_client_balance = sum(client.get_current_balance() for client in Client.objects.all())
        context['trust_balance'] = total_client_balance

        # Verify they match (for health check)
        if bank_account:
            difference = abs(context['bank_register_balance'] - total_client_balance)
            context['balances_match'] = difference < 0.01
            context['balance_difference'] = difference
        else:
            context['balances_match'] = True
            context['balance_difference'] = 0

        # Count pending transactions for display
        context['pending_transactions_count'] = BankTransaction.objects.filter(
            status='pending'
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

        for client in Client.objects.all():
            balance = client.get_current_balance()

            # Determine trust status based on actual balance
            if balance > 0:
                trust_status = 'ACTIVE_WITH_FUNDS'
            elif balance == 0:
                trust_status = 'ACTIVE_ZERO_BALANCE'
            else:
                trust_status = 'NEGATIVE_BALANCE'

            trust_status_counts[trust_status] += 1

            if balance > 0:  # Still show top 5 clients with funds
                # Get client's cases - use case_title instead of case_number
                cases = client.cases.all()
                case_titles = [case.case_title for case in cases if case.is_active]

                clients_with_balances.append({
                    'client': client,
                    'balance': balance,
                    'last_activity': client.get_last_transaction_date(),
                    'cases': case_titles,
                    'trust_status': trust_status
                })

        # Active Clients = clients with funds in trust (for compliance focus)
        context['active_clients_count'] = trust_status_counts['ACTIVE_WITH_FUNDS']
        context['clients_with_balances'] = sorted(clients_with_balances, key=lambda x: x['balance'], reverse=True)[:5]
        
        # Add trust status breakdown
        context['trust_status_counts'] = trust_status_counts
        
        # Clients with no recent deposits (2+ years)
        two_years_ago = today - timedelta(days=730)
        stale_clients = []
        
        for client in Client.objects.all():
            balance = client.get_current_balance()
            if balance > 0:
                # Find last deposit through transaction items
                last_deposit = BankTransaction.objects.filter(
                    client=client,
                    transaction_type='DEPOSIT'
                ).exclude(status='voided').aggregate(Max('transaction_date'))['transaction_date__max']
                
                if last_deposit and last_deposit < two_years_ago:
                    stale_clients.append({
                        'client': client,
                        'balance': balance,
                        'last_deposit': last_deposit
                    })
        
        context['stale_clients'] = sorted(stale_clients, key=lambda x: x['balance'], reverse=True)[:3]
        context['stale_clients_count'] = len(stale_clients)
        
        # Outstanding checks (missing checks over 90 days)
        ninety_days_ago = today - timedelta(days=90)
        outstanding_checks = []

        # Find checks issued more than 90 days ago (use check_number field)
        old_checks = BankTransaction.objects.filter(
            check_number__isnull=False,
            transaction_type='WITHDRAWAL',
            transaction_date__lt=ninety_days_ago
        ).exclude(status='voided').exclude(check_number='')

        for check in old_checks:
            # Since we're using consolidated table, check if it's cleared
            if not check.status == 'cleared':
                days_outstanding = (today - check.transaction_date).days

                # Get payee from consolidated transaction data
                payee = 'Unknown'
                if check.payee:
                    payee = check.payee
                elif check.vendor:
                    payee = check.vendor.vendor_name
                elif check.client:
                    payee = check.client.full_name

                outstanding_checks.append({
                    'check': check,
                    'check_number': check.check_number,
                    'days_outstanding': days_outstanding,
                    'payee': payee
                })

        # Sort by amount (highest first) and limit to top 25
        context['outstanding_checks'] = sorted(outstanding_checks, key=lambda x: x['check'].amount, reverse=True)[:25]
        context['outstanding_checks_count'] = len(outstanding_checks)
        
        # Trust Health Assessment
        trust_health = self._calculate_trust_health()
        context.update(trust_health)
        
        # Add detailed data for health metrics
        context.update(self._get_health_details())
        
        # Add total client balance for template (for client ledger display)
        total_client_balance = sum(client.get_current_balance() for client in Client.objects.all())
        context['total_client_balance'] = total_client_balance

        # Add unallocated funds amount
        if bank_account:
            context['unallocated_funds'] = bank_account.get_current_balance() - total_client_balance
        else:
            context['unallocated_funds'] = 0
        
        # Add total health issues count for badge
        total_health_issues = len(trust_health.get('health_issues', [])) + len(trust_health.get('health_warnings', []))
        context['total_health_issues'] = total_health_issues
        
        return context
    
    def _get_health_details(self):
        """Get detailed data for each health metric"""
        details = {}
        
        # Uncleared transactions details
        uncleared_transactions = BankTransaction.objects.filter(status='pending').select_related('bank_account')
        details['uncleared_transactions_list'] = []
        for txn in uncleared_transactions:
            details['uncleared_transactions_list'].append({
                'transaction': txn,  # FIX: Include the full transaction object for API serialization
                'number': txn.transaction_number,
                'type': txn.transaction_type,
                'date': txn.transaction_date,
                'amount': txn.amount,
                'description': txn.description,
                'reference': txn.reference_number,
                'days_old': (date.today() - txn.transaction_date).days
            })
        
        # Outstanding checks details
        ninety_days_ago = date.today() - timedelta(days=90)
        old_check_transactions = BankTransaction.objects.filter(
            check_number__isnull=False,
            transaction_type='WITHDRAWAL',
            transaction_date__lt=ninety_days_ago
        ).exclude(status='voided').exclude(check_number='')

        details['outstanding_checks_list'] = []
        for check in old_check_transactions:
            if not check.status == 'cleared':
                # Get payee from consolidated transaction data
                payee = 'Unknown'
                if check.payee:
                    payee = check.payee
                elif check.vendor:
                    payee = check.vendor.vendor_name
                elif check.client:
                    payee = check.client.full_name

                details['outstanding_checks_list'].append({
                    'number': check.check_number,
                    'reference': check.check_number,  # Use check_number as reference
                    'date': check.transaction_date,
                    'amount': check.amount,
                    'payee': payee,
                    'days_outstanding': (date.today() - check.transaction_date).days
                })
        
        # Negative balance clients details
        details['negative_balance_clients'] = []
        for client in Client.objects.all():
            balance = client.get_current_balance()
            if balance < 0:
                details['negative_balance_clients'].append({
                    'name': client.full_name,
                    'balance': balance,
                    'email': client.email,
                    'phone': client.phone
                })
        
        # Recent transactions (last 10 uncleared)
        details['recent_uncleared'] = BankTransaction.objects.filter(
            status='pending'
        ).order_by('-transaction_date')[:10]

        # All uncleared transactions with days old calculation
        details['uncleared_transactions_list'] = []
        for txn in BankTransaction.objects.filter(status='pending').exclude(status='voided').order_by('-transaction_date'):
            details['uncleared_transactions_list'].append({
                'transaction': txn,
                'days_old': (date.today() - txn.transaction_date).days
            })

        return details
    
    def _calculate_trust_health(self):
        """Calculate comprehensive trust account health metrics"""
        from decimal import Decimal
        
        health_data = {
            'trust_health_score': 100,
            'trust_health_status': 'EXCELLENT',
            'trust_health_color': 'success',
            'health_issues': [],
            'health_warnings': []
        }
        
        # Get trust account and client data
        bank_account = BankAccount.objects.first()
        if not bank_account:
            health_data.update({
                'trust_health_score': 0,
                'trust_health_status': 'CRITICAL',
                'trust_health_color': 'danger',
                'health_issues': ['No trust account configured']
            })
            return health_data
        
        bank_register_balance = bank_account.get_current_balance()  # ALL transactions (Bank Register)

        # Calculate total client balances for reconciliation
        total_client_balance = sum(client.get_current_balance() for client in Client.objects.all())

        # 1. Balance Reconciliation Health (40 points max)
        # Trust Balance (sum of clients) MUST equal Bank Register Balance (sum of transactions)
        balance_difference = abs(bank_register_balance - total_client_balance)
        reconciliation_ratio = balance_difference / max(bank_register_balance, 1) if bank_register_balance > 0 else 0

        if reconciliation_ratio < 0.001:  # Less than 0.1% difference (perfect)
            reconciliation_score = 40
        elif reconciliation_ratio < 0.01:  # Less than 1% difference
            reconciliation_score = 30
            health_data['health_warnings'].append(
                f'Minor balance variance: ${balance_difference:,.2f} '
                f'(Bank Register: ${bank_register_balance:,.2f} vs Clients: ${total_client_balance:,.2f})'
            )
        elif reconciliation_ratio < 0.05:  # Less than 5% difference
            reconciliation_score = 20
            health_data['health_issues'].append(
                f'Balance reconciliation issue: ${balance_difference:,.2f} - investigate immediately'
            )
        else:
            reconciliation_score = 0
            health_data['health_issues'].append(
                f'CRITICAL balance variance: ${balance_difference:,.2f} - '
                f'Bank Register ${bank_register_balance:,.2f} vs Clients ${total_client_balance:,.2f}'
            )
        
        # 2. Negative Client Balances (25 points max)
        clients_with_negative = Client.objects.all()
        negative_clients = [c for c in clients_with_negative if c.get_current_balance() < 0]
        negative_balance_total = sum(abs(c.get_current_balance()) for c in negative_clients)
        
        if len(negative_clients) == 0:
            negative_score = 25
        elif len(negative_clients) <= 2 and negative_balance_total < 10000:
            negative_score = 15
            health_data['health_warnings'].append(f'{len(negative_clients)} client(s) with negative balance')
        elif len(negative_clients) <= 5:
            negative_score = 10
            health_data['health_issues'].append(f'{len(negative_clients)} clients with negative balances')
        else:
            negative_score = 0
            health_data['health_issues'].append(f'{len(negative_clients)} clients with negative balances ({negative_balance_total:,.2f})')
        
        # 3. Uncleared Transactions Health (20 points max)
        total_transactions = BankTransaction.objects.count()
        uncleared_transactions = BankTransaction.objects.filter(status='pending').exclude(status='voided').count()
        uncleared_ratio = uncleared_transactions / max(total_transactions, 1)

        # Always show warning if ANY uncleared transactions exist
        if uncleared_transactions == 0:
            uncleared_score = 20
        elif uncleared_ratio < 0.1:  # Less than 10% uncleared
            uncleared_score = 18
            health_data['health_warnings'].append(f'{uncleared_transactions} uncleared transactions')
        elif uncleared_ratio < 0.25:  # Less than 25% uncleared
            uncleared_score = 15
            health_data['health_warnings'].append(f'{uncleared_transactions} uncleared transactions')
        elif uncleared_ratio < 0.5:  # Less than 50% uncleared
            uncleared_score = 10
            health_data['health_warnings'].append(f'{uncleared_transactions} uncleared transactions')
        else:
            uncleared_score = 0
            health_data['health_warnings'].append(f'{uncleared_transactions} uncleared transactions')
        
        # 4. Unallocated Funds Assessment (10 points max)
        # Unallocated = funds in bank register not assigned to any client
        # Note: total_client_balance already calculated above
        unallocated_amount = bank_register_balance - total_client_balance
        unallocated_ratio = unallocated_amount / max(bank_register_balance, 1) if bank_register_balance > 0 else 0

        if 0 <= unallocated_ratio <= 0.05:  # 0-5% unallocated is normal
            surplus_score = 10
        elif 0.05 < unallocated_ratio <= 0.15:  # 5-15% unallocated needs monitoring
            surplus_score = 7
            health_data['health_warnings'].append(f'Moderate unallocated funds: {unallocated_amount:,.2f}')
        elif unallocated_ratio > 0.15:  # >15% unallocated needs investigation
            surplus_score = 5
            health_data['health_issues'].append(f'Large unallocated funds: {unallocated_amount:,.2f}')
        else:  # Negative (clients owe more than trust has)
            surplus_score = 0
            health_data['health_issues'].append(f'Trust account deficit: {abs(unallocated_amount):,.2f}')
        
        # 5. Outstanding Checks Risk (5 points max)
        # Use the same logic as dashboard - only count truly outstanding checks
        ninety_days_ago = date.today() - timedelta(days=90)
        old_check_transactions = BankTransaction.objects.filter(
            check_number__isnull=False,
            transaction_type='WITHDRAWAL',
            transaction_date__lt=ninety_days_ago
        ).exclude(status='voided').exclude(check_number='')

        # Count only checks that haven't cleared
        outstanding_count = 0
        for check in old_check_transactions:
            if not check.status == 'cleared':
                outstanding_count += 1
        
        if outstanding_count == 0:
            checks_score = 5
        elif outstanding_count <= 3:
            checks_score = 3
            health_data['health_warnings'].append(f'{outstanding_count} checks outstanding >90 days')
        else:
            checks_score = 0
            health_data['health_issues'].append(f'{outstanding_count} checks outstanding >90 days')
        
        # Calculate final score and status
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
            'negative_clients_count': len(negative_clients),
            'uncleared_transactions_count': uncleared_transactions,
            'surplus_amount': unallocated_amount,
            'total_client_balance': total_client_balance,
            # Note: Do NOT include 'trust_balance' here - it's already set correctly in get_context_data()
        })

        return health_data

class UnclearedTransactionsView(LoginRequiredMixin, TemplateView):
    """View for displaying uncleared transactions organized by age groups"""
    template_name = 'dashboard/uncleared_transactions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all uncleared transactions (pending/not cleared)
        uncleared = BankTransaction.objects.filter(
            status='pending'
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
