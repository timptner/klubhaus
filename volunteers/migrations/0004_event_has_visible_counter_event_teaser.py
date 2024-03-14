# Generated by Django 4.2.7 on 2024-03-14 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteers', '0003_alter_event_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='has_visible_counter',
            field=models.BooleanField(default=False, help_text='Zeigt die aktuelle Zahl angemeldeter Freiwilliger an.', verbose_name='Sichtbarer Zähler'),
        ),
        migrations.AddField(
            model_name='event',
            name='teaser',
            field=models.CharField(default='Weitere Informationen sind in der Veranstaltungsbeschreibung zu finden.', max_length=500, verbose_name='Teaser'),
            preserve_default=False,
        ),
    ]
