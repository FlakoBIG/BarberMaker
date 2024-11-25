
from django.shortcuts import render, get_object_or_404, redirect
from .forms import BarberiaForm,CorteForm
from firebase_admin import firestore
from django.http import HttpResponse
from BarberMaker import firebase_config
from datetime import datetime
db = firestore.client()

# Create your views here.
def opciones(request):
    return render(request,'opciones.html')

def listar_barberias(request):
    # Recuperar la colección "barberias-registradas"
    barberias_ref = db.collection('barberias-registradas')
    documentos = barberias_ref.stream()

    barberias = []
    for doc in documentos:
        # Obtener los datos del documento
        barberia = doc.to_dict()
        # Depuración para verificar el contenido del documento
        print(f"Documento ID: {doc.id}, Datos: {barberia}")

        # Agregar el ID del documento
        barberia['id'] = doc.id
        barberias.append(barberia)

    # Verifica qué datos se están pasando a la plantilla
    print(f"Barberías: {barberias}")

    # Renderizar los datos en la plantilla
    return render(request, 'listar_barberias.html', {'barberias': barberias})

def barberia_seleccionada(request, barberia_id):
    db = firestore.client()
    barberia_ref = db.collection('datos-barberias').document(barberia_id)
    barberia_doc = barberia_ref.get()

    if barberia_doc.exists:
        barberia_data = barberia_doc.to_dict()  # Obtener los datos del documento
        cortes = barberia_data.get('cortes', {})  # Obtener los cortes (si existen)
        
        return render(request, 'barberia_seleccionada.html', {
            'barberia': barberia_data,
            'cortes': cortes,  # Pasar los cortes al template
        })
    else:
        return render(request, 'error.html', {'message': 'Barbería no encontrada'})


def administrar_barberia(request, barberia_id):
    db = firestore.client()
    barberia_ref = db.collection('datos-barberias').document(barberia_id)
    barberia_doc = barberia_ref.get()

    if barberia_doc.exists:
        barberia_data = barberia_doc.to_dict()  # Obtener los datos del documento
        cortes = barberia_data.get('cortes', {})  # Obtener los cortes (si existen)
        
        return render(request, 'administrar_barberia.html', {
            'barberia': barberia_data,
            'cortes': cortes,  # Pasar los cortes al template
        })
    else:
        return render(request, 'error.html', {'message': 'Barbería no encontrada'})


def crear_barberia(request):
    if request.method == 'POST':
        barberia_form = BarberiaForm(request.POST)
        
        if barberia_form.is_valid():
            # Recoger los datos del formulario
            nombre = barberia_form.cleaned_data['nombre']
            direccion = barberia_form.cleaned_data['direccion']
            maps = barberia_form.cleaned_data['maps']
            horario1 = barberia_form.cleaned_data['horario1']
            horario2 = barberia_form.cleaned_data['horario2']
            
            # Convertir las horas a cadenas (HH:MM)
            horario1_str = horario1.strftime('%H:%M')  # Hora de apertura
            horario2_str = horario2.strftime('%H:%M')  # Hora de cierre
            
            # Obtener la hora actual
            now = datetime.now()
            current_time = now.strftime('%H:%M')  # Hora actual en formato HH:MM
            
            # Calcular el estado basado en la hora actual y los horarios de apertura y cierre
            if horario1_str <= current_time <= horario2_str:
                estado = 1  # Abierto
            else:
                estado = 0  # Cerrado

            # Crear los datos para guardar en la colección 'datos-barberias'
            barberia_data = {
                'nombre': nombre,
                'estado': estado,  # El estado se calcula automáticamente
                'direccion': direccion,
                'maps': maps,
                'horario1': horario1_str,  # Guardamos las horas como cadena
                'horario2': horario2_str,  # Guardamos las horas como cadena
            }
            # Guardar la barbería en la colección 'datos-barberias' y obtener la referencia al documento
            barberia_ref = db.collection('datos-barberias').add(barberia_data)

            # Acceder al ID del documento usando .id de la referencia
            barberia_id = barberia_ref[1].id  # El ID está en el atributo .id de la referencia del documento
            db.collection('datos-barberias').document(barberia_id).update({
                'id': barberia_id  # Agregar el campo 'id' con el valor del ID
            })
            # Crear los datos para guardar en la colección 'barberias-registradas'
            barberia_registrada_data = {
                'nombre': nombre,
                'estado': estado  # Guardamos solo el nombre y el estado
            }

            # Guardar en 'barberias-registradas' con el mismo ID
            db.collection('barberias-registradas').document(barberia_id).set(barberia_registrada_data)

            # Redirigir a la lista de barberías o la vista que desees
            return redirect('listar_barberias')  # O la URL que desees

    else:
        barberia_form = BarberiaForm()

    return render(request, 'crear_barberia.html', {'barberia_form': barberia_form})

