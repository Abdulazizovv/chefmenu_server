# Generated by Django 4.0 on 2024-05-06 05:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='foods',
            field=models.ManyToManyField(to='orders.OrderItems'),
        ),
    ]
