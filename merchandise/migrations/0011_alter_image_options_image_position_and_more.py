# Generated by Django 4.2.1 on 2023-06-25 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchandise', '0010_alter_size_options_size_position_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='image',
            options={'ordering': ['product', 'position'], 'verbose_name': 'Bild', 'verbose_name_plural': 'Bilder'},
        ),
        migrations.AddField(
            model_name='image',
            name='position',
            field=models.PositiveSmallIntegerField(null=True, verbose_name='Position'),
        ),
        migrations.AddConstraint(
            model_name='image',
            constraint=models.UniqueConstraint(fields=('product', 'title'), name='unique_image_title'),
        ),
        migrations.AddConstraint(
            model_name='image',
            constraint=models.UniqueConstraint(fields=('product', 'position'), name='unique_image_position'),
        ),
    ]
