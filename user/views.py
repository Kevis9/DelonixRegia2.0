#!/usr/bin/python
#coding=utf-8
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.http import JsonResponse,HttpResponse
from .models import User_Profile_Stu,\
    User_Profile_Graduate,\
    User_Profile_Company,JobExperience,\
    EducationExperience,Friends,Message,Company_Resume,\
    Graduate_Resume
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token ,rotate_token
from django.core.mail import send_mail,send_mass_mail,EmailMultiAlternatives
from django.views.decorators.http import require_http_methods
import simplejson
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
localurl="http://172.16.3.61:8000"


#生成随机字符串
def get_random_str():
    word_range='AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz1234567890'
    four_letter_1=random.sample(word_range,4)
    four_letter_2=''.join(four_letter_1)
    return four_letter_2

#注册用户
@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    response = {} #字典
    if(request.method=="POST"):
        response["msg"] = 'true'
        req=simplejson.loads(request.body)
        username=req["username"]
        password=req["password"]
        email=req["email"]
        identity=req["identity"]
        user=User.objects.filter(username=username)
        emailexist=User.objects.filter(email=email)
        #用户名已存在
        if user and user[0].is_active:
            response["msg"]='f_ualready'
            return JsonResponse(response)
        if emailexist and emailexist[0].is_active:
            response["msg"]='f_ealready'
            return JsonResponse(response)
        #如果不存在,创建一个user
        if not user:
            user=User.objects.create_user(username=username,password=password)
            user.email=email
            user.is_active=False
            user.save()
            # 保存到数据库
            # 设置用户的身份
            # 初始化部分信息
            if identity=="1":
                profile=User_Profile_Graduate(user=user)
            if identity=="2":
                profile = User_Profile_Stu(user=user)
            if identity=="3":
                profile = User_Profile_Company(user=user)
            profile.identity = identity
            profile.email = email
            profile.save()
            fuser = Friends(user=user, followedby=user)
            fuser.save()
            job=JobExperience(user=user)
            job.save()
            e=EducationExperience(user=user)
            e.save()
        #如果用户已存在但是不是有效的,那么直接对这个用户发送邮件
        #发送邮件
        #生成随机字符串
        random_str=get_random_str()
        url = localurl+"/delonixregia/verify/"+random_str+"/"
        subject="激活邮件"
        content="点击下方进行激活"
        recipient_emial=[email]
        html_content="<p>欢迎使用凤凰花开,请点击</p><a href='"+url+"'>此处</a><p>进行验证<p>"
        from_email=settings.DEFAULT_FROM_EMAIL
        mail=EmailMultiAlternatives(subject,content,from_email,recipient_emial)
        mail.attach_alternative(html_content,"text/html")
        try:
            mail.send()
            #发送成功，把随机字符串保存在cache中
            cache.set(random_str,username,15*60)
        except Exception as e:
            response["msg"]="f_send" #发送失败
            return JsonResponse(response)
        return JsonResponse(response)

#激活用户
@csrf_exempt
@require_http_methods(["POST"])#限制请求方法
def active(request):
    response={}
    if(request.method=="POST"):
        response["msg"] = "true"
        req=simplejson.loads(request.body)
        username=cache.get(req["rstr"])
        print(req["rstr"])
        if username:
            try:
                user=User.objects.get(username=username)
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
        req=simplejson.loads(request.body)
        email=req["email"]
        if User.objects.filter(email=email):
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
        req = simplejson.loads(request.body)
        email=cache.get(req["random_str"])
        if email:
            user=User.objects.get(email=email)
            user.set_password(req["newpassword"])
            user.save()
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
        req = simplejson.loads(request.body)
        username = req['username']
        oldpassword=req["oldpassword"]
        newpassword=req["newpassword"]
        try:
            user = User.objects.get(username=username)
            if check_password(oldpassword,user.password):
                #修改密码的函数
                user.set_password(newpassword)
                user.save()
            else:
                response["msg"]="false"
        except Exception as e:
            response["msg"]="false"
        return JsonResponse(response)

