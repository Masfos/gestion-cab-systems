from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_eliminar_id_interno'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vehiculo',
            old_name='horas',
            new_name='kilometraje',
        ),
    ]
