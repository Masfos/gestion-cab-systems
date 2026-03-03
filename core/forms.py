from django import forms
from .models import OrdenTrabajo, Cliente, Vehiculo, Material

class EstiloBaseForm(forms.ModelForm):
    # Clase base para no repetir el bucle de bootstrap en cada formulario
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class OrdenTrabajoForm(EstiloBaseForm):
    # Campo extra para soportar múltiples archivos desde el template
    fotos_adicionales = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        required=False,
        label="Agregar fotos"
    )

    class Meta:
        model = OrdenTrabajo
        fields = ['vehiculo', 'descripcion', 'estado']

class ClienteForm(EstiloBaseForm):
    class Meta:
        model = Cliente
        fields = '__all__'

class VehiculoForm(EstiloBaseForm):
    class Meta:
        model = Vehiculo
        fields = '__all__'

class MaterialForm(EstiloBaseForm):
    class Meta:
        model = Material
        fields = '__all__'