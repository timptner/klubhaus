# Generated by Django 4.1.8 on 2023-05-28 16:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('merchandise', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.CharField(choices=[('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL')], max_length=2, verbose_name='Größe')),
                ('state', models.PositiveSmallIntegerField(choices=[(0, 'Ausstehend'), (1, 'Bestätigt'), (2, 'Bezahlt'), (3, 'Abholbereit'), (4, 'Abgeschlossen')], default=0, verbose_name='Status')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Erstellt am')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='merchandise.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Bestellung',
                'verbose_name_plural': 'Bestellungen',
                'ordering': ['created_at'],
            },
        ),
    ]
