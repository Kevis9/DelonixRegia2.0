# Generated by Django 2.1 on 2019-04-13 03:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(blank=True, max_length=300, null=True, verbose_name='帖子内容')),
                ('created_time', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'verbose_name': '失物招领的评论',
                'verbose_name_plural': '失物招领的评论',
            },
        ),
        migrations.CreateModel(
            name='LostandFound',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=50, null=True, verbose_name='标题')),
                ('content', models.CharField(blank=True, max_length=300, null=True, verbose_name='帖子内容')),
                ('itemtype', models.CharField(choices=[('L', '遗失'), ('F', '拾取')], max_length=20, null=True, verbose_name='帖子类型')),
                ('created_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('like_count', models.BigIntegerField(default=0, null=True, verbose_name='点赞数')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '失物招领帖子',
                'verbose_name_plural': '失物招领帖子',
            },
        ),
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img_url', models.CharField(blank=True, max_length=1000, null=True)),
                ('post', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='lostandfound.LostandFound')),
            ],
            options={
                'verbose_name': '失物招领的照片',
                'verbose_name_plural': '失物招领的照片',
            },
        ),
        migrations.AddField(
            model_name='comment',
            name='to_which_post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='lostandfound.LostandFound'),
        ),
        migrations.AddField(
            model_name='comment',
            name='to_which_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='失物招领评论接受者', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='失物招领评论发送者', to=settings.AUTH_USER_MODEL),
        ),
    ]