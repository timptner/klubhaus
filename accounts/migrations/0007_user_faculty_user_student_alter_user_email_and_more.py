# Generated by Django 4.1.8 on 2023-05-18 11:11

import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_modification_options_alter_user_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='faculty',
            field=models.CharField(blank=True, choices=[('FMB', 'Maschinenbau'), ('FVST', 'Verfahrens- und Systemtechnik'), ('FEIT', 'Elektro- und Informationstechnik'), ('FIN', 'Informatik'), ('FMA', 'Mathematik'), ('FNW', 'Naturwissenschaften'), ('FME', 'Medizin'), ('FHW', 'Humanwissenschaften'), ('FWW', 'Wirtschaftswissenschaften')], max_length=4, verbose_name='Fakultät'),
        ),
        migrations.AddField(
            model_name='user',
            name='student',
            field=models.CharField(blank=True, max_length=6, null=True, unique=True, validators=[django.core.validators.RegexValidator(flags=re.RegexFlag['ASCII'], message='Die Matrikelnummer darf nur aus sechs Ziffern bestehen.', regex='^\\d{6}$')], verbose_name='Matrikelnummer'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True, validators=[django.core.validators.RegexValidator(flags=re.RegexFlag['ASCII'], message='Die E-Mail-Adresse darf nur aus Buchstaben, Ziffern, Bindestrichen oder Punkten bestehen und muss mit "@st.ovgu.de" enden.', regex='^[\\w\\-\\.]+@st\\.ovgu\\.de$')], verbose_name='E-Mail-Adresse'),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, max_length=50, validators=[django.core.validators.RegexValidator(flags=re.RegexFlag['ASCII'], message='Die Mobilnummer darf nur aus Ziffern bestehen und muss einen Ländercode, beginnen mit einem Pluszeichen, besitzen.', regex='^\\+[\\d]+$')], verbose_name='Mobilnummer'),
        ),
    ]
