from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.http import JsonResponse,HttpResponse
from .models import user_profile_stu,\
    user_profile_graduate,\
    user_profile_company,jobexperience,imageprofile,\
    educationexperice,friends
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
            if identity=="1":
                profile=user_profile_graduate(user=user)
                profile.identity=identity
                profile.save()
            if identity=="2":
                profile = user_profile_stu(user=user)
                profile.identity = identity
                profile.save()
            if identity=="3":
                profile = user_profile_company(user=user)
                profile.identity = identity
                profile.save()
            img=imageprofile(user=user,imgurl=None)
            img.save()
            job=jobexperience(user=user)
            job.save()
            e=educationexperice(user=user)
            e.save()
        #如果用户已存在但是不是有效的,那么直接对这个用户发送邮件
        #发送邮件
        #生成随机字符串
        random_str=get_random_str()
        url = "http://172.16.32.1:8000/delonixregia/verify/"+random_str+"/"
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



#更改密码
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
            user.password=req["newpassword"]
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
        response["msg"] = "ture"
        req = simplejson.loads(request.body)
        username = req['username']
        oldpassword=req["oldpassword"]
        newpassword=req["newpassword"]
        try:
            user = User.objects.get(username=username)
            if check_password(oldpassword,user.password):
                user.password=newpassword
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
        req=simplejson.loads(request.body)
        username=req['username']
        password=req['password']
        try:
            user_a = User.objects.get(username=username)  # 这个设置是为了更详细的检查出错误来,因为这个地方get函数不会返回none，一旦找不到，便会给一个exception
            user = authenticate(username=username, password=password)  # 而authenticate就能返回一个none
            if user:
                login(request,user)
                # request.session['is_login']=True
                # request.session['username']=username
                cache.set(request.session.session_key,{"username":username,"is_login":True},None)
            else:
                msg = "密码错误"
            userstuprofile=list(user_profile_stu.objects.filter(user=user))
            usergraduateprofile=list(user_profile_graduate.objects.filter(user=user))
            usergraduatecompany = list(user_profile_company.objects.filter(user=user))
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

#登出
def log_out(request):
    response={"msg":"true"}
    # del request.session["sessionid"]
    #删除cache中的配置
    cache.delete(simplejson.loads(request).get("sessionid"))

    return response