@csrf_exempt
#登陆
def log_in(request):
    # 设置响应
    response={}
    if request.method=="POST":
        # str=request.META.get("HTTP_SESSIONID")
        msg = 'true'
        try:
            print(request.body)
            req=simplejson.loads(request.body)
        except Exception as e:
            print(e)
        username=req['username']
        password=req['password']
        try:
            user_a = User.objects.get(username=username)  # 这个设置是为了更详细的检查出错误来,因为这个地方get函数不会返回none，一旦找不到，便会给一个exception
            user = authenticate(username=username, password=password)  # 而authenticate就能返回一个none
            if user:
                login(request,user)
                # request.session['is_login']=True
                # request.session['username']=username
                # cache.set(key,value,timeout) timeout代笔缓存的时间，None意味着永久
                # 在这里我将cache设置成数据库的BACKEND,memcached也可以，基于内存，或者redis
                cache.set(request.session.session_key,{"username":username,"is_login":True},3600*24*3)
            else:
                msg = "密码错误"
                return JsonResponse({"msg":msg})
            userstuprofile=list(User_Profile_Stu.objects.filter(user=user))
            usergraduateprofile=list(User_Profile_Graduate.objects.filter(user=user))
            usergraduatecompany = list(User_Profile_Company.objects.filter(user=user))
            if len(userstuprofile)>0:
                response["identity"]=userstuprofile[0].identity
            if len(usergraduateprofile)>0:
                response["identity"] = usergraduateprofile[0].identity
            if len(usergraduatecompany) > 0:
                response["identity"] = usergraduatecompany[0].identity
            response["msg"]=msg
            response["sessionid"]=request.session.session_key
            return JsonResponse(response)
        except Exception as e:
            print(e)
            msg = "用户不存在"
            response["msg"]=msg
            return JsonResponse(response)
    response=HttpResponse()
    get_token(request)  # 产生一个token 用于csrf验证
    return response

@csrf_exempt
#登出
def log_out(request):
    response={"msg":"true"}
    # del request.session["sessionid"]
    #删除cache中的配置
    try:
        sessionid=simplejson.loads(request.body)["sessionid"]
        cache.delete(sessionid)
    except Exception as e:
        print(e)
        response["msg"]="false"
    return JsonResponse(response)

@csrf_exempt
#获取个人信息
def get_profile(request):
    if(request.method=="POST"):
        req = simplejson.loads(request.body)
        identity=req.get("identity")
        sessionid=req.get("sessionid")
        dic=cache.get(sessionid)
        #cache过期
        if dic is None:
            return JsonResponse({"msg":"expire"})
        username=cache.get(sessionid).get("username",None)
        is_login = cache.get(sessionid).get("is_login", False)  # 如果is_login没有设置值的话，默认为False
        # username = request.session.get("username", None)
        # is_login = request.session.get("is_login", False)  # 如果is_login没有设置值的话，默认为False
        response = {}
        msg = 'true'
        #登陆成功
        if is_login:
            user=User.objects.get(username=username)
            #毕业生
            if identity=='1':
                try:
                    userprofile = User_Profile_Graduate.objects.get(user=user)
                    #模型转为字典
                    response=model_to_dict(userprofile)
                    response["msg"]=msg
                    #工作经历的获取
                    joblist=list(JobExperience.objects.filter(user=user))
                    response["jobexperience"]=[]
                    for job in joblist:
                        response["jobexperience"].append(model_to_dict(job))
                    print(response["jobexperience"])
                    # 头像获取
                    response["imgurl"] = userprofile.imgurl
                    return JsonResponse(response)
                except Exception as e:
                    return JsonResponse({"msg":"false"})
            #企业
            if identity=='3':
                try:
                    userprofile = User_Profile_Company.objects.get(user=user)
                    response["name"] = User_Profile_Company.name
                    response["email"]=User_Profile_Company.email
                    response["honour"]=User_Profile_Company.honour
                    response["identity"]=User_Profile_Company.identity
                    response["user_id"] = user.id
                    response["msg"]=msg
                    # 头像获取
                    response["imgurl"] = userprofile.imgurl
                    return JsonResponse(response)
                except Exception as e:
                    response["msg"]=e
                    return JsonResponse(response)
            return JsonResponse({"msg":"no identity"})
        else:
            response["msg"]="false"
            return JsonResponse(response)
    else:
        return JsonResponse({"msg:WM"})

