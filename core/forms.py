from django import forms
from .models import OrdenTrabajo, Cliente, Vehiculo, Material

class OrdenTrabajoForm(forms.ModelForm):
    imagenes = forms.FileField(
        required=False,
        label="Adjuntar Fotos del Trabajo"
    )

    class Meta:
        model = OrdenTrabajo
        fields = ['vehiculo', 'descripcion', 'estado']

    def __init__(self, *args, **kwargs):
        super(OrdenTrabajoForm, self).__init__(*args, **kwargs)
        # Forzamos el uso de FileInput (que sí soporta multiple) 
        # y eliminamos cualquier rastro de ClearableFileInput
        self.fields['imagenes'].widget = forms.FileInput(attrs={
            'multiple': True,
            'class': 'form-control',
            'accept': 'image/*'
        })