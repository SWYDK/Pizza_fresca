# Generated by Django 5.0.6 on 2024-07-22 15:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_orders_paid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orders',
            name='delivered',
        ),
        migrations.RemoveField(
            model_name='orders',
            name='deliveredDone',
        ),
    ]
