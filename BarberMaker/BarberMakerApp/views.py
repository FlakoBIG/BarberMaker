from django.shortcuts import render, get_object_or_404, redirect
from .forms import *
from .models import *
from firebase_admin import auth, firestore,exceptions,storage
import uuid ,os
from django.contrib import messages
from django.http import HttpResponseForbidden
from BarberMaker import firebase_config
from datetime import datetime,timedelta

USUARIO_ACTUAL_PATH = os.path.join('usuario', 'usuario_actual.py')
db = firestore.client()

def opciones(request):
    return render(request,'opciones.html')

def listar_barberias(request):
    # Recuperar el texto de búsqueda de los parámetros GET
    query = request.GET.get('q', '')  # Si no hay búsqueda, se asigna una cadena vacía

    # Recuperar la colección "barberias-registradas"
    barberias_ref = db.collection('barberias-registradas')
    documentos = barberias_ref.stream()

    barberias = []
    for doc in documentos:
        # Obtener los datos del documento
        barberia = doc.to_dict()
        # Agregar el ID del documento
        barberia['id'] = doc.id

        # Si hay un término de búsqueda, filtrar por nombre
        if query.lower() in barberia.get('nombre', '').lower():
            barberias.append(barberia)
        elif not query:  # Si no hay búsqueda, agregar todas las barberías
            barberias.append(barberia)

    # Verifica qué datos se están pasando a la plantilla
    print(f"Barberías filtradas: {barberias}")

    # Renderizar los datos en la plantilla
    return render(request, 'listar_barberias.html', {'barberias': barberias, 'query': query})

def eliminar_barberia(request, barberia_id):
    from usuario.usuario_actual import tipo_usuario, uid

    # Verificar si el tipo de usuario actual es "dueño"
    if not tipo_usuario or tipo_usuario.lower() != 'duenio':
        return redirect('listar_barberias')

    try:
        # Eliminar documentos en las colecciones relacionadas
        colecciones_relacionadas = ['Fotos', 'postulantes', 'trabajadores']
        
        for coleccion in colecciones_relacionadas:
            # Obtener todos los documentos en la colección asociada
            docs = db.collection(coleccion).where('barberia', '==', barberia_id).stream()
            for doc in docs:
                # Eliminar cada documento
                doc.reference.delete()

        # Eliminar la barbería de 'datos-barberias'
        db.collection('datos-barberias').document(barberia_id).delete()

        # Eliminar la barbería de 'barberias-registradas'
        db.collection('barberias-registradas').document(barberia_id).delete()

        # Actualizar el documento del usuario para dejar el campo 'barberia' vacío y cambiar 'tipo_usuario' a 'cliente'
        db.collection('usuarios').document(uid).update({
            'barberia': '',  # Borra el campo 'barberia'
            'tipo_usuario': 'cliente'  # Cambia el tipo de usuario a 'cliente'
        })

        # Actualizar el archivo usuario_actual.py para reflejar los cambios
        ruta_archivo = os.path.join('usuario', 'usuario_actual.py')

        # Leer los datos existentes del archivo
        with open(ruta_archivo, 'r') as file:
            lines = file.readlines()

        # Escribir los nuevos valores en el archivo
        with open(ruta_archivo, 'w') as file:
            for line in lines:
                if line.startswith("tipo_usuario"):
                    file.write("tipo_usuario = 'cliente'\n")  # Cambiar tipo_usuario a 'cliente'
                elif line.startswith("barberia"):
                    file.write("barberia = ''\n")  # Vaciar el campo barberia
                else:
                    file.write(line)

        # Mensaje de éxito (puedes usar notificaciones o redirecciones)
        print(f"Barbería {barberia_id} eliminada con éxito.")

    except Exception as e:
        # Manejo de errores
        print(f"Error al eliminar la barbería: {e}")

    # Redirigir a la lista de barberías
    return redirect('listar_barberias')

