from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import OrdenTrabajo, Cliente, Vehiculo, ImagenOrden
from .forms import OrdenTrabajoForm

class ClienteCreateView(LoginRequiredMixin, CreateView):
    model = Cliente
    fields = ['nombre', 'telefono', 'email', 'direccion']
    template_name = 'cliente_form.html'  # Diseño oscuro CAB Systems
    success_url = reverse_lazy('dashboard')

class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    model = Cliente
    fields = ['nombre', 'telefono', 'email', 'direccion']
    template_name = 'cliente_form.html'  # Diseño oscuro CAB Systems
    success_url = reverse_lazy('dashboard')

class VehiculoCreateView(LoginRequiredMixin, CreateView):
    model = Vehiculo
    fields = ['patente', 'marca', 'modelo', 'anio', 'cliente']
    template_name = 'vehiculo_form.html'  # Diseño oscuro y corrección de "Año"
    success_url = reverse_lazy('dashboard')

class VehiculoUpdateView(LoginRequiredMixin, UpdateView):
    model = Vehiculo
    fields = ['patente', 'marca', 'modelo', 'anio', 'cliente']
    template_name = 'vehiculo_form.html'  # Diseño oscuro y corrección de "Año"
    success_url = reverse_lazy('dashboard')

@login_required
def dashboard(request):
    ordenes = OrdenTrabajo.objects.all().order_by('-id')
    return render(request, 'dashboard.html', {'ordenes': ordenes})

@login_required
def crear_orden(request):
    if request.method == 'POST':
        form = OrdenTrabajoForm(request.POST, request.FILES)
        if form.is_valid():
            orden = form.save()
            imagenes = request.FILES.getlist('imagenes')
            for img in imagenes:
                ImagenOrden.objects.create(orden=orden, imagen=img)
            return redirect('dashboard')
    else:
        form = OrdenTrabajoForm()
    return render(request, 'crear_orden.html', {'form': form})

@login_required
def editar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if request.method == 'POST':
        form = OrdenTrabajoForm(request.POST, request.FILES, instance=orden)
        if form.is_valid():
            form.save()
            imagenes = request.FILES.getlist('imagenes')
            for img in imagenes:
                ImagenOrden.objects.create(orden=orden, imagen=img)
            return redirect('dashboard')
    else:
        form = OrdenTrabajoForm(instance=orden)
    return render(request, 'editar_orden.html', {'form': form, 'orden': orden})

@login_required
def eliminar_imagen(request, imagen_id):
    imagen = get_object_or_404(ImagenOrden, id=imagen_id)
    orden_id = imagen.orden.id
    imagen.delete()
    return redirect('editar_orden', pk=orden_id)

@login_required
def descargar_imagen(request, imagen_id):
    imagen_obj = get_object_or_404(ImagenOrden, id=imagen_id)
    # Servir la imagen como descarga
    response = HttpResponse(imagen_obj.imagen, content_type="application/octet-stream")
    response['Content-Disposition'] = f'attachment; filename="{imagen_obj.imagen.name}"'
    return response