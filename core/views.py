from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, FileResponse, Http404
from .models import OrdenTrabajo, Cliente, Vehiculo, Material, ImagenOrden, MaterialUsado
from .forms import OrdenTrabajoForm, ClienteForm, VehiculoForm, MaterialForm, RegistroTrabajadorForm, MaterialUsadoForm
import os
import json

# --- Utilidades de acceso ---
def es_admin(user):
    return user.is_superuser or user.groups.filter(name="Administrador/a").exists()

# --- Dashboard ---
@login_required
def dashboard(request):
    u = request.user
    ctx = {
        "ordenes": OrdenTrabajo.objects.all().order_by("-id"),
        "clientes": Cliente.objects.all().order_by("-id"),
        "vehiculos": Vehiculo.objects.all().order_by("-id"),
        "es_admin": es_admin(u),
        "es_tecnico": u.groups.filter(name="Técnico/a").exists(),
        "es_mixto": u.groups.filter(name="Usuario Mixto").exists(),
    }
    return render(request, "dashboard.html", ctx)

@login_required
def ver_orden(request, orden_id):
    orden = get_object_or_404(OrdenTrabajo.objects.prefetch_related('imagenes'), id=orden_id)
    return render(request, "ver_orden.html", {"orden": orden, "es_admin": es_admin(request.user)})

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
    return render(request, "formulario.html", {"form": form, "titulo": "Nueva Orden", "vehiculos_json": json.dumps(list(Vehiculo.objects.values("id", "cliente_id", "marca", "modelo", "patente")))})

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
    return render(request, "formulario.html", {"form": form, "titulo": "Editar Orden", "orden": orden, "vehiculos_json": json.dumps(list(Vehiculo.objects.values("id", "cliente_id", "marca", "modelo", "patente")))})

@login_required
def eliminar_orden(request, orden_id):
    if not es_admin(request.user): return HttpResponseForbidden()
    get_object_or_404(OrdenTrabajo, id=orden_id).delete()
    return redirect("dashboard")

# --- Clientes ---
@login_required
def crear_cliente(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = ClienteForm()
    return render(request, "formulario.html", {"form": form, "titulo": "Nuevo Cliente", "es_cliente_form": True})

@login_required
def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if request.method == "POST":
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = ClienteForm(instance=cliente)
    return render(request, "formulario.html", {"form": form, "titulo": "Editar Cliente", "es_cliente_form": True})

@login_required
def eliminar_cliente(request, cliente_id):
    if not es_admin(request.user): return HttpResponseForbidden()
    get_object_or_404(Cliente, id=cliente_id).delete()
    return redirect("dashboard")

# --- Vehiculos ---
@login_required
def crear_vehiculo(request):
    if request.method == "POST":
        form = VehiculoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = VehiculoForm()
    return render(request, "formulario.html", {"form": form, "titulo": "Nuevo Vehiculo"})

@login_required
def editar_vehiculo(request, vehiculo_id):
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id)
    if request.method == "POST":
        form = VehiculoForm(request.POST, instance=vehiculo)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = VehiculoForm(instance=vehiculo)
    return render(request, "formulario.html", {"form": form, "titulo": "Editar Vehiculo"})

@login_required
def eliminar_vehiculo(request, vehiculo_id):
    if not es_admin(request.user): return HttpResponseForbidden()
    get_object_or_404(Vehiculo, id=vehiculo_id).delete()
    return redirect("dashboard")

# --- Inventario ---
@login_required
def lista_materiales(request):
    q = request.GET.get("q", "")
    mats = Material.objects.filter(nombre__icontains=q) if q else Material.objects.all()
    return render(request, "lista_materiales.html", {"materiales": mats, "q": q, "es_admin": es_admin(request.user)})

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

# --- Personal ---
@login_required
def lista_usuarios(request):
    if not es_admin(request.user): return HttpResponseForbidden()
    return render(request, "lista_usuarios.html", {"usuarios": User.objects.all()})

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
        return FileResponse(img.imagen.open('rb'), as_attachment=True, filename=os.path.basename(img.imagen.name))
    except:
        raise Http404("Archivo no encontrado")

# --- Materiales en Orden ---
@login_required
def agregar_material_orden(request, orden_id):
    orden = get_object_or_404(OrdenTrabajo, id=orden_id)
    if request.method == "POST":
        form = MaterialUsadoForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.orden = orden
            item.save()
            return redirect("editar_orden", orden_id=orden.id)
    else:
        form = MaterialUsadoForm()
    return render(request, "formulario.html", {"form": form, "titulo": "Agregar Material"})

@login_required
def editar_material_orden(request, item_id):
    item = get_object_or_404(MaterialUsado, id=item_id)
    if request.method == "POST":
        form = MaterialUsadoForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("editar_orden", orden_id=item.orden.id)
    else:
        form = MaterialUsadoForm(instance=item)
    return render(request, "formulario.html", {"form": form, "titulo": "Editar Material"})

@login_required
def eliminar_material_orden(request, item_id):
    if not es_admin(request.user): return HttpResponseForbidden()
    item = get_object_or_404(MaterialUsado, id=item_id)
    orden_id = item.orden.id
    item.delete()
    return redirect("editar_orden", orden_id=orden_id)


@login_required
def eliminar_material(request, material_id):
    if not es_admin(request.user):
        return HttpResponseForbidden()
    get_object_or_404(Material, id=material_id).delete()
    return redirect("lista_materiales")


# --- AJAX ---
from django.http import JsonResponse

@login_required
def vehiculos_por_cliente(request):
    cliente_id = request.GET.get('cliente_id')
    if not cliente_id:
        return JsonResponse({'vehiculos': []})
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        # Buscar vehículos del cliente y de otros clientes de la misma empresa
        if cliente.empresa:
            vehiculos = Vehiculo.objects.filter(
                cliente__empresa=cliente.empresa
            ).order_by('-id')
        else:
            vehiculos = Vehiculo.objects.filter(cliente=cliente).order_by('-id')
        data = [
            {
                'id': v.id,
                'text': f"{v.marca} {v.modelo} [{v.patente}] - {v.cliente.nombre}"
            }
            for v in vehiculos
        ]
        return JsonResponse({'vehiculos': data})
    except Cliente.DoesNotExist:
        return JsonResponse({'vehiculos': []})


@login_required
def editar_material_bodega(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    if request.method == "POST":
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            form.save()
            return redirect("lista_materiales")
    else:
        form = MaterialForm(instance=material)
    return render(request, "formulario.html", {"form": form, "titulo": "Editar Material"})


@login_required
def eliminar_imagen(request, imagen_id):
    if not es_admin(request.user):
        return HttpResponseForbidden()
    img = get_object_or_404(ImagenOrden, id=imagen_id)
    orden_id = img.orden.id
    img.delete()
    return redirect("editar_orden", orden_id=orden_id)