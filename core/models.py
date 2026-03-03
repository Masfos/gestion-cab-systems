from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction

class Cliente(models.Model):
    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Vehiculo(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    patente = models.CharField(max_length=20)
    anio = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.patente}"

class OrdenTrabajo(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('finalizado', 'Finalizado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Orden {self.id} - {self.vehiculo.patente}"

class ImagenOrden(models.Model):
    # Relación para permitir múltiples fotos por cada orden
    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name="imagenes")
    imagen = models.ImageField(upload_to='ordenes/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

class Material(models.Model):
    nombre = models.CharField(max_length=150)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nombre

class MaterialUsado(models.Model):
    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name="materiales_usados")
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Lógica para descontar stock automáticamente al registrar uso
        if self.pk:
            anterior = MaterialUsado.objects.get(pk=self.pk)
            dif = self.cantidad - anterior.cantidad
        else:
            dif = self.cantidad

        if dif > 0 and self.material.stock < dif:
            raise ValidationError(f"Stock insuficiente. Disponible: {self.material.stock}")

        self.material.stock -= dif
        self.material.save()
        super().save(*args, **kwargs)