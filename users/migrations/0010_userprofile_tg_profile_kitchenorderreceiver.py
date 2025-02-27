# Generated by Django 5.0.6 on 2024-06-11 05:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('botapp', '0001_initial'),
        ('users', '0009_user_user_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='tg_profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='botapp.botusers'),
        ),
        migrations.CreateModel(
            name='KitchenOrderReceiver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('kitchen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_receivers', to='users.kitchen')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_receivers', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
