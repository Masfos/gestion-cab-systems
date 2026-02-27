from django.contrib import admin
from .models import (
    Cliente,
    Vehiculo,
    OrdenTrabajo,
    ImagenOrden,
    Material,
    MaterialUsado
)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'email')
    search_fields = ('nombre', 'telefono', 'email')


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('marca', 'modelo', 'patente', 'cliente')
    search_fields = ('marca', 'modelo', 'patente')
    list_filter = ('marca',)


@admin.register(OrdenTrabajo)
class OrdenTrabajoAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehiculo', 'estado', 'fecha_creacion')
    list_filter = ('estado',)
    search_fields = ('vehiculo__patente',)


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'stock')
    search_fields = ('nombre',)


@admin.register(MaterialUsado)
class MaterialUsadoAdmin(admin.ModelAdmin):
    list_display = ('orden', 'material', 'cantidad')
    list_filter = ('orden',)