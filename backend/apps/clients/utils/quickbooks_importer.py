"""
QuickBooks Importer
===================
Handles importing parsed QuickBooks data into IOLTA Guard database.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Tuple

from django.db import transaction
from django.utils import timezone

from apps.clients.models import Client, Case
from apps.bank_accounts.models import BankTransaction, BankAccount
from apps.vendors.models import Vendor
from django.db import connection


class QuickBooksImporter:
    """Import QuickBooks data into IOLTA Guard."""

    def __init__(self, user, filename=None):
        """
        Initialize importer.

        Args:
            user: User performing the import
            filename: Original CSV filename (optional)
        """
        self.user = user
        self.filename = filename
        self.import_log_id = None

        # Get default bank account for transactions
        self.bank_account = BankAccount.objects.first()
        if not self.bank_account:
            raise ValueError("No bank account found. Please create a bank account first.")

        self.stats = {
            'clients_created': 0,
            'clients_existing': 0,
            'vendors_created': 0,
            'vendors_existing': 0,
            'cases_created': 0,
            'transactions_imported': 0,
            'transactions_skipped': 0,
            'errors': []
        }

    def import_data(self, validated_data: List[Dict]) -> Dict:
        """
        Import validated QuickBooks data.

        Args:
            validated_data: List of validated transaction dicts

        Returns:
            dict: Import statistics and results
        """
        start_time = timezone.now()

        # Create import log entry
        self._create_import_log(len(validated_data))

        try:
            # Step 1: Group transactions by client
            grouped = self._group_by_client(validated_data)

            # Step 2: Process each client (each in its own transaction)
            for client_name, transactions in grouped.items():
                try:
                    # Use atomic transaction per client, not globally
                    # This way one client's error doesn't affect others
                    with transaction.atomic():
                        self._import_client_data(client_name, transactions)
                except Exception as e:
                    self.stats['errors'].append({
                        'client': client_name,
                        'error': str(e)
                    })
                    # Continue with other clients

            # Calculate duration
            end_time = timezone.now()
            duration = (end_time - start_time).total_seconds()

            # Update import log with final status
            status = 'completed' if not self.stats['errors'] else 'partial'
            self._update_import_log(status, end_time)

            return {
                'success': True,
                'summary': {
                    **self.stats,
                    'duration_seconds': round(duration, 2),
                    'import_log_id': self.import_log_id
                }
            }
        except Exception as e:
            # Mark import as failed
            self._update_import_log('failed', timezone.now())
            raise

    def _group_by_client(self, data: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group transactions by client name.

        Args:
            data: Validated transaction data

        Returns:
            dict: {client_name: [transactions]}
        """
        grouped = {}
        for row in data:
            client = row['account']
            if client not in grouped:
                grouped[client] = []
            grouped[client].append(row)
        return grouped

    def _import_client_data(self, client_name: str, transactions: List[Dict]):
        """
        Import data for one client (client, case, transactions).

        Args:
            client_name: Name of the client
            transactions: List of transactions for this client
        """
        # Step 1: Get or create client
        client = self._get_or_create_client(client_name)

        # Step 2: Create case for this import
        case = self._create_case(client, transactions)

        # Step 3: Import transactions
        self._import_transactions(case, transactions)

    def _split_name(self, full_name: str) -> Tuple[str, str]:
        """
        Split full name into first and last name.

        Args:
            full_name: Full name from QuickBooks

        Returns:
            tuple: (first_name, last_name)
        """
        parts = full_name.strip().split(None, 1)  # Split on first whitespace
        if len(parts) == 2:
            return parts[0], parts[1]
        else:
            return parts[0], ''  # Only one name provided

    def _get_or_create_client(self, client_name: str) -> Client:
        """
        Get existing client or create new one.

        Args:
            client_name: Name of the client

        Returns:
            Client: Client instance
        """
        # Check if client exists (by client_name)
        existing_client = Client.objects.filter(
            client_name=client_name,
        ).first()

        if existing_client:
            self.stats['clients_existing'] += 1
            return existing_client

        # Generate unique client number
        # Format: QB-0001, QB-0002, etc.
        existing_numbers = Client.objects.filter(
            client_number__startswith='QB-'
        ).values_list('client_number', flat=True)

        if existing_numbers:
            # Extract numeric parts and find max
            max_num = 0
            for num in existing_numbers:
                try:
                    # Extract number from "QB-0001" format
                    numeric_part = int(num.split('-')[1])
                    max_num = max(max_num, numeric_part)
                except (ValueError, IndexError):
                    continue
            new_number_int = max_num + 1
        else:
            new_number_int = 1

        client_number = f'QB-{new_number_int:04d}'

        # Create new client with data_source='csv'
        client = Client.objects.create(
            client_number=client_number,
            client_name=client_name,
            is_active=True,
            data_source='csv'
        )

        self.stats['clients_created'] += 1
        return client

    def _get_or_create_vendor(self, payee_name: str) -> Vendor:
        """
        Get existing vendor or create new one from payee name.

        Args:
            payee_name: Name of the payee/vendor from CSV

        Returns:
            Vendor: Vendor instance
        """
        if not payee_name or not payee_name.strip():
            return None

        payee_name = payee_name.strip()

        # Check if vendor exists (by vendor_name)
        existing_vendor = Vendor.objects.filter(
            vendor_name=payee_name
        ).first()

        if existing_vendor:
            self.stats['vendors_existing'] += 1
            return existing_vendor

        # Generate unique vendor number
        # Format: QBVEN-0001, QBVEN-0002, etc.
        existing_numbers = Vendor.objects.filter(
            vendor_number__startswith='QBVEN-'
        ).values_list('vendor_number', flat=True)

        if existing_numbers:
            # Extract numeric parts and find max
            max_num = 0
            for num in existing_numbers:
                try:
                    # Extract number from "QBVEN-0001" format
                    numeric_part = int(num.split('-')[1])
                    max_num = max(max_num, numeric_part)
                except (ValueError, IndexError):
                    continue
            new_number_int = max_num + 1
        else:
            new_number_int = 1

        vendor_number = f'QBVEN-{new_number_int:04d}'

        # Create new vendor with data_source='csv_import'
        vendor = Vendor.objects.create(
            vendor_number=vendor_number,
            vendor_name=payee_name,
            is_active=True,
            data_source='csv_import'
        )

        self.stats['vendors_created'] += 1
        return vendor

    def _create_case(self, client: Client, transactions: List[Dict]) -> Case:
        """
        Create case for imported transactions.

        Case name format: "{Client Name} Case"

        Args:
            client: Client instance
            transactions: List of transactions (to determine opened_date)

        Returns:
            Case: Created case instance
        """
        # Case naming: "{Client Name} Case"
        full_name = f"{client.client_name}".strip()
        case_title = f"{full_name} Case"

        # Get date of first transaction
        dates = [t['date'] for t in transactions if t['date']]
        first_transaction_date = min(dates) if dates else datetime.now().date()

        # Generate unique case number
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        case_number = f'QB-{timestamp}-{client.id}'

        # Create case with data_source='csv'
        case = Case.objects.create(
            client=client,
            case_title=case_title,
            case_number=case_number,
            case_status='Open',
            opened_date=first_transaction_date,
            case_description=f'Imported from QuickBooks on {datetime.now().strftime("%Y-%m-%d")}. '
                           f'Contains {len(transactions)} transactions.',
            is_active=True,
            data_source='csv'
        )

        self.stats['cases_created'] += 1
        return case

    def _import_transactions(self, case: Case, transactions: List[Dict]):
        """
        Import all transactions for a case.

        Args:
            case: Case instance
            transactions: List of transaction dicts
        """
        # Sort transactions by date (oldest first) to ensure deposits happen before withdrawals
        transactions = sorted(transactions, key=lambda t: t.get("date", ""))

        for trans_data in transactions:
            try:
                self._create_transaction(case, trans_data)
                self.stats['transactions_imported'] += 1
            except Exception as e:
                self.stats['transactions_skipped'] += 1
                self.stats['errors'].append({
                    'row': trans_data.get('row_number'),
                    'error': f'Failed to import transaction: {str(e)}'
                })

    def _create_transaction(self, case: Case, trans_data: Dict):
        """
        Create a single transaction.

        Args:
            case: Case instance
            trans_data: Transaction data dict
        """
        # Determine transaction type for IOLTA Guard
        qb_type = trans_data['type']
        amount_type = trans_data['amount_type']

        # Map QuickBooks type to IOLTA Guard type
        if qb_type in ['Check', 'Expense'] and amount_type == 'payment':
            transaction_type = 'Withdrawal'
        elif qb_type in ['Deposit', 'Journal'] and amount_type == 'deposit':
            transaction_type = 'Deposit'
        else:
            raise ValueError(f'Cannot determine transaction type for {qb_type}/{amount_type}')

        # Determine status based on reconciliation
        qb_status = trans_data.get('reconciliation_status', '')
        if qb_status in ['Reconciled', 'Cleared']:
            status = 'Cleared'
        else:
            status = 'Pending'

        # Get or create vendor from payee field
        vendor = None
        if trans_data.get('payee'):
            vendor = self._get_or_create_vendor(trans_data['payee'])

        # Create transaction with data_source='csv'
        BankTransaction.objects.create(
            bank_account=self.bank_account,
            client=case.client,
            case=case,
            vendor=vendor,  # Link to created vendor
            transaction_date=trans_data['date'],
            transaction_type=transaction_type,
            amount=trans_data['amount'],
            payee=trans_data['payee'] or '',
            reference_number=trans_data['ref_no'] or None,
            description=trans_data['memo'] or '',
            status=status,
            created_by=self.user,
            data_source='csv'
        )

    def get_import_stats(self) -> Dict:
        """
        Get current import statistics.

        Returns:
            dict: Import stats
        """
        return self.stats

    def _create_import_log(self, total_rows: int):
        """
        Create import log entry at start of import.

        Args:
            total_rows: Total number of rows to import
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO import_logs (
                    import_type,
                    filename,
                    status,
                    total_rows,
                    created_by_id,
                    started_at,
                    created_at,
                    updated_at
                ) VALUES (
                    'quickbooks_csv',
                    %s,
                    'in_progress',
                    %s,
                    %s,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                )
                RETURNING id
            """, [
                self.filename,
                total_rows,
                self.user.id
            ])
            self.import_log_id = cursor.fetchone()[0]

    def _update_import_log(self, status: str, completed_at: timezone.datetime):
        """
        Update import log with final results.

        Args:
            status: Final status (completed, failed, partial)
            completed_at: Completion timestamp
        """
        if not self.import_log_id:
            return

        import json

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE import_logs
                SET
                    status = %s,
                    completed_at = %s,
                    clients_created = %s,
                    clients_existing = %s,
                    cases_created = %s,
                    transactions_created = %s,
                    transactions_skipped = %s,
                    errors = %s::jsonb,
                    summary = %s::jsonb,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, [
                status,
                completed_at,
                self.stats['clients_created'],
                self.stats['clients_existing'],
                self.stats['cases_created'],
                self.stats['transactions_imported'],
                self.stats['transactions_skipped'],
                json.dumps(self.stats['errors']),  # Proper JSON conversion
                json.dumps({
                    'vendors_created': self.stats['vendors_created'],
                    'vendors_existing': self.stats['vendors_existing']
                }),  # summary JSON with vendor stats
                self.import_log_id
            ])
