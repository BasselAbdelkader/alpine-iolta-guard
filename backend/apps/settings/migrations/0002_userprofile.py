# Generated manually on 2025-11-14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('settings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(
                    choices=[
                        ('managing_attorney', 'Managing Attorney'),
                        ('staff_attorney', 'Staff Attorney'),
                        ('paralegal', 'Paralegal'),
                        ('bookkeeper', 'Bookkeeper'),
                        ('system_admin', 'System Administrator')
                    ],
                    default='paralegal',
                    help_text='User role determines permissions',
                    max_length=30
                )),
                ('phone', models.CharField(blank=True, help_text='Contact phone number', max_length=20)),
                ('employee_id', models.CharField(blank=True, help_text='Employee ID or bar number', max_length=50)),
                ('department', models.CharField(blank=True, help_text='Department or practice area', max_length=100)),
                ('is_active', models.BooleanField(default=True, help_text='User can access the system')),
                ('can_approve_transactions', models.BooleanField(
                    default=False,
                    help_text='Can approve high-value transactions (≥ $10,000)'
                )),
                ('can_reconcile', models.BooleanField(default=False, help_text='Can perform bank reconciliation')),
                ('can_print_checks', models.BooleanField(default=False, help_text='Can print checks (requires dual approval)')),
                ('can_manage_users', models.BooleanField(default=False, help_text='Can create/edit user accounts')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(
                    blank=True,
                    help_text='Admin who created this user',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='created_profiles',
                    to=settings.AUTH_USER_MODEL
                )),
                ('user', models.OneToOneField(
                    help_text='Link to Django User account',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='profile',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'User Profile',
                'verbose_name_plural': 'User Profiles',
                'db_table': 'user_profiles',
            },
        ),
    ]
