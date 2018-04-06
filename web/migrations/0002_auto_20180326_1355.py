# Generated by Django 2.0 on 2018-03-26 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='age',
            field=models.IntegerField(blank=True, default=1, verbose_name='age'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='city',
            field=models.CharField(blank=True, max_length=255, verbose_name='city'),
        ),
        migrations.AddField(
            model_name='user',
            name='country',
            field=models.CharField(blank=True, max_length=255, verbose_name='country'),
        ),
        migrations.AddField(
            model_name='user',
            name='nor_citizen',
            field=models.BooleanField(default=False, verbose_name='norwegian citizen'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='challenge',
            name='file',
            field=models.FileField(blank=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='key',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterUniqueTogether(
            name='submission',
            unique_together={('team', 'challenge')},
        ),
    ]