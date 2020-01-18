#!python
#coding:utf-8
from django.contrib import admin
from django.urls import path,re_path
from django.conf.urls import include
from django.views.generic import RedirectView
from django.views.generic.base import TemplateView
from django.views.static import serve
from django.conf import settings
import os
urlpatterns = [
    #管理
    path('admin/', admin.site.urls),
    #跳转到关于用户的urls去
    path('user/',include('user.urls')),
    #跳转到登陆界面
    path('',RedirectView.as_view(url="/delonixregia/")),
    #登陆界面
    path('delonixregia/log_in/',TemplateView.as_view(template_name="index.html")),
    #邮箱激活界面
    re_path('delonixregia/verify/(?P<verificationcode>[a-zA-Z0-9]{4})/',TemplateView.as_view(template_name="verify.html")),
    #验证是否成界面
    re_path('delonixregia/active/(?P<verificationcode>[a-zA-Z0-9]{4})/',TemplateView.as_view(template_name="active.html")),
    #失物招领
    path('lostandfound/',include('lostandfound.urls')),
    #朋友圈
    path('friendcircle/',include('friendcircle.urls')),
    #二手交易
    path('secondhandtrade/',include('secondhandtrade.urls')),
    #招聘
    path('recruit/',include('recruit.urls')),
    #测试
    path('map',TemplateView.as_view(template_name="test.html")),
    #静态文件的获取,简历
    re_path('media/resume/(?P<path>.*)',serve,{"document_root":os.path.join(settings.MEDIA_ROOT,"resume")})
]
