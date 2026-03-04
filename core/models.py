from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction

# Registro cliente
class Cliente(models.Model):
    nombre = models.CharField(max_length=150)
    empresa = models.CharField(max_length=150, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.empresa})" if self.empresa else self.nombre

class Vehiculo(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    patente = models.CharField(max_length=20)
    anio = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        empresa_txt = f" ({self.cliente.empresa})" if self.cliente.empresa else ""
        return f"{self.marca} {self.modelo} [{self.patente}] - {self.cliente.nombre}{empresa_txt}"


# Orden de trabajo asociada a un vehículo y su cliente
class OrdenTrabajo(models.Model):
    # Estados de la orden
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('finalizado', 'Finalizado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )

    descripcion = models.TextField()

    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ordenes_creadas"
    )

    modificado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ordenes_modificadas"
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Orden #{self.id} - {self.vehiculo.patente}"


# Imágenes adjuntas
class ImagenOrden(models.Model):
    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name="imagenes")
    imagen = models.ImageField(upload_to="ordenes/")
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Imagen de Orden #{self.orden.id}"


# Materiales en bodega
class Material(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} (Stock: {self.stock})"


# Registro de materiales utilizados en una orden
class MaterialUsado(models.Model):
    orden = models.ForeignKey(
        'OrdenTrabajo',
        on_delete=models.CASCADE,
        related_name="materiales_usados"
    )
    material = models.ForeignKey('Material', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def clean(self):
        if self.pk:
            anterior = MaterialUsado.objects.get(pk=self.pk)
            diferencia = self.cantidad - anterior.cantidad
        else:
            diferencia = self.cantidad

        if diferencia > 0 and self.material.stock < diferencia:
            raise ValidationError(
                f"No hay suficiente stock disponible: {self.material.stock}"
            )

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.pk:
            anterior = MaterialUsado.objects.get(pk=self.pk)
            diferencia = self.cantidad - anterior.cantidad
        else:
            diferencia = self.cantidad

        self.clean()

        # Se descuenta del stock según la cantidad usada en la orden
        self.material.stock -= diferencia
        self.material.save()

        super().save(*args, **kwargs)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        # Al eliminar el registro, se devuelve la cantidad al stock
        self.material.stock += self.cantidad
        self.material.save()

        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.material.nombre} - {self.cantidad}"