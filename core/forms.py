from django import forms
from django.contrib.auth.models import User, Group
from .models import OrdenTrabajo, Cliente, Vehiculo, Material

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
        fields = ['nombre', 'empresa', 'telefono', 'email']
        labels = {
            'empresa': 'Empresa / Flota (Opcional)',
        }

class VehiculoForm(EstiloBaseForm):
    class Meta:
        model = Vehiculo
        fields = ['cliente', 'patente', 'marca', 'modelo', 'anio']
        labels = {
            'anio': 'Año',
        }
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
        }

class MaterialForm(EstiloBaseForm):
    class Meta:
        model = Material
        fields = ['nombre', 'descripcion', 'stock']

class OrdenTrabajoForm(EstiloBaseForm):
    fotos = MultipleFileField(required=False, label="Evidencia Fotográfica (Puedes seleccionar varias)")

    class Meta:
        model = OrdenTrabajo
        fields = ['vehiculo', 'cliente', 'descripcion', 'estado']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describa el problema o trabajo...'}),
            'vehiculo': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
            'cliente': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
            'estado': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
        }

# --- REGISTRO DE TRABAJADORES ---

class RegistroTrabajadorForm(forms.ModelForm):
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control bg-dark text-white border-secondary'})
    )
    rol = forms.ChoiceField(
        choices=[
            ('Administrador', 'Administrador/a'),
            ('Técnico', 'Técnico/a'),
            ('Mixto', 'Usuario Mixto')
        ],
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