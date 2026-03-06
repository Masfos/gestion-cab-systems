from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_campos_nuevos'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vehiculo',
            name='id_interno',
        ),
    ]
