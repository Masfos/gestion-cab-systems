from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_alter_ordentrabajo_estado'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='empresa',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
