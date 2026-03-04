from django import forms
from django.contrib.auth.models import User, Group
from .models import OrdenTrabajo, Cliente, Vehiculo, Material

# 1. Widget corregido para subida múltiple sin errores
class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={'multiple': True, 'class': 'form-control bg-dark text-white border-secondary'}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class EstiloBaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control bg-dark text-white border-secondary'})

# --- FORMULARIOS ---

class ClienteForm(EstiloBaseForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'empresa', 'telefono', 'email'] # RECUPERADO: empresa
        labels = {'empresa': 'Empresa / Flota (Opcional)'}

class VehiculoForm(EstiloBaseForm):
    class Meta:
        model = Vehiculo
        fields = ['cliente', 'patente', 'marca', 'modelo', 'anio']
        labels = {'anio': 'Año'}

class OrdenTrabajoForm(EstiloBaseForm):
    fotos = MultipleFileField(required=False, label="Evidencia Fotográfica")

    class Meta:
        model = OrdenTrabajo
        # RECUPERADO: cliente para selección manual
        fields = ['vehiculo', 'cliente', 'descripcion', 'estado']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'vehiculo': forms.Select(attrs={'class': 'form-select'}),
            'cliente': forms.Select(attrs={'class': 'form-select'}),
        }

class RegistroTrabajadorForm(forms.ModelForm):
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}))
    rol = forms.ChoiceField(
        choices=[('Administrador', 'Administrador/a'), ('Técnico', 'Técnico/a'), ('Mixto', 'Usuario Mixto')],
        widget=forms.Select(attrs={'class': 'form-control bg-dark text-white border-secondary'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'Nombres'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'Apellidos'}),
            'email': forms.EmailInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            rol_nombre = self.cleaned_data.get('rol')
            grupo, _ = Group.objects.get_or_create(name=rol_nombre)
            user.groups.add(grupo)
        return user