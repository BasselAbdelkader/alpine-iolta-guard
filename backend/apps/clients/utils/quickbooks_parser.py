"""
QuickBooks CSV Parser and Validator
====================================
Parses and validates QuickBooks export CSV files for import into IOLTA Guard.
"""

import csv
import io
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Tuple


class QuickBooksParser:
    """Parse and validate QuickBooks CSV files."""

    # Required columns in QuickBooks CSV
    REQUIRED_COLUMNS = [
        'Date', 'Type', 'Account', 'Payee',
        'Memo', 'Payment', 'Deposit'
    ]

    # Valid transaction types
    VALID_TYPES = ['Check', 'Deposit', 'Expense', 'Journal']

    def __init__(self, file_content):
        """
        Initialize parser with file content.

        Args:
            file_content: File content (string or bytes)
        """
        self.file_content = file_content
        self.rows = []
        self.headers = []
        self.errors = []
        self.warnings = []

    def parse(self) -> Tuple[bool, List[Dict], List[Dict], List[Dict]]:
        """
        Parse CSV file and return structured data.

        Returns:
            tuple: (success, data, errors, warnings)
        """
        # Try different encodings
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']

        for encoding in encodings:
            try:
                if isinstance(self.file_content, bytes):
                    content = self.file_content.decode(encoding)
                else:
                    content = self.file_content

                # Parse CSV
                csv_file = io.StringIO(content)
                reader = csv.DictReader(csv_file)
                self.headers = reader.fieldnames
                self.rows = list(reader)
                break
            except (UnicodeDecodeError, AttributeError):
                if encoding == encodings[-1]:
                    self.errors.append({
                        'row': None,
                        'field': None,
                        'error': f'Could not read file with encoding: {encoding}'
                    })
                    return False, [], self.errors, self.warnings
                continue

        # Validate structure
        if not self._validate_structure():
            return False, [], self.errors, self.warnings

        # Validate each row
        valid_data = self._validate_rows()

        return True, valid_data, self.errors, self.warnings

    def _validate_structure(self) -> bool:
        """
        Validate CSV file structure.

        Returns:
            bool: True if structure is valid
        """
        # Check if file has data
        if not self.rows:
            self.errors.append({
                'row': None,
                'field': None,
                'error': 'File is empty or has no data rows'
            })
            return False

        # Check required columns
        missing_columns = []
        for col in self.REQUIRED_COLUMNS:
            if col not in self.headers:
                missing_columns.append(col)

        if missing_columns:
            self.errors.append({
                'row': None,
                'field': None,
                'error': f'Missing required columns: {", ".join(missing_columns)}'
            })
            return False

        return True

    def _validate_rows(self) -> List[Dict]:
        """
        Validate each row and return valid data.

        Returns:
            list: Valid rows
        """
        valid_data = []
        journal_without_account_count = 0

        for idx, row in enumerate(self.rows, start=2):  # Start at 2 (header is row 1)
            row_errors = []

            # Validate Date
            date_value, date_error = self._validate_date(row.get('Date', ''))
            if date_error:
                row_errors.append(('Date', date_error))

            # Validate Type
            type_value, type_error = self._validate_type(row.get('Type', ''))
            if type_error:
                row_errors.append(('Type', type_error))

            # Validate Account
            account_value, account_error = self._validate_account(
                row.get('Account', ''),
                row.get('Type', '')
            )
            if account_error:
                row_errors.append(('Account', account_error))

            # Track Journal entries without account
            if row.get('Type', '') == 'Journal' and not row.get('Account', '').strip():
                journal_without_account_count += 1
                account_value = 'Unassigned'  # Will use Unassigned client

            # Validate Amount
            amount_value, amount_type, amount_error = self._validate_amount(
                row.get('Payment', ''),
                row.get('Deposit', '')
            )
            if amount_error:
                row_errors.append(('Amount', amount_error))

            # If row has errors, log them
            if row_errors:
                for field, error in row_errors:
                    self.errors.append({
                        'row': idx,
                        'field': field,
                        'error': error,
                        'value': row.get(field, '')
                    })
            else:
                # Row is valid, add to valid data
                valid_data.append({
                    'row_number': idx,
                    'date': date_value,
                    'type': type_value,
                    'account': account_value,
                    'payee': row.get('Payee', '').strip(),
                    'memo': row.get('Memo', '').strip(),
                    'amount': amount_value,
                    'amount_type': amount_type,  # 'payment' or 'deposit'
                    'ref_no': row.get('Ref No.', '').strip(),
                    'reconciliation_status': row.get('Reconciliation Status', '').strip(),
                    'raw_row': row
                })

        # Add warning about Journal entries
        if journal_without_account_count > 0:
            self.warnings.append({
                'message': f'{journal_without_account_count} Journal entries have no Account '
                          f'(will be assigned to "Unassigned" client)'
            })

        return valid_data

    def _validate_date(self, date_str: str) -> Tuple[datetime.date, str]:
        """
        Validate and parse date field.

        Args:
            date_str: Date string from CSV

        Returns:
            tuple: (parsed_date, error_message)
        """
        if not date_str or not date_str.strip():
            return None, 'Date is required'

        # Try parsing MM/DD/YYYY format
        try:
            parsed_date = datetime.strptime(date_str.strip(), '%m/%d/%Y').date()

            # Check reasonable date range (2020-2030)
            if parsed_date.year < 2020 or parsed_date.year > 2030:
                return None, f'Date out of reasonable range: {date_str}'

            return parsed_date, None
        except ValueError:
            return None, f'Invalid date format (expected MM/DD/YYYY): {date_str}'

    def _validate_type(self, type_str: str) -> Tuple[str, str]:
        """
        Validate transaction type.

        Args:
            type_str: Type string from CSV

        Returns:
            tuple: (type_value, error_message)
        """
        if not type_str or not type_str.strip():
            return None, 'Type is required'

        type_value = type_str.strip()

        if type_value not in self.VALID_TYPES:
            return None, f'Invalid type (expected {", ".join(self.VALID_TYPES)}): {type_value}'

        return type_value, None

    def _validate_account(self, account_str: str, type_str: str) -> Tuple[str, str]:
        """
        Validate account (client) field.

        Args:
            account_str: Account string from CSV
            type_str: Transaction type

        Returns:
            tuple: (account_value, error_message)
        """
        account_value = account_str.strip() if account_str else ''

        # Journal entries can have empty account
        if type_str == 'Journal' and not account_value:
            return '', None  # Will be handled as "Unassigned"

        # Other types must have account
        if not account_value:
            return None, 'Account (client) is required'

        return account_value, None

    def _validate_amount(self, payment_str: str, deposit_str: str) -> Tuple[Decimal, str, str]:
        """
        Validate amount fields (Payment or Deposit).

        Args:
            payment_str: Payment amount string
            deposit_str: Deposit amount string

        Returns:
            tuple: (amount, amount_type, error_message)
        """
        payment = payment_str.strip() if payment_str else ''
        deposit = deposit_str.strip() if deposit_str else ''

        # Must have either payment OR deposit (not both, not neither)
        if payment and deposit:
            return None, None, 'Cannot have both Payment and Deposit'

        if not payment and not deposit:
            return None, None, 'Must have either Payment or Deposit'

        # Parse payment
        if payment:
            try:
                amount = self._parse_amount(payment)
                if amount <= 0:
                    return None, None, f'Payment amount must be positive: {payment}'
                return amount, 'payment', None
            except (ValueError, InvalidOperation):
                return None, None, f'Invalid payment amount: {payment}'

        # Parse deposit
        if deposit:
            try:
                amount = self._parse_amount(deposit)
                if amount <= 0:
                    return None, None, f'Deposit amount must be positive: {deposit}'
                return amount, 'deposit', None
            except (ValueError, InvalidOperation):
                return None, None, f'Invalid deposit amount: {deposit}'

        return None, None, 'Unknown amount error'

    def _parse_amount(self, amount_str: str) -> Decimal:
        """
        Parse amount string to Decimal.

        Args:
            amount_str: Amount string (may have commas)

        Returns:
            Decimal: Parsed amount
        """
        # Remove commas and whitespace
        cleaned = amount_str.replace(',', '').strip()
        return Decimal(cleaned)

    def extract_clients(self, data: List[Dict]) -> List[str]:
        """
        Extract unique client names from validated data.

        Args:
            data: Validated transaction data

        Returns:
            list: Unique client names
        """
        clients = set()
        for row in data:
            account = row['account']
            if account:
                clients.add(account)

        return sorted(list(clients))

    def group_by_client(self, data: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group transactions by client.

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

    def get_summary(self, data: List[Dict]) -> Dict:
        """
        Get summary statistics about the data.

        Args:
            data: Validated transaction data

        Returns:
            dict: Summary statistics
        """
        if not data:
            return {
                'total_rows': len(self.rows),
                'valid_rows': 0,
                'error_rows': len(self.errors),
                'unique_clients': 0,
                'date_range': None,
                'transaction_types': {}
            }

        clients = self.extract_clients(data)
        dates = [row['date'] for row in data if row['date']]

        # Count transaction types
        type_counts = {}
        for row in data:
            trans_type = row['type']
            type_counts[trans_type] = type_counts.get(trans_type, 0) + 1

        return {
            'total_rows': len(self.rows),
            'valid_rows': len(data),
            'error_rows': len(self.errors),
            'unique_clients': len(clients),
            'date_range': {
                'start': min(dates).isoformat() if dates else None,
                'end': max(dates).isoformat() if dates else None
            },
            'transaction_types': type_counts
        }
