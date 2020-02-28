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
            # 发送成功，把随机字符串保存在cache中
            # Cache的设置有讲究, key要为随机字符串，是为了防止用户使用同一个邮箱多次申请
            # Cache必须用键值对来标志用户，不然会出现刷号现象--邮箱可以绕过验证
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
            content = "这是您的验证码："+random_str+"\n如果您不是当前用户，请忽略"
            recipient_emial = [email]
            from_email = settings.DEFAULT_FROM_EMAIL
            mail = EmailMultiAlternatives(subject, content, from_email, recipient_emial)
            try:
                mail.send()
                # 发送成功，把随机字符串保存在cache中
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
            user_a = USER.objects.get(username=username)  # 这个设置是为了更详细的检查出错误来,因为这个地方get函数不会返回none，一旦找不到，便会给一个exception
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
                    #friend=Friends(USER=fUSER) 这样写应该只是在内存中创建，不再表中创建
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
        # 将关注的人的头像，姓名和id返回
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
        # 将关注的人的头像，姓名和id返回
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
            #文件复制的方法有很多种，这个地方使用shutil模块，也可以自己定义
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


#校方接口
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