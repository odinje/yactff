# Generated by Django 2.0.10 on 2019-01-14 06:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_auto_20180326_1355'),
    ]

    operations = [
        migrations.RenameField(
            model_name='challenge',
            old_name='points',
            new_name='_points',
        ),
        migrations.RemoveField(
            model_name='user',
            name='age',
        ),
        migrations.RemoveField(
            model_name='user',
            name='city',
        ),
        migrations.RemoveField(
            model_name='user',
            name='country',
        ),
        migrations.RemoveField(
            model_name='user',
            name='nor_citizen',
        ),
    ]
