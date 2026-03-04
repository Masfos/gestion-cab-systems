from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.http import HttpResponseForbidden, FileResponse
from .models import OrdenTrabajo, Cliente, Vehiculo, Material, ImagenOrden, MaterialUsado
from .forms import (
    OrdenTrabajoForm, ClienteForm, VehiculoForm, 
    MaterialForm, RegistroTrabajadorForm
)
import os

def es_admin(user):
    return user.is_superuser or user.groups.filter(name="Administrador").exists()

@login_required
def dashboard(request):
    ordenes = OrdenTrabajo.objects.all().select_related('vehiculo__cliente').order_by("-id")
    ctx = {
        "ordenes": ordenes,
        "en_proceso_count": ordenes.filter(estado='en_proceso').count(),
        "terminadas_count": ordenes.filter(estado='terminado').count(),
        "es_admin": es_admin(request.user),
    }
    return render(request, "dashboard.html", ctx)

@login_required
def ver_orden(request, orden_id):
    # prefetch_related asegura que las fotos y materiales carguen sin error
    orden = get_object_or_404(
        OrdenTrabajo.objects.prefetch_related('imagenes', 'materiales_usados__material'), 
        id=orden_id
    )
    return render(request, "ver_orden.html", {"orden": orden})

@login_required
def crear_orden(request):
    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST, request.FILES)
        if form.is_valid():
            orden = form.save(commit=False)
            orden.creado_por = request.user
            orden.save()
            for f in request.FILES.getlist('fotos'):
                ImagenOrden.objects.create(orden=orden, imagen=f)
            return redirect("dashboard")
    else:
        form = OrdenTrabajoForm()
    return render(request, "formulario.html", {"form": form, "titulo": "Nueva Orden"})

@login_required
def editar_orden(request, orden_id):
    orden = get_object_or_404(OrdenTrabajo, id=orden_id)
    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST, request.FILES, instance=orden)
        if form.is_valid():
            form.save()
            for f in request.FILES.getlist('fotos_adicionales'):
                ImagenOrden.objects.create(orden=orden, imagen=f)
            return redirect("ver_orden", orden_id=orden.id)
    else:
        form = OrdenTrabajoForm(instance=orden)
    return render(request, "editar_orden.html", {"form": form, "orden": orden})

@login_required
def registrar_usuario(request):
    if not es_admin(request.user): return HttpResponseForbidden()
    if request.method == "POST":
        form = RegistroTrabajadorForm(request.POST)
        if form.is_valid():
            user = form.save()
            grupo_id = request.POST.get('grupo')
            if grupo_id:
                grupo = Group.objects.filter(id=grupo_id).first()
                if grupo: user.groups.add(grupo)
            return redirect("lista_usuarios")
    else:
        form = RegistroTrabajadorForm()
    return render(request, "registrar_usuario.html", {"form": form, "grupos": Group.objects.all()})

@login_required
def lista_usuarios(request):
    if not es_admin(request.user): return HttpResponseForbidden()
    return render(request, "lista_usuarios.html", {"usuarios": User.objects.all()})

@login_required
def eliminar_usuario(request, user_id):
    if not es_admin(request.user): return HttpResponseForbidden()
    u = get_object_or_404(User, id=user_id)
    if not u.is_superuser: u.delete()
    return redirect("lista_usuarios")

@login_required
def crear_cliente(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else: form = ClienteForm()
    return render(request, "formulario.html", {"form": form, "titulo": "Nuevo Cliente"})

@login_required
def crear_vehiculo(request):
    if request.method == "POST":
        form = VehiculoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else: form = VehiculoForm()
    return render(request, "vehiculo_form.html", {"form": form})

@login_required
def lista_materiales(request):
    return render(request, "lista_materiales.html", {"materiales": Material.objects.all()})

@login_required
def agregar_material(request):
    if request.method == "POST":
        form = MaterialForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista_materiales")
    else: form = MaterialForm()
    return render(request, "formulario.html", {"form": form, "titulo": "Nuevo Material"})

@login_required
def descargar_imagen(request, imagen_id):
    img = get_object_or_404(ImagenOrden, id=imagen_id)
    return FileResponse(open(img.imagen.path, 'rb'), as_attachment=True)