from django import forms
from .models import Barberia,Corte
from django import forms

class CorteForm(forms.ModelForm):
    class Meta:
        model = Corte
        fields = ['nombre', 'precio']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Corte'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio'}),
        }

class BarberiaForm(forms.Form):
    nombre = forms.CharField(max_length=255, label='Nombre de la Barbería')
    direccion = forms.CharField(max_length=255, label='Dirección')
    maps = forms.CharField(widget=forms.Textarea, required=False, label='Mapa')
    horario1 = forms.TimeField(label='Abre', widget=forms.TimeInput(attrs={'type': 'time'}))
    horario2 = forms.TimeField(label='Cierra', widget=forms.TimeInput(attrs={'type': 'time'}))
