#!/usr/bin/python
#coding=utf-8
# from django.contrib.auth.models import USER,Group
from django.contrib.auth import authenticate,login,logout
from django.http import JsonResponse,HttpResponse
from .models import User_Profile_Stu,\
    User_Profile_Graduate,\
    User_Profile_Company,JobExperience,\
    EduExperience,Friends,Message,Company_Resume,\
    Graduate_Resume,User_Admin,USER
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token ,rotate_token
from django.core.mail import send_mail,send_mass_mail,EmailMultiAlternatives
from django.views.decorators.http import require_http_methods
import json
from django.conf import settings
import uuid
import hashlib
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.contrib.auth.hashers import check_password,make_password
import random
from django.forms.models import model_to_dict
from django.db.models import Q
import os
import uuid
import shutil
import datetime
from django.db.models.aggregates import Count,Avg
from django.db import connection

localurl="http://0.0.0.0:8000/"
salt = 'wobuzhidaoyongshenmejiamisuanfabijiaohaozLPQ'

#生成随机字符串
def get_random_str():
    word_range='AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz1234567890'
    four_letter_1=random.sample(word_range,6)
    four_letter_2=''.join(four_letter_1)
    return four_letter_2

@csrf_exempt
#发送随机字符串到邮箱
def send_random_str(request):
    if(request.method=='POST'):
        req = request.POST
        response = {}
        #首先判断邮箱是否已经存在
        email_exist = USER.objects.filter(email=req["email"])
        if email_exist:
            response["msg"] = 3  #邮箱已经存在
            return JsonResponse(response)
        response["msg"] = 1
        random_str = get_random_str()
        # url = localurl + "/delonixregia/verify/" + random_str + "/"
        subject = "验证码邮件"
        content = "请在注册界面输入以下验证码:"+random_str
        recipient_email = [req["email"]]
        from_email = settings.DEFAULT_FROM_EMAIL
        mail = EmailMultiAlternatives(subject, content, from_email, recipient_email)
        try:
            mail.send()
            # 发送成功,把随机字符串保存在cache中
            # Cache的设置有讲究, key要为随机字符串,是为了防止用户使用同一个邮箱多次申请
            # Cache必须用键值对来标志用户,不然会出现刷号现象--邮箱可以绕过验证
            cache.set(random_str, req["email"], 2 * 60) #设置时间长为2分钟的cache
        except Exception as e:
            response["msg"] = 2     #发送失败
        return JsonResponse(response)

@csrf_exempt
#验证随机字符串
def verify_random_str(request):
    if (request.method == 'POST'):
        response = {}
        response["msg"] = 1
        req = request.POST
        email = cache.get(req["random_str"])
        if email is not None:
            if email != req["email"]:
                response["msg"]=2
            else:
                cache.delete(req["random_str"])
        else:
            response["msg"]=2
        return JsonResponse(response)

#注册用户(毕业生)
#企业用户的注册由管理员完成
@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    response = {}
    if(request.method=="POST"):
        response["msg"] = 1
        req = request.POST
        #检验用户是否存在
        user = USER(identity="1")
        user_exist = USER.objects.filter(email=req["email"])
        if user_exist:
            response["msg"] = 2 #用户存在
            return JsonResponse(response)
        #使用邮箱来作为用户名
        user=USER.objects.create_user(username=req["email"],password=req["password"])
        user.email=req["email"]
        user.save()
        profile = User_Profile_Graduate.objects.get(user=user)
        # profile = User_Profile_Graduate(USER=USER)
        profile.email = req["email"]
        profile.name = req["name"]
        profile.gender = req["gender"]
        profile.phonenum = req["phonenum"]
        profile.major = req["major"]
        profile.birth_date = req["birth_date"]
        profile.graduate_date = req["graduate_date"]
        profile.stunum = req["stunum"]
        profile.institute = req["institute"]
        profile.save()
        # fUSER = Friends(USER=USER, followedby=USER)
        # fUSER.save()
        # job=JobExperience(USER=USER)
        # job.save()
        # e=EducationExperience(USER=USER)
        # e.save()
        return JsonResponse(response)

#激活用户
@csrf_exempt
@require_http_methods(["POST"])#限制请求方法
def active(request):
    response={}
    if(request.method=="POST"):
        response["msg"] = "true"
        req=json.loads(request.body)
        username=cache.get(req["rstr"])
        print(req["rstr"])
        if username:
            try:
                user=user.objects.get(username=username)
                user.is_active=True
                user.save()
            except Exception as e:
                print(e)
                response["msg"]="false"
            return JsonResponse(response)
        else:
            response["msg"]="false"
            return JsonResponse(response)


#找回密码
@csrf_exempt
@require_http_methods(["POST"])
def findpas(request):
    response={}
    if(request.method=="POST"):
        response["msg"]="true"
        req=json.loads(request.body)
        email=req["email"]
        if USER.objects.filter(email=email):
            # 生成随机字符串
            random_str = get_random_str()
            subject = "找回密码"
            content = "这是您的验证码："+random_str+"\n如果您不是当前用户,请忽略"
            recipient_emial = [email]
            from_email = settings.DEFAULT_FROM_EMAIL
            mail = EmailMultiAlternatives(subject, content, from_email, recipient_emial)
            try:
                mail.send()
                # 发送成功,把随机字符串保存在cache中
                cache.set(random_str, email, 15 * 60)
            except Exception as e:
                response["msg"] = "f_send"  # 发送失败
        else:
            response["msg"]="false"
        return JsonResponse(response)

#验证并重置密码
@csrf_exempt
@require_http_methods(["POST"])
def verifyandsetpas(request):
    response={}
    if (request.method == "POST"):
        response["msg"] = "true"
        req = json.loads(request.body)
        email=cache.get(req["random_str"])
        if email:
            USER=USER.objects.get(email=email)
            USER.set_password(req["newpassword"])
            USER.save()
        else:
            response["msg"]="false"
    return JsonResponse(response)

#修改密码
@csrf_exempt
@require_http_methods(["POST"])
def changepas(request):
    response = {}
    if request.method == 'POST':
        response["msg"] = "true"
        req = json.loads(request.body)
        username = req['username']
        oldpassword=req["oldpassword"]
        newpassword=req["newpassword"]
        try:
            USER = USER.objects.get(username=username)
            if check_password(oldpassword,USER.password):
                #修改密码的函数
                USER.set_password(newpassword)
                USER.save()
            else:
                response["msg"]="false"
        except Exception as e:
            response["msg"]="false"
        return JsonResponse(response)

#检查Cookie
@require_http_methods(["GET"])
def check_log(request):
    req = request.get_signed_cookie('is_logged',salt=salt,default=None)
    dic = {}
    dic["msg"] = 1
    if req is None:
        dic["msg"] = 2
    return JsonResponse(dic)

@csrf_exempt
@require_http_methods(["POST"])
#登陆
def log_in(request):
    # 设置响应
    dic={}
    response = HttpResponse()
    if request.method=="POST":
        dic["msg"] = 1
        req = request.POST
        # print(req)
        username=req['username']
        password=req['password']
        try:
            user_a = USER.objects.get(username=username)  # 这个设置是为了更详细的检查出错误来,因为这个地方get函数不会返回none,一旦找不到,便会给一个exception
            # print(user_a.password)
            user = authenticate(username=username, password=password)  # 而authenticate就能返回一个none
            if user:
                #判断USER的身份是否正确
                identity = req["identity"]
                if identity != user.identity:
                    dic["msg"] = 4      #用户身份错误
                else:
                    print(user.id)
                    response.set_signed_cookie('is_logged',user.id,salt="wobuzhidaoyongshenmejiamisuanfabijiaohaozLPQ",max_age=24*3600*7)   #Cookie的有效期为7天
                    response.content = json.dumps(dic)
            else:
                dic["msg"] = 3  #用户密码错误
            response.content = json.dumps(dic)
            return response
        except Exception as e:
            print(e)
            dic["msg"] = 2     #用户不存在
            return JsonResponse(dic)
    # get_token(request)  # 产生一个token 用于csrf验证
    return response