def barberia_seleccionada(request, barberia_id):
    from usuario.usuario_actual import correo, password

    if not correo or not password:
        return redirect('login') 
    else:
        db = firestore.client()
        barberia_ref = db.collection('datos-barberias').document(barberia_id)
        barberia_doc = barberia_ref.get()

        if barberia_doc.exists:
            barberia_data = barberia_doc.to_dict()
            cortes = barberia_data.get('cortes', {})
            precio=barberia_data.get('precio',{})

            citas_ref = db.collection('citas').where('barberia_id', '==', barberia_id)
            cita_docs = citas_ref.stream()

            citas = []
            for cita_doc in cita_docs:
                cita = cita_doc.to_dict()
                citas.append(cita)

            horario1_str = barberia_data.get('horario1')
            horario2_str = barberia_data.get('horario2')

            horario1 = datetime.strptime(horario1_str, '%H:%M')
            horario2 = datetime.strptime(horario2_str, '%H:%M')

            horarios_disponibles = []
            current_time = horario1
            while current_time <= horario2:
                horarios_disponibles.append(current_time.strftime('%H:%M'))
                current_time += timedelta(minutes=30)

            if request.method == 'POST':
                hora_cita = request.POST.get('hora')
                corte_seleccionado = request.POST.get('corte')
                corte_seleccionado1 = request.POST.get('precio')
                
                correo_usuario = request.POST.get('correo')

                hora_cita_obj = datetime.strptime(hora_cita, '%H:%M')

                if horario1 <= hora_cita_obj <= horario2:
                    # Crear la cita en la base de datos
                    cita_data = {
                        'barberia_id': barberia_id,
                        'hora': hora_cita,
                        'corte': corte_seleccionado,
                        'precio':corte_seleccionado1 ,
                        'correo_usuario': correo_usuario,
                    }

                    db.collection('citas').add(cita_data)
                    messages.success(request, 'Cita registrada exitosamente.')
                    return redirect('barberia_seleccionada', barberia_id=barberia_id)

                else:
                    return render(request, 'barberia_seleccionada.html', {
                        'barberia': barberia_data,
                        'cortes': cortes,
                        'precio':precio,
                        'citas': citas,
                        'error': 'La hora seleccionada está fuera del horario de atención de la barbería.'
                    })

            return render(request, 'barberia_seleccionada.html', {
                'barberia': barberia_data,
                'cortes': cortes,
                'precio':precio,
                'citas': citas,
                'horarios_disponibles': horarios_disponibles,
            })
        else:
            return render(request, 'error.html', {'message': 'Barbería no encontrada'})

def administrar_barberia(request):
    from usuario.usuario_actual import tipo_usuario, uid  # Asumiendo que tienes el UID del usuario actual

    # Verificar que el usuario sea dueño
    if not tipo_usuario or tipo_usuario.lower() != 'duenio':
        return redirect('listar_barberias')

    # Recuperar el UID del usuario actual
    if not uid:
        return render(request, 'error.html', {'message': 'Usuario no autenticado'})

    # Buscar en la base de datos de Firebase el campo 'barberia' en el documento del usuario actual
    usuario_ref = db.collection('usuarios').document(uid)
    usuario_doc = usuario_ref.get()

    if usuario_doc.exists:
        # Obtener el ID de la barbería desde el campo 'barberia'
        barberia_id = usuario_doc.to_dict().get('barberia')

        if not barberia_id:
            return render(request, 'error.html', {'message': 'No se ha asociado una barbería al usuario'})

        # Buscar los datos de la barbería con el ID obtenido
        barberia_ref = db.collection('datos-barberias').document(barberia_id)
        barberia_doc = barberia_ref.get()

        if barberia_doc.exists:
            barberia_data = barberia_doc.to_dict()  # Obtener los datos de la barbería
            cortes = barberia_data.get('cortes', {})  # Obtener los cortes disponibles
            precio = barberia_data.get('precio', {})  # Obtener los precios
            estado = barberia_data.get('estado', 0)  # Obtener el estado actual (0 o 1)
            citas_ref = db.collection('citas').where('barberia_id', '==', barberia_id)  # Consultar citas asociadas
            citas_docs = citas_ref.stream()

            citas = []
            for cita_doc in citas_docs:
                cita = cita_doc.to_dict()
                cita['id'] = cita_doc.id  # Asegurarse de que cada cita tiene un ID válido

                cita['nombre_corte'] = cita.get('corte', 'Desconocido')
                cita['precio_corte'] = cita.get('precio', 'No disponible')
                cita['correo_usuario'] = cita.get('correo', 'No registrado')
                cita['hora_cita'] = cita.get('hora', 'No especificada')

                citas.append(cita)

            # Lógica para cambiar el estado de la barbería
            if request.method == 'POST':
                # Cambiar el estado de la barbería
                nuevo_estado = 1 if estado == 0 else 0  # Si está cerrado, lo abrimos; si está abierto, lo cerramos.
                barberia_ref.update({'estado': nuevo_estado})  # Actualizar el estado en Firestore

                # Actualizar también en barberias-registradas
                barberias_registradas_ref = db.collection('barberias-registradas').document(barberia_id)
                barberias_registradas_ref.update({'estado': nuevo_estado})  # Actualizar el estado en barberias-registradas

                return redirect('administrar_barberia')  # Redirigir para actualizar la página

            return render(request, 'administrar_barberia.html', {
                'barberia': barberia_data,
                'cortes': cortes,
                'precio': precio,
                'citas': citas,  # Pasar las citas con el ID a la plantilla
                'estado': estado  # Pasar el estado a la plantilla para mostrarlo
            })
        else:
            return render(request, 'error.html', {'message': 'Barbería no encontrada'})
    else:
        return render(request, 'error.html', {'message': 'Usuario no encontrado'})

