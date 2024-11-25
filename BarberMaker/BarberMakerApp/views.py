from django.shortcuts import render, get_object_or_404, redirect
from .forms import *
from .models import *
from firebase_admin import auth, firestore,exceptions,storage
import uuid ,os
from django.contrib import messages
from django.http import HttpResponse
from BarberMaker import firebase_config
from datetime import datetime

USUARIO_ACTUAL_PATH = os.path.join('usuario', 'usuario_actual.py')
db = firestore.client()

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
                precio = int(precio)  # Asegurarse de que el precio sea un número

                # Obtener el documento actual de la barbería
                barberia_doc = barberia_ref.get()

                if barberia_doc.exists:
                    barberia_data = barberia_doc.to_dict()
                    cortes = barberia_data.get('cortes', {})

                    # Validar que el nombre del corte no esté ya en los cortes existentes
                    if nombre in cortes:
                        # Si el corte ya existe, redirige sin error
                        return redirect('administrar_barberia', barberia_id=barberia_id)

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

def guardar_usuario_actual(correo, password, nombre, telefono, uid):
    """
    Guarda el correo, la contraseña, el nombre, el teléfono y la UID en un archivo Python llamado usuario_actual.py.
    Crea la carpeta y el archivo si no existen.
    """
    # Ruta al directorio
    directorio = os.path.join('usuario')

    # Crear el directorio si no existe
    if not os.path.exists(directorio):
        os.makedirs(directorio)

    # Ruta completa al archivo
    ruta_archivo = os.path.join(directorio, 'usuario_actual.py')

    # Escribir las credenciales y la UID en el archivo
    with open(ruta_archivo, 'w') as file:
        file.write(f"correo = '{correo}'\n")
        file.write(f"password = '{password}'\n")
        file.write(f"uid = '{uid}'\n")
        file.write(f"nombre = '{nombre}'\n")
        file.write(f"telefono = '{telefono}'\n")

#DEINEL
def login_view(request):
    """
    Vista para iniciar sesión de un usuario.
    """
    if request.method == 'POST':
        correo = request.POST.get('correo')
        password = request.POST.get('password')

        try:
            # Intentar autenticar al usuario y obtener su UID
            user = auth.get_user_by_email(correo)
            uid = user.uid

            # Recuperar nombre y teléfono desde Firestore
            db = firestore.client()
            usuario_ref = db.collection('usuarios').document(uid)
            usuario_doc = usuario_ref.get()

            if usuario_doc.exists:
                usuario_data = usuario_doc.to_dict()
                nombre = usuario_data.get('nombre', 'No definido')  # Valor por defecto
                telefono = usuario_data.get('telefono', 'No definido')  # Valor por defecto

                # Guardar las credenciales y los datos adicionales en usuario_actual.py
                guardar_usuario_actual(correo, password, nombre, telefono, uid)

                # Mensaje de éxito y redirección
                messages.success(request, 'Inicio de sesión exitoso.')
                return redirect('listar_barberias')  # Reemplaza con tu URL deseada
            else:
                messages.error(request, 'No se encontraron los datos del usuario en la base de datos.')
                return redirect('login')

        except exceptions.FirebaseError as e:
            # Capturar errores relacionados con Firebase
            messages.error(request, f'Error al iniciar sesión: {e}')
            return redirect('login')

    return render(request, 'login.html')

