from django.urls import path,re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns=[
    #发布帖子
    path("uploadpost/",views.uploadpost),
    #发布评论
    path("uploadcomment/",views.uploadcomment),
    #获得所有的帖子
    path("getpost/",views.getpost),
    #获得对应帖子的评论
    path("getpostcomments/",views.getpostcomment,name="getpostcomment"),
    #点赞
    path("add_likecount/",views.add_likecount),

]
