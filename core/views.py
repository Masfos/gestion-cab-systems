from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, FileResponse, Http404
from .models import OrdenTrabajo, Cliente, Vehiculo, Material, ImagenOrden
from .forms import OrdenTrabajoForm, ClienteForm, VehiculoForm, MaterialForm, RegistroTrabajadorForm
import os

# --- SEGURIDAD ---
def es_admin(user):
    return user.is_superuser or user.groups.filter(name="Administrador/a").exists()

# --- DASHBOARD Y ÓRDENES ---
@login_required
def dashboard(request):
    u = request.user
    ctx = {
        "ordenes": OrdenTrabajo.objects.all().order_by("-id"),
        "es_admin": es_admin(u),
        "es_tecnico": u.groups.filter(name="Técnico/a").exists(),
        "es_mixto": u.groups.filter(name="Usuario Mixto").exists(),
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
            orden.cliente, orden.creado_por = orden.vehiculo.cliente, request.user
            orden.save()
            for f in request.FILES.getlist('fotos'): 
                ImagenOrden.objects.create(orden=orden, imagen=f)
            return redirect("dashboard")
    return render(request, "formulario.html", {"form": OrdenTrabajoForm(), "titulo": "Nueva Orden"})

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
    return render(request, "formulario.html", {"form": OrdenTrabajoForm(instance=orden), "titulo": "Editar Orden"})

@login_required
def eliminar_orden(request, orden_id):
    if not es_admin(request.user): return HttpResponseForbidden()
    get_object_or_404(OrdenTrabajo, id=orden_id).delete()
    return redirect("dashboard")

# --- MATERIALES ---
@login_required
def lista_materiales(request):
    q = request.GET.get("q", "")
    mats = Material.objects.filter(nombre__icontains=q) if q else Material.objects.all()
    return render(request, "lista_materiales.html", {"materiales": mats})

@login_required
def agregar_material(request):
    if request.method == "POST":
        form = MaterialForm(request.POST)
        if form.is_valid(): form.save(); return redirect("lista_materiales")
    return render(request, "formulario.html", {"form": MaterialForm(), "titulo": "Registrar Nuevo Material"})

# --- GESTIÓN DE PERSONAL (USUARIOS) ---
@login_required
def lista_usuarios(request):
    if not es_admin(request.user): return HttpResponseForbidden()
    return render(request, "lista_usuarios.html", {"usuarios": User.objects.all()})

@login_required
def registrar_usuario(request):
    if not es_admin(request.user): return HttpResponseForbidden()
    if request.method == "POST":
        form = RegistroTrabajadorForm(request.POST)
        if form.is_valid(): form.save(); return redirect("lista_usuarios")
    return render(request, "formulario.html", {"form": RegistroTrabajadorForm(), "titulo": "Nuevo Trabajador"})

@login_required
def eliminar_usuario(request, user_id):
    if not es_admin(request.user): return HttpResponseForbidden()
    u = get_object_or_404(User, id=user_id)
    if not u.is_superuser and u != request.user:
        u.delete()
    return redirect("lista_usuarios")

# --- MULTIMEDIA Y DESCARGAS ---
@login_required
def descargar_imagen(request, imagen_id):
    img = get_object_or_404(ImagenOrden, id=imagen_id)
    try:
        return FileResponse(img.imagen.open('rb'), as_attachment=True, filename=os.path.basename(img.imagen.name))
    except Exception:
        raise Http404("Archivo no encontrado")