# Generated by Django 2.1.4 on 2018-12-13 20:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oingo', '0005_friendship_is_request'),
    ]

    operations = [
        migrations.RenameField(
            model_name='friendship',
            old_name='firends',
            new_name='friends',
        ),
    ]