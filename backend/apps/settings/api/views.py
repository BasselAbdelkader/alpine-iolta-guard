import csv
import json
from decimal import Decimal, InvalidOperation
from datetime import datetime
from io import StringIO

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone

from apps.settings.models import ImportAudit, UserProfile
from apps.clients.models import Client, Case
from apps.vendors.models import Vendor
from apps.bank_accounts.models import BankAccount, BankTransaction
from .serializers import ImportAuditSerializer, CSVPreviewSerializer, UserProfileSerializer, UserCreateSerializer, UserUpdateSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def csv_preview(request):
    """
    Preview CSV file before import - shows counts of new vs existing entities.

    Expected CSV format:
    first_name, last_name, email, phone, address, city, state, zip_code,
    case_description, case_amount, transaction_date, transaction_type, amount, description
    """
    serializer = CSVPreviewSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    csv_file = serializer.validated_data['csv_file']

    # File size validation (max 10MB to prevent DoS)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    if csv_file.size > MAX_FILE_SIZE:
        return Response({
            'error': f'File too large. Maximum size is 10MB, your file is {csv_file.size / (1024*1024):.2f}MB'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Read CSV file
        csv_content = csv_file.read().decode('utf-8')
        csv_reader = csv.DictReader(StringIO(csv_content))

        # Tracking sets for unique entities
        new_clients = set()
        existing_clients = set()
        new_vendors = set()
        existing_vendors = set()
        new_cases = set()
        existing_cases = set()
        total_transactions = 0

        # Total counts (including duplicates from CSV)
        total_client_rows = 0
        total_case_rows = 0
        total_vendor_rows = 0
        total_transaction_rows = 0

        validation_errors = []
        preview_rows = []
        row_number = 1

        for row in csv_reader:
            row_number += 1
            row_errors = []

            # Validate required fields
            first_name = row.get('first_name', '').strip()
            last_name = row.get('last_name', '').strip()

            # Count client row (every row is a client row)
            if first_name and last_name:
                total_client_rows += 1

            if not first_name or not last_name:
                row_errors.append(f'Row {row_number}: Missing first_name or last_name')
                validation_errors.append({'row': row_number, 'errors': row_errors})
                continue

            # Check if client exists
            client_key = (first_name.lower(), last_name.lower())
            client_exists = Client.objects.filter(
                first_name__iexact=first_name,
                last_name__iexact=last_name
            ).exists()

            if client_exists:
                existing_clients.add(client_key)
            else:
                new_clients.add(client_key)

            # Check case
            case_description = row.get('case_description', '').strip()
            if case_description:
                total_case_rows += 1  # Count case row

                case_title = f"{first_name} {last_name}'s Case"
                case_key = (client_key, case_title.lower())

                # Check if case exists for this client
                if client_exists:
                    client_obj = Client.objects.filter(
                        first_name__iexact=first_name,
                        last_name__iexact=last_name
                    ).first()

                    if client_obj:
                        case_exists = Case.objects.filter(
                            client=client_obj,
                            case_title__iexact=case_title
                        ).exists()

                        if case_exists:
                            existing_cases.add(case_key)
                        else:
                            new_cases.add(case_key)
                else:
                    # New client = new case
                    new_cases.add(case_key)

                # Validate case amount
                case_amount_str = row.get('case_amount', '').strip()
                if case_amount_str:
                    try:
                        case_amount = Decimal(case_amount_str)
                        if case_amount < 0:
                            row_errors.append(f'Row {row_number}: Case amount cannot be negative')
                    except (InvalidOperation, ValueError):
                        row_errors.append(f'Row {row_number}: Invalid case amount format')

            # Check vendor (if vendor_name is provided)
            vendor_name = row.get('vendor_name', '').strip()
            if vendor_name:
                total_vendor_rows += 1  # Count vendor row

                vendor_exists = Vendor.objects.filter(vendor_name__iexact=vendor_name).exists()
                if vendor_exists:
                    existing_vendors.add(vendor_name.lower())
                else:
                    new_vendors.add(vendor_name.lower())

            # Validate transaction
            transaction_type = row.get('transaction_type', '').strip().upper()
            amount_str = row.get('amount', '').strip()
            transaction_date_str = row.get('transaction_date', '').strip()

            if amount_str:
                total_transaction_rows += 1  # Count transaction row
                try:
                    amount = Decimal(amount_str)
                    if amount <= 0:
                        row_errors.append(f'Row {row_number}: Transaction amount must be greater than zero')
                    else:
                        total_transactions += 1
                except (InvalidOperation, ValueError):
                    row_errors.append(f'Row {row_number}: Invalid transaction amount format')

            if transaction_date_str:
                try:
                    datetime.strptime(transaction_date_str, '%Y-%m-%d')
                except ValueError:
                    try:
                        datetime.strptime(transaction_date_str, '%m/%d/%Y')
                    except ValueError:
                        row_errors.append(f'Row {row_number}: Invalid date format (use YYYY-MM-DD or MM/DD/YYYY)')

            if transaction_type and transaction_type not in ['DEPOSIT', 'WITHDRAWAL', 'TRANSFER_OUT', 'TRANSFER_IN']:
                row_errors.append(f'Row {row_number}: Invalid transaction type')

            # Add row to preview
            preview_rows.append({
                'row': row_number,
                'client': f"{first_name} {last_name}",
                'client_status': 'Existing' if client_exists else 'New',
                'case': case_description[:50] if case_description else '',
                'transaction_amount': amount_str,
                'errors': row_errors
            })

            if row_errors:
                validation_errors.append({'row': row_number, 'errors': row_errors})

        # Calculate duplicates (total in CSV - new - existing)
        duplicate_clients = total_client_rows - len(new_clients) - len(existing_clients)
        duplicate_cases = total_case_rows - len(new_cases) - len(existing_cases)
        duplicate_vendors = total_vendor_rows - len(new_vendors) - len(existing_vendors)

        # Prepare response
        response_data = {
            'preview_summary': {
                # Total counts from CSV (including duplicates within CSV)
                'total_clients_in_csv': total_client_rows,
                'total_cases_in_csv': total_case_rows,
                'total_vendors_in_csv': total_vendor_rows,
                'total_transactions_in_csv': total_transaction_rows,

                # New entities (will be created)
                'expected_clients': len(new_clients),
                'expected_cases': len(new_cases),
                'expected_vendors': len(new_vendors),
                'expected_transactions': total_transactions,

                # Existing entities (already in system)
                'existing_clients': len(existing_clients),
                'existing_cases': len(existing_cases),
                'existing_vendors': len(existing_vendors),

                # Duplicates within CSV (will be skipped)
                'duplicate_clients_in_csv': duplicate_clients,
                'duplicate_cases_in_csv': duplicate_cases,
                'duplicate_vendors_in_csv': duplicate_vendors,

                # Overall stats
                'total_rows': row_number - 1,
                'validation_errors_count': len(validation_errors),
            },
            'validation_errors': validation_errors[:20],  # Limit to first 20 errors
            'preview_rows': preview_rows[:10],  # Show first 10 rows as sample
            'has_errors': len(validation_errors) > 0,
            'can_proceed': len(validation_errors) == 0,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except UnicodeDecodeError:
        return Response(
            {'error': 'Invalid CSV file encoding. Please use UTF-8 encoding.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Error processing CSV file: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def csv_import_confirm(request):
    """
    Import CSV data after preview validation.
    Creates ImportAudit record and imports all data.
    """
    serializer = CSVPreviewSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    csv_file = serializer.validated_data['csv_file']

    # File size validation (max 10MB to prevent DoS)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    if csv_file.size > MAX_FILE_SIZE:
        return Response({
            'error': f'File too large. Maximum size is 10MB, your file is {csv_file.size / (1024*1024):.2f}MB'
        }, status=status.HTTP_400_BAD_REQUEST)

    username = request.user.username if hasattr(request.user, 'username') else 'system'

    # Create ImportAudit record
    audit = ImportAudit.objects.create(
        import_type='csv',
        file_name=csv_file.name,
        status='in_progress',
        imported_by=username
    )

    try:
        # Read CSV file
        csv_content = csv_file.read().decode('utf-8')
        csv_reader = csv.DictReader(StringIO(csv_content))

        # Get the first bank account for transactions
        bank_account = BankAccount.objects.first()
        if not bank_account:
            raise Exception('No bank account found. Please create a bank account first.')

        total_records = 0
        successful_records = 0
        failed_records = 0

        # Track skipped counts
        clients_skipped = 0
        cases_skipped = 0
        vendors_skipped = 0
        rows_with_errors = 0

        # Track total counts from CSV
        total_client_rows = 0
        total_case_rows = 0
        total_vendor_rows = 0
        total_transaction_rows = 0

        with transaction.atomic():
            for row in csv_reader:
                total_records += 1

                try:
                    # Get or create client
                    first_name = row.get('first_name', '').strip()
                    last_name = row.get('last_name', '').strip()

                    # Count client row
                    if first_name and last_name:
                        total_client_rows += 1

                    client, client_created = Client.objects.get_or_create(
                        first_name__iexact=first_name,
                        last_name__iexact=last_name,
                        defaults={
                            'first_name': first_name,
                            'last_name': last_name,
                            'email': row.get('email', '').strip() or None,
                            'phone': row.get('phone', '').strip() or None,
                            'address': row.get('address', '').strip() or None,
                            'city': row.get('city', '').strip() or None,
                            'state': row.get('state', '').strip() or None,
                            'zip_code': row.get('zip_code', '').strip() or None,
                            'data_source': 'csv_import',
                            'import_batch_id': audit.id,
                        }
                    )

                    if client_created:
                        audit.clients_created += 1
                    else:
                        clients_skipped += 1  # Existing client (duplicate)

                    # Create case if case_description is provided
                    case = None
                    case_description = row.get('case_description', '').strip()
                    if case_description:
                        total_case_rows += 1  # Count case row

                        case_title = f"{first_name} {last_name}'s Case"
                        case_amount_str = row.get('case_amount', '').strip()
                        case_amount = Decimal(case_amount_str) if case_amount_str else None

                        case, case_created = Case.objects.get_or_create(
                            client=client,
                            case_title__iexact=case_title,
                            defaults={
                                'case_title': case_title,
                                'case_description': case_description,
                                'case_amount': case_amount,
                                'case_status': 'Open',
                                'opened_date': timezone.now().date(),
                                'data_source': 'csv_import',
                                'import_batch_id': audit.id,
                            }
                        )

                        if case_created:
                            audit.cases_created += 1
                        else:
                            cases_skipped += 1  # Existing case (duplicate)

                    # Create vendor if vendor_name is provided
                    vendor = None
                    vendor_name = row.get('vendor_name', '').strip()
                    if vendor_name:
                        total_vendor_rows += 1  # Count vendor row

                        # Check if vendor name matches current client (client as vendor)
                        client_full_name = f"{first_name} {last_name}"
                        is_client_vendor = vendor_name.lower() == client_full_name.lower()

                        # Check if vendor already exists
                        existing_vendor = Vendor.objects.filter(vendor_name__iexact=vendor_name).first()

                        if existing_vendor:
                            vendor = existing_vendor
                            vendors_skipped += 1  # Existing vendor (duplicate)
                        else:
                            # Create new vendor
                            vendor = Vendor.objects.create(
                                vendor_name=vendor_name,
                                contact_person=row.get('vendor_contact', '').strip() or None,
                                email=row.get('vendor_email', '').strip() or None,
                                phone=row.get('vendor_phone', '').strip() or None,
                                client=client if is_client_vendor else None,  # Link to client if same person
                                data_source='csv_import',
                                import_batch_id=audit.id,
                            )
                            audit.vendors_created += 1

                    # Create transaction
                    amount_str = row.get('amount', '').strip()
                    if amount_str:
                        total_transaction_rows += 1  # Count transaction row
                        amount = Decimal(amount_str)
                        transaction_date_str = row.get('transaction_date', '').strip()

                        # Parse date
                        try:
                            trans_date = datetime.strptime(transaction_date_str, '%Y-%m-%d').date()
                        except ValueError:
                            trans_date = datetime.strptime(transaction_date_str, '%m/%d/%Y').date()

                        # Generate transaction number
                        current_year = datetime.now().year
                        last_transaction = BankTransaction.objects.filter(
                            transaction_number__startswith=f'TXN-{current_year}'
                        ).order_by('-id').first()

                        if last_transaction:
                            try:
                                last_num = int(last_transaction.transaction_number.split('-')[2])
                                transaction_number = f"TXN-{current_year}-{last_num + 1:03d}"
                            except (ValueError, IndexError):
                                transaction_number = f"TXN-{current_year}-{BankTransaction.objects.count() + 1:03d}"
                        else:
                            transaction_number = f"TXN-{current_year}-001"

                        BankTransaction.objects.create(
                            transaction_number=transaction_number,
                            bank_account=bank_account,
                            transaction_type=row.get('transaction_type', 'DEPOSIT').strip().upper(),
                            transaction_date=trans_date,
                            amount=amount,
                            description=row.get('description', '').strip() or 'CSV Import',
                            reference_number=row.get('reference_number', '').strip() or '',
                            payee=row.get('payee', '').strip() or f"{first_name} {last_name}",
                            client=client,
                            case=case,
                            vendor=vendor,
                            item_type='CLIENT_DEPOSIT' if row.get('transaction_type', '').strip().upper() == 'DEPOSIT' else 'DISBURSEMENT',
                            status='pending',
                            data_source='csv_import',
                            import_batch_id=audit.id,
                        )

                        audit.transactions_created += 1

                    successful_records += 1

                except Exception as e:
                    failed_records += 1
                    rows_with_errors += 1

                    # Enhanced error logging with row data
                    import traceback
                    error_details = {
                        'row_number': total_records,
                        'error': str(e),
                        'error_type': type(e).__name__,
                        'row_data': {
                            'client': f"{row.get('first_name', '')} {row.get('last_name', '')}",
                            'case': row.get('case_title', ''),
                            'amount': row.get('amount', ''),
                            'transaction_date': row.get('transaction_date', '')
                        },
                        'traceback': traceback.format_exc()
                    }

                    error_msg = f"Row {total_records}: {str(e)} | Data: {error_details['row_data']}\n"
                    audit.error_log = (audit.error_log or '') + error_msg

                    # Log to system for monitoring
                    import logging
                    logger = logging.getLogger('csv_import')
                    logger.error(f"CSV Import Error: {error_details}")

        # Update audit record with all counts
        audit.total_records = total_records
        audit.successful_records = successful_records
        audit.failed_records = failed_records

        # Set skipped counts
        audit.clients_skipped = clients_skipped
        audit.cases_skipped = cases_skipped
        audit.vendors_skipped = vendors_skipped
        audit.rows_with_errors = rows_with_errors

        # Set total counts from CSV
        audit.total_clients_in_csv = total_client_rows
        audit.total_cases_in_csv = total_case_rows
        audit.total_vendors_in_csv = total_vendor_rows
        audit.total_transactions_in_csv = total_transaction_rows

        audit.mark_completed()

        return Response({
            'message': 'CSV import completed successfully',
            'audit': ImportAuditSerializer(audit).data
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        audit.mark_failed(str(e))
        return Response(
            {'error': f'Import failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def import_audit_list(request):
    """List all import audits"""
    audits = ImportAudit.objects.all().order_by('-import_date')
    serializer = ImportAuditSerializer(audits, many=True)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def import_audit_delete(request, pk):
    """Delete an import batch and all its associated data"""
    try:
        audit = ImportAudit.objects.get(pk=pk)
        deleted_counts = audit.delete_imported_data()
        audit.delete()

        return Response({
            'message': 'Import batch deleted successfully',
            'deleted_counts': deleted_counts
        }, status=status.HTTP_200_OK)
    except ImportAudit.DoesNotExist:
        return Response(
            {'error': 'Import audit not found'},
            status=status.HTTP_404_NOT_FOUND
        )


# ==================================================================================
# USER MANAGEMENT API ENDPOINTS
# ==================================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    """
    List all user profiles with their roles and permissions.
    Only accessible by users with can_manage_users permission.
    """
    # Check permission
    try:
        user_profile = request.user.profile
        if not user_profile.can_manage_users:
            return Response(
                {'error': 'You do not have permission to manage users'},
                status=status.HTTP_403_FORBIDDEN
            )
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'User profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Get all user profiles
    profiles = UserProfile.objects.all().select_related('user', 'created_by').order_by('-created_at')

    # Filter by role if provided
    role = request.GET.get('role')
    if role:
        profiles = profiles.filter(role=role)

    # Filter by active status
    is_active = request.GET.get('is_active')
    if is_active is not None:
        is_active_bool = is_active.lower() == 'true'
        profiles = profiles.filter(is_active=is_active_bool)

    serializer = UserProfileSerializer(profiles, many=True)

    return Response({
        'count': profiles.count(),
        'users': serializer.data,
        'role_choices': [
            {'value': code, 'label': label}
            for code, label in UserProfile.ROLE_CHOICES
        ]
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_user(request):
    """
    Create a new user with profile.
    Only accessible by users with can_manage_users permission.
    """
    # Check permission
    try:
        user_profile = request.user.profile
        if not user_profile.can_manage_users:
            return Response(
                {'error': 'You do not have permission to manage users'},
                status=status.HTTP_403_FORBIDDEN
            )
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'User profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Create user
    serializer = UserCreateSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    profile = serializer.save()

    # Return created profile
    response_serializer = UserProfileSerializer(profile)
    return Response({
        'message': 'User created successfully',
        'user': response_serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request, user_id):
    """
    Get details of a specific user.
    Only accessible by users with can_manage_users permission.
    """
    # Check permission
    try:
        user_profile = request.user.profile
        if not user_profile.can_manage_users:
            return Response(
                {'error': 'You do not have permission to manage users'},
                status=status.HTTP_403_FORBIDDEN
            )
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'User profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Get user profile
    try:
        profile = UserProfile.objects.select_related('user', 'created_by').get(id=user_id)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    """
    Update user profile.
    Only accessible by users with can_manage_users permission.
    """
    # Check permission
    try:
        user_profile = request.user.profile
        if not user_profile.can_manage_users:
            return Response(
                {'error': 'You do not have permission to manage users'},
                status=status.HTTP_403_FORBIDDEN
            )
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'User profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Get user profile
    try:
        profile = UserProfile.objects.select_related('user').get(id=user_id)
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Update user
    serializer = UserUpdateSerializer(data=request.data, partial=(request.method == 'PATCH'))
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    updated_profile = serializer.update(profile, serializer.validated_data)

    # Return updated profile
    response_serializer = UserProfileSerializer(updated_profile)
    return Response({
        'message': 'User updated successfully',
        'user': response_serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request, user_id):
    """
    Delete (deactivate) a user.
    Only accessible by users with can_manage_users permission.
    Does not actually delete the user, just marks as inactive.
    """
    # Check permission
    try:
        user_profile = request.user.profile
        if not user_profile.can_manage_users:
            return Response(
                {'error': 'You do not have permission to manage users'},
                status=status.HTTP_403_FORBIDDEN
            )
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'User profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Get user profile
    try:
        profile = UserProfile.objects.select_related('user').get(id=user_id)

        # Prevent deleting self
        if profile.user.id == request.user.id:
            return Response(
                {'error': 'You cannot delete your own account'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Deactivate user and profile
        profile.user.is_active = False
        profile.user.save()
        profile.is_active = False
        profile.save()

        return Response({
            'message': 'User deactivated successfully'
        }, status=status.HTTP_200_OK)

    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """
    Get current logged-in user's profile.
    Accessible by all authenticated users.
    """
    try:
        profile = request.user.profile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'User profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )
