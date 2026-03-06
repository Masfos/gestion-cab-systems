from django import forms
from django.contrib.auth.models import User, Group
from django.core.validators import MinValueValidator
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
    tiene_empresa = forms.ChoiceField(
        choices=[('no', 'No'), ('si', 'Sí')],
        label='¿Tiene empresa?',
        widget=forms.Select(attrs={
            'class': 'form-control bg-dark text-white border-secondary',
            'style': 'border-radius: 10px; padding: 12px;',
            'id': 'id_tiene_empresa'
        })
    )

    class Meta:
        model = Cliente
        fields = ['nombre', 'rut', 'telefono', 'email', 'tiene_empresa',
                  'empresa', 'rut_empresa', 'giro', 'ciudad', 'direccion']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-cargar tiene_empresa si ya hay empresa guardada
        if self.instance and self.instance.pk and self.instance.empresa:
            self.fields['tiene_empresa'].initial = 'si'
        else:
            self.fields['tiene_empresa'].initial = 'no'
        # Campos empresa opcionales
        for f in ['empresa', 'rut_empresa', 'giro', 'ciudad', 'direccion']:
            self.fields[f].required = False

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('tiene_empresa') == 'no':
            instance.empresa = None
            instance.rut_empresa = None
            instance.giro = None
            instance.ciudad = None
            instance.direccion = None
        if commit:
            instance.save()
        return instance

class VehiculoForm(EstiloBaseForm):
    class Meta:
        model = Vehiculo
        fields = ['cliente', 'patente', 'marca', 'modelo', 'anio',
                  'serie_vin', 'horas']
        labels = {
            'anio': 'Año',
            'serie_vin': 'Serie / VIN',
            'horas': 'Horas',
        }

class MaterialForm(EstiloBaseForm):
    stock = forms.IntegerField(
        validators=[MinValueValidator(0, message='El stock no puede ser negativo.')],
        widget=forms.NumberInput(attrs={
            'min': '0',
            'class': 'form-control bg-dark text-white border-secondary',
            'style': 'border-radius: 10px; padding: 12px;'
        })
    )

    class Meta:
        model = Material
        fields = ['nombre', 'descripcion', 'stock']

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        qs = Material.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                f'Ya existe un material con el nombre "{nombre}". Use Editar para modificar su stock.'
            )
        return nombre

class OrdenTrabajoForm(EstiloBaseForm):
    class Meta:
        model = OrdenTrabajo
        fields = ['cliente', 'vehiculo', 'descripcion', 'observaciones', 'estado']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describa el trabajo a realizar...'}),
            'observaciones': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Observaciones del vehículo...'}),
        }
        labels = {
            'observaciones': 'Observaciones del Vehículo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = Cliente.objects.order_by('-id')
        self.fields['cliente'].label_from_instance = lambda obj: f"{obj.nombre} ({obj.empresa})" if obj.empresa else obj.nombre
        self.fields['vehiculo'].queryset = Vehiculo.objects.order_by('-id')
        self.fields['vehiculo'].label_from_instance = lambda obj: f"{obj.marca} {obj.modelo} [{obj.patente}] - {obj.cliente.nombre} ({obj.cliente.empresa if obj.cliente.empresa else 'Particular'})"

# FORMULARIO PARA REGISTRO DE TRABAJADORES
class RegistroTrabajadorForm(forms.ModelForm):
    password = forms.CharField(
        label="Contrasena",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    rol = forms.ChoiceField(
        choices=[
            ('Administrador/a', 'Administrador/a'),
            ('Tecnico/a', 'Tecnico/a'),
            ('Usuario Mixto', 'Usuario Mixto'),
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

