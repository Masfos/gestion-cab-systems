from django import forms
from .models import OrdenTrabajo, Cliente, Vehiculo, Material

# --- PARCHE PARA SUBIDA MÚLTIPLE ---
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={'multiple': True, 'class': 'form-control'}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result
# ----------------------------------

class EstiloBaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class ClienteForm(EstiloBaseForm):
    class Meta:
        model = Cliente
        # Se cambió 'correo' por 'email' para coincidir con tu modelo
        fields = ['nombre', 'telefono', 'email']

class VehiculoForm(EstiloBaseForm):
    class Meta:
        model = Vehiculo
        fields = ['cliente', 'patente', 'marca', 'modelo', 'anio']
        labels = {
            'anio': 'Año'
        }

class MaterialForm(EstiloBaseForm):
    class Meta:
        model = Material
        fields = ['nombre', 'stock']

class OrdenTrabajoForm(EstiloBaseForm):
    # Campo con el parche para evitar el ValueError
    fotos = MultipleFileField(required=False, label="Evidencia Fotográfica")

    class Meta:
        model = OrdenTrabajo
        fields = ['vehiculo', 'descripcion', 'estado']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }