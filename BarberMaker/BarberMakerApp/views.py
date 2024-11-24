from django.shortcuts import render
from django.shortcuts import render, redirect
from .forms import PersonaForm
from firebase_admin import firestore
from BarberMaker import firebase_config

# Create your views here.
def index(request):
    return render(request,'index.html')

def crear_persona(request):
    if request.method == 'POST':
        form = PersonaForm(request.POST)
        if form.is_valid():
            # Recoger los datos del formulario
            nombre = form.cleaned_data['nombre']
            correo = form.cleaned_data['correo']

            # Guardar los datos en Firebase
            db = firestore.client()
            personas_ref = db.collection('personas')
            personas_ref.add({
                'nombre': nombre,
                'correo': correo
            })

            return redirect('listar_personas')  # Redirige después de guardar

    else:
        form = PersonaForm()

    return render(request, 'crear_persona.html', {'form': form})


def listar_personas(request):
    db = firestore.client()
    personas_ref = db.collection('personas')
    personas = personas_ref.stream()

    personas_list = [{'id': persona.id, **persona.to_dict()} for persona in personas]
    
    return render(request, 'listar_personas.html', {'personas': personas_list})