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
    #添加好友
    path('add_friend/',views.addfriend,name='add_friend'),
    #展示好友列表
    path('show_friends/',views.showfriends,name='show_friends'),
    #搜索用户
    path('search_user/',views.searchuser,name='search_user'),
    #是否接受好友申请
    path('accept_friend/',views.acceptfriend,name='accept_friend'),
    #函数验证的函数
    path('verify/',views.active,name='verify')


]