@csrf_exempt
#获取个人信息
def get_profile(request):
    req = simplejson.loads(request.body)
    print(req)
    identity=req.get("identity",None)
    sessionid=req.get("sessionid",None)
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
                userprofile = user_profile_graduate.objects.get(user=user)
                response["phonenumber"]=userprofile.phonenumber
                response["living_province"]=userprofile.living_city
                response["school"]=userprofile.university
                response["name"] = userprofile.name
                response["gender"] = userprofile.gender
                response["age"]=userprofile.age
                response["major"] = userprofile.major
                response["email"]=userprofile.email
                response["birth_data"]=userprofile.birth_data
                response["education_backgroud"] = userprofile.education_backgroud
                response["living_city"]=userprofile.living_city
                response["school_period_start"]=userprofile.school_period_start
                response["school_period_end"]=userprofile.school_period_end
                response["honour"]=userprofile.honour
                response["self_judement"]=userprofile.self_judement
                response["user_id"] = user.id
                response["identity"]=userprofile.identity
                response["msg"]=msg
                #工作经历的获取
                response["jobexperience"]=list(jobexperience.objects.filter(user=user))
                # 头像获取
                img = imageprofile.objects.filter(user=user)[0]
                response["imgurl"] = img.imgurl
                return JsonResponse(response)
            except Exception as e:
                return JsonResponse(response)
        #在校生
        if identity=='2':
            try:
                userprofile = user_profile_stu.objects.get(user=user)
                response["phonenumber"]=userprofile.phonenumber
                response["name"] = userprofile.name
                response["gender"] = userprofile.gender
                response["age"]=userprofile.age
                response["major"] = userprofile.major
                response["email"]=userprofile.email
                response["birth_data"]=userprofile.birth_data
                response["user_id"] = user.id
                response["identity"]=userprofile.identity
                response["institution"]=userprofile.institution
                response["self_judgement"] = userprofile.self_judgement
                response["self_sign"] = userprofile.self_sign
                response["living_city"] = userprofile.living_city
                response["living_province"]=userprofile.living_province
                response["university"] = userprofile.university
                response["msg"]=msg

                # 头像获取
                img=imageprofile.objects.filter(user=user)[0]
                response["imgurl"] = img.imgurl
                # 教育经历获取
                e_education=list(educationexperice.objects.filter(user=user))
                educations={}
                i=1
                for education in e_education:
                    strn = "education" + str(i)
                    edu = {}
                    edu["startime"]=education.startime
                    edu["endtime"]=education.endtime
                    edu["school"]=education.school
                    edu["major"]=education.major
                    edu["educationbackground"]=education.educationbackground
                    edu["edu_id"]=education.id
                    educations[strn]=edu
                    i=i+1
                response["edu_e"]=educations
                # 工作经历
                j_experience=list(jobexperience.objects.filter(user=user))
                jobs={}
                i = 1
                for j in j_experience:
                    strn = "job" + str(i)
                    job = {}
                    job["job_place"] = j.job_place
                    job["job"] = j.job
                    job["job_period_start"] = j.job_period_start
                    job["job_period_end"] = j.job_period_end
                    job["job_city"] = j.job_city
                    job["job_salary"] = j.job_salary
                    job["job_id"]=j.id
                    job["job_province"]=j.job_province
                    jobs[strn] = job
                    i=i+1
                response["job_e"]=jobs
                return JsonResponse(response)
            except Exception as e:
                return JsonResponse(response)
        #企业
        if identity=='3':
            try:
                userprofile = user_profile_company.objects.get(user=user)
                response["name"] = user_profile_company.name
                response["email"]=user_profile_company.email
                response["honour"]=user_profile_company.honour
                response["identity"]=user_profile_company.identity
                response["user_id"] = user.id
                response["msg"]=msg
                # 头像获取
                img = imageprofile.objects.filter(user=user)[0]
                response["imgurl"] = img.imgurl
                return JsonResponse(response)
            except Exception as e:
                response["msg"]=e
                return JsonResponse(response)
    else:
        response["msg"]="false"
        return JsonResponse(response)

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
        #获取用户
        block=req["block"]
        user = User.objects.get(username=username)
        if is_login:
            #毕业生
            if identity == '1':
                try:
                    userprofile = user_profile_graduate.objects.get(user=user)
                    if block=="0":
                        userprofile.name = req["name"]
                        userprofile.gender = req["gender"]
                        # 头像
                        image=imageprofile.objects.get(user=user)
                        image.imgurl = req["imgurl"]
                        image.save()

                    if block=="1":
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
                            education_e = educationexperice(user=user)
                            education_e.major = req["major"]
                            education_e.school = req["school"]
                            education_e.startime = req["startime"]
                            education_e.endtime = req["endtime"]
                            education_e.educationbackground = req["educationbackground"]
                            education_e.save()
                        else:
                            education_e=educationexperice.objects.get(id=req["edu_id"])
                            education_e.delete()
                    if block=="3":
                        if req["add"]=="1":

                            jobe = jobexperience(user=user)
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
                            jobe=jobexperience.objects.get(id=req["job_id"])
                            jobe.delete()
                    if block=="4":
                        userprofile.self_judement = req["self_judement"]
                        userprofile.self_sign = req["self_sign"]
                    userprofile.save()
                except Exception as e:
                    response["msg"]=e
                return JsonResponse(response)
            #在校生
            if identity == '2':
                try:
                    userprofile = user_profile_stu.objects.get(user=user)
                    if block == "0":
                        userprofile.name = req["name"]
                        userprofile.gender = req["gender"]
                        # 头像
                        image = imageprofile.objects.get(user=user)
                        image.imgurl = req["imgurl"]
                        image.save()
                    if block=="1":
                        print(userprofile)
                        userprofile.age = req["age"]
                        userprofile.birth_data = req["birth_data"]
                        userprofile.major = req["major"]
                        userprofile.education_background = req["education_background"]
                        userprofile.university = req["university"]
                        userprofile.living_city = req["living_city"]
                        userprofile.living_province = req["living_province"]
                        userprofile.email = req["email"]
                        userprofile.phonenumber = req["phonenumber"]
                        userprofile.school_period_start = req["school_period_start"]
                        userprofile.school_period_end = req["school_period_end"]
                    if block=="2":
                        # 教育经历
                        if req["add"]=="1":
                            education_e = educationexperice(user=user)
                            print(user)
                            education_e.major = req["major"]
                            print(education_e.major)
                            education_e.school = req["school"]
                            print(education_e.school)
                            education_e.startime = req["startime"]
                            print(education_e.startime)
                            education_e.endtime = req["endtime"]
                            print(education_e.endtime)
                            education_e.educationbackground = req["educationbackground"]
                            print(education_e.educationbackground)
                            education_e.save()
                        else:
                            education_e=educationexperice.objects.get(id=req["edu_id"])
                            education_e.delete()
                    if block=="3":
                        if req["add"]=="1":
                            jobe = jobexperience(user=user)
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
                            jobe=jobexperience.objects.get(id=req["job_id"])
                            print(req["job_id"])
                            jobe.delete()
                    if block=="4":
                        print(req["self_judgement"])
                        print(req["self_sign"])
                        userprofile.self_judgement = req["self_judgement"]
                        userprofile.self_sign = req["self_sign"]
                    userprofile.save()
                    response["msg"]="true"
                except Exception as e:
                    response['msg']=e
                return JsonResponse(response)
            #企业
            if identity == '3':
                try:
                    userprofile = user_profile_company.objects.get(user=user)
                    userprofile.phonenumber=req["phonenumber"]
                    userprofile.name=req["name"]
                    userprofile.email=req["email"]
                    # 头像
                    image = imageprofile(user=user)
                    image.imgurl = req["imgurl"]
                    image.save()
                    userprofile.save()
                    response["msg"]="true"
                except Exception as e:
                    response['msg']=e
                return JsonResponse(response)
    get_token(request)
    return JsonResponse(response)

