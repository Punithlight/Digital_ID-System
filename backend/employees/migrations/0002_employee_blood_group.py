from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='blood_group',
            field=models.CharField(
                blank=True,
                choices=[
                    ('A+', 'A+'), ('A-', 'A-'),
                    ('B+', 'B+'), ('B-', 'B-'),
                    ('AB+', 'AB+'), ('AB-', 'AB-'),
                    ('O+', 'O+'), ('O-', 'O-'),
                ],
                max_length=5,
            ),
        ),
    ]
