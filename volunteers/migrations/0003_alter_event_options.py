# Generated by Django 4.1.8 on 2023-05-14 09:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('volunteers', '0002_alter_volunteer_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ['-date'], 'verbose_name': 'Veranstaltung', 'verbose_name_plural': 'Veranstaltungen'},
        ),
    ]