@csrf_exempt
#添加好友
def addfriend(request):
    response={}
    if request.method=="POST":
        req=simplejson.loads(request.body)
        sessionid=req["sessionid"]
        fid=req["fid"]
        dic=cache.get(sessionid)
        response["msg"]="true"
        if dic is None:
            return JsonResponse({"msg":"expire"})
        username=dic["username"]
        is_login=dic["is_login"]
        if is_login:
            try:
                fuser=User.objects.get(id=fid)
                user=User.objects.get(username=username)
                friend=friends(user=fuser)
                friend.whosfriend=user
                friend.save()
            except Exception as e:
                response["msg"]=e
            return JsonResponse(response)
        else:
            response["msg"]="false"
            return JsonResponse(response)
    return JsonResponse({"msg":"wrongmethod"})

@csrf_exempt
#选择是否接受好友
def acceptfriend(requst):
    response={}
    response["msg"]="true"
    if requst.method=="POST":
        req=simplejson.loads(requst.body)
        sessionid=req["sessionid"]
        whosfriend=User.objects.get(id=req["fid"])
        dic=cache.get(sessionid)
        if dic is None:
            return JsonResponse({"msg":"expire"})
        is_login=dic["is_login"]
        username=dic["username"]

        is_acc=req["is_ac"]
        if is_login:
            if is_acc=="1":
                try:
                    user=User.objects.get(username=username)
                    friendship=list(friends.objects.filter(user=user,whosfriend=whosfriend))
                    if len(friendship)>0:
                        friendship[0].is_friend=True
                        friendship[0].save()
                    else:
                        response["msg"]="no such message"
                except Exception as e:
                    response["msg"]=e
            else:
                user = User.objects.get(username=username)
                friendship = list(friends.objects.filter(user=user, whosfriend=whosfriend))
                if len(friendship) > 0:
                    friendship[0].delete()
                else:
                    response["msg"] = "no such message"
            return JsonResponse(response)
        else:
            return JsonResponse({"msg":"false"})
    return JsonResponse({"msg":"wrongmethod"})

