# Generated by Django 5.0.4 on 2024-05-07 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('election', '0008_alter_candidate_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='election',
            name='image',
            field=models.ImageField(blank=True, default='pictures/default_election.jpg', null=True, upload_to='pictures/'),
        ),
    ]