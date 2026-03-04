from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Usuarios
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/registrar/', views.registrar_usuario, name='registrar_usuario'),
    path('usuarios/eliminar/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),

    # Ordenes
    path('orden/crear/', views.crear_orden, name='crear_orden'),
    path('orden/ver/<int:orden_id>/', views.ver_orden, name='ver_orden'),
    path('orden/detalle/<int:orden_id>/', views.ver_orden, name='detalle_orden'),
    path('orden/editar/<int:orden_id>/', views.editar_orden, name='editar_orden'),
    path('orden/eliminar/<int:orden_id>/', views.eliminar_orden, name='eliminar_orden'),

    # Clientes
    path('cliente/crear/', views.crear_cliente, name='crear_cliente'),
    path('cliente/editar/<int:cliente_id>/', views.editar_cliente, name='editar_cliente'),
    path('cliente/eliminar/<int:cliente_id>/', views.eliminar_cliente, name='eliminar_cliente'),

    # Vehiculos
    path('vehiculo/crear/', views.crear_vehiculo, name='crear_vehiculo'),
    path('vehiculo/editar/<int:vehiculo_id>/', views.editar_vehiculo, name='editar_vehiculo'),
    path('vehiculo/eliminar/<int:vehiculo_id>/', views.eliminar_vehiculo, name='eliminar_vehiculo'),

    # Inventario
    path('materiales/', views.lista_materiales, name='lista_materiales'),
    path('materiales/agregar/', views.agregar_material, name='agregar_material'),

    # Materiales en Orden
    path('orden/<int:orden_id>/material/agregar/', views.agregar_material_orden, name='agregar_material'),
    path('material/<int:item_id>/editar/', views.editar_material_orden, name='editar_material'),
    path('material/<int:item_id>/eliminar/', views.eliminar_material_orden, name='eliminar_material'),

    # Imagenes
    path('imagen/descargar/<int:imagen_id>/', views.descargar_imagen, name='descargar_imagen'),
    path('ajax/vehiculos/', views.vehiculos_por_cliente, name='ajax_vehiculos'),
    path('materiales/eliminar/<int:material_id>/', views.eliminar_material, name='eliminar_material_bodega'),
]