from django import forms
from .models import OrdenTrabajo, Cliente, Vehiculo, Material

class OrdenTrabajoForm(forms.ModelForm):
    imagenes = forms.FileField(
        widget=forms.FileInput(attrs={
            'multiple': True, 
            'class': 'form-control',
            'accept': 'image/*'
        }),
        required=False,
        label="Adjuntar Fotos"
    )

    class Meta:
        model = OrdenTrabajo
        fields = ['vehiculo', 'descripcion', 'estado']

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