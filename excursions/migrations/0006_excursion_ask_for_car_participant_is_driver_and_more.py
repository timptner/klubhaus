# Generated by Django 4.1.8 on 2023-05-18 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('excursions', '0005_participant_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='excursion',
            name='ask_for_car',
            field=models.BooleanField(default=False, verbose_name='Auto-Besitz abfragen'),
        ),
        migrations.AddField(
            model_name='participant',
            name='is_driver',
            field=models.BooleanField(null=True, verbose_name='Fahrer'),
        ),
        migrations.AddField(
            model_name='participant',
            name='seats',
            field=models.PositiveSmallIntegerField(null=True, verbose_name='Sitzplätze'),
        ),
        migrations.AddConstraint(
            model_name='participant',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('is_driver__isnull', True), ('seats__isnull', True)), models.Q(('is_driver__isnull', False), ('seats__isnull', False)), _connector='OR'), name='driver_has_seats_or_null'),
        ),
    ]
