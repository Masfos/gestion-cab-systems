from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.http import HttpResponseForbidden, FileResponse
from .models import OrdenTrabajo, Cliente, Vehiculo, Material, ImagenOrden
from .forms import (
    OrdenTrabajoForm, ClienteForm, VehiculoForm, 
    MaterialForm, RegistroTrabajadorForm
)

# --- Utilidades ---
def es_admin(user):
    return user.is_superuser or user.groups.filter(name="Administrador").exists()

# --- Dashboard ---

@login_required
def dashboard(request):
    ordenes = OrdenTrabajo.objects.all().order_by("-id")
    u = request.user
    
    # CALCULOS DE MÉTRICAS (Esto soluciona el Error 500)
    en_proceso_count = ordenes.filter(estado='en_proceso').count()
    terminadas_count = ordenes.filter(estado='terminado').count()
    
    ctx = {
        "ordenes": ordenes,
        "en_proceso_count": en_proceso_count,
        "terminadas_count": terminadas_count,
        "es_admin": es_admin(u),
        "es_tecnico": u.groups.filter(name="Técnico").exists(),
        "es_mixto": u.groups.filter(name="Mixto").exists(),
    }
    return render(request, "dashboard.html", ctx)

# --- Órdenes de Trabajo ---

@login_required
def crear_orden(request):
    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST, request.FILES)
        if form.is_valid():
            orden = form.save(commit=False)
            orden.creado_por = request.user
            orden.save()
            
            # Guardar múltiples fotos desde el widget MultipleFileInput
            fotos = request.FILES.getlist('fotos')
            for f in fotos:
                ImagenOrden.objects.create(orden=orden, imagen=f)
                
            return redirect("dashboard")
    else:
        form = OrdenTrabajoForm()
    return render(request, "formulario.html", {"form": form, "titulo": "Nueva Orden de Trabajo"})

@login_required
def ver_orden(request, orden_id):
    orden = get_object_or_404(OrdenTrabajo.objects.prefetch_related('imagenes'), id=orden_id)
    return render(request, "ver_orden.html", {"orden": orden})

@login_required
def editar_orden(request, orden_id):
    orden = get_object_or_404(OrdenTrabajo, id=orden_id)
    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST, request.FILES, instance=orden)
        if form.is_valid():
            form.save()
            # Fotos nuevas en edición
            for f in request.FILES.getlist('fotos_adicionales'):
                ImagenOrden.objects.create(orden=orden, imagen=f)
            return redirect("ver_orden", orden_id=orden.id)
    else:
        form = OrdenTrabajoForm(instance=orden)
    return render(request, "editar_orden.html", {"form": form, "orden": orden})

@login_required
def eliminar_orden(request, orden_id):
    if not es_admin(request.user): return HttpResponseForbidden()
    orden = get_object_or_404(OrdenTrabajo, id=orden_id)
    orden.delete()
    return redirect("dashboard")

# --- Clientes y Vehículos ---

@login_required
def crear_cliente(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = ClienteForm()
    return render(request, "formulario.html", {"form": form, "titulo": "Registrar Cliente / Empresa"})

@login_required
def crear_vehiculo(request):
    if request.method == "POST":
        form = VehiculoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = VehiculoForm()
    return render(request, "vehiculo_form.html", {"form": form})

# --- Personal ---

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
            user = form.save()
            rol = request.POST.get('rol')
            if rol:
                grupo, _ = Group.objects.get_or_create(name=rol)
                user.groups.add(grupo)
            return redirect("lista_usuarios")
    else:
        form = RegistroTrabajadorForm()
    return render(request, "registrar_usuario.html", {"form": form, "grupos": Group.objects.all()})

@login_required
def eliminar_usuario(request, user_id):
    if not es_admin(request.user): return HttpResponseForbidden()
    u = get_object_or_404(User, id=user_id)
    if not u.is_superuser and u != request.user:
        u.delete()
    return redirect("lista_usuarios")

# --- Materiales e Imágenes ---

@login_required
def lista_materiales(request):
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

@login_required
def descargar_imagen(request, imagen_id):
    img = get_object_or_404(ImagenOrden, id=imagen_id)
    return FileResponse(open(img.imagen.path, 'rb'), as_attachment=True)