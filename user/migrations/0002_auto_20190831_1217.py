# Generated by Django 2.2.4 on 2019-08-31 12:17

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friends',
            name='followedby',
            field=models.ManyToManyField(related_name='myfollows', to=settings.AUTH_USER_MODEL, verbose_name='谁的朋友'),
        ),
    ]
