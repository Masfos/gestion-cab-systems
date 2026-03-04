from django import formsffrom django.contrib.auth.models import User
from .models import OrdenTrabajo, Cliente, Vehiculo, Material

class EstiloBaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control bg-dark text-white border-secondary'})

class ClienteForm(EstiloBaseForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'empresa', 'telefono', 'email']

class VehiculoForm(EstiloBaseForm):
    class Meta:
        model = Vehiculo
        fields = ['cliente', 'marca', 'modelo', 'patente', 'anio']

class OrdenTrabajoForm(EstiloBaseForm):
    class Meta:
        model = OrdenTrabajo
        # SOLO los campos que existen en el modelo
        fields = ['vehiculo', 'descripcion', 'estado']

class MaterialForm(EstiloBaseForm):
    class Meta:
        model = Material
        fields = ['nombre', 'stock']

class RegistroTrabajadorForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}))
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
     if commit:
            user.save()
     if commit:
            user.save()
        return user