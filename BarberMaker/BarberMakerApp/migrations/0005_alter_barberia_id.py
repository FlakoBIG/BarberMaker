# Generated by Django 3.2 on 2024-11-24 23:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BarberMakerApp', '0004_auto_20241124_1737'),
    ]

    operations = [
        migrations.AlterField(
            model_name='barberia',
            name='id',
            field=models.CharField(max_length=100, primary_key=True, serialize=False),
        ),
    ]