from django import forms
from .models import OrdenTrabajo, Cliente, Vehiculo, Material

class OrdenTrabajoForm(forms.ModelForm):
    imagenes = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'multiple': True, 'class': 'form-control'}),
        required=False,
        label="Adjuntar Imágenes"
    )

    class Meta:
        model = OrdenTrabajo
        fields = '__all__'

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = '__all__'

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = '__all__'