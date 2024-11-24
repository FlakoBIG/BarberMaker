from django.db import models

# Modelo base abstracto para las personas
class Persona(models.Model):
    uid = models.CharField(max_length=100, primary_key=True)  # Firebase UID
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15, null=True, blank=True)
    tipo = models.CharField(max_length=20)  # 'cliente', 'dueño', 'empleado'

    class Meta:
        abstract = True

# Modelo para dueños de barberías
class DuenoBarberia(Persona):
    estado_pago = models.BooleanField(default=False)  # Indica si el dueño ha realizado el pago
    def eliminar_dueno(self):
        """
        Al eliminar un dueño, elimina todas sus barberías y las citas asociadas.
        """
        barberias = Barberia.objects.filter(dueno=self)
        for barberia in barberias:
            barberia.eliminar_barberia()
        self.delete()

# Modelo para clientes
class Cliente(Persona):
    def cancelar_cita(self, cita_id):
        """
        Permite al cliente cancelar una cita específica.
        """
        cita = Cita.objects.filter(uid=cita_id, cliente=self, estado='pendiente').first()
        if cita:
            cita.estado = 'cancelada'
            cita.save()

# Modelo para empleados
class Empleado(Persona):
    barberia = models.ForeignKey('Barberia', on_delete=models.SET_NULL, null=True, blank=True)  # Barbería donde trabaja
    especialidades = models.JSONField(default=list)  # Ejemplo: ["Corte", "Barba"]
    horario = models.JSONField(default=dict)  # Ejemplo: {"lunes": ["10:00", "18:00"]}
    curriculo = models.FileField(upload_to="curriculos/", null=True, blank=True)

# Modelo para barberías
class Barberia(models.Model):
    uid = models.CharField(max_length=100, primary_key=True)
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=200)
    horario = models.JSONField(default=dict)  # Ejemplo: {"lunes": "10:00-18:00"}
    dueno = models.ForeignKey(DuenoBarberia, on_delete=models.CASCADE, related_name="barberias")  # Relación con el dueño
    empleados = models.ManyToManyField(Empleado, blank=True, related_name="barberias")
    servicios = models.JSONField(default=list)  # Ejemplo: [{"nombre": "Corte", "precio": 20}]
    estado = models.CharField(max_length=20, default='cerrado')  # 'abierto', 'cerrado'
    descripcion = models.TextField(null=True, blank=True)

    def eliminar_barberia(self):
        """
        Al eliminar una barbería, se eliminan sus citas y se desvinculan sus empleados.
        """
        Cita.objects.filter(barberia=self).delete()
        empleados = Empleado.objects.filter(barberia=self)
        for empleado in empleados:
            empleado.barberia = None
            empleado.save()
        self.delete()

# Modelo para citas
class Cita(models.Model):
    uid = models.CharField(max_length=100, primary_key=True)
    fecha = models.DateTimeField()
    servicio = models.CharField(max_length=100)  # Servicio elegido
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="citas")  # Relación con el cliente
    barberia = models.ForeignKey(Barberia, on_delete=models.CASCADE, related_name="citas")  # Relación con la barbería
    empleado = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, blank=True, related_name="citas")  # Relación opcional con un empleado
    estado = models.CharField(max_length=20, default='pendiente')  # 'pendiente', 'completada', 'cancelada'
    detalles = models.JSONField(default=dict)  # Ejemplo: {"corte": "moderno", "observaciones": "Preferir tijeras"}

    @staticmethod
    def verificar_disponibilidad(cliente_id, barberia_id, fecha):
        """
        Verifica si hay disponibilidad para una cita en la fecha indicada.
        """
        return not Cita.objects.filter(cliente_id=cliente_id, barberia_id=barberia_id, fecha=fecha, estado='pendiente').exists()
    
class Corte(models.Model):
    uid = models.CharField(max_length=100, primary_key=True)  # Identificador único
    nombre = models.CharField(max_length=100)  # Nombre del corte
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # Precio del corte
    descripcion = models.TextField(null=True, blank=True)  # Descripción del corte
    tiempo_estimado = models.DurationField(null=True, blank=True)  # Tiempo estimado en realizar el corte
    barberia = models.ForeignKey(
        'Barberia',
        on_delete=models.CASCADE,
        related_name='cortes'  # Relación inversa para acceder a los cortes de una barbería
    )

    def __str__(self):
        return f"{self.nombre} - {self.barberia.nombre}"