#登出
def log_out(request):
    dic = {}
    response = HttpResponse()
    dic["msg"] = 1
    try:
        response.delete_cookie('is_logged')
        response.content = json.dumps(dic)
    except Exception as e:
        print(e)
        dic["msg"] = 2
        response.content = json.dumps(dic)
    return response


@require_http_methods(["GET"])
#获取用户个人基本信息
def get_profile(request):
    # 首先检验cookie是否过期---请求check_log接口
    # cookie里面存了用户的信息
    uid = request.get_signed_cookie('is_logged',salt=salt,default=None)
    dic = {}
    dic["msg"] = 1
    if uid is None:
        dic["msg"] = 3
    else:
        # 根据用户的身份返回不同的信息
        try:
            user = USER.objects.get(id=uid)
            if (user.identity == "1"):
                profile = User_Profile_Graduate.objects.get(user=uid)
                dic = model_to_dict(profile)
            if (user.identity == "3"):
                profile = User_Profile_Company.objects.get(user=uid)
                dic = model_to_dict(profile)
            if (user.identity == "4"):
                profile = User_Admin.objects.get(user=uid)
                dic = model_to_dict(profile)
        except Exception as e:
            dic["msg"] = 2
            print(e)
    return JsonResponse(dic)

@csrf_exempt
@require_http_methods(["POST"])
#更新个人信息
def update_profile(request):
    dic = {}
    if(request.method=="POST"):
        req = request.POST
        dic["msg"] = 1
        #获取Cookie
        uid = request.get_signed_cookie('is_logged',salt=salt,default=None)
        if uid is None:
            dic["msg"] = 2  #Cookie失效
        else:
            try:
                user = USER.objects.get(id=uid)
                if user.identity == "1":
                    #毕业生
                    profile = User_Profile_Graduate.objects.get(user=uid)
                    profile.update(req)
                if user.identity == "3":
                    #企业
                    profile = User_Profile_Company.objects.get(user=uid)
                    profile.update(req)
                if user.identity == "4":
                    #管理员
                    profile = User_Admin.objects.get(user=uid)
                    profile.update(req)
            except Exception as e:
                print(e)
                dic["msg"] = 3  #信息修改失败
    return JsonResponse(dic)

@csrf_exempt
@require_http_methods(["POST"])
#添加工作经历
def add_jobexp(request):
    dic = {}
    if(request.method=="POST"):
        req = request.POST
        dic["msg"] = 1
        #获取Cookie
        uid = request.get_signed_cookie('is_logged',salt=salt,default=None)
        if uid is None:
            dic["msg"] = 2  #Cookie失效
        else:
            try:
                user = USER.objects.get(id=uid)
                if user.identity != "1":
                    dic["msg"] = 4  #身份不符
                else:
                    jobexp = JobExperience(user=user)
                    jobexp.update(req)
            except Exception as e:
                print(e)
                dic["msg"] = 3  #添加失败
    return JsonResponse(dic)

@csrf_exempt
@require_http_methods(["POST"])
#删除工作经历
def del_jobexp(request):
    dic = {}
    if(request.method=="POST"):
        req = request.POST
        dic["msg"] = 1
        #获取Cookie
        uid = request.get_signed_cookie('is_logged',salt=salt,default=None)
        if uid is None:
            dic["msg"] = 2  #Cookie失效
        else:
            try:
                user = USER.objects.get(id=uid)
                if user.identity != "1":
                    dic["msg"] = 4  #身份不符
                else:
                    job_exp =  JobExperience.objects.get(id=req["id"])
                    job_exp.delete()
            except Exception as e:
                print(e)
                dic["msg"] = 3  #删除失败
    return JsonResponse(dic)

@csrf_exempt
@require_http_methods(["POST"])
#更新职业经历
def update_jobexp(request):
    dic = {}
    if(request.method=="POST"):
        req = request.POST
        dic["msg"] = 1
        #获取Cookie
        uid = request.get_signed_cookie('is_logged',salt=salt,default=None)
        if uid is None:
            dic["msg"] = 2  #Cookie失效
        else:
            try:
                user = USER.objects.get(id=uid)
                if user.identity != "1":
                    dic["msg"] = 4      #身份不符
                else:
                    job_exp =  JobExperience.objects.get(id=req["id"])
                    req = req.dict()
                    del req["id"]   #去掉id
                    job_exp.update(req)
            except Exception as e:
                print(e)
                dic["msg"] = 3  #信息修改失败
    return JsonResponse(dic)

@require_http_methods(["GET"])
#获取职业经历
def get_jobexp(request):
    dic = {}
    if(request.method=="GET"):
        dic["msg"] = 1
        #获取Cookie
        uid = request.get_signed_cookie('is_logged',salt=salt,default=None)
        if uid is None:
            dic["msg"] = 2  #Cookie失效
        else:
            try:
                user = USER.objects.get(id=uid)
                if user.identity != "1":
                    dic["msg"] = 4  #身份不符
                else:
                    job_exps = user.jobexperience_set.all()
                    job_arr = []
                    for job in job_exps:
                        # print(json.dumps(model_to_dict(job)))
                        job_arr.append(model_to_dict(job))
                    # print(json.dumps(job_arr))
                    dic["jobs"]=job_arr
            except Exception as e:
                print(e)
                dic["msg"] = 3  #获取失败
    return JsonResponse(dic)

@csrf_exempt
@require_http_methods(["POST"])
#添加深造经历
def add_eduexp(request):
    dic = {}
    if(request.method=="POST"):
        req = request.POST
        dic["msg"] = 1
        #获取Cookie
        uid = request.get_signed_cookie('is_logged',salt=salt,default=None)
        if uid is None:
            dic["msg"] = 2  #Cookie失效
        else:
            try:
                user = USER.objects.get(id=uid)
                if user.identity != "1":
                    dic["msg"] = 4  #身份不符
                else:
                    eduexp = EduExperience(user=user)
                    eduexp.update(req)
            except Exception as e:
                print(e)
                dic["msg"] = 3  #添加失败
    return JsonResponse(dic)

@csrf_exempt
@require_http_methods(["POST"])
#删除深造经历
def del_eduexp(request):
    dic = {}
    if(request.method=="POST"):
        req = request.POST
        dic["msg"] = 1
        #获取Cookie
        uid = request.get_signed_cookie('is_logged',salt=salt,default=None)
        if uid is None:
            dic["msg"] = 2  #Cookie失效
        else:
            try:
                user = USER.objects.get(id=uid)
                if user.identity != "1":
                    dic["msg"] = 4  #身份不符
                else:
                    edu_exp =  EduExperience.objects.get(id=req["id"])
                    edu_exp.delete()
            except Exception as e:
                print(e)
                dic["msg"] = 3  #删除失败
    return JsonResponse(dic)