def crear_barberia(request):
    from usuario.usuario_actual import tipo_usuario, uid
    # Verificar si el tipo_usuario es 'cliente'
    if not tipo_usuario or tipo_usuario.lower() != 'cliente':
        return redirect('listar_barberias')

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

            # Actualizar el campo tipo_usuario en la colección 'usuarios'
            db.collection('usuarios').document(uid).update({
                'tipo_usuario': 'duenio',
                'barberia': barberia_id  # Añadimos el campo barberia con la UID de la barbería
            })

            # Ahora actualizar el archivo usuario_actual.py directamente
            # Abre el archivo usuario_actual.py para actualizarlo
            ruta_archivo = os.path.join('usuario', 'usuario_actual.py')

            # Leer los datos existentes del archivo
            with open(ruta_archivo, 'r') as file:
                lines = file.readlines()

            # Escribir en el archivo para actualizar tipo_usuario y barberia
            with open(ruta_archivo, 'w') as file:
                for line in lines:
                    if line.startswith("tipo_usuario"):
                        file.write(f"tipo_usuario = 'duenio'\n")  # Cambia 'tipo_usuario' a 'duenio'
                    elif line.startswith("barberia"):  # Actualiza el campo barberia
                        file.write(f"barberia = '{barberia_id}'\n")  # Guarda la UID de la barbería
                    else:
                        file.write(line)

            # Redirigir a la lista de barberías o la vista que desees
            return redirect('listar_barberias')  # O la URL que desees

    else:
        barberia_form = BarberiaForm()

    return render(request, 'crear_barberia.html', {'barberia_form': barberia_form})

def modificar_barberia(request, barberia_id):
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
                return redirect('administrar_barberia')
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
                        return redirect('administrar_barberia')

                    # Si el corte no existe, agregarlo
                    cortes[nombre] = precio
                    barberia_ref.update({'cortes': cortes})

                else:
                    # Si no existe, crear un nuevo documento con cortes
                    barberia_ref.set({'cortes': {nombre: precio}}, merge=True)

            except ValueError:
                # Manejar el caso donde el precio no es un número válido
                return redirect('administrar_barberia')

    # Redirige a la vista original después de agregar el corte
    return redirect('administrar_barberia')

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
    return redirect('administrar_barberia')

def modificar_corte(request, barberia_id, corte_nombre):
    try:
        # Acceder al documento que contiene el diccionario de cortes
        cortes_ref = db.collection('datos-barberias').document(barberia_id)
        cortes_doc = cortes_ref.get()

        if not cortes_doc.exists:
            raise Exception("Documento de cortes no encontrado")

        cortes = cortes_doc.to_dict().get('cortes', {})

        # Verificar si el corte existe en el diccionario
        if corte_nombre not in cortes:
            raise Exception("Corte no encontrado en el diccionario")

        if request.method == 'POST':
            # Obtener el nuevo precio del formulario
            nuevo_precio = request.POST.get('precio')

            if nuevo_precio:
                try:
                    # Convertir el precio a int y actualizar el diccionario
                    nuevo_precio_int = int(nuevo_precio)
                    cortes[corte_nombre] = nuevo_precio_int  # Actualizar el precio del corte

                    # Actualizar el documento en Firestore
                    cortes_ref.update({'cortes': cortes})
                    print(f"Precio actualizado para el corte '{corte_nombre}': {nuevo_precio_int}")
                except ValueError:
                    return render(request, 'error.html', {'error': 'Precio no válido'})

            # Redirigir a la vista principal de la barbería
            return redirect('administrar_barberia')

    except Exception as e:
        return render(request, 'error.html', {'error': str(e)})

