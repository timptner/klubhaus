# Generated by Django 4.1.8 on 2023-05-28 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchandise', '0002_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='size',
            field=models.CharField(choices=[('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL')], default='M', max_length=2, verbose_name='Größe'),
        ),
    ]
