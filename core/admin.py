from django.contrib import admin
from .models import Cliente, Vehiculo, OrdenTrabajo, ImagenOrden, Material, MaterialUsado

class ImagenInline(admin.TabularInline):
    model = ImagenOrden
    extra = 1

class MaterialUsadoInline(admin.TabularInline):
    model = MaterialUsado
    extra = 1

@admin.register(OrdenTrabajo)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehiculo', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('vehiculo__patente', 'vehiculo__cliente__nombre')
    inlines = [ImagenInline, MaterialUsadoInline]

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('patente', 'marca', 'modelo', 'cliente')
    search_fields = ('patente', 'cliente__nombre')

admin.site.register(Cliente)
admin.site.register(Material)