def guardar_usuario_actual(correo, password, nombre, telefono, uid, tipo_usuario):
    """
    Guarda el correo, la contraseña, el nombre, el teléfono, la UID y el tipo de usuario 
    en un archivo Python llamado usuario_actual.py.
    Crea la carpeta y el archivo si no existen.
    """
    # Ruta al directorio
    directorio = os.path.join('usuario')

    # Crear el directorio si no existe
    if not os.path.exists(directorio):
        os.makedirs(directorio)

    # Ruta completa al archivo
    ruta_archivo = os.path.join(directorio, 'usuario_actual.py')

    # Escribir las credenciales y los datos en el archivo
    with open(ruta_archivo, 'w') as file:
        file.write(f"correo = '{correo}'\n")
        file.write(f"password = '{password}'\n")
        file.write(f"uid = '{uid}'\n")
        file.write(f"nombre = '{nombre}'\n")
        file.write(f"telefono = '{telefono}'\n")
        file.write(f"tipo_usuario = '{tipo_usuario}'\n")

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

            # Recuperar datos adicionales desde Firestore
            db = firestore.client()
            usuario_ref = db.collection('usuarios').document(uid)
            usuario_doc = usuario_ref.get()

            if usuario_doc.exists:
                usuario_data = usuario_doc.to_dict()
                nombre = usuario_data.get('nombre', 'No definido')  # Valor por defecto
                telefono = usuario_data.get('telefono', 'No definido')  # Valor por defecto
                tipo_usuario = usuario_data.get('tipo_usuario', 'No definido')  # Valor por defecto

                # Guardar las credenciales y los datos adicionales en usuario_actual.py
                guardar_usuario_actual(correo, password, nombre, telefono, uid, tipo_usuario)

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
        # Referencia a la barbería específica
        barberia_ref = db.collection('datos-barberias').document(barberia_id)
        barberia = barberia_ref.get()

        if not barberia.exists:
            messages.error(request, 'La barbería no existe.')
            return redirect('administrar_barberia') 

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
        return redirect('administrar_barberia')

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

def lista_de_trabajadores(request, barberia_id):
    try:
        # Referencia a la barbería específica
        barberia_ref = db.collection('datos-barberias').document(barberia_id)
        barberia = barberia_ref.get()

        if not barberia.exists:
            messages.error(request, 'La barbería no existe.')
            return redirect('administrar_barberia')  # Redirigir si la barbería no existe

        # Obtener los trabajadores de la barbería
        trabajadores_ref = barberia_ref.collection('trabajadores')
        trabajadores = trabajadores_ref.stream()

        # Crear una lista con los datos de los trabajadores
        lista_trabajadores = []
        for trab in trabajadores:
            data = trab.to_dict()
            print(f"Trabajador encontrado: {data}")  # Mensaje de depuración
            
            # Asegúrate de que las claves coincidan con las de tu Firestore
            lista_trabajadores.append({
                'nombre': data.get('nombre'),  # Cambia 'Nombre' por 'nombre'
                'correo': data.get('correo'),  # Cambia 'Correo' por 'correo'
                'curriculum_url': data.get('curriculum_url'),
                'uid': data.get('uid')
            })

        # Si la lista está vacía, muestra un mensaje en la consola
        if not lista_trabajadores:
            print("No se encontraron trabajadores para esta barbería.")

        # Pasar los datos a la plantilla
        return render(request, 'ListaTrabajadores.html', {
            'trabajadores': lista_trabajadores,
            'barberia_nombre': barberia.to_dict().get('nombre'),  # Nombre de la barbería
            'barberia_id': barberia_id,
        })

    except Exception as e:
        print(f"Error al recuperar los trabajadores: {e}")
        messages.error(request, 'Hubo un problema al recuperar la lista de trabajadores.')
        return redirect('administrar_barberia')

def galeria_fotos(request, barberia_id):
    try:
        # Referencia a la barbería específica y su subcolección Fotos
        barberia_ref = db.collection('datos-barberias').document(barberia_id)
        fotos_ref = barberia_ref.collection('Fotos')
        fotos = fotos_ref.stream()

        # Lista de fotos
        lista_fotos = []
        for foto in fotos:
            data = foto.to_dict()
            lista_fotos.append({
                'nombre': data.get('nombre'),
                'url': data.get('url'),
                'id_foto': data.get('id_foto'),
            })

        # Manejar la ausencia de fotos
        if not lista_fotos:
            print("No hay fotos en la galería.")  # Mensaje informativo en la consola

        return render(request, 'Fotos_admin.html', {
            'fotos': lista_fotos,
            'barberia_id': barberia_id,
        })

    except Exception as e:
        print(f"Error al cargar la galería: {e}")
        messages.error(request, "Error al cargar la galería.")
        return redirect('administrar_barberia')