@csrf_exempt
@require_http_methods(["POST"])
#更新深造经历
def update_eduexp(request):
    dic = {}
    if(request.method=="POST"):
        req = request.POST
        dic["msg"] = 1
        #获取Cookie
        uid = request.get_signed_cookie('is_logged',salt=salt,default=None)
        if uid is None:
            dic["msg"] = 2  #Cookie失效
        else:
            try:
                user = USER.objects.get(id=uid)
                if user.identity != "1":
                    dic["msg"] = 4      #身份不符
                else:
                    edu_exp =  EduExperience.objects.get(id=req["id"])
                    req = req.dict()
                    del req["id"]   #去掉id
                    edu_exp.update(req)
            except Exception as e:
                print(e)
                dic["msg"] = 3  #信息修改失败
    return JsonResponse(dic)


@require_http_methods(["GET"])
#获取深造经历
def get_eduexp(request):
    dic = {}
    if(request.method=="GET"):
        dic["msg"] = 1
        #获取Cookie
        uid = request.get_signed_cookie('is_logged',salt=salt,default=None)
        if uid is None:
            dic["msg"] = 2  #Cookie失效
        else:
            try:
                user = USER.objects.get(id=uid)
                if user.identity != "1":
                    dic["msg"] = 4  #身份不符
                else:
                    edu_exps = user.eduexperience_set.all()
                    edu_arr = []
                    for edu in edu_exps:
                        # print(json.dumps(model_to_dict(job)))
                        edu_arr.append(model_to_dict(edu))
                    # print(json.dumps(job_arr))
                    dic["edus"]=edu_arr
            except Exception as e:
                print(e)
                dic["msg"] = 3  #获取失败
    return JsonResponse(dic)

@csrf_exempt
#关注某人
def follw(request):
    response={}
    if request.method=="POST":
        req=json.loads(request.body)
        sessionid=req["sessionid"]
        #被关注人的id
        fid=req["fid"]
        dic=cache.get(sessionid)
        response["msg"]="true"
        if dic is None:
            return JsonResponse({"msg":"expire"})
        #申请者username
        username=dic["username"]
        is_login=dic["is_login"]
        if is_login:
            try:
                # 拿到申请者USER
                USER = USER.objects.get(username=username)
                #关注人的id
                fUSER=USER.objects.get(id=fid)
                tmp=list(Friends.objects.filter(USER=fUSER))
                if(len(tmp)==0):
                    #friend=Friends(USER=fUSER) 这样写应该只是在内存中创建,不再表中创建
                    friend=Friends.objects.create(USER=fUSER)
                    print(friend.id)
                else:
                    friend=tmp[0]
                friend.myfollows.add(USER)
                friend.save()
                message=Message(text=req["text"],msgfrom=USER,msgto=fUSER,headline=req["headline"])
                message.save()
            except Exception as e:
                response["msg"]="false"
                print(e)
            return JsonResponse(response)
        else:
            response["msg"]="false"
            return JsonResponse(response)
    return JsonResponse({"msg":"WM"})

@csrf_exempt
#取消关注某人
def unfollow(request):
    if(request.method=="POST"):
        req=json.loads(request.body)
        dic=cache.get(req["sessionid"])
        if dic is None:
            return JsonResponse({"msg":"expire"})
        try:
            fUSER=Friends.objects.get(USER=USER.objects.get(id=req["fid"]))
            fUSER.followedby.remove(USER.objects.get(username=dic["username"]))
            return JsonResponse({"msg":"true"})
        except Exception as e:
            return JsonResponse({"msg":"false"})
    else:
        return JsonResponse({"msg":"WM"})

@csrf_exempt
#展示我关注的人
def showmyfollows(request):
    response = {}
    response["msg"] = "true"
    req = json.loads(request.body)
    sessionid = req["sessionid"]
    dic = cache.get(sessionid)
    if dic is None:
        return JsonResponse({"msg": "expire"})
    is_login = dic["is_login"]
    username = dic["username"]
    if is_login:
        USER = USER.objects.get(username=username)
        # 获得该用户的所有关注的人
        try:
            concerns = list(USER.myfollows.all())
        except Exception as e:
            concerns=[]
        # 将关注的人的头像,姓名和id返回
        response["follows"] = []
        for f in concerns:
            profile1=list(User_Profile_Graduate.objects.filter(USER=f.USER))
            profile2 =list(User_Profile_Company.objects.filter(USER=f.USER))
            dic={}
            if(len(profile1)>0):
                dic["imgurl"] = profile1[0].imgurl
                dic["name"] = profile1[0].name
                dic["gender"]=profile1[0].gender
            if(len(profile2)>0):
                dic["imgurl"] = profile2[0].imgurl
                dic["name"] = profile2[0].name
                dic["gender"]=""
            dic["id"]=f.USER.id
            response["follows"].append(dic)
        return JsonResponse(response)
    else:
        return JsonResponse({"msg": "false"})

@csrf_exempt
#展示我的粉丝
def showmyfans(request):
    response = {}
    response["msg"] = "true"
    req = json.loads(request.body)
    sessionid = req["sessionid"]
    dic = cache.get(sessionid)
    if dic is None:
        return JsonResponse({"msg": "expire"})
    is_login = dic["is_login"]
    username = dic["username"]
    if is_login:
        USER = USER.objects.get(username=username)
        # 获得所有关注该用户的人
        try:
            fans = Friends.objects.get(USER=USER).myfollows.all()
        except Exception as e:
            print(e)
            fans =[]
        # 将关注的人的头像,姓名和id返回
        response["fans"] = []
        for f in fans:
            profile1=list(User_Profile_Graduate.objects.filter(USER=f))
            profile2=list(User_Profile_Company.objects.filter(USER=f))
            dic={}
            if(len(profile1)>0):
                dic["imgurl"] = profile1[0].imgurl
                dic["name"] = profile1[0].name
                dic["gender"]=profile1[0].gender
            if(len(profile2)>0):
                dic["imgurl"] = profile2[0].imgurl
                dic["name"] = profile2[0].name
                dic["gender"] = profile2[0].gender
            dic["id"] = f.id
            response["fans"].append(dic)
        return JsonResponse(response)
    else:
        return JsonResponse({"msg": "false"})

@csrf_exempt
#展示我的消息
def showmymessage(request):
    if(request.method=="POST"):
        response = {}
        response["msg"] = "true"
        req = json.loads(request.body)
        sessionid = req["sessionid"]
        dic = cache.get(sessionid)
        if dic is None:
            return JsonResponse({"msg": "expire"})
        is_login = dic["is_login"]
        username = dic["username"]
        if is_login:
            try:
                msgs=list(USER.objects.get(username=username).myreceivemsg.all())
            except Exception as e:
                msgs=[]
            response["messages"]=[]
            for m in msgs:
                profile1=list(User_Profile_Graduate.objects.filter(USER=m.msgfrom))
                profile2 = list(User_Profile_Company.objects.filter(USER=m.msgfrom))
                dic={}
                if(len(profile1)>0):
                    dic["name"] = profile1[0].name
                    dic["imgurl"] = profile1[0].imgurl
                if(len(profile2)>0):
                    dic["name"] = profile1[0].name
                    dic["imgurl"] = profile1[0].imgurl
                dic["id"] = m.msgfrom.id
                dic["text"]=m.text
                dic["headline"]=m.headline
                if dic is not None:
                    response["messages"].append(dic)
            return JsonResponse(response)
        else:
            return JsonResponse({"msg":"false"})
    else:
        return JsonResponse({"msg": "WM"})

