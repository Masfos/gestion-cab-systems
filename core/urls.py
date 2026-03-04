from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Órdenes
    path('orden/crear/', views.crear_orden, name='crear_orden'),
    path('orden/ver/<int:orden_id>/', views.ver_orden, name='ver_orden'),
    path('orden/detalle/<int:orden_id>/', views.ver_orden, name='detalle_orden'), # Alias
    path('orden/editar/<int:orden_id>/', views.editar_orden, name='editar_orden'),
    path('orden/eliminar/<int:orden_id>/', views.eliminar_orden, name='eliminar_orden'),

    # Usuarios
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/registrar/', views.registrar_usuario, name='registrar_usuario'),
    path('usuarios/eliminar/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),

    # Entidades
    path('cliente/crear/', views.crear_cliente, name='crear_cliente'),
    path('vehiculo/crear/', views.crear_vehiculo, name='crear_vehiculo'),
    path('materiales/', views.lista_materiales, name='lista_materiales'),
    path('materiales/agregar/', views.agregar_material, name='agregar_material'),
    
    # Media
    path('descargar-img/<int:imagen_id>/', views.descargar_imagen, name='descargar_imagen'),
]