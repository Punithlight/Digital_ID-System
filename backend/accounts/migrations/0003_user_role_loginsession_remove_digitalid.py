from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_user_managers_digitalid'),
    ]

    operations = [
        # Add role to User
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[('superadmin', 'Super Admin'), ('admin', 'HR / Admin'), ('employee', 'Employee')],
                default='employee',
                max_length=20,
            ),
        ),
        # Drop old DigitalID (will move to digital_id app)
        migrations.DeleteModel(
            name='DigitalID',
        ),
        # Create LoginSession
        migrations.CreateModel(
            name='LoginSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(max_length=255, unique=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='login_sessions',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
        ),
    ]
