# Generated by Django 4.2 on 2024-05-13 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_alter_orders_order_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='order_number',
            field=models.CharField(editable=False, max_length=255, unique=True),
        ),
    ]
