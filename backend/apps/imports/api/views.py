"""
Import Approval API Views
=========================
Two-stage approval system for CSV imports.

Business Rules:
- Only users with can_approve_imports permission can approve/reject
- Cannot approve own import (dual control / maker-checker)
- Only imports with status='pending_review' can be approved/rejected
- Approve: Copy staging → production, delete staging, notify importer
- Reject: Delete staging, notify importer
"""

import logging
from decimal import Decimal
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import User, Permission
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.imports.models import StagingClient, StagingCase, StagingBankTransaction, ImportNotification
from apps.clients.models import Client, Case
from apps.bank_accounts.models import BankTransaction, BankAccount
from apps.vendors.models import Vendor
from apps.settings.models import ImportLog

logger = logging.getLogger(__name__)


def create_notification(users, notification_type, import_batch_id, message, created_by):
    """
    Create notifications for multiple users.

    Args:
        users: List of User objects or queryset
        notification_type: Type of notification
        import_batch_id: Import batch ID
        message: Notification message
        created_by: User who created the notification
    """
    notifications = [
        ImportNotification(
            user=user,
            notification_type=notification_type,
            import_batch_id=import_batch_id,
            message=message,
            created_by=created_by
        )
        for user in users
    ]
    ImportNotification.objects.bulk_create(notifications)
    logger.info(f"Created {len(notifications)} notifications for import batch {import_batch_id}")


