# Generated by Django 5.0.6 on 2024-07-22 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_orders_time_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='paid',
            field=models.BooleanField(default=False, verbose_name='Оплачен'),
        ),
    ]