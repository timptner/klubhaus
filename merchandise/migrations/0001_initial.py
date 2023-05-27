# Generated by Django 4.1.8 on 2023-05-27 17:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Name')),
                ('desc', models.TextField(verbose_name='Beschreibung')),
                ('price', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Preis')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Erstellt am')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Bearbeitet am')),
            ],
            options={
                'verbose_name': 'Produkt',
                'verbose_name_plural': 'Produkte',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='Titel')),
                ('file', models.ImageField(upload_to='', verbose_name='Datei')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='merchandise.product')),
            ],
            options={
                'verbose_name': 'Bild',
                'verbose_name_plural': 'Bilder',
                'ordering': ['title'],
            },
        ),
    ]
