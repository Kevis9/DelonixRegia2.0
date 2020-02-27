# Generated by Django 3.0.2 on 2020-02-27 13:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('friendcircle', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='friendpost',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='myposts', to=settings.AUTH_USER_MODEL, verbose_name='创建人'),
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='postcomments', to='friendcircle.FriendPost', verbose_name='父帖'),
        ),
        migrations.AddField(
            model_name='comment',
            name='to_which_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='responsecomment', to=settings.AUTH_USER_MODEL, verbose_name='回复的人'),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mycomments', to=settings.AUTH_USER_MODEL, verbose_name='创建人'),
        ),
    ]
