# Generated by Django 4.1.8 on 2023-05-14 13:16

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('excursions', '0002_excursion_image_excursion_location_excursion_website'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='excursion',
            options={'ordering': ['-date'], 'verbose_name': 'Exkursion', 'verbose_name_plural': 'Exkursionen'},
        ),
        migrations.AlterModelOptions(
            name='participant',
            options={'ordering': ['created_at'], 'verbose_name': 'Teilnehmer', 'verbose_name_plural': 'Teilnehmer'},
        ),
        migrations.RemoveField(
            model_name='excursion',
            name='seats',
        ),
        migrations.RemoveField(
            model_name='participant',
            name='registered_at',
        ),
        migrations.AddField(
            model_name='excursion',
            name='state',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Geplant'), (1, 'Geöffnet'), (2, 'Geschlossen'), (3, 'Archiviert')], default=0, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='participant',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Erstellt am'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='excursion',
            name='date',
            field=models.DateField(verbose_name='Datum'),
        ),
        migrations.AlterField(
            model_name='excursion',
            name='desc',
            field=models.TextField(verbose_name='Beschreibung'),
        ),
        migrations.AlterField(
            model_name='excursion',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='Bild'),
        ),
        migrations.AlterField(
            model_name='excursion',
            name='location',
            field=models.CharField(blank=True, max_length=200, verbose_name='Standort'),
        ),
        migrations.AlterField(
            model_name='excursion',
            name='title',
            field=models.CharField(max_length=200, verbose_name='Titel'),
        ),
        migrations.AlterField(
            model_name='excursion',
            name='website',
            field=models.URLField(blank=True, verbose_name='Webseite'),
        ),
    ]