def get_approvers():
    """
    Get all users who can approve imports (Managing Attorney + Accountant).

    Returns:
        QuerySet of User objects with approval permission
    """
    permission = Permission.objects.get(codename='can_approve_imports')
    return User.objects.filter(
        Q(groups__permissions=permission) | Q(user_permissions=permission)
    ).distinct()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_import(request, import_batch_id):
    """
    Approve an import and commit staging data to production.

    Workflow:
    1. Validate user has can_approve_imports permission
    2. Validate user != importer (dual control)
    3. Validate approval_status == 'pending_review'
    4. BEGIN TRANSACTION
        - Copy staging_clients → clients
        - Copy staging_cases → cases (link to production clients)
        - Copy staging_transactions → bank_transactions (link to production clients/cases)
        - Update client balances
        - Set approval_status='committed'
        - Delete staging records
        - Create notification for importer
    5. COMMIT
    6. Return success + production record IDs
    """
    try:
        # Get import log
        try:
            import_log = ImportLog.objects.get(id=import_batch_id)
        except ImportLog.DoesNotExist:
            return Response(
                {'error': f'Import batch {import_batch_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Validate permission
        if not request.user.has_perm('imports.can_approve_imports'):
            return Response(
                {'error': 'You do not have permission to approve imports'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Validate dual control (cannot approve own import)
        if import_log.created_by and request.user.id == import_log.created_by.id:
            return Response(
                {'error': 'You cannot approve your own import (dual control violation)'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Validate status
        if import_log.approval_status != 'pending_review':
            return Response(
                {
                    'error': f'Import cannot be approved. Current status: {import_log.get_approval_status_display()}',
                    'current_status': import_log.approval_status
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get staging data counts
        staging_clients = StagingClient.objects.filter(import_batch_id=import_batch_id)
        staging_cases = StagingCase.objects.filter(import_batch_id=import_batch_id)
        staging_transactions = StagingBankTransaction.objects.filter(import_batch_id=import_batch_id).order_by('transaction_date', 'staging_id')

        staging_counts = {
            'clients': staging_clients.count(),
            'cases': staging_cases.count(),
            'transactions': staging_transactions.count()
        }

        # Get default bank account
        bank_account = BankAccount.objects.first()
        if not bank_account:
            return Response(
                {'error': 'No bank account found. Please create a bank account first.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # BEGIN TRANSACTION - Atomic commit to production
        with transaction.atomic():
            production_ids = {
                'clients': [],
                'cases': [],
                'transactions': []
            }

            # Map staging IDs to production IDs
            staging_to_production_client = {}
            staging_to_production_case = {}

            # 1. Copy staging_clients → clients (skip duplicates by name)
            clients_created = 0
            clients_skipped = 0

            for staging_client in staging_clients:
                # Check if client already exists by name (unique constraint: first_name + last_name)
                existing_client = Client.objects.filter(
                    first_name=staging_client.first_name,
                    last_name=staging_client.last_name
                ).first()

                if existing_client:
                    # Client with same name already exists, use existing one
                    staging_to_production_client[staging_client.staging_id] = existing_client.id
                    clients_skipped += 1
                    logger.info(f"Skipped duplicate client: {staging_client.first_name} {staging_client.last_name} (using existing ID {existing_client.id})")
                else:
                    # Create new client
                    production_client = Client.objects.create(
                        client_number=staging_client.client_number,
                        first_name=staging_client.first_name,
                        last_name=staging_client.last_name,
                        email=staging_client.email,
                        phone=staging_client.phone,
                        address=staging_client.address,
                        city=staging_client.city,
                        state=staging_client.state,
                        zip_code=staging_client.zip_code,
                        trust_account_status=staging_client.trust_account_status,
                        is_active=staging_client.is_active,
                        data_source=staging_client.data_source
                    )
                    staging_to_production_client[staging_client.staging_id] = production_client.id
                    production_ids['clients'].append(production_client.id)
                    clients_created += 1

            logger.info(f"Created {clients_created} new clients, skipped {clients_skipped} duplicates")

            # 2. Copy staging_cases → cases
            for staging_case in staging_cases:
                production_client_id = staging_to_production_client.get(staging_case.staging_client_id)
                if not production_client_id:
                    raise ValueError(f"Production client not found for staging client {staging_case.staging_client_id}")

                production_case = Case.objects.create(
                    client_id=production_client_id,
                    case_number=staging_case.case_number,
                    case_title=staging_case.case_title,
                    case_description=staging_case.case_description,
                    case_status=staging_case.case_status,
                    opened_date=staging_case.opened_date,
                    closed_date=staging_case.closed_date,
                    is_active=staging_case.is_active,
                    data_source=staging_case.data_source
                )
                staging_to_production_case[staging_case.staging_id] = production_case.id
                production_ids['cases'].append(production_case.id)

            logger.info(f"Copied {len(production_ids['cases'])} cases to production")

            # 2.5. Create vendors from unique payees in withdrawal transactions
            # Get all unique payees from withdrawal staging transactions
            unique_payees = staging_transactions.filter(
                transaction_type='WITHDRAWAL'
            ).exclude(
                payee=''
            ).values_list('payee', flat=True).distinct()

            staging_to_production_vendor = {}  # Map payee name to vendor
            vendors_created = 0
            vendors_skipped = 0

            # Get all production clients for matching (client-vendor linking)
            all_clients = {
                f"{c.first_name} {c.last_name}".lower(): c
                for c in Client.objects.all()
            }

            for payee_name in unique_payees:
                payee_name = payee_name.strip()
                if not payee_name:
                    continue

                # Check if vendor already exists (by name, case-insensitive)
                existing_vendor = Vendor.objects.filter(vendor_name__iexact=payee_name).first()

                if existing_vendor:
                    # Use existing vendor
                    staging_to_production_vendor[payee_name] = existing_vendor
                    vendors_skipped += 1
                else:
                    # Check if payee matches a client name (client-vendor)
                    matching_client = all_clients.get(payee_name.lower())

                    # Create new vendor
                    new_vendor = Vendor.objects.create(
                        vendor_name=payee_name,
                        client=matching_client if matching_client else None,  # Link if client-vendor
                        data_source='csv_import'
                    )
                    staging_to_production_vendor[payee_name] = new_vendor
                    vendors_created += 1

                    if matching_client:
                        logger.info(f"Created client-vendor: {payee_name} → Client #{matching_client.id}")
                    else:
                        logger.info(f"Created vendor: {payee_name}")

            production_ids['vendors'] = [v.id for v in staging_to_production_vendor.values()]
            logger.info(f"Created {vendors_created} vendors, skipped {vendors_skipped} existing vendors")

            # 3. Copy staging_transactions → bank_transactions
            for staging_transaction in staging_transactions:
                production_client_id = staging_to_production_client.get(staging_transaction.staging_client_id)
                production_case_id = staging_to_production_case.get(staging_transaction.staging_case_id)

                if not production_client_id or not production_case_id:
                    raise ValueError(
                        f"Production client/case not found for staging transaction {staging_transaction.staging_id}"
                    )

                # Get vendor for withdrawal transactions (link payee to vendor)
                vendor_id = None
                if staging_transaction.transaction_type == 'WITHDRAWAL' and staging_transaction.payee:
                    vendor = staging_to_production_vendor.get(staging_transaction.payee.strip())
                    if vendor:
                        vendor_id = vendor.id

                production_transaction = BankTransaction.objects.create(
                    bank_account=bank_account,
                    client_id=production_client_id,
                    case_id=production_case_id,
                    vendor_id=vendor_id,  # Link to vendor if available
                    transaction_date=staging_transaction.transaction_date,
                    transaction_type=staging_transaction.transaction_type,
                    amount=staging_transaction.amount,
                    payee=staging_transaction.payee,
                    reference_number=staging_transaction.reference_number,
                    description=staging_transaction.description,
                    status=staging_transaction.status,
                    data_source=staging_transaction.data_source
                )
                production_ids['transactions'].append(production_transaction.id)

            logger.info(f"Copied {len(production_ids['transactions'])} transactions to production")

            # 4. Client balances are calculated properties (sum of transactions)
            # No need to recalculate - they update automatically
            logger.info(f"Created {len(production_ids['clients'])} clients with transaction-based balances")

            # 5. Update import_log status
            import_log.approval_status = 'committed'
            import_log.reviewed_by = request.user
            import_log.reviewed_at = timezone.now()
            import_log.review_notes = request.data.get('notes', '')
            import_log.save(update_fields=['approval_status', 'reviewed_by', 'reviewed_at', 'review_notes', 'updated_at'])

            # 6. Delete staging records
            staging_transactions.delete()
            staging_cases.delete()
            staging_clients.delete()

            logger.info(f"Deleted staging records for import batch {import_batch_id}")

        # 7. Create notification for importer (outside transaction)
        if import_log.created_by:
            create_notification(
                users=[import_log.created_by],
                notification_type='import_approved',
                import_batch_id=import_batch_id,
                message=f'{request.user.get_full_name() or request.user.username} approved your import "{import_log.filename}" with {staging_counts["clients"]} clients, {staging_counts["cases"]} cases, {staging_counts["transactions"]} transactions, and {vendors_created} vendors.',
                created_by=request.user
            )

        return Response({
            'success': True,
            'message': 'Import approved and committed to production',
            'import_batch_id': import_batch_id,
            'approved_by': request.user.get_full_name() or request.user.username,
            'staging_counts': staging_counts,
            'production_ids': production_ids,
            'vendors_created': vendors_created,
            'vendors_skipped': vendors_skipped
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error approving import {import_batch_id}: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Failed to approve import: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_import(request, import_batch_id):
    """
    Reject an import and delete staging data.

    Workflow:
    1. Validate user has can_reject_imports permission
    2. Validate user != importer (dual control)
    3. Validate approval_status == 'pending_review'
    4. Delete staging records
    5. Set approval_status='rejected'
    6. Save review_notes
    7. Create notification for importer
    8. Return success + rejection reason
    """
    try:
        # Get import log
        try:
            import_log = ImportLog.objects.get(id=import_batch_id)
        except ImportLog.DoesNotExist:
            return Response(
                {'error': f'Import batch {import_batch_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Validate permission
        if not request.user.has_perm('imports.can_reject_imports'):
            return Response(
                {'error': 'You do not have permission to reject imports'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Validate dual control (cannot reject own import)
        if import_log.created_by and request.user.id == import_log.created_by.id:
            return Response(
                {'error': 'You cannot reject your own import (dual control violation)'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Validate status
        if import_log.approval_status != 'pending_review':
            return Response(
                {
                    'error': f'Import cannot be rejected. Current status: {import_log.get_approval_status_display()}',
                    'current_status': import_log.approval_status
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get rejection reason
        rejection_reason = request.data.get('reason', 'No reason provided')

        # Get staging data counts before deletion
        staging_counts = {
            'clients': StagingClient.objects.filter(import_batch_id=import_batch_id).count(),
            'cases': StagingCase.objects.filter(import_batch_id=import_batch_id).count(),
            'transactions': StagingBankTransaction.objects.filter(import_batch_id=import_batch_id).count()
        }

        # Delete staging records
        with transaction.atomic():
            StagingBankTransaction.objects.filter(import_batch_id=import_batch_id).delete()
            StagingCase.objects.filter(import_batch_id=import_batch_id).delete()
            StagingClient.objects.filter(import_batch_id=import_batch_id).delete()

            # Update import_log status
            import_log.approval_status = 'rejected'
            import_log.reviewed_by = request.user
            import_log.reviewed_at = timezone.now()
            import_log.review_notes = rejection_reason
            import_log.save(update_fields=['approval_status', 'reviewed_by', 'reviewed_at', 'review_notes', 'updated_at'])

        logger.info(f"Rejected import batch {import_batch_id} and deleted {staging_counts['clients']} clients, {staging_counts['cases']} cases, {staging_counts['transactions']} transactions")

        # Create notification for importer
        if import_log.created_by:
            create_notification(
                users=[import_log.created_by],
                notification_type='import_rejected',
                import_batch_id=import_batch_id,
                message=f'{request.user.get_full_name() or request.user.username} rejected your import "{import_log.filename}": {rejection_reason}',
                created_by=request.user
            )

        return Response({
            'success': True,
            'message': 'Import rejected and staging data deleted',
            'import_batch_id': import_batch_id,
            'rejected_by': request.user.get_full_name() or request.user.username,
            'reason': rejection_reason,
            'deleted_counts': staging_counts
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error rejecting import {import_batch_id}: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Failed to reject import: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_imports(request):
    """
    Get list of imports pending approval.

    Returns imports with approval_status='pending_review' that:
    - User can approve (has permission and didn't create it)
    - User created (to see their own pending imports)
    """
    can_approve = request.user.has_perm('imports.can_approve_imports')

    if can_approve:
        # Show all pending imports except own
        pending_imports = ImportLog.objects.filter(
            approval_status='pending_review'
        ).exclude(
            created_by=request.user
        ).select_related('created_by')
    else:
        # Show only own pending imports
        pending_imports = ImportLog.objects.filter(
            approval_status='pending_review',
            created_by=request.user
        )

    # Get staging counts for each import
    import_data = []
    for import_log in pending_imports:
        staging_counts = {
            'clients': StagingClient.objects.filter(import_batch_id=import_log.id).count(),
            'cases': StagingCase.objects.filter(import_batch_id=import_log.id).count(),
            'transactions': StagingBankTransaction.objects.filter(import_batch_id=import_log.id).count()
        }

        import_data.append({
            'id': import_log.id,
            'filename': import_log.filename,
            'import_type': import_log.import_type,
            'created_by': import_log.created_by.get_full_name() if import_log.created_by else 'Unknown',
            'created_at': import_log.created_at.isoformat(),
            'approval_status': import_log.approval_status,
            'staging_counts': staging_counts,
            'can_approve': can_approve and import_log.created_by_id != request.user.id
        })

    return Response({
        'pending_imports': import_data,
        'can_approve': can_approve
    }, status=status.HTTP_200_OK)
