# Generated by Django 5.0.3 on 2024-05-05 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_kitchen_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='kitchen',
            name='facebook',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='kitchen',
            name='instagram',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='kitchen',
            name='telegram',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='kitchen',
            name='twitter',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
