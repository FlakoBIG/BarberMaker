from django import forms
from .models import Persona,DuenoBarberia,Cliente,Empleado,Barberia,Cita,Corte

class PersonaForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = ['nombre', 'correo']

class DuenoBarberiaForm(forms.ModelForm):
    class Meta:
        model = DuenoBarberia
        fields = ['nombre', 'correo', 'telefono','estado_pago']
        widgets = {
            'correo': forms.EmailInput(attrs={'type': 'email'}),
        }

    def __init__(self, *args, **kwargs):
        super(DuenoBarberiaForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'placeholder': 'Nombre del dueño'})
        self.fields['telefono'].widget.attrs.update({'placeholder': 'Teléfono del dueño'})

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'correo', 'telefono']
        widgets = {
            'correo': forms.EmailInput(attrs={'type': 'email'}),
        }

    def __init__(self, *args, **kwargs):
        super(ClienteForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'placeholder': 'Nombre del cliente'})
        self.fields['telefono'].widget.attrs.update({'placeholder': 'Teléfono del cliente'})

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['nombre', 'correo', 'telefono', 'especialidades', 'horario','curriculum']
        widgets = {
            'correo': forms.EmailInput(attrs={'type': 'email'}),
            'especialidades': forms.Textarea(attrs={'placeholder': 'Especialidades del empleado'}),
            'horario': forms.Textarea(attrs={'placeholder': 'Horario del empleado'}),
        }

    def __init__(self, *args, **kwargs):
        super(EmpleadoForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'placeholder': 'Nombre del empleado'})
        self.fields['telefono'].widget.attrs.update({'placeholder': 'Teléfono del empleado'})

class BarberiaForm(forms.ModelForm):
    class Meta:
        model = Barberia
        fields = ['nombre', 'ubicacion', 'horario', 'servicios','empleado']
        widgets = {
            'horario': forms.Textarea(attrs={'placeholder': 'Horario de la barbería'}),
            'servicios': forms.Textarea(attrs={'placeholder': 'Servicios ofrecidos por la barbería'}),
        }

    def __init__(self, *args, **kwargs):
        super(BarberiaForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'placeholder': 'Nombre de la barbería'})
        self.fields['ubicacion'].widget.attrs.update({'placeholder': 'Ubicación de la barbería'})

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['fecha', 'servicio', 'empleado_id', 'detalles','corte']
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'servicio': forms.TextInput(attrs={'placeholder': 'Servicio solicitado'}),
            'detalles': forms.Textarea(attrs={'placeholder': 'Detalles adicionales'}),
        }

    def __init__(self, *args, **kwargs):
        super(CitaForm, self).__init__(*args, **kwargs)
        self.fields['servicio'].widget.attrs.update({'placeholder': 'Nombre del servicio'})

class CorteForm(forms.ModelForm):
    class Meta:
        model = Corte
        fields = ['nombre', 'precio', 'descripcion', 'tiempo_estimado']
        widgets = {
            'descripcion': forms.Textarea(attrs={'placeholder': 'Descripción del corte'}),
            'tiempo_estimado': forms.TextInput(attrs={'placeholder': 'Formato: HH:MM:SS'}),
        }

    def __init__(self, *args, **kwargs):
        super(CorteForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'placeholder': 'Nombre del corte'})
        self.fields['precio'].widget.attrs.update({'placeholder': 'Precio del corte'})