@csrf_exempt
#根据关键字模糊搜索用户
#关键字有:邮箱,姓名,用户名,
def searchUSER(request):
    response={}
    response["msg"]="true"
    req=json.loads(request.body)
    if request.method=="POST":
        dic=cache.get(req["sessionid"])
        if dic is None:
            return JsonResponse({"msg":"expire"})
        USER=USER.objects.get(username=dic["username"])
        key=req["key"]
        response["USERs"]=[]
        ans1=list(User_Profile_Graduate.objects.filter(Q(name__icontains=key)|Q(email__icontains=key)))
        ans2=list(User_Profile_Company.objects.filter(Q(name__icontains=key)|Q(email__icontains=key)))
        try:
            myfollows = list(USER.myfollows.all())
        except Exception as e:
            myfollows=[]
        myfollowsid=[]
        for m in myfollows:
            myfollowsid.append(m.USER.id)
        ans2.extend(ans1)
        for a in ans2:
            dic = {}
            tmp=model_to_dict(a)
            dic["name"] = tmp["name"]
            dic["id"] = tmp["id"]
            dic["imgurl"] = tmp["imgurl"]
            dic["gender"] = tmp.get("gender","")
            try:
                myfollowsid.index(a.id)
                dic["canfollow"]="false"
            except Exception as e:
                dic["canfollow"]="true"
            response["USERs"].append(dic)
        ans3=USER.objects.filter(username__icontains=key)
        for a in ans3:
            dic={}
            profile1=list(User_Profile_Graduate.objects.filter(USER=a))
            dic["name"]=None
            dic["imgurl"]=None
            if(len(profile1)>0):
                dic["name"]=profile1[0].name
                dic["imgurl"]=profile1[0].imgurl
                dic["gender"] = profile1[0].gender
            profile2=list(User_Profile_Company.objects.filter(USER=a))
            if (len(profile2) > 0):
                dic["name"] = profile2[0].name
                dic["imgurl"] = profile2[0].imgurl
                dic["gender"] = ""
            print(a.id)
            dic["id"] = a.id
            try:
                myfollowsid.index(a.id)
                dic["canfollow"]="false"
            except Exception as e:
                dic["canfollow"]="true"
            response["USERs"].append(dic)
        return JsonResponse(response)

    else:
        return JsonResponse({"msg":"WM"})

@csrf_exempt
#上传简历
#前端使用表单提交数据
def uploadresume(request):
    if(request.method=="POST"):
        sessionid = request.POST["sessionid"]
        print(request.POST)
        dic = cache.get(sessionid)
        if dic is None:
            return JsonResponse({"msg": "expire"})
        is_login = dic["is_login"]
        username = dic["username"]
        try:
            gra_USER = USER.objects.get(username=username)
            #检验该用户的文件名是否存在
            if(len(Graduate_Resume.objects.filter(Q(USER=gra_USER) and Q(name=request.POST["name"])))>0):
                return JsonResponse({"msg":"exist"})
            file = request.FILES['resume']
            #创建一个唯一的文件名,注意加上后缀名,wb+代表二进制写的形式打开文件
            id=os.path.join("media","resume",str(uuid.uuid4())+os.path.splitext(file.name)[1])
            #创建一个resume实例,记录路径
            resume=Graduate_Resume(USER=gra_USER,url=id,name=request.POST["name"])
            resume.save()
            try:
                with open(os.path.join(settings.BASE_DIR,id),'wb+') as f:
                    for chunk in file.chunks():
                        f.write(chunk)
            except Exception as e:
                #如果上传失败则删除实例
                resume.delete()
                return JsonResponse({"msg":"false"})
            #上传并且创建实例成功
            return JsonResponse({"msg":"true","url":id})
        except Exception as e:
            print(e)
            return JsonResponse({"msg":"false"})
    else:
        return JsonResponse({"msg":"WM"})

@csrf_exempt
#删除简历
def deleteresume(request):
    if (request.method == "POST"):
        req=json.loads(request.body)
        sessionid = req["sessionid"]
        dic = cache.get(sessionid)
        if dic is None:
            return JsonResponse({"msg": "expire"})
        try:
            # 检验该用户的文件名是否存在,存在则删除该文件,否则返回错误
            file1=Graduate_Resume.objects.filter(url=req["url"])
            file2=Company_Resume.objects.filter(url=req["url"])
            # 如果删除者是毕业生
            if (len(file1) > 0):
                path=os.path.join(settings.BASE_DIR,file1[0].url)
                os.remove(path)
                # 删除对应的model实例
                file1[0].delete()
                return JsonResponse({"msg":"true"})
            # 如果删除者是企业
            if (len(file2)>0):
                path = os.path.join(settings.BASE_URL,file1[0].url)
                os.remove(path)
                file2[0].delete()
                return JsonResponse({"msg": "true"})
            return JsonResponse({"msg":"false"})
        except Exception as e:
            print(e)
            return JsonResponse({"msg":"false"})
    else:
        return JsonResponse({"msg": "WM"})

@csrf_exempt
#展示毕业生简历,返回url
def showgraresume(request):
    if (request.method == "POST"):
        req=json.loads(request.body)
        sessionid = req["sessionid"]
        dic = cache.get(sessionid)
        response={}
        response["msg"]="true"
        if dic is None:
            return JsonResponse({"msg": "expire"})
        username = dic["username"]
        try:
            gra_USER=USER.objects.get(username=username)
            try:
                resumes=list(gra_USER.myresume.all())
            except Exception as e:
                #报出异常一般是all()数量为0
                print(e)
                resumes=[]
            response["resumes"]=[]
            for r in resumes:
                dic=model_to_dict(r)
                response["resumes"].append(dic)
            return JsonResponse(response)
        except Exception as e:
            return JsonResponse({"msg":"false"})
    else:
        return JsonResponse({"msg": "WM"})

#展示企业获得的简历,返回url
def showcompanyresume(request):
    if (request.method == "GET"):
        req=json.loads(request.body)
        sessionid = req["sessionid"]
        dic = cache.get(sessionid)
        response={}
        response["msg"]="true"
        if dic is None:
            return JsonResponse({"msg": "expire"})
        username = dic["username"]
        try:
            com_USER=USER.objects.get(username=username)
            try:
                resumes=list(com_USER.resumto.all())
            except Exception as e:
                #报出异常一般是all()数量为0
                print(e)
                resumes=[]
            response["resumes"]=[]
            for r in resumes:
                dic=model_to_dict(r)
                response["resumes"].append(dic)
            return JsonResponse(response)
        except Exception as e:
            return JsonResponse({"msg":"false"})
    else:
        return JsonResponse({"msg": "WM"})

@csrf_exempt
#投递简历
def sendresume(request):
    if (request.method == "POST"):
        req = json.loads(request.body)
        sessionid = req["sessionid"]
        dic = cache.get(sessionid)
        response = {}
        response["msg"] = "true"
        if dic is None:
            return JsonResponse({"msg": "expire"})
        username = dic["username"]
        try:
            gra_USER=USER.objects.get(username=username)
            com_USER=USER.objects.get(id=req["cid"])
            #找到文件路径
            path=os.path.join(settings.BASE_DIR,req["url"])
            #复制一份该文件,并且创建企业简历实例
            #文件复制的方法有很多种,这个地方使用shutil模块,也可以自己定义
            tmp=os.path.splitext(req["url"])
            new_id=str(uuid.uuid4())+tmp[len(tmp)-1]
            new_path=os.path.join(settings.BASE_DIR,"media","resume",new_id)
            #创建企业简历实例
            com_resume=Company_Resume(USER=gra_USER,url=new_id,company=com_USER,name=req["name"])
            #创建消息发送给相应的企业
            msg=Message(msgfrom=gra_USER,msgto=com_USER,text=req["text"],headline=req["headline"])
            # 复制文件并且保存实例在数据库
            shutil.copyfile(path, new_path)
            com_resume.save()
            msg.save()
            return JsonResponse({"msg":"true"})
        except Exception as e:
            return JsonResponse({"msg":"false"})
    else:
        return JsonResponse({"msg": "WM"})

