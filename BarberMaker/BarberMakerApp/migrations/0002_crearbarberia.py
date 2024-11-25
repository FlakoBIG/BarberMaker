# Generated by Django 3.2 on 2024-11-24 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BarberMakerApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CrearBarberia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_barberia', models.CharField(max_length=100)),
                ('direccion', models.CharField(max_length=200)),
                ('horario_abrir', models.TimeField()),
                ('horario_cerrar', models.TimeField()),
                ('nombre_dueño', models.CharField(max_length=100)),
                ('telefono', models.CharField(max_length=15)),
                ('foto', models.ImageField(blank=True, null=True, upload_to='barberias/')),
            ],
        ),
    ]