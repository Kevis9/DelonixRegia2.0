#!/usr/bin/python
#coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from user.models import USER

class LostandFound(models.Model):
    ITEM_TYPE= (
        ('L',"遗失"),
        ("F","拾取")
    )

    #帖子的id是django自己加的一个AutoField
    user=models.ForeignKey(USER,on_delete=models.CASCADE,null=True)
    title=models.CharField("标题",max_length=50,null=True,blank=True)
    content=models.CharField("帖子内容",max_length=300,null=True,blank=True)
    itemtype=models.CharField("帖子类型",max_length=20,choices=ITEM_TYPE,null=True)
    created_time=models.DateTimeField(auto_now_add=True,null=True)
    like_count=models.BigIntegerField("点赞数",null=True,default=0)
    class Meta:
        verbose_name = '失物招领帖子'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.user)

    def get_absolute_url(self):
        return reverse('lostandfpost', args=[self.user.id])

class Picture(models.Model):
    post=models.ForeignKey(LostandFound,on_delete=models.CASCADE,null=True)
    img_url=models.CharField(max_length=1000,null=True,blank=True)
    class Meta:
        verbose_name = '失物招领的照片'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.post)

    def get_absolute_url(self):
        return reverse('lostandfimg', args=[self.post.id])

class Comment(models.Model):
    user=models.ForeignKey(USER,on_delete=models.CASCADE,null=True,related_name="失物招领评论发送者")
    content = models.CharField("帖子内容", max_length=300, null=True, blank=True)
    #评论是针对哪个帖子的
    to_which_post=models.ForeignKey(LostandFound,on_delete=models.CASCADE,null=True,blank=True)
    # #父评论
    # to_which_comment=models.ForeignKey('self',on_delete=models.CASCADE,null=True,blank=True)
    #针对某个用户的
    to_which_user=models.ForeignKey(USER,on_delete=models.CASCADE,null=True,blank=True,related_name="失物招领评论接受者")
    created_time=models.DateTimeField(auto_now_add=True,null=True)
    class Meta:
        verbose_name = '失物招领的评论'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.user)

    def get_absolute_url(self):
        return reverse('lostandfcomment', args=[self.user.id])
