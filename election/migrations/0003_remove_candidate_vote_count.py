# Generated by Django 5.0.4 on 2024-04-04 10:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('election', '0002_remove_vote_voter_voter_has_voted'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidate',
            name='vote_count',
        ),
    ]
