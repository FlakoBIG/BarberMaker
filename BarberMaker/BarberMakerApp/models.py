from django.db import models


class Corte(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre

class Barberia(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    nombre = models.CharField(max_length=255)
    estado = models.IntegerField(choices=[(1, 'Abierto'), (0, 'Cerrado')])
    direccion = models.CharField(max_length=255)
    maps = models.TextField(blank=True, null=True)
    horario1 = models.TimeField()  # Hora de apertura
    horario2 = models.TimeField()  # Hora de cierre
    cortes = models.ManyToManyField(Corte)  # Relación muchos a muchos con Corte

    def __str__(self):
        return self.nombre