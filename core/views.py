from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, FileResponse, Http404
from .models import OrdenTrabajo, Cliente, Vehiculo, Material, ImagenOrden
from .forms import (
    OrdenTrabajoForm, ClienteForm, VehiculoForm, 
    MaterialForm, RegistroTrabajadorForm
)
import os

# --- Utilidades ---
def es_admin(user):
    return user.is_superuser or user.groups.filter(name="Administrador").exists()

# --- Órdenes de Trabajo ---

@login_required
def dashboard(request):
    ordenes = OrdenTrabajo.objects.all().order_by("-id")
    u = request.user
    ctx = {
        "ordenes": ordenes,
        "es_admin": es_admin(u),
        "es_tecnico": u.groups.filter(name="Técnico").exists(),
        "es_mixto": u.groups.filter(name="Mixto").exists(),
    }
    return render(request, "dashboard.html", ctx)

@login_required
def ver_orden(request, orden_id):
    orden = get_object_or_404(OrdenTrabajo.objects.prefetch_related('imagenes'), id=orden_id)
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
    return render(request, "formulario.html", {"form": form, "titulo": "Nueva Orden de Trabajo"})

@login_required
def editar_orden(request, orden_id):
    orden = get_object_or_404(OrdenTrabajo, id=orden_id)
    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST, request.FILES, instance=orden)
        if form.is_valid():
            orden = form.save(commit=False)
            orden.modificado_por = request.user
            orden.save()
            for f in request.FILES.getlist('fotos'): 
                ImagenOrden.objects.create(orden=orden, imagen=f)
            return redirect("dashboard")
    else:
        form = OrdenTrabajoForm(instance=orden)
    return render(request, "formulario.html", {"form": form, "titulo": f"Editar Orden #{orden.id}"})

@login_required
def eliminar_orden(request, orden_id):
    if not es_admin(request.user): return HttpResponseForbidden()
    get_object_or_404(OrdenTrabajo, id=orden_id).delete()
    return redirect("dashboard")

# --- Gestión de Clientes ---

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
def eliminar_cliente(request, cliente_id):
    if not es_admin(request.user): return HttpResponseForbidden()
    get_object_or_404(Cliente, id=cliente_id).delete()
    return redirect("dashboard")

# --- Gestión de Vehículos ---

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

@login_required
def eliminar_vehiculo(request, vehiculo_id):
    if not es_admin(request.user): return HttpResponseForbidden()
    get_object_or_404(Vehiculo, id=vehiculo_id).delete()
    return redirect("dashboard")

# --- Inventario / Materiales (Restaurado) ---

@login_required
def lista_materiales(request):
    q = request.GET.get("q", "")
    if q:
        materiales = Material.objects.filter(nombre__icontains=q)
    else:
        materiales = Material.objects.all()
    return render(request, "lista_materiales.html", {"materiales": materiales})

@login_required
def agregar_material(request):
    if request.method == "POST":
        form = MaterialForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista_materiales")
    else:
        form = MaterialForm()
    return render(request, "formulario.html", {"form": form, "titulo": "Registrar Material"})

# --- Personal y Usuarios (Restaurado) ---

@login_required
def lista_usuarios(request):
    if not es_admin(request.user): return HttpResponseForbidden()
    usuarios = User.objects.all()
    return render(request, "lista_usuarios.html", {"usuarios": usuarios})

@login_required
def registrar_usuario(request):
    if not es_admin(request.user): return HttpResponseForbidden()
    if request.method == "POST":
        form = RegistroTrabajadorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista_usuarios")
    else:
        form = RegistroTrabajadorForm()
    return render(request, "formulario.html", {"form": form, "titulo": "Nuevo Trabajador"})

@login_required
def eliminar_usuario(request, user_id):
    if not es_admin(request.user): return HttpResponseForbidden()
    u = get_object_or_404(User, id=user_id)
    if not u.is_superuser and u != request.user:
        u.delete()
    return redirect("lista_usuarios")

# --- Multimedia ---

@login_required
def descargar_imagen(request, imagen_id):
    img = get_object_or_404(ImagenOrden, id=imagen_id)
    try:
        return FileResponse(img.imagen.open('rb'), as_attachment=True)
    except Exception:
        raise Http404("El archivo no existe en el servidor.")