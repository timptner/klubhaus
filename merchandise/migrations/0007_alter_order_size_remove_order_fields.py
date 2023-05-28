import django.db.models.deletion

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchandise', '0006_populate_order_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='size',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='merchandise.size'),
        ),
        migrations.RemoveField(
            model_name='order',
            name='product',
        ),
        migrations.RemoveField(
            model_name='order',
            name='size_legacy',
        ),
    ]
