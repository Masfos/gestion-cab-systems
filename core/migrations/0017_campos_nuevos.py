from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_cliente_rut'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='rut_empresa',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='cliente',
            name='giro',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='cliente',
            name='ciudad',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='cliente',
            name='direccion',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='vehiculo',
            name='serie_vin',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='vehiculo',
            name='id_interno',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='vehiculo',
            name='horas',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ordentrabajo',
            name='observaciones',
            field=models.TextField(blank=True, null=True),
        ),
    ]