def agregar_foto_cliente(request, barberia_id):
    try:
        # Referencia a la barbería específica y su subcolección Fotos
        barberia_ref = db.collection('datos-barberias').document(barberia_id)
        fotos_ref = barberia_ref.collection('Fotos')
        fotos = fotos_ref.stream()

        # Lista de fotos
        lista_fotos = []
        for foto in fotos:
            data = foto.to_dict()
            lista_fotos.append({
                'nombre': data.get('nombre'),
                'url': data.get('url'),
                'id_foto': data.get('id_foto'),
            })

        # Manejar la ausencia de fotos
        if not lista_fotos:
            print("No hay fotos en la galería.")  # Mensaje informativo en la consola

        # Renderiza la plantilla de fotos sin opciones de agregar fotos
        return render(request, 'Fotos.html', {
            'fotos': lista_fotos,
            'barberia_id': barberia_id,
        })

    except Exception as e:
        print(f"Error al cargar la galería: {e}")
        messages.error(request, "Error al cargar la galería.")
        return redirect('administrar_barberia')

def agregar_foto(request, barberia_id):
    if request.method == 'POST':
        try:
            # Datos del formulario
            nombre = request.POST.get('nombre')
            archivo = request.FILES['archivo']
            id_foto = str(uuid.uuid4())  # Generar ID aleatorio para la foto

            # Referencia al bucket de Firebase Storage
            bucket = storage.bucket()  # Esto accede al bucket de Firebase configurado por defecto.
            
            # Crear una referencia al archivo en el bucket
            blob = bucket.blob(f'fotos/{archivo.name}')
            
            # Subir el archivo
            blob.upload_from_file(archivo, content_type=archivo.content_type)

            # Hacer que la URL sea pública
            blob.make_public()
            url = blob.public_url  # Obtener la URL pública

            # Guardar los datos en Firestore
            foto_ref = db.collection('datos-barberias').document(barberia_id).collection('Fotos').document(id_foto)
            foto_ref.set({
                'nombre': nombre,
                'url': url,
                'id_foto': id_foto,
            })

            messages.success(request, 'Foto agregada exitosamente.')
        except Exception as e:
            print(f"Error al agregar foto: {e}")
            messages.error(request, 'Error al agregar la foto.')
        return redirect('galeria_fotos', barberia_id=barberia_id)
 
def eliminar_foto(request, barberia_id, id_foto):
    try:
        # Referencia al documento de la foto en Firestore
        foto_ref = db.collection('datos-barberias').document(barberia_id).collection('Fotos').document(id_foto)
        foto_data = foto_ref.get()

        if foto_data.exists:
            # Obtén la URL o el nombre del archivo para eliminar de Storage
            foto_info = foto_data.to_dict()
            url = foto_info.get('url')

            # Elimina el archivo de Firebase Storage
            if url:
                bucket = storage.bucket()
                blob_name = url.split("fotos/")[-1]  # Obtén el nombre del archivo desde la URL
                blob = bucket.blob(f'fotos/{blob_name}')
                blob.delete()

            # Elimina el documento de Firestore
            foto_ref.delete()

            messages.success(request, 'Foto eliminada exitosamente.')
        else:
            messages.error(request, 'La foto no existe.')

    except Exception as e:
        print(f"Error al eliminar la foto: {e}")
        messages.error(request, 'Error al eliminar la foto.')

    return redirect('galeria_fotos', barberia_id=barberia_id)

def cambiar_estado(request, cita_id):
    db = firestore.client()
    
    # Obtener la cita
    cita_ref = db.collection('citas').document(cita_id)
    cita_doc = cita_ref.get()

    if cita_doc.exists:
        cita_data = cita_doc.to_dict()
        
        # Asegúrate de que todos los campos existan en cita_data antes de usarlos
        barberia_id = cita_data.get('barberia_id', None)
        if barberia_id is None:
            return render(request, 'error.html', {'message': 'No se encontró barberia_id en la cita'})
        
        # Restante de la lógica para cambiar el estado o procesar la cita
        # Tu lógica aquí
        
        # Si todo va bien, redirige a donde sea necesario
        return render(request, 'administrar_barberia.html')
    
    else:
        return render(request, 'error.html', {'message': 'Cita no encontrada'})
    
def eliminar_cita(request, cita_id):
    db = firestore.client()
    cita_ref = db.collection('citas').document(cita_id)

    # Verificar si la cita existe antes de eliminarla
    if cita_ref.get().exists:
        cita_ref.delete()
        messages.success(request, 'Cita eliminada exitosamente.')
    else:
        messages.error(request, 'Cita no encontrada.')

    # Asegurarse de que el ID de la barbería esté presente en la solicitud
    barberia_id = request.POST.get('barberia_id')  # Verificar que esté presente
    if not barberia_id:
        messages.error(request, 'El ID de la barbería no fue proporcionado.')
        return redirect('listar_barberias')  # Redirigir si no se encontró el barberia_id

    # Volver a la vista de administración de barbería
    return redirect('administrar_barberia')   