@csrf_exempt
#下载文件
def downloadfile(request):
    if(request.method=="POST"):
        req = json.loads(request.body)
        sessionid = req["sessionid"]
        dic = cache.get(sessionid)
        response = {}
        response["msg"] = "true"
        if dic is None:
            return JsonResponse({"msg": "expire"})
        with open(os.path.join(settings.BASE_DIR,req["url"]),'rb') as f:
            response = HttpResponse(f)
            tmp=os.path.splitext(req["url"])
            response['Content-Disposition'] = 'attachment;filename='+'"'+tmp[len(tmp)-2]+tmp[len(tmp)-1]+'"'
            response["Content-Type"]="application/octet-stream"
        return response



#展示城市
@csrf_exempt
def showcity(request):
    if(request.method=="POST"):
        req=json.loads(request.body)
        dic=cache.get(req["sessionid"])
        if dic is None:
            return JsonResponse({"msg":"expire"})
        if(dic["username"]!="stu"):
            return JsonResponse({"msg":"forbid"})
        #获取指定年份的毕业生
        if(req["year"]=="total"):
            try:
                gra_profile = list(User_Profile_Graduate.objects.all())
            except Exception as e:
                gra_profile=[]
        else:
            gra_profile=list(User_Profile_Graduate.objects.filter(school_period_end__year=int(req["year"])))
        #获取毕业生的所有就职经历
        jobs=[]
        response={}
        for g in gra_profile:
            jobs.extend(list(g.USER.myjobexp.filter(job_period_end=None)))
        for j in jobs:
            if(response[j.job_city]):
                response[j.job_city]+=1
            else:
                response[j.job_city]=1
        response["msg"]="true"
        return JsonResponse(response)
    else:
        return JsonResponse({"msg":"WM"})

#获取月薪
@csrf_exempt
def showsalary(request):
    if(request.method=="POST"):
        req=json.loads(request.body)
        dic=cache.get(req["sessionid"])
        if dic is None:
            return JsonResponse({"msg":"expire"})
        if(dic["username"]!="stu"):
            return JsonResponse({"msg":"forbid"})
        #获取指定年份的毕业生
        if(req["year"]=="total"):
            try:
                gra_profile = list(User_Profile_Graduate.objects.all())
            except Exception as e:
                gra_profile=[]
        else:
            gra_profile=list(User_Profile_Graduate.objects.filter(school_period_end__year=int(req["year"])))
        #获取毕业生的所有就职经历
        jobs=[]
        response={}
        response["10k"]=0
        response["10k-30k"]=0
        response["30k-50k"]=0
        response["50k"]=0
        for g in gra_profile:
            jobs.extend(list(g.USER.myjobexp.filter(job_period_end=None)))
        for j in jobs:
            if(float(j.job_salary)/12<10000):
                response["10k"]+=1
            elif(float(j.job_salary)/12<30000):
                response["10k-30k"]+=1
            elif(float(j.job_salary)/12<50000):
                response["30k-50k"]+=1
            else:
                response["50k"]+=1
        response["msg"]="true"
        return JsonResponse(response)
    else:
        return JsonResponse({"msg":"WM"})

#就业率
#返回近五年来的就业率
@csrf_exempt
def ShoweRateByYear(request):
    if(request.method=="POST"):
        req=json.loads(request.body)
        dic=cache.get(req["sessionid"])
        if dic is None:
            return JsonResponse({"msg":"expire"})
        if(dic["username"]!="stu"):
            return JsonResponse({"msg":"forbid"})
        #获取前一年
        yearnow=datetime.date.today().year
        response={}
        response["msg"]="true"
        for y in range(yearnow-6,yearnow):
            gra_profile=list(User_Profile_Graduate.objects.filter(school_period_end__year=y))
            gotjob=0
            for g in gra_profile:
                try:
                    g.myjobexp.all()
                    gotjob+=1
                except Exception as e:
                    print(e)
            if(len(gra_profile)>0):
                response[str(y)]=gotjob/len(gra_profile)
            else:
                response[str(y)]=0
    else:
        return JsonResponse({"msg":"WM"})

#按专业获取就业率
@csrf_exempt
def ShoweRateByMajor(request):
    if(request.method=="POST"):
        req=json.loads(request.body)
        dic=cache.get(req["sessionid"])
        if dic is None:
            return JsonResponse({"msg":"expire"})
        if(dic["username"]!="stu"):
            return JsonResponse({"msg":"forbid"})
        majors=("临床医学","护理学","汉语言文学","英语","新闻学","广播电视学","广告学","机械设计制造及其自动化","电子信息工程","通信工程","光电信息科学与工程","计算机科学与技术"\
                ,"土木工程","工业设计","法学","金融学","国际经济与贸易","艺术设计学","视觉传达设计","环境设计","产品设计","公共艺术",\
                "数字媒体艺术","工商管理","市场营销","会计学","公共事业管理","行政管理")
        response={}
        response["msg"]="true"
        for m in majors:
            #拿到当前专业的所有profile
            gra_profile=list(User_Profile_Graduate.objects.filter(major=m))
            gotjob=0
            for g in gra_profile:
                try:
                    g.myjobexp.all()
                    gotjob+=1
                except Exception as e:
                    print(e)
            if(len(gra_profile)>0):
                response[m]=gotjob/len(gra_profile)
            else:
                response[m]=0
    else:
        return JsonResponse({"msg":"WM"})

#毕业方向
#按照职位来获取
@csrf_exempt
def ShowJobField(request):
    if (request.method == "POST"):
        req = json.loads(request.body)
        dic = cache.get(req["sessionid"])
        if dic is None:
            return JsonResponse({"msg": "expire"})
        if (dic["username"] != "stu"):
            return JsonResponse({"msg": "forbid"})
        response = {}
        response["msg"] = "true"
        fields={}
        if (req["year"] == "total"):
            try:
                gra_profile = list(User_Profile_Graduate.objects.all())
            except Exception as e:
                gra_profile = []
        else:
            gra_profile = list(User_Profile_Graduate.objects.filter(school_period_end__year=int(req["year"])))
        jobs=[]
        for g in gra_profile:
            jobs.extend(list(g.USER.myjobexp.filter(job_period_end=None)))
        for j in jobs:
            if(fields[j.job]):
                fields[j.job]+=1
            else:
                fields[j.job]=1
        response={}
        response["fields"]=fields
        return JsonResponse(response)
    else:
        return JsonResponse({"msg": "WM"})

#便于复用的函数
#获取某年毕业总人数,男生人数,女生人数(本科)
def get_gra_num(year):
    dic = {}
    all_gra = User_Profile_Graduate.objects.filter(graduate_date__year=year,edu_degree="1")
    dic["total_num"] = all_gra.count()
    dic["m_num"] = all_gra.filter(gender='0').count()
    dic["f_num"] = all_gra.filter(gender='1').count()
    return dic