@csrf_exempt
#更新个人信息
def update_profile(request):
    response = {}
    if(request.method=="POST"):
        response["msg"] = "true"
        sessionid=simplejson.loads(request.body).get("sessionid",None)
        dic=cache.get(sessionid)
        req=simplejson.loads(request.body)
        #cache过期
        if dic is None:
            return JsonResponse({"msg":"expire"})
        username=dic["username"]
        is_login=dic["is_login"]
        identity = req.get("identity", None)
        # username = request.session.get("username", None)
        # is_login = request.session.get("is_login", False)
        # identity = simplejson.loads(request.body).get("identity", None)
        #block代表不同的区域
        block=req["block"]
        user = User.objects.get(username=username)
        if is_login:
            #毕业生
            if identity == '1':
                try:
                    userprofile = User_Profile_Graduate.objects.get(user=user)
                    if block=="0":
                        # userprofile.update(**req)
                        userprofile.name=req["name"]
                        userprofile.gender = req["gender"]
                        #头像
                        userprofile.imgurl=req["imgurl"]
                    if block=="1":
                        # 因为字典的内容和model可能对不上，故不用此函数
                        # userprofile.update(**req)
                        userprofile.age = req["age"]
                        userprofile.birth_data = req["birth_data"]
                        userprofile.major = req["major"]
                        userprofile.education_backgroud = req["education_backgroud"]
                        userprofile.university = req["university"]
                        userprofile.living_city = req["living_city"]
                        userprofile.living_provice=req["living_provice"]
                        userprofile.email = req["email"]
                        userprofile.phonenumber = req["phonenumber"]
                        userprofile.school_period_start = req["school_period_start"]
                        userprofile.school_period_end = req["school_period_end"]
                    if block=="2":
                        if req["add"]=="1":
                            education_e = EducationExperience(user=user)
                            education_e.update(**req)
                            education_e.major = req["major"]
                            education_e.school = req["school"]
                            education_e.startime = req["startime"]
                            education_e.endtime = req["endtime"]
                            education_e.educationbackground = req["educationbackground"]
                            education_e.save()
                        else:
                            education_e=EducationExperience.objects.get(id=req["edu_id"])
                            education_e.delete()
                    if block=="3":
                        if req["add"]=="1":
                            jobe = JobExperience(user=user)
                            # jobe.update(**req)
                            jobe.job_place = req["job_place"]
                            jobe.job = req["job"]
                            jobe.job_period_start = req["job_period_start"]
                            jobe.job_period_end = req["job_period_end"]
                            jobe.job_salary = req["job_salary"]
                            jobe.job_city = req["job_city"]
                            jobe.job_province = req["job_province"]
                            jobe.save()
                        #删除工作经历
                        else:
                            jobe=JobExperience.objects.get(id=req["job_id"])
                            jobe.delete()
                    if block=="4":
                        userprofile.self_judement = req["self_judement"]
                        userprofile.self_sign = req["self_sign"]
                    userprofile.save()
                except Exception as e:
                    response["msg"]="false"
                return JsonResponse(response)
            #企业
            if identity == '3':
                try:
                    userprofile = User_Profile_Company.objects.get(user=user)
                    userprofile.phonenumber=req["phonenumber"]
                    userprofile.name=req["name"]
                    userprofile.email=req["email"]
                    # 头像
                    userprofile.imgurl=req["imgurl"]
                    userprofile.save()
                    response["msg"]="true"
                except Exception as e:
                    response['msg']=e
                return JsonResponse(response)
    get_token(request)
    return JsonResponse(response)

