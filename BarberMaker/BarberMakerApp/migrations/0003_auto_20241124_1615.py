# Generated by Django 3.2 on 2024-11-24 19:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('BarberMakerApp', '0002_crearbarberia'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cita',
            name='barberia',
        ),
        migrations.RemoveField(
            model_name='cita',
            name='cliente',
        ),
        migrations.RemoveField(
            model_name='cita',
            name='corte',
        ),
        migrations.RemoveField(
            model_name='cita',
            name='empleado',
        ),
        migrations.RemoveField(
            model_name='corte',
            name='barberia',
        ),
        migrations.RemoveField(
            model_name='empleado',
            name='barberia',
        ),
        migrations.DeleteModel(
            name='Barberia',
        ),
        migrations.DeleteModel(
            name='Cita',
        ),
        migrations.DeleteModel(
            name='Cliente',
        ),
        migrations.DeleteModel(
            name='Corte',
        ),
        migrations.DeleteModel(
            name='DuenoBarberia',
        ),
        migrations.DeleteModel(
            name='Empleado',
        ),
    ]