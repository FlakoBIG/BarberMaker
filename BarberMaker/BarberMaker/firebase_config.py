import firebase_admin
from firebase_admin import credentials, firestore,storage
import os

# Usamos una ruta relativa para acceder al archivo de credenciales de Firebase
cred = credentials.Certificate(os.path.join(os.path.dirname(__file__), 'barbermaker-firebase.json'))
# Inicializar Firebase


firebase_admin.initialize_app(cred, {
    'storageBucket': 'greenapp-4261a.appspot.com'  # Reemplaza con tu ID de Firebase
})

# Verificar Firestore
db = firestore.client()
print("Conexión a Firebase Firestore exitosa!")