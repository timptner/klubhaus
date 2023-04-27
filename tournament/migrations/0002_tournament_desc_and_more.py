# Generated by Django 4.1.8 on 2023-04-27 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='desc',
            field=models.TextField(blank=True, verbose_name='Beschreibung'),
        ),
        migrations.AddConstraint(
            model_name='tournament',
            constraint=models.CheckConstraint(check=models.Q(('registration_end__gt', models.F('registration_start'))), name='registration_end_after_start'),
        ),
        migrations.AddConstraint(
            model_name='tournament',
            constraint=models.CheckConstraint(check=models.Q(('registration_end__lt', models.F('date'))), name='registration_end_before_date'),
        ),
    ]
