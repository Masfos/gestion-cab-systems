from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, FileResponse, Http404
from .models import OrdenTrabajo, Cliente, Vehiculo, Material, ImagenOrden
from .forms import OrdenTrabajoForm, ClienteForm, VehiculoForm, MaterialForm, RegistroTrabajadorForm
import os

@login_required
def dashboard(request):
    u = request.user
    ctx = {
        "ordenes": OrdenTrabajo.objects.all().order_by("-id"),
        "es_admin": u.is_superuser or u.groups.filter(name="Administrador/a").exists(),
        "es_tecnico": u.groups.filter(name="Técnico/a").exists(),
        "es_mixto": u.groups.filter(name="Usuario Mixto").exists(),
    }
    return render(request, "dashboard.html", ctx)

@login_required
def ver_orden(request, orden_id):
    # El prefetch_related es CRUCIAL para las vistas previas de imágenes
    orden = get_object_or_404(OrdenTrabajo.objects.prefetch_related('imagenes'), id=orden_id)
    return render(request, "ver_orden.html", {"orden": orden})

@login_required
def crear_orden(request):
    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST, request.FILES)
        if form.is_valid():
            orden = form.save(commit=False)
            # Restauramos lo que faltaba:
            orden.cliente = orden.vehiculo.cliente # Asigna cliente automático
            orden.creado_por = request.user        # Guarda quién la hizo
            orden.save()
            # Guardado de múltiples fotos para vista previa
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
            orden.modificado_por = request.user # Registra quién editó
            orden.save()
            for f in request.FILES.getlist('fotos'): 
                ImagenOrden.objects.create(orden=orden, imagen=f)
            return redirect("dashboard")
    else:
        form = OrdenTrabajoForm(instance=orden)
    return render(request, "formulario.html", {"form": form, "titulo": "Editar Orden"})

# Funciones de eliminación que Railway exige
@login_required
def eliminar_orden(request, orden_id):
    if not (request.user.is_superuser or request.user.groups.filter(name="Administrador/a").exists()):
        return HttpResponseForbidden()
    get_object_or_404(OrdenTrabajo, id=orden_id).delete()
    return redirect("dashboard")

@login_required
def eliminar_usuario(request, user_id):
    if not (request.user.is_superuser or request.user.groups.filter(name="Administrador/a").exists()):
        return HttpResponseForbidden()
    u = get_object_or_404(User, id=user_id)
    if not u.is_superuser and u != request.user: u.delete()
    return redirect("lista_usuarios")

# ... (Mantén tus otras funciones de Clientes, Vehículos y Materiales igual) ...

@login_required
def descargar_imagen(request, imagen_id):
    img = get_object_or_404(ImagenOrden, id=imagen_id)
    try:
        return FileResponse(img.imagen.open('rb'), as_attachment=True, filename=os.path.basename(img.imagen.name))
    except:
        raise Http404("Imagen no encontrada")