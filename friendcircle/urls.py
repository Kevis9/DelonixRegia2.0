from django.urls import path,re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns=[
    #发布帖子
    path("uploadpost/",views.uploadpost),
    #发布评论
    path("uploadcomment/",views.uploadcomment),
    #删除评论
    path("deletecommnet/",views.deletecomment),
    #获得所有的帖子
    path("getallpost/",views.getallpost),
    #点赞
    path("add_likecount/",views.add_likecount),
    # #获得贴子的评论
    # path("getpostcomments/",views.getpostcomment)
]