#!/usr/bin/python
#coding=utf-8
from django.urls import path
from . import views

urlpatterns=[
    #保证这个应用里面的都是接口，是给前端提供数据的接口
    #注册
    path('register/',views.register),
    #验证邮箱
    path('active/',views.active),
    #登陆
    path('login/',views.log_in),
    #登出
    path('logout/',views.log_out),
    #更改密码
    path('changepas/',views.changepas),
    #找回密码
    path('findpas/',views.findpas),
    #验证并重置密码
    path('verifyandsetpas/',views.verifyandsetpas),
    #获取个人信息
    path('get_profile/', views.get_profile, name='get_profile'),
    #更新个人信息
    path('update_profile/', views.update_profile, name='update_profile'),
    #函数验证的函数
    path('verify/',views.active,name='verify'),
    # 关注某人
    path('follow/', views.follw, name='follow'),
    # 取消关注
    path('unfollow/',views.unfollow,name='unfollow'),
    # 展示我关注的人
    path('myfollows/', views.showmyfollows, name='showmyfollows'),
    # 展示关注我的人
    path('myfans/',views.showmyfans,name='showmyfans'),
    # 搜索用户
    path('searchuser/', views.searchuser, name='serachuser'),
    # 展示我的消息
    path('mymsgs/',views.showmymessage,name='showmymessage'),
    # 上传简历
    path('uploadresume/',views.uploadresume,name='uploadresume'),
    # 展示毕业生简历信息
    path('showgraresume/',views.showgraresume,name='showgraresume'),
    # 展示企业简历信息
    path('showcomresume/',views.showcompanyresume,name='showcomresume'),
    # 删除简历
    path('deleteresume/',views.deleteresume,name='deleteresume'),
    # 投递简历
    path('sendresume/',views.sendresume,name='sendresume'),
    # 下载文件
    path('downloadfile/',views.downloadfile,name="downloadfile"),
    #校方接口
    # 查看城市分布
    path('showcity',views.showcity,name="showcity"),
    # 查看就业率近五年
    path('ShoweRateByYear',views.ShoweRateByYear,name='showratebyyaer'),
    #查看就业率按专业
    path('ShoweRateByMajor',views.ShoweRateByMajor,name='ShoweRateByMajor'),
    #查看方向
    path('ShowJobField',views.ShowJobField,name='ShowJobField'),
    #查看薪水
    path('showsalary',views.showsalary,name="showsalary"),
    #查看升学情况
    path('ShowFurtherEducation/',views.ShowFurtherEducation,name="ShowFurtherEducation")

]