@csrf_exempt
#展示好友列表
def showfriends(requst):
    response = {}
    response["msg"] = "true"
    req = simplejson.loads(requst.body)
    sessionid = req["sessionid"]
    dic = cache.get(sessionid)
    if dic is None:
        return JsonResponse({"msg": "expire"})
    is_login = dic["is_login"]
    username = dic["username"]

    if is_login:
       user=User.objects.get(username=username)
       fs=list(friends.objects.filter(whosfriend=user))
       #获取所有的朋友列表
       isf={}
       notf={}
       whosendmemessage={}
       #循环时会用到
       i=1
       j=1
       k=1
       for f in fs:
           if f.is_friend:
               strn = "f1" + str(i)
               dicn = {}
               user = f.user
               print(user)
               dicn["fname"] = user.username
               dicn["fid"] = user.id
               img = list(imageprofile.objects.filter(user=user))
               profile_s = list(user_profile_stu.objects.filter(user=user))
               profile_g = list(user_profile_graduate.objects.filter(user=user))
               if len(profile_g) > 0:
                   dicn["fself_sign"] = profile_g[0].self_sign
               if len(profile_s) > 0:
                   dicn["fself_sign"] = profile_s[0].self_sign
               if len(profile_g) < 0 and len(profile_s) < 0:
                   dicn["fself_sign"] = ""
               if len(img)>0:
                   dicn["fimgurl"] = img[0].imgurl
               else:
                   response["fimgurl"] =""
               isf[strn] = dicn
               i = i + 1
           else:
               strn = "nf" + str(j)
               dicn = {}
               user = f.user
               dicn["fname"] = user.username
               dicn["fid"] = user.id
               img = list(imageprofile.objects.filter(user=user))
               profile_s = list(user_profile_stu.objects.filter(user=user))
               profile_g = list(user_profile_graduate.objects.filter(user=user))
               if len(profile_g) > 0:
                   dicn["fself_sign"] = profile_g[0]. self_sign
               if len(profile_s) > 0:
                   dicn["fself_sign"] = profile_s[0].self_sign
               if len(profile_g) < 0 and len(profile_s) < 0:
                   dicn["fself_sign"] = ""
               if len(img)>0:
                   dicn["fimurl"] = img[0].imgurl
               else:
                   dicn ["fimurl"] =""
               isf[strn] = dicn
               i = i + 1
               notf[strn] = dicn
       print(username)
       user=User.objects.get(username=username)
       message=list(friends.objects.filter(user=user,is_friend=False))
       for u in message:
           strn="m"+str(k)
           dicn = {}
           user=User.objects.get(id=u.whosfriend.id)
           print(user)
           dicn["fname"]=user.username
           dicn["fid"]=user.id
           img = list(imageprofile.objects.filter(user=user))
           if len(img)>0:
               dicn["imgurl"] = img[0].imgurl
           else:dicn["imgurl"]=""
           whosendmemessage[strn]=dicn
           k=k+1

       response["whosendmemessage"]=whosendmemessage
       response["friends"] = isf
       response["nfriends"] = notf
       response["msg"]="true"
       return JsonResponse(response)
    else:
        return JsonResponse({"msg": "false"})

@csrf_exempt
#搜索某个用户
def searchuser(requst):
    response={}
    response["msg"]="true"
    if requst.method=="POST":
        req=simplejson.loads(requst.body)
        email=req["email"]
        sessionid = req["sessionid"]
        dic=cache.get(sessionid)
        if dic is None:
            return JsonResponse({"msg":"expire"})
        username=dic["username"]
        is_login=dic["is_login"]
        if is_login:
            try:
                searcher=User.objects.get(email=email,is_active=True)
                user=list(User.objects.filter(email=email,is_active=True))
                #不存在该用户
                if len(user)==0:
                    response["msg"]="false"
                else:
                    response["username"]=user[0].username
                    img=list(imageprofile.objects.filter(user=user[0]))
                    profile_s = list(user_profile_stu.objects.filter(user=user[0]))
                    profile_g = list(user_profile_graduate.objects.filter(user=user[0]))
                    friend= list(friends.objects.filter(user=user[0],whosfriend=searcher))
                    if len(friend)>0:
                        response["is_f"]="1"
                    else:
                        response["is_f"]="0"
                    if len(profile_g)>0:
                        response["self_sign"]=profile_g[0].self_sign
                    if len(profile_s)>0:
                        response["self_sign"] =profile_s[0].self_sign
                    response["imgurl"]=img[0].imgurl
                    response["uid"]=user[0].id
            except Exception as e:
                print(e)
                response["msg"]=e
            return JsonResponse(response)



