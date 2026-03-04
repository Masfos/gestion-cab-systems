from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, FileResponse
from .models import OrdenTrabajo, Cliente, Vehiculo, Material, ImagenOrden
from .forms import OrdenTrabajoForm, ClienteForm, VehiculoForm, MaterialForm, RegistroTrabajadorForm

def es_admin(user):
    return user.is_superuser or user.groups.filter(name="Administrador/a").exists()

# --- Vistas de Dashboard y Órdenes ---

@login_required
def dashboard(request):
    ordenes = OrdenTrabajo.objects.all().order_by("-id")
    u = request.user
    ctx = {
        "ordenes": ordenes,
        "es_admin": es_admin(u),
        "es_tecnico": u.groups.filter(name="Técnico/a").exists(),
        "es_mixto": u.groups.filter(name="Usuario Mixto").exists(),
    }
    return render(request, "dashboard.html", ctx)

@login_required
def ver_orden(request, orden_id):
    orden = get_object_or_404(OrdenTrabajo, id=orden_id)
    return render(request, "ver_orden.html", {"orden": orden})

@login_required
def crear_orden(request):
    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST, request.FILES)
        if form.is_valid():
            orden = form.save(commit=False)
            orden.cliente = orden.vehiculo.cliente
            orden.creado_por = request.user
            orden.save()
            files = request.FILES.getlist('fotos')
            for f in files:
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
            files = request.FILES.getlist('fotos')
            for f in files:
                ImagenOrden.objects.create(orden=orden, imagen=f)
            return redirect("dashboard")
    else:
        form = OrdenTrabajoForm(instance=orden)
    return render(request, "formulario.html", {"form": form, "titulo": f"Editar Orden #{orden.id}"})

@login_required
def eliminar_orden(request, orden_id):
    if not es_admin(request.user):
        return HttpResponseForbidden()
    orden = get_object_or_404(OrdenTrabajo, id=orden_id)
    if request.method == "POST":
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
    form = ClienteForm()
    return render(request, "formulario.html", {"form": form, "titulo": "Registrar Cliente"})

@login_required
def crear_vehiculo(request):
    if request.method == "POST":
        form = VehiculoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    form = VehiculoForm()
    return render(request, "formulario.html", {"form": form, "titulo": "Registrar Vehículo"})

# --- Materiales ---

@login_required
def lista_materiales(request):
    q = request.GET.get("q", "")
    items = Material.objects.all()
    if q:
        items = items.filter(nombre__icontains=q)
    return render(request, "lista_materiales.html", {"materiales": items})

@login_required
def agregar_material(request):
    if request.method == "POST":
        form = MaterialForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista_materiales")
    form = MaterialForm()
    return render(request, "formulario.html", {"form": form, "titulo": "Agregar Material"})

@login_required
def descargar_imagen(request, imagen_id):
    img = get_object_or_404(ImagenOrden, id=imagen_id)
    return FileResponse(img.imagen.open(), as_attachment=True)

# --- Personal (Corregido) ---

@login_required
def lista_usuarios(request):
    if not es_admin(request.user):
        return HttpResponseForbidden()
    return render(request, "lista_usuarios.html", {"usuarios": User.objects.all()})

@login_required
def registrar_usuario(request):
    if not es_admin(request.user):
        return HttpResponseForbidden()
    
    if request.method == "POST":
        form = RegistroTrabajadorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista_usuarios")
    else:
        form = RegistroTrabajadorForm()
    return render(request, "formulario.html", {"form": form, "titulo": "Registrar Nuevo Trabajador"})

@login_required
def eliminar_usuario(request, user_id):
    if not es_admin(request.user):
        return HttpResponseForbidden()
    u = get_object_or_404(User, id=user_id)
    if u.is_superuser or u == request.user:
        return redirect("lista_usuarios")
    u.delete()
    return redirect("lista_usuarios")