from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, FileResponse
from .models import OrdenTrabajo, Cliente, Vehiculo, Material, ImagenOrden
from .forms import OrdenTrabajoForm, ClienteForm, VehiculoForm, MaterialForm

# --- Utilidades de acceso ---
def es_admin(user):
    return user.is_superuser or user.groups.filter(name="Administrador/a").exists()

# --- Vistas de Dashboard y Órdenes ---

@login_required
def dashboard(request):
    # Listado principal ordenado por ID descendente
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
    return render(request, "ver_orden.html", {
        "orden": orden, 
        "es_admin": es_admin(request.user)
    })

@login_required
def crear_orden(request):
    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST)
        if form.is_valid():
            orden = form.save()
            # Procesamos las fotos adicionales subidas manualmente
            fotos = request.FILES.getlist('fotos_adicionales')
            for f in fotos:
                ImagenOrden.objects.create(orden=orden, imagen=f)
            return redirect("ver_orden", orden_id=orden.id)
    else:
        form = OrdenTrabajoForm()
    return render(request, "formulario.html", {"form": form, "titulo": "Nueva Orden"})

@login_required
def editar_orden(request, orden_id):
    orden = get_object_or_404(OrdenTrabajo, id=orden_id)
    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST, instance=orden)
        if form.is_valid():
            form.save()
            # Manejo de fotos para evitar errores de almacenamiento en el servidor
            fotos = request.FILES.getlist('fotos_adicionales')
            for f in fotos:
                ImagenOrden.objects.create(orden=orden, imagen=f)
            return redirect("ver_orden", orden_id=orden.id)
    else:
        form = OrdenTrabajoForm(instance=orden)
    return render(request, "editar_orden.html", {"form": form, "orden": orden})

@login_required
def eliminar_orden(request, orden_id):
    if request.method == "POST" and es_admin(request.user):
        get_object_or_404(OrdenTrabajo, id=orden_id).delete()
        return redirect("dashboard")
    return HttpResponseForbidden()

# --- Clientes y Vehículos ---

@login_required
def crear_cliente(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    form = ClienteForm()
    return render(request, "formulario.html", {"form": form, "titulo": "Nuevo Cliente"})

@login_required
def eliminar_cliente(request, cliente_id):
    if request.method == "POST" and es_admin(request.user):
        get_object_or_404(Cliente, id=cliente_id).delete()
        return redirect("dashboard")
    return HttpResponseForbidden()

@login_required
def crear_vehiculo(request):
    if request.method == "POST":
        form = VehiculoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    form = VehiculoForm()
    return render(request, "vehiculo_form.html", {"form": form, "titulo": "Nuevo Vehículo"})

@login_required
def eliminar_vehiculo(request, vehiculo_id):
    if request.method == "POST" and es_admin(request.user):
        get_object_or_404(Vehiculo, id=vehiculo_id).delete()
        return redirect("dashboard")
    return HttpResponseForbidden()

# --- Inventario y Multimedia ---

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

# --- Personal ---

@login_required
def lista_usuarios(request):
    if not es_admin(request.user):
        return HttpResponseForbidden()
    return render(request, "lista_usuarios.html", {"usuarios": User.objects.all()})

@login_required
def registrar_usuario(request):
    # Lógica de registro pendiente según diseño de formulario de usuario
    return render(request, "formulario_usuario.html")

@login_required
def eliminar_usuario(request, user_id):
    if request.method == "POST" and es_admin(request.user):
        target = get_object_or_404(User, id=user_id)
        if not target.is_superuser: target.delete()
        return redirect("lista_usuarios")
    return HttpResponseForbidden()