def modificar_barberia(request, barberia_id):
    db = firestore.client()
    barberia_ref = db.collection('datos-barberias').document(barberia_id)
    barberia_doc = barberia_ref.get()

    if barberia_doc.exists:
        barberia_data = barberia_doc.to_dict()

        if request.method == 'POST':
            barberia_form = BarberiaForm(request.POST)
            if barberia_form.is_valid():
                # Recoger los datos del formulario
                nombre = barberia_form.cleaned_data['nombre']
                direccion = barberia_form.cleaned_data['direccion']
                maps = barberia_form.cleaned_data['maps']
                horario1 = barberia_form.cleaned_data['horario1']
                horario2 = barberia_form.cleaned_data['horario2']
                
                # Convertir las horas a cadenas (HH:MM)
                horario1_str = horario1.strftime('%H:%M')
                horario2_str = horario2.strftime('%H:%M')

                # Obtener la hora actual
                now = datetime.now()
                current_time = now.strftime('%H:%M')

                # Calcular el estado basado en la hora actual
                if horario1_str <= current_time <= horario2_str:
                    estado = 1  # Abierto
                else:
                    estado = 0  # Cerrado

                # Crear los datos para actualizar en 'datos-barberias'
                barberia_ref.update({
                    'nombre': nombre,
                    'estado': estado,
                    'direccion': direccion,
                    'maps': maps,
                    'horario1': horario1_str,
                    'horario2': horario2_str,
                })

                # Crear los datos para actualizar en 'barberias-registradas'
                barberia_registrada_data = {
                    'nombre': nombre,
                    'estado': estado
                }

                # Actualizar 'barberias-registradas' con el mismo ID
                barberia_registrada_ref = db.collection('barberias-registradas').document(barberia_id)
                barberia_registrada_ref.set(barberia_registrada_data)

                # Redirigir a la lista de barberías o la vista que desees
                return redirect('administrar_barberia', barberia_id=barberia_id)
        else:
            # Si el método es GET, pre-cargar los datos en el formulario
            barberia_form = BarberiaForm(initial=barberia_data)

        return render(request, 'modificar_barberia.html', {'form': barberia_form, 'barberia': barberia_data})

    else:
        return render(request, 'error.html', {'message': 'Barbería no encontrada'})

def agregar_corte(request, barberia_id):
    db = firestore.client()
    barberia_ref = db.collection('datos-barberias').document(barberia_id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        precio = request.POST.get('precio')

        # Validar que ambos campos estén presentes
        if nombre and precio:
            try:
                precio = float(precio)  # Asegurarse de que el precio sea un número

                # Obtener el documento actual de la barbería
                barberia_doc = barberia_ref.get()

                if barberia_doc.exists:
                    barberia_data = barberia_doc.to_dict()
                    cortes = barberia_data.get('cortes', {})

                    # Validar que el nombre del corte no esté ya en los cortes existentes
                    if nombre in cortes:
                        # Si el corte ya existe, devolver un mensaje de error y permanecer en el modal
                        return render(request, 'agregar_corte.html', {
                            'error': f"El corte '{nombre}' ya está registrado.",
                            'barberia_id': barberia_id
                        })

                    # Si el corte no existe, agregarlo
                    cortes[nombre] = precio
                    barberia_ref.update({'cortes': cortes})

                else:
                    # Si no existe, crear un nuevo documento con cortes
                    barberia_ref.set({'cortes': {nombre: precio}}, merge=True)

            except ValueError:
                # Manejar el caso donde el precio no es un número válido
                return redirect('administrar_barberia', barberia_id=barberia_id)

    # Redirige a la vista original después de agregar el corte
    return redirect('administrar_barberia', barberia_id=barberia_id)


def eliminar_corte(request, barberia_id, corte_nombre):
    print(f"Solicitando eliminar el corte: {corte_nombre} de la barbería: {barberia_id}")
    
    if request.method == 'POST':
        # Conectar a Firestore
        db = firestore.client()
        barberia_ref = db.collection('datos-barberias').document(barberia_id)

        # Obtener el documento de la barbería
        barberia_doc = barberia_ref.get()
        
        if barberia_doc.exists:
            barberia_data = barberia_doc.to_dict()
            cortes = barberia_data.get('cortes', {})
            print(f"Cortes existentes antes de eliminar: {cortes}")

            # Eliminar el corte
            if corte_nombre in cortes:
                del cortes[corte_nombre]
                print(f"Corte {corte_nombre} eliminado correctamente.")
                
                # Actualizar el documento
                barberia_ref.update({'cortes': cortes})
                print(f"Datos de la barbería actualizados. Nuevos cortes: {cortes}")
            else:
                print(f"No se encontró el corte {corte_nombre} en los datos de la barbería.")
        else:
            print(f"No se encontró el documento de la barbería con ID {barberia_id}.")
    
    # Redirigir de vuelta a la página de la barbería
    return redirect('administrar_barberia', barberia_id=barberia_id)