#获取各个学院的毕业人数
def get_instituition_num(year):
    dic = {}
    all_gra = User_Profile_Graduate.objects.filter(graduate_date__year=year, edu_degree="1").values(
        'institute').annotate(Count('institute'))
    for d in all_gra:
        dic[d['institute']] = d['institute__count']
    return dic

#获取就业人数
def get_emp_num(year):
    dic = {}
    all_gra = User_Profile_Graduate.objects.filter(graduate_date__year=year, edu_degree="1")
    all_user = all_gra.values('user')
    jobexps = JobExperience.objects.filter(user__in=all_user,employ_date__year=year)
    eduexps = EduExperience.objects.filter(user__in=all_user,admission_date__year=year).values('user').distinct()
    dic["深造人数"] = eduexps.count()
    dic["各类企业"] = jobexps.filter(com_type="1").values('user').distinct().count()
    dic["机关,事业单位"] = jobexps.filter(com_type="2").values('user').distinct().count()
    return dic

#获取各省就业人数
def get_province_num(year):
    dic = {}
    all_gra = User_Profile_Graduate.objects.filter(graduate_date__year=year, edu_degree="1")
    all_user = all_gra.values('user')
    jobexps = JobExperience.objects.filter(user__in=all_user,employ_date__year=year).values('province').annotate(Count('province'))
    for d in jobexps:
        dic[d['province']] = d['province__count']
    return dic

#获取广东省各市就业人数
def get_city_num(year):
    dic = {}
    all_gra = User_Profile_Graduate.objects.filter(graduate_date__year=year, edu_degree="1")
    all_user = all_gra.values('user')
    jobexps = JobExperience.objects.filter(user__in=all_user, employ_date__year=year,province='广东省').values('city').annotate(
        Count('city'))
    for d in jobexps:
        dic[d['city']] = d['city__count']
    return dic

#获取行业类型人数
def get_field_num(year):
    dic = {}
    all_gra = User_Profile_Graduate.objects.filter(graduate_date__year=year, edu_degree="1")
    all_user = all_gra.values('user')
    jobexps = JobExperience.objects.filter(user__in=all_user, employ_date__year=year)
    dic["教育"] = jobexps.filter(field_type="1").count()
    dic["租赁和商务服务业"] = jobexps.filter(field_type="2").count()
    dic["制造业"] = jobexps.filter(field_type="3").count()
    dic["信息传输,软件和信息技术服务业"] = jobexps.filter(field_type="4").count()
    return dic

#获取职业类型人数
def get_job_num(year):
    dic = {}
    all_gra = User_Profile_Graduate.objects.filter(graduate_date__year=year, edu_degree="1")
    all_user = all_gra.values('user')
    jobexps = JobExperience.objects.filter(user__in=all_user, employ_date__year=year)
    dic["专业技术人员"] = jobexps.filter(job_type="1").count()
    dic["商业和服务业"] = jobexps.filter(job_type="2").count()
    dic["办事人员和有关人员"] = jobexps.filter(job_type="3").count()
    dic["不便分类"] = jobexps.filter(job_type="4").count()
    return dic

#境内外升学人数
def get_admission_num(year):
    dic = {}
    all_gra = User_Profile_Graduate.objects.filter(graduate_date__year=year, edu_degree="1")
    all_user = all_gra.values('user')
    eduexp = EduExperience.objects.filter(user__in=all_user,admission_date__year=year)
    dic["dom_num"] = eduexp.filter(country='中国').count()
    dic['out_num'] = eduexp.exclude(country='中国').count()
    return dic

#境内各高校升学人数
def get_dom_u_num(year):
    dic = {}
    all_gra = User_Profile_Graduate.objects.filter(graduate_date__year=year, edu_degree="1")
    all_user = all_gra.values('user')
    eduexp = EduExperience.objects.filter(user__in=all_user, admission_date__year=year)
    dom = eduexp.filter(country='中国').values('uvty_name').annotate(Count('uvty_name'))
    for d in dom:
        dic[d["uvty_name"]] = d["uvty_name__count"]

#境外各高校升学人数
def get_out_u_num(year):
    dic = {}
    all_gra = User_Profile_Graduate.objects.filter(graduate_date__year=year, edu_degree="1")
    all_user = all_gra.values('user')
    eduexp = EduExperience.objects.filter(user__in=all_user, admission_date__year=year)
    dom = eduexp.exclude(country='中国').values('uvty_name').annotate(Count('uvty_name'))
    for d in dom:
        dic[d["uvty_name"]] = d["uvty_name__count"]

#获取本科毕业生平均月薪
#专业对口人数
#500强人数
def get_avg_salary(year):
    dic = {}
    all_gra = User_Profile_Graduate.objects.filter(graduate_date__year=year, edu_degree="1")
    all_user = all_gra.values('user')
    jobexps = JobExperience.objects.filter(user__in=all_user, employ_date__year=year)
    dic["ave_salary"] = jobexps.aggregate(Avg('salary'))["salary__avg"]
    dic["m_pro_num"] = jobexps.filter(major_pro=1).count()
    dic["top500_num"] = jobexps.filter(istop500=1).count()
    return dic

#获取各个学院平均月薪
def get_i_ave_salary(year):
    dic = {}
    all_gra = User_Profile_Graduate.objects.filter(graduate_date__year=year, edu_degree="1")
    all_user = all_gra.values('user')
    jobexps = JobExperience.objects.filter(user__in=all_user, employ_date__year=year)
    institute = ['工学院','医学院','商学院','理学院','法学院','新闻学院','艺术学院','文学院']
    i_user = {}
    for i in institute:
        i_user[i] = all_gra.filter(institute=i).values('user')
    for i in institute:
        dic[i] = jobexps.filter(user__in=i_user[i]).aggregate(Avg('salary'))['salary__avg']
    return dic

#各个专业的平均月薪
def get_m_ave_salary(year):
    dic = {}
    all_gra = User_Profile_Graduate.objects.filter(graduate_date__year=year, edu_degree="1")
    all_user = all_gra.values('user')
    jobexps = JobExperience.objects.filter(user__in=all_user, employ_date__year=year)
    major = ["临床医学", "护理学", "汉语言文学", "英语", "新闻学", "广播电视学", "广告学", "机械设计制造及其自动化", "电子信息工程", "通信工程", "光电信息科学与工程",
             "计算机科学与技术" \
        , "土木工程", "工业设计", "法学", "金融学", "国际经济与贸易", "艺术设计学", "视觉传达设计", "环境设计", "产品设计", "公共艺术",
             "数字媒体艺术", "工商管理", "市场营销", "会计学", "公共事业管理", "行政管理"]
    m_user = {}
    for i in major:
        m_user[i] = all_gra.filter(major=i).values('user')
    for i in major:
        dic[i] = jobexps.filter(user__in=m_user[i]).aggregate(Avg('salary'))['salary__avg']
    return dic



