from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from .models import OrdenTrabajo, Cliente, Vehiculo, Material, ImagenOrden
from .forms import OrdenTrabajoForm, ClienteForm, VehiculoForm, MaterialForm
from django.http import FileResponse
import os

# Verifica si el usuario tiene permisos de administrador o mixto
def es_jefe(user):
    return user.groups.filter(name__in=["Administrador/a", "Usuario Mixto"]).exists()


@login_required
def dashboard(request):
    ordenes = OrdenTrabajo.objects.all().order_by("-id")
    user = request.user
    es_admin = user.groups.filter(name="Administrador/a").exists()
    es_tecnico = user.groups.filter(name="Técnico/a").exists()
    es_mixto = user.groups.filter(name="Usuario Mixto").exists()

    context = {
        "ordenes": ordenes,
        "es_admin": es_admin,
        "es_tecnico": es_tecnico,
        "es_mixto": es_mixto,
    }
    return render(request, "dashboard.html", context)


# Vistas para gestión de empleados (solo accesibles por administradores)
@login_required
@user_passes_test(es_jefe)
def lista_usuarios(request):
    usuarios = User.objects.all()
    return render(request, "lista_usuarios.html", {"usuarios": usuarios})

@login_required
@user_passes_test(es_jefe)
def registrar_usuario(request):
    grupos = Group.objects.all()
    error = None
    if request.method == "POST":
        u = request.POST.get("username")
        p = request.POST.get("password")
        g_id = request.POST.get("grupo")
        if not g_id:
            error = "Debes seleccionar un rol para el empleado."
        else:
            nuevo_user = User.objects.create_user(username=u, password=p)
            grupo = Group.objects.get(id=g_id)
            nuevo_user.groups.add(grupo)
            return redirect("lista_usuarios")
    return render(request, "registrar_usuario.html", {"grupos": grupos, "error": error})

@login_required
@user_passes_test(es_jefe)
def eliminar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    if usuario != request.user:
        usuario.delete()
    return redirect("lista_usuarios")


# Vistas para crear, ver y editar órdenes de trabajo
@login_required
def crear_orden(request):
    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = OrdenTrabajoForm()
    return render(request, "formulario.html", {"form": form, "titulo": "Nueva Orden"})

@login_required
def ver_orden(request, orden_id):
    orden = get_object_or_404(OrdenTrabajo, id=orden_id)
    return render(request, "ver_orden.html", {"orden": orden})

@login_required
def editar_orden(request, orden_id):
    orden = get_object_or_404(OrdenTrabajo, id=orden_id)
    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST, instance=orden)
        if form.is_valid():
            form.save()
            for archivo in request.FILES.getlist("imagenes"):
                ImagenOrden.objects.create(orden=orden, imagen=archivo)
            return redirect("ver_orden", orden_id=orden.id)
    else:
        form = OrdenTrabajoForm(instance=orden)
    return render(request, "editar_orden.html", {"form": form, "orden": orden})

@login_required
def lista_ordenes(request):
    ordenes = OrdenTrabajo.objects.all().order_by("-id")
    return render(request, "lista_ordenes.html", {"ordenes": ordenes})


# Vistas para registrar clientes y vehículos
@login_required
def crear_cliente(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = ClienteForm()
    return render(request, "formulario.html", {"form": form, "titulo": "Nuevo Cliente"})

@login_required
def crear_vehiculo(request):
    if request.method == "POST":
        form = VehiculoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = VehiculoForm()
    return render(request, "formulario.html", {"form": form, "titulo": "Nuevo Vehículo"})


# Vistas del inventario de bodega
@login_required
def agregar_material(request):
    if request.method == "POST":
        form = MaterialForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista_materiales")
    else:
        form = MaterialForm()
    return render(request, "formulario.html", {"form": form, "titulo": "Agregar Material"})

@login_required
def lista_materiales(request):
    query = request.GET.get("q")
    materiales = Material.objects.all()
    if query:
        materiales = materiales.filter(nombre__icontains=query)
    return render(request, "lista_materiales.html", {"materiales": materiales})


# Vistas para manejo de imágenes adjuntas a órdenes
@login_required
def eliminar_imagen(request, imagen_id):
    imagen = get_object_or_404(ImagenOrden, id=imagen_id)
    orden_id = imagen.orden.id
    imagen.delete()
    return redirect("editar_orden", orden_id=orden_id)

@login_required
def descargar_imagen(request, imagen_id):
    imagen = get_object_or_404(ImagenOrden, id=imagen_id)
    return FileResponse(imagen.imagen.open(), as_attachment=True)