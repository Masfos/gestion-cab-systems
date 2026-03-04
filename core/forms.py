from django import forms
from django.contrib.auth.models import User, Group
from .models import OrdenTrabajo, Cliente, Vehiculo, Material, MaterialUsado

# --- SUBIDA MÚLTIPLE DE IMÁGENES ---
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
        
class EstiloBaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control bg-dark text-white border-secondary',
                'style': 'border-radius: 10px; padding: 12px;'
            })

class ClienteForm(EstiloBaseForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'telefono', 'email']

class VehiculoForm(EstiloBaseForm):
    class Meta:
        model = Vehiculo
        fields = ['cliente', 'patente', 'marca', 'modelo', 'anio']
        labels = {
            'anio': 'Año',
        }

class MaterialForm(EstiloBaseForm):
    class Meta:
        model = Material
        fields = ['nombre', 'descripcion', 'stock']
        widgets = {
            'stock': forms.NumberInput(attrs={'min': '0', 'class': 'form-control bg-dark text-white border-secondary', 'style': 'border-radius: 10px; padding: 12px;'}),
        }


class OrdenTrabajoForm(EstiloBaseForm):
    class Meta:
        model = OrdenTrabajo
        fields = ['vehiculo', 'descripcion', 'estado']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describa el trabajo...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehiculo'].label_from_instance = lambda obj: f"{obj.marca} {obj.modelo} [{obj.patente}] - {obj.cliente.nombre} ({obj.cliente.empresa if obj.cliente.empresa else 'Particular'})"


# FORMULARIO PARA REGISTRO DE TRABAJADORES
class RegistroTrabajadorForm(forms.ModelForm):
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    rol = forms.ChoiceField(
        choices=[
            ('Administrador', 'Administrador/a'),
            ('Técnico', 'Técnico/a'),
            ('Mixto', 'Usuario Mixto')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
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

class MaterialUsadoForm(EstiloBaseForm):
    class Meta:
        model = MaterialUsado
        fields = ['material', 'cantidad']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['material'].queryset = Material.objects.order_by('nombre')
        self.fields['material'].label_from_instance = lambda obj: f"{obj.nombre} (Stock: {obj.stock})"