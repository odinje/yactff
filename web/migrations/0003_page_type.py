# Generated by Django 2.0 on 2017-12-07 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_auto_20171207_1539'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='type',
            field=models.CharField(default='html', max_length=4),
        ),
    ]
