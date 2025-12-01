from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bank_accounts', '0001_initial'),
    ]

    operations = [
        # Remove the check_number field
        migrations.RemoveField(
            model_name='banktransaction',
            name='check_number',
        ),
    ]
