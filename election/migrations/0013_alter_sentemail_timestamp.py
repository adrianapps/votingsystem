# Generated by Django 5.0.4 on 2024-05-19 21:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('election', '0012_sentemail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sentemail',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]