def register_view(request):
    """
    Vista para registrar un nuevo usuario.
    """
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        password = request.POST.get('password')
        telefono = request.POST.get('telefono')

        # Validar que todos los campos están presentes
        if not all([nombre, correo, password, telefono]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('register')

        try:
            # Verificar si el correo ya existe en Firebase
            user_query = auth.get_user_by_email(correo)
            if user_query:
                messages.error(request, 'El correo ya está registrado en Firebase.')
                return redirect('register')
        except exceptions.NotFoundError:
            # Esto indica que el correo no existe en Firebase, continuar con el registro
            pass
        except exceptions.FirebaseError as e:
            messages.error(request, f'Error al verificar el usuario: {e}')
            return redirect('register')

        try:
            # Crear el usuario en Firebase Authentication
            user = auth.create_user(
                email=correo,
                password=password,
                display_name=nombre,
            )

            # Guardar el usuario en Firestore
            db.collection('usuarios').document(user.uid).set({
                'nombre': nombre,
                'correo': correo,
                'telefono': telefono,
                'tipo_usuario': 'cliente',
            })

            # Guardar en la base de datos local de Django
            if not Usuario.objects.filter(correo=correo).exists():
                usuario = Usuario(uid=user.uid, nombre=nombre, correo=correo, telefono=telefono)
                usuario.save()

            messages.success(request, 'Usuario registrado exitosamente. ¡Inicia sesión!')
            return redirect('login')

        except exceptions.FirebaseError as e:
            messages.error(request, f'Error al registrar el usuario: {e}')
            return redirect('register')

    return render(request, 'register.html')

# Vista para la página principal (Dashboard) después de iniciar sesión
def dashboard(request):
    """
    Página principal después de iniciar sesión.
    """
    if 'uid' not in request.session:
        return redirect('login')  # Redirige si no está autenticado

    uid = request.session['uid']
    user_doc = db.collection('usuarios').document(uid).get()

    if not user_doc.exists:
        messages.error(request, 'No se encontró el usuario. Por favor, inicia sesión nuevamente.')
        return redirect('login')

    user_data = user_doc.to_dict()
    return render(request, 'dashboard.html', {'user': user_data})

def subir_curriculum(curriculum_file, barberia_id):
    """
    Sube un archivo PDF a Firebase Storage y retorna la URL pública.
    """
    try:
        # Obtener el bucket de Firebase Storage
        bucket = storage.bucket()

        # Generar un nombre único para el archivo y subirlo
        archivo_id = str(uuid.uuid4())
        archivo_path = f'curriculums/{barberia_id}/{archivo_id}_{curriculum_file.name}'
        blob = bucket.blob(archivo_path)
        blob.upload_from_file(curriculum_file, content_type=curriculum_file.content_type)

        # Obtener la URL pública del archivo subido
        blob.make_public()
        return blob.public_url  # Retornar la URL para guardar en Firestore
    except Exception as e:
        print(f"Error al subir el archivo: {e}")
        return None

def postular(request, barberia_id):
    """
    Maneja la postulación de un usuario a una barbería específica.
    """
    import usuario.usuario_actual as usuario_actual  # Importar datos del usuario actual
    db = firestore.client()

    # Buscar la barbería usando el ID proporcionado
    barberia_ref = db.collection('datos-barberias').document(barberia_id)
    barberia = barberia_ref.get()

    if not barberia.exists:
        messages.error(request, 'La barbería no existe.')
        return redirect('index')  # Redirigir si la barbería no existe

    barberia_data = barberia.to_dict()

    if request.method == 'POST' and request.FILES.get('curriculum'):
        # Recuperar datos del usuario actual
        nombre = usuario_actual.nombre  # Obtener nombre del usuario
        correo = usuario_actual.correo  # Obtener correo del usuario
        uid = usuario_actual.uid  # Obtener UID del usuario
        curriculum = request.FILES['curriculum']

        if not (nombre and correo and curriculum and uid):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('postular', barberia_id=barberia_id)

        # Subir el currículum y obtener la URL pública
        file_url = subir_curriculum(curriculum, barberia_id)

        if file_url:
            try:
                # Usar el UID como ID del documento del postulante
                postulante_id = uid  # Usar el UID del usuario como el ID del documento

                # Guardar los datos del postulante en Firestore
                barberia_ref.collection('postulantes').document(postulante_id).set({
                    'uid': uid,  # Agregar el UID del usuario
                    'nombre': nombre,
                    'correo': correo,
                    'curriculum_url': file_url
                })

                messages.success(request, 'Postulación enviada exitosamente.')
                return redirect('index')
            except Exception as e:
                print(f"Error al guardar los datos en Firestore: {e}")
                messages.error(request, 'Hubo un problema al guardar la postulación. Intenta nuevamente.')
                return redirect('postular', barberia_id=barberia_id)
        else:
            messages.error(request, 'Hubo un problema al subir tu currículum. Intenta nuevamente.')
            return redirect('postular', barberia_id=barberia_id)

    # Agregar los datos del usuario al contexto para la plantilla
    return render(request, 'Postular.html', {
        'barberia': barberia_data,
        'nombre': usuario_actual.nombre,
        'correo': usuario_actual.correo,
    })

def lista_de_postulantes(request, barberia_id):
    try:
        # Conectar a Firestore
        db = firestore.client()

        # Referencia a la barbería específica
        barberia_ref = db.collection('datos-barberias').document(barberia_id)
        barberia = barberia_ref.get()

        if not barberia.exists:
            messages.error(request, 'La barbería no existe.')
            return redirect('administrar_barberia', barberia_id=barberia_id)  # Redirigir si la barbería no existe

        # Obtener los postulantes de la barbería
        postulantes_ref = barberia_ref.collection('postulantes')
        postulantes = postulantes_ref.stream()

        # Crear una lista con los datos de los postulantes
        lista_postulantes = []
        for post in postulantes:
            data = post.to_dict()
            print(f"Postulante encontrado: {data}")  # Mensaje de depuración
            
            # Asegúrate de que las claves coincidan con las de tu Firestore
            lista_postulantes.append({
                'nombre': data.get('nombre'),  # Cambia 'Nombre' por 'nombre'
                'correo': data.get('correo'),  # Cambia 'Correo' por 'correo'
                'curriculum_url': data.get('curriculum_url'),
                'uid':data.get('uid')
            })

        # Si la lista está vacía, muestra un mensaje en la consola
        if not lista_postulantes:
            print("No se encontraron postulantes para esta barbería.")

        # Pasar los datos a la plantilla
        return render(request, 'ListaPostulantes.html', {
            'postulantes': lista_postulantes,
            'barberia_nombre': barberia.to_dict().get('nombre'),# Nombre de la barbería
            'barberia_id':barberia_id,

        })

    except Exception as e:
        print(f"Error al recuperar los postulantes: {e}")
        messages.error(request, 'Hubo un problema al recuperar la lista de postulantes.')
        return redirect('administrar_barberia', barberia_id=barberia_id)

def contratar_postulante(request, barberia_id, postulante_uid):
    try:
        # Referencia a la barbería y al postulante
        barberia_ref = db.collection('datos-barberias').document(barberia_id)
        postulante_ref = barberia_ref.collection('postulantes').document(postulante_uid)
        postulante_data = postulante_ref.get().to_dict()

        if postulante_data:
            # Crear un nuevo trabajador en la colección 'trabajadores' con el uid del postulante como ID
            trabajadores_ref = barberia_ref.collection('trabajadores')
            nuevo_trabajador_ref = trabajadores_ref.document(postulante_uid)  # Usar el UID del postulante como ID
            nuevo_trabajador_ref.set(postulante_data)

            # Eliminar al postulante después de contratarlo (opcional)
            postulante_ref.delete()

            messages.success(request, f"{postulante_data['nombre']} ha sido contratado exitosamente.")
        else:
            messages.error(request, "No se encontraron datos del postulante.")

    except Exception as e:
        print(f"Error al contratar al postulante: {e}")
        messages.error(request, "Ocurrió un error al procesar la solicitud.")

    # Redirigir a la lista de postulantes
    return redirect('lista_de_postulantes', barberia_id=barberia_id)


