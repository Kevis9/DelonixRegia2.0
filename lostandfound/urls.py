#!/usr/bin/python
#coding=utf-8
from django.urls import path,re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns=[
    #发布帖子
    path("uploadpost/",views.uploadpost_lostf),
    #上传图片re_path("uploadpic/(?P<arg>\S*)/",views.uploadimg),
    #获取图片
    #re_path("getpic/(?P<arg>\S*)/",views.getimg),
    #发布评论
    path("uploadcomment/",views.uploadcomment),
    #获得所有的帖子
    path("getpost/",views.getpost),
    #获得对应帖子的评论
    path("getpostcomments/",views.getpostcomment,name="getpostcomment"),
    #点赞
    path("add_likecount/",views.add_likecount),

]
