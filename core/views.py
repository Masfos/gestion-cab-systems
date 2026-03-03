from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from .models import OrdenTrabajo, Cliente, Vehiculo, Material, ImagenOrden
from .forms import OrdenTrabajoForm, ClienteForm, VehiculoForm, MaterialForm
from django.http import FileResponse, HttpResponseForbidden
from django.core.exceptions import PermissionDenied

def es_admin(user):
    return user.is_superuser or user.groups.filter(name="Administrador/a").exists()

@login_required
def dashboard(request):
    ordenes = OrdenTrabajo.objects.all().order_by("-id")
    user = request.user
    context = {
        "ordenes": ordenes,
        "es_admin": es_admin(user),
        "es_tecnico": user.groups.filter(name="Técnico/a").exists(),
        "es_mixto": user.groups.filter(name="Usuario Mixto").exists(),
    }
    return render(request, "dashboard.html", context)

@login_required
def ver_orden(request, orden_id):
    orden = get_object_or_404(OrdenTrabajo, id=orden_id)
    return render(request, "ver_orden.html", {"orden": orden, "es_admin": es_admin(request.user)})

@login_required
def editar_orden(request, orden_id):
    orden = get_object_or_404(OrdenTrabajo, id=orden_id)
    
    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST, instance=orden)
        if form.is_valid():
            form.save()
            fotos = request.FILES.getlist('fotos_nuevas') 
            for f in fotos:
                ImagenOrden.objects.create(orden=orden, imagen=f)
                
            return redirect("ver_orden", orden_id=orden.id)
    else:
        form = OrdenTrabajoForm(instance=orden)
    
    return render(request, "editar_orden.html", {
        "form": form,
        "orden": orden
    })
    
@login_required
def eliminar_orden(request, orden_id):
    if request.method == "POST" and es_admin(request.user):
        orden = get_object_or_404(OrdenTrabajo, id=orden_id)
        orden.delete()
        return redirect("dashboard")
    return HttpResponseForbidden()

@login_required
@user_passes_test(es_admin)
def lista_usuarios(request):
    usuarios = User.objects.all()
    return render(request, "lista_usuarios.html", {"usuarios": usuarios})

@login_required
@user_passes_test(es_admin)
def registrar_usuario(request):
    grupos = Group.objects.all()
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        grupo_id = request.POST.get("grupo")
        if not grupo_id:
            error = "Debes seleccionar un rol."
        else:
            nuevo_user = User.objects.create_user(username=username, password=password)
            nuevo_user.groups.add(Group.objects.get(id=grupo_id))
            return redirect("lista_usuarios")
    return render(request, "registrar_usuario.html", {"grupos": grupos, "error": error})

@login_required
@user_passes_test(es_admin)
def eliminar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    if usuario == request.user or usuario.is_superuser:
        raise PermissionDenied("No puedes eliminar este usuario.")
    usuario.delete()
    return redirect("lista_usuarios")

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
    else:
        form = VehiculoForm()
    return render(request, "vehiculo_form.html", {"form": form, "titulo": "Nuevo Vehículo"})

@login_required
def eliminar_vehiculo(request, vehiculo_id):
    if request.method == "POST" and es_admin(request.user):
        get_object_or_404(Vehiculo, id=vehiculo_id).delete()
        return redirect("dashboard")
    return HttpResponseForbidden()

@login_required
def lista_materiales(request):
    query = request.GET.get("q")
    materiales = Material.objects.all()
    if query: materiales = materiales.filter(nombre__icontains=query)
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
    return render(request, "formulario.html", {"form": form, "titulo": "Agregar Material"})

@login_required
def descargar_imagen(request, imagen_id):
    imagen = get_object_or_404(ImagenOrden, id=imagen_id)
    return FileResponse(imagen.imagen.open(), as_attachment=True)