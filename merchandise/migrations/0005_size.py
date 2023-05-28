import django.db.models.deletion

from django.db import migrations, models


def populate_size(apps, schema_editor):
    Order = apps.get_model('merchandise', 'Order')
    Size = apps.get_model('merchandise', 'Size')
    for row in Order.objects.order_by().values('product', 'size').distinct():
        Size.objects.create(
            label=row['size'],
            product_id=row['product'],
        )


class Migration(migrations.Migration):

    dependencies = [
        ('merchandise', '0004_product_is_stocked'),
    ]

    operations = [
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=15, verbose_name='Bezeichnung')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='merchandise.product')),
            ],
            options={
                'verbose_name': 'Größe',
                'verbose_name_plural': 'Größen',
                'ordering': ['label'],
            },
        ),
        migrations.AddConstraint(
            model_name='size',
            constraint=models.UniqueConstraint(fields=('product', 'label'), name='unique_size'),
        ),
        migrations.RunPython(populate_size, reverse_code=migrations.RunPython.noop),
        migrations.RenameField(
            model_name='order',
            old_name='size',
            new_name='size_legacy'
        ),
        migrations.AddField(
            model_name='order',
            name='size',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='merchandise.size', null=True),
        ),
    ]
