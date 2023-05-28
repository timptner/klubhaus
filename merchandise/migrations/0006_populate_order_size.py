from django.db import migrations


def populate_order_size(apps, schema_editor):
    Order = apps.get_model('merchandise', 'Order')
    Size = apps.get_model('merchandise', 'Size')
    for order in Order.objects.all():
        size = Size.objects.get(
            label=order.size_legacy,
            product_id=order.product_id,
        )

        order.size = size
        order.save()


class Migration(migrations.Migration):

    dependencies = [
        ('merchandise', '0005_size'),
    ]

    operations = [
        migrations.RunPython(populate_order_size, reverse_code=migrations.RunPython.noop),
    ]