@csrf_exempt
#关注某人
def follw(request):
    response={}
    if request.method=="POST":
        req=simplejson.loads(request.body)
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
                # 拿到申请者user
                user = User.objects.get(username=username)
                #关注人的id
                fuser=User.objects.get(id=fid)
                tmp=list(Friends.objects.filter(user=fuser))
                if(len(tmp)==0):
                    #friend=Friends(user=fuser) 这样写应该只是在内存中创建，不再表中创建
                    friend=Friends.objects.create(user=fuser)
                    print(friend.id)
                else:
                    friend=tmp[0]
                friend.myfollows.add(user)
                friend.save()
                message=Message(text=req["text"],msgfrom=user,msgto=fuser,headline=req["headline"])
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
        req=simplejson.loads(request.body)
        dic=cache.get(req["sessionid"])
        if dic is None:
            return JsonResponse({"msg":"expire"})
        try:
            fuser=Friends.objects.get(user=User.objects.get(id=req["fid"]))
            fuser.followedby.remove(User.objects.get(username=dic["username"]))
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
    req = simplejson.loads(request.body)
    sessionid = req["sessionid"]
    dic = cache.get(sessionid)
    if dic is None:
        return JsonResponse({"msg": "expire"})
    is_login = dic["is_login"]
    username = dic["username"]
    if is_login:
        user = User.objects.get(username=username)
        # 获得该用户的所有关注的人
        try:
            concerns = list(user.myfollows.all())
        except Exception as e:
            concerns=[]
        # 将关注的人的头像，姓名和id返回
        response["follows"] = []
        for f in concerns:
            profile1=list(User_Profile_Graduate.objects.filter(user=f.user))
            profile2 =list(User_Profile_Company.objects.filter(user=f.user))
            dic={}
            if(len(profile1)>0):
                dic["imgurl"] = profile1[0].imgurl
                dic["name"] = profile1[0].name
                dic["gender"]=profile1[0].gender
            if(len(profile2)>0):
                dic["imgurl"] = profile2[0].imgurl
                dic["name"] = profile2[0].name
                dic["gender"]=""
            dic["id"]=f.user.id
            response["follows"].append(dic)
        return JsonResponse(response)
    else:
        return JsonResponse({"msg": "false"})