#获取某一年毕业总人数,
#获取某一年毕业统计信息
@require_http_methods(["GET"])
def statistic_info(request):
    year = request.GET["year"]
    dic = {}
    dic["msg"] = 1
    uid = request.get_signed_cookie('is_logged', salt=salt, default=None)
    if uid is None:
        dic["msg"] = 2  # Cookie失效
    else:
        try:
            user = USER.objects.get(id=uid)
            if user.identity != "4":
                dic["msg"] = 4                              #身份不符
            else:
                dic.update(get_gra_num(year))               #获取毕业总人数,男生数量,女生数量
                dic["i_num"] = get_instituition_num(year)   #获取学院毕业人数
                dic['e_num'] = get_emp_num(year)            #就业人数 包括深造 各类企业 机关单位
                dic["province_num"] = get_province_num(year)   #各省就业人数
                dic['city_num'] = get_city_num(year)           #广东省各市就业人数
                dic['field_num'] = get_field_num(year)         #行业类型人数
                dic['job_num'] = get_job_num(year)             #职业类型人数
                dic.update(get_admission_num(year))            #获取境内外升学人数
                dic['dom_u_num'] = get_dom_u_num(year)         #境内各高校升学人数
                dic['out_u_num'] = get_out_u_num(year)         #境外各高校升学人数
                dic.update(get_avg_salary(year))               #获取本科毕业生的平均工资
                dic['i_ave_salary'] = get_i_ave_salary(year)   #各个学院平均工资
                dic['m_ava_salary'] = get_m_ave_salary(year)   #各个专业平均工资
        except Exception as e:
            print(e)
            dic["msg"] = 3                      #未知错误
    return JsonResponse(dic)

