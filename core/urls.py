from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Órdenes, Clientes, Vehículos y Materiales
    path('orden/nueva/', views.crear_orden, name='crear_orden'),
    path('cliente/nuevo/', views.crear_cliente, name='crear_cliente'),
    path('vehiculo/nuevo/', views.crear_vehiculo, name='crear_vehiculo'),
    path('material/agregar/', views.agregar_material, name='agregar_material'),
    path('ordenes/', views.lista_ordenes, name='lista_ordenes'),
    path('materiales/', views.lista_materiales, name='lista_materiales'),
    path('orden/<int:orden_id>/', views.ver_orden, name='ver_orden'),
    path('orden/editar/<int:orden_id>/', views.editar_orden, name='editar_orden'),
    path('imagen/eliminar/<int:imagen_id>/', views.eliminar_imagen, name='eliminar_imagen'),
    path('imagen/descargar/<int:imagen_id>/', views.descargar_imagen, name='descargar_imagen'),

    # Gestión de Empleados
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/registrar/', views.registrar_usuario, name='registrar_usuario'),
    path('usuarios/eliminar/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),
]