@csrf_exempt
#展示我的粉丝
def showmyfans(request):
    response = {}
    response["msg"] = "true"
    req = simplejson.loads(request.body)
    sessionid = req["sessionid"]
    dic = cache.get(sessionid)
    if dic is None:
        return JsonResponse({"msg": "expire"})
    is_login = dic["is_login"]
    username = dic["username"]
    if is_login:
        user = User.objects.get(username=username)
        # 获得所有关注该用户的人
        try:
            fans = Friends.objects.get(user=user).myfollows.all()
        except Exception as e:
            print(e)
            fans =[]
        # 将关注的人的头像，姓名和id返回
        response["fans"] = []
        for f in fans:
            profile1=list(User_Profile_Graduate.objects.filter(user=f))
            profile2=list(User_Profile_Company.objects.filter(user=f))
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
        req = simplejson.loads(request.body)
        sessionid = req["sessionid"]
        dic = cache.get(sessionid)
        if dic is None:
            return JsonResponse({"msg": "expire"})
        is_login = dic["is_login"]
        username = dic["username"]
        if is_login:
            try:
                msgs=list(User.objects.get(username=username).myreceivemsg.all())
            except Exception as e:
                msgs=[]
            response["messages"]=[]
            for m in msgs:
                profile1=list(User_Profile_Graduate.objects.filter(user=m.msgfrom))
                profile2 = list(User_Profile_Company.objects.filter(user=m.msgfrom))
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
def searchuser(request):
    response={}
    response["msg"]="true"
    req=simplejson.loads(request.body)
    if request.method=="POST":
        dic=cache.get(req["sessionid"])
        if dic is None:
            return JsonResponse({"msg":"expire"})
        user=User.objects.get(username=dic["username"])
        key=req["key"]
        response["users"]=[]
        ans1=list(User_Profile_Graduate.objects.filter(Q(name__icontains=key)|Q(email__icontains=key)))
        ans2=list(User_Profile_Company.objects.filter(Q(name__icontains=key)|Q(email__icontains=key)))
        try:
            myfollows = list(user.myfollows.all())
        except Exception as e:
            myfollows=[]
        myfollowsid=[]
        for m in myfollows:
            myfollowsid.append(m.user.id)
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
            response["users"].append(dic)
        ans3=User.objects.filter(username__icontains=key)
        for a in ans3:
            dic={}
            profile1=list(User_Profile_Graduate.objects.filter(user=a))
            dic["name"]=None
            dic["imgurl"]=None
            if(len(profile1)>0):
                dic["name"]=profile1[0].name
                dic["imgurl"]=profile1[0].imgurl
                dic["gender"] = profile1[0].gender
            profile2=list(User_Profile_Company.objects.filter(user=a))
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
            response["users"].append(dic)
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
            gra_user = User.objects.get(username=username)
            #检验该用户的文件名是否存在
            if(len(Graduate_Resume.objects.filter(Q(user=gra_user) and Q(name=request.POST["name"])))>0):
                return JsonResponse({"msg":"exist"})
            file = request.FILES['resume']
            #创建一个唯一的文件名,注意加上后缀名,wb+代表二进制写的形式打开文件
            id=os.path.join("media","resume",str(uuid.uuid4())+os.path.splitext(file.name)[1])
            #创建一个resume实例,记录路径
            resume=Graduate_Resume(user=gra_user,url=id,name=request.POST["name"])
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
        req=simplejson.loads(request.body)
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
        req=simplejson.loads(request.body)
        sessionid = req["sessionid"]
        dic = cache.get(sessionid)
        response={}
        response["msg"]="true"
        if dic is None:
            return JsonResponse({"msg": "expire"})
        username = dic["username"]
        try:
            gra_user=User.objects.get(username=username)
            try:
                resumes=list(gra_user.myresume.all())
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
        req=simplejson.loads(request.body)
        sessionid = req["sessionid"]
        dic = cache.get(sessionid)
        response={}
        response["msg"]="true"
        if dic is None:
            return JsonResponse({"msg": "expire"})
        username = dic["username"]
        try:
            com_user=User.objects.get(username=username)
            try:
                resumes=list(com_user.resumto.all())
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
        req = simplejson.loads(request.body)
        sessionid = req["sessionid"]
        dic = cache.get(sessionid)
        response = {}
        response["msg"] = "true"
        if dic is None:
            return JsonResponse({"msg": "expire"})
        username = dic["username"]
        try:
            gra_user=User.objects.get(username=username)
            com_user=User.objects.get(id=req["cid"])
            #找到文件路径
            path=os.path.join(settings.BASE_DIR,req["url"])
            #复制一份该文件,并且创建企业简历实例
            #文件复制的方法有很多种，这个地方使用shutil模块，也可以自己定义
            tmp=os.path.splitext(req["url"])
            new_id=str(uuid.uuid4())+tmp[len(tmp)-1]
            new_path=os.path.join(settings.BASE_DIR,"media","resume",new_id)
            #创建企业简历实例
            com_resume=Company_Resume(user=gra_user,url=new_id,company=com_user,name=req["name"])
            #创建消息发送给相应的企业
            msg=Message(msgfrom=gra_user,msgto=com_user,text=req["text"],headline=req["headline"])
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
        req = simplejson.loads(request.body)
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
        req=simplejson.loads(request.body)
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
            jobs.extend(list(g.user.myjobexp.filter(job_period_end=None)))
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
        req=simplejson.loads(request.body)
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
            jobs.extend(list(g.user.myjobexp.filter(job_period_end=None)))
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
        req=simplejson.loads(request.body)
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
        req=simplejson.loads(request.body)
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
        req = simplejson.loads(request.body)
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
            jobs.extend(list(g.user.myjobexp.filter(job_period_end=None)))
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