# 随机生成毕业生--测试阶段
def rand_create(request):
    #姓
    first_name = [
        '赵', '钱', '孙', '李', '周', '吴', '郑', '王', '冯', '陈', '褚', '卫', '蒋', '沈', '韩', '杨', '朱', '秦', '尤', '许',
        '何', '吕', '施', '张', '孔', '曹', '严', '华', '金', '魏', '陶', '姜', '戚', '谢', '邹', '喻', '柏', '水', '窦', '章',
        '云', '苏', '潘', '葛', '奚', '范', '彭', '郎', '鲁', '韦', '昌', '马', '苗', '凤', '花', '方', '俞', '任', '袁', '柳',
        '酆', '鲍', '史', '唐', '费', '廉', '岑', '薛', '雷', '贺', '倪', '汤', '滕', '殷', '罗', '毕', '郝', '邬', '安', '常',
        '乐', '于', '时', '傅', '皮', '卞', '齐', '康', '伍', '余', '元', '卜', '顾', '孟', '平', '黄', '和', '穆', '萧', '尹',
        '姚', '邵', '堪', '汪', '祁', '毛', '禹', '狄', '米', '贝', '明', '臧', '计', '伏', '成', '戴', '谈', '宋', '茅', '庞',
        '熊', '纪', '舒', '屈', '项', '祝', '董', '梁']
    #名
    last_name = [
        '的', '一', '是', '了', '我', '不', '人', '在', '他', '有', '这', '个', '上', '们', '来', '到', '时', '大', '地', '为',
        '子', '中', '你', '说', '生', '国', '年', '着', '就', '那', '和', '要', '她', '出', '也', '得', '里', '后', '自', '以',
        '会', '家', '可', '下', '而', '过', '天', '去', '能', '对', '小', '多', '然', '于', '心', '学', '么', '之', '都', '好',
        '看', '起', '发', '当', '没', '成', '只', '如', '事', '把', '还', '用', '第', '样', '道', '想', '作', '种', '开', '美',
        '总', '从', '无', '情', '己', '面', '最', '女', '但', '现', '前', '些', '所', '同', '日', '手', '又', '行', '意', '动',
        '方', '期', '它', '头', '经', '长', '儿', '回', '位', '分', '爱', '老', '因', '很', '给', '名', '法', '间', '斯', '知',
        '世', '什', '两', '次', '使', '身', '者', '被', '高', '已', '亲', '其', '进', '此', '话', '常', '与', '活', '正', '感',
        '见', '明', '问', '力', '理', '尔', '点', '文', '几', '定', '本', '公', '特', '做', '外', '孩', '相', '西', '果', '走',
        '将', '月', '十', '实', '向', '声', '车', '全', '信', '重', '三', '机', '工', '物', '气', '每', '并', '别', '真', '打',
        '太', '新', '比', '才', '便', '夫', '再', '书', '部', '水', '像', '眼', '等', '体', '却', '加', '电', '主', '界', '门',
        '利', '海', '受', '听', '表', '德', '少', '克', '代', '员', '许', '稜', '先', '口', '由', '死', '安', '写', '性', '马',
        '光', '白', '或', '住', '难', '望', '教', '命', '花', '结', '乐', '色', '更', '拉', '东', '神', '记', '处', '让', '母',
        '父', '应', '直', '字', '场', '平', '报', '友', '关', '放', '至', '张', '认', '接', '告', '入', '笑', '内', '英', '军',
        '候', '民', '岁', '往', '何', '度', '山', '觉', '路', '带', '万', '男', '边', '风', '解', '叫', '任', '金', '快', '原',
        '吃', '妈', '变', '通', '师', '立', '象', '数', '四', '失', '满', '战', '远', '格', '士', '音', '轻', '目', '条', '呢',
        '病', '始', '达', '深', '完', '今', '提', '求', '清', '王', '化', '空', '业', '思', '切', '怎', '非', '找', '片', '罗',
        '钱', '紶', '吗', '语', '元', '喜', '曾', '离', '飞', '科', '言', '干', '流', '欢', '约', '各', '即', '指', '合', '反',
        '题', '必', '该', '论', '交', '终', '林', '请', '医', '晚', '制', '球', '决', '窢', '传', '画', '保', '读', '运', '及',
        '则', '房', '早', '院', '量', '苦', '火', '布', '品', '近', '坐', '产', '答', '星', '精', '视', '五', '连', '司', '巴',
        '奇', '管', '类', '未', '朋', '且', '婚', '台', '夜', '青', '北', '队', '久', '乎', '越', '观', '落', '尽', '形', '影',
        '红', '爸', '百', '令', '周', '吧', '识', '步', '希', '亚', '术', '留', '市', '半', '热', '送', '兴', '造', '谈', '容',
        '极', '随', '演', '收', '首', '根', '讲', '整', '式', '取', '照', '办', '强', '石', '古', '华', '諣', '拿', '计', '您',
        '装', '似', '足', '双', '妻', '尼', '转', '诉', '米', '称', '丽', '客', '南', '领', '节', '衣', '站', '黑', '刻', '统',
        '断', '福', '城', '故', '历', '惊', '脸', '选', '包', '紧', '争', '另', '建', '维', '绝', '树', '系', '伤', '示', '愿',
        '持', '千', '史', '谁', '准', '联', '妇', '纪', '基', '买', '志', '静', '阿', '诗', '独', '复', '痛', '消', '社', '算',
        '义', '竟', '确', '酒', '需', '单', '治', '卡', '幸', '兰', '念', '举', '仅', '钟', '怕', '共', '毛', '句', '息', '功',
        '官', '待', '究', '跟', '穿', '室', '易', '游', '程', '号', '居', '考', '突', '皮', '哪', '费', '倒', '价', '图', '具',
        '刚', '脑', '永', '歌', '响', '商', '礼', '细', '专', '黄', '块', '脚', '味', '灵', '改', '据', '般', '破', '引', '食',
        '仍', '存', '众', '注', '笔', '甚', '某', '沉', '血', '备', '习', '校', '默', '务', '土', '微', '娘', '须', '试', '怀',
        '料', '调', '广', '蜖', '苏', '显', '赛', '查', '密', '议', '底', '列', '富', '梦', '错', '座', '参', '八', '除', '跑',
        '亮', '假', '印', '设', '线', '温', '虽', '掉', '京', '初', '养', '香', '停', '际', '致', '阳', '纸', '李', '纳', '验',
        '助', '激', '够', '严', '证', '帝', '饭', '忘', '趣', '支', '春', '集', '丈', '木', '研', '班', '普', '导', '顿', '睡',
        '展', '跳', '获', '艺', '六', '波', '察', '群', '皇', '段', '急', '庭', '创', '区', '奥', '器', '谢', '弟', '店', '否',
        '害', '草', '排', '背', '止', '组', '州', '朝', '封', '睛', '板', '角', '况', '曲', '馆', '育', '忙', '质', '河', '续',
        '哥', '呼', '若', '推', '境', '遇', '雨', '标', '姐', '充', '围', '案', '伦', '护', '冷', '警', '贝', '著', '雪', '索',
        '剧', '啊', '船', '险', '烟', '依', '斗', '值', '帮', '汉', '慢', '佛', '肯', '闻', '唱', '沙', '局', '伯', '族', '低',
        '玩', '资', '屋', '击', '速', '顾', '泪', '洲', '团', '圣', '旁', '堂', '兵', '七', '露', '园', '牛', '哭', '旅', '街',
        '劳', '型', '烈', '姑', '陈', '莫', '鱼', '异', '抱', '宝', '权', '鲁', '简', '态', '级', '票', '怪', '寻', '杀', '律',
        '胜', '份', '汽', '右', '洋', '范', '床', '舞', '秘', '午', '登', '楼', '贵', '吸', '责', '例', '追', '较', '职', '属',
        '渐', '左', '录', '丝', '牙', '党', '继', '托', '赶', '章', '智', '冲', '叶', '胡', '吉', '卖', '坚', '喝', '肉', '遗',
        '救', '修', '松', '临', '藏', '担', '戏', '善', '卫', '药', '悲', '敢', '靠', '伊', '村', '戴', '词', '森', '耳', '差',
        '短', '祖', '云', '规', '窗', '散', '迷', '油', '旧', '适', '乡', '架', '恩', '投', '弹', '铁', '博', '雷', '府', '压',
        '超', '负', '勒', '杂', '醒', '洗', '采', '毫', '嘴', '毕', '九', '冰', '既', '状', '乱', '景', '席', '珍', '童', '顶',
        '派', '素', '脱', '农', '疑', '练', '野', '按', '犯', '拍', '征', '坏', '骨', '余', '承', '置', '臓', '彩', '灯', '巨',
        '琴', '免', '环', '姆', '暗', '换', '技', '翻', '束', '增', '忍', '餐', '洛', '塞', '缺', '忆', '判', '欧', '层', '付',
        '阵', '玛', '批', '岛', '项', '狗', '休', '懂', '武', '革', '良', '恶', '恋', '委', '拥', '娜', '妙', '探', '呀', '营',
        '退', '摇', '弄', '桌', '熟', '诺', '宣', '银', '势', '奖', '宫', '忽', '套', '康', '供', '优', '课', '鸟', '喊', '降',
        '夏', '困', '刘', '罪', '亡', '鞋', '健', '模', '败', '伴', '守', '挥', '鲜', '财', '孤', '枪', '禁', '恐', '伙', '杰',
        '迹', '妹', '藸', '遍', '盖', '副', '坦', '牌', '江', '顺', '秋', '萨', '菜', '划', '授', '归', '浪', '听', '凡', '预',
        '奶', '雄', '升', '碃', '编', '典', '袋', '莱', '含', '盛', '济', '蒙', '棋', '端', '腿', '招', '释', '介', '烧', '误',
        '乾', '坤']
    #专业
    major = ["临床医学", "护理学", "汉语言文学", "英语", "新闻学", "广播电视学", "广告学", "机械设计制造及其自动化", "电子信息工程", "通信工程", "光电信息科学与工程", "计算机科学与技术" \
        , "土木工程", "工业设计", "法学", "金融学", "国际经济与贸易", "艺术设计学", "视觉传达设计", "环境设计", "产品设计", "公共艺术",
    "数字媒体艺术", "工商管理", "市场营销", "会计学", "公共事业管理", "行政管理"]
    #学院
    institute = ['工学院','医学院','商学院','理学院','法学院','新闻学院','艺术学院','文学院']
    #省份
    province = ['北京市','天津市','上海市','重庆市','河北省','山西省','辽宁省','吉林省','黑龙江省',
                '江苏省','浙江省','安徽省','福建省','江西省','山东省','河南省','湖北省','湖南省',
                '广东省','海南省','四川省','贵州省','云南省','陕西省','甘肃省','青海省','台湾省',
                '内蒙古自治区','广西壮族自治区','西藏自治区','宁夏回族自治区','新疆维吾尔自治区',
                '香港特别行政区','澳门特别行政区']
    #国家或地区
    country = ['中国','美国','加拿大','日本']
    #城市
    city = ['广州市','韶关市','深圳市','珠海市','汕头市','佛山市','江门市','湛江市','茂名市','肇庆市','惠州市','梅州市']
    #月薪
    salary = [3000,4000,5000,6000,7000,8000,9000,10000,20000,30000,40000,50000,60000,70000,80000,90000,100000]
    #企业类型
    com_type = [ '1','2' ]
    #行业类型
    field_type = ['1','2','3','4','5']
    #职业类型
    job_type = ['1','2','3','4']
    #几所高校
    uvty_name = ['浙江大学','清华大学','同济大学','汕头大学','四川大学','上海大学','湖南大学','哈佛大学','香港大学','麻省理工','爱尔兰大学','早稻田大学']

    #随机信息
    try:
        for i in range(3000):
            dic = {}
            dic["name"] = first_name[random.randint(0, len(first_name) - 1)] + last_name[
                random.randint(0, len(last_name) - 1)]
            dic["gender"] = random.randint(0, 1)
            dic['major'] = major[random.randint(0, len(major) - 1)]
            dic["institute"] = institute[random.randint(0, len(institute) - 1)]
            dic["graduate_date"] = str(random.randint(2018, 2019)) + '-' + '8' + '-' + '22'
            user = USER.objects.create_user(username='gra_'+str(i),password=12345)
            profile = User_Profile_Graduate.objects.get(user=user)
            profile.update(dic)
            #就业还是深造,decided randomly
            tmp = random.randint(0,1)
            #就业
            if tmp==1:
                jdic = {}
                jdic['employ_date'] = dic["graduate_date"]
                jdic['province'] = province[random.randint(0,len(province)-1)]
                if jdic['province'] == '广东省':
                    jdic['city'] = city[random.randint(0,len(city)-1)]
                else:
                    jdic['city'] = '北京'
                jdic['salary'] = salary[random.randint(0,len(salary)-1)]
                jdic['major_pro'] = random.randint(0,1)
                jdic['istop500'] = random.randint(0,1)
                jdic['com_type'] = com_type[random.randint(0,len(com_type)-1)]
                jdic['field_type'] = field_type[random.randint(0, len(field_type) - 1)]
                jdic['job_type'] = job_type[random.randint(0, len(job_type) - 1)]
                jobexp = JobExperience(user=user)
                jobexp.update(jdic)
            else:
                #深造
                edic={}
                edic['admission_date'] = dic["graduate_date"]
                edic['uvty_name'] = uvty_name[random.randint(0,len(uvty_name)-1)]
                edic['marjor'] = major[random.randint(0, len(major) - 1)]
                edic['country'] = country[random.randint(0,len(country)-1)]
                edic['edic'] = '硕士'
                eduexp = EduExperience(user=user)
                eduexp.update(edic)
        return JsonResponse({"msg":1})
    except Exception as e:
        print(e)
        return JsonResponse({"msg":0})



