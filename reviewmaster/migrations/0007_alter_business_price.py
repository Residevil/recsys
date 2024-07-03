# Generated by Django 5.0.4 on 2024-06-29 23:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviewmaster', '0006_alter_business_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='business',
            name='price',
            field=models.CharField(choices=[('$$$', 'Expensive'), ('$$$$', 'Luxurious'), ('$$', 'Reasonable'), ('$', 'Cheap')], max_length=10),
        ),
    ]
