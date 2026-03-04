from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_cliente_empresa'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='rut',
            field=models.CharField(blank=True, max_length=12, null=True, unique=True),
        ),
    ]
