from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import SecondHandTrade,Picture,Comment
from django.http import JsonResponse
from django.conf import settings
import simplejson
from django.core.cache import cache
#注意导入这个应用的时候
from user.models import User_Profile_Graduate,User_Profile_Stu,User_Profile_Company

#上传帖子基本信息
@csrf_exempt
def uploadpost(request):
    response={}
    if(request.method=="POST"):
        req=simplejson.loads(request.body)
        sessionid=req["sessionid"]
        dic = cache.get(sessionid)
        if dic is None:
            return JsonResponse({"msg":"expire"})
        username=dic["username"]
        itemtype=req["itemtype"]
        title=req["title"]
        content=req["content"]
        imgurls=req["imgurls"]
        try:
            user=User.objects.get(username=username)
            post=SecondHandTrade(user=user,title=title,content=content,itemtype=itemtype,like_count=0)
            post.save()
            for i in range(len(imgurls)):
                img=Picture(img_url=imgurls[i],post=post)
                img.save()
            response["msg"]="true"
            response["post_id"]=post.id
            response["post_time"]=post.created_time
        except Exception as e:
            response["msg"]=e
            print(e)
            return JsonResponse(response)
        return JsonResponse(response)

#发布评论
@csrf_exempt
def uploadcomment(request):
    if(request.method=="POST"):
        response = {"msg":"true"}
        req=simplejson.loads(request.body)
        to_which_post=SecondHandTrade.objects.get(id=req["postid"])
        to_which_user=None
        try:
            touserid=req.get("touserid",None)
            if touserid is not None:
                # 回复评论的id
                to_which_user = User.objects.get(id=req["receiverid"])
            user=User.objects.get(id=req["senderid"])
            content=req["content"]
            comment=Comment(user=user,content=content,to_which_user=to_which_user,to_which_post=to_which_post)
            comment.save()
        except Exception as e:
            response["msg"]="false"
        return JsonResponse(response)

@csrf_exempt
#获取所有帖子的信息
def getpost(request):
    if(request.method=="POST"):
        response={}
        posts=list(SecondHandTrade.objects.all().order_by("-created_time"))
        i=1
        for post in posts:
           postname="post"+str(i)
           j = 1
           i=i+1
           response[postname]={}
           response[postname]["content"]=post.content
           response[postname]["postid"] = post.id
           response[postname]["userid_p"] =post.user.id
           response[postname]["like_count"] = post.like_count
           response[postname]["created_time"]=post.created_time
           response[postname]["title"]=post.title
           response[postname]["itemtype"]=post.itemtype
           #获取发布者的昵称
           user=User.objects.get(id=post.user.id)
           stu_profile = list(User_Profile_Stu.objects.filter(user=user))
           c_profile = list(User_Profile_Company.objects.filter(user=user))
           g_profile = list(User_Profile_Graduate.objects.filter(user=user))
           if len(stu_profile) > 0:
               response[postname]["postername"] = stu_profile[0].name
           if len(c_profile) > 0:
               response[postname]["postername"] = c_profile[0].name
           if len(g_profile) > 0:
               response[postname]["postername"] = g_profile[0].name
           #获取发布者的头像
           try:
               user = User.objects.get(id=post.user.id)
           except Exception as e:
               print(e)
           img=list(ImageProfile.objects.filter(user=user))
           if len(img)>0:
               response[postname]["userimg"] = img[0].imgurl
           imgs=Picture.objects.filter(post=post)
           arr_img=[]
           for k in range(len(imgs)):
               arr_img.append(imgs[k].img_url)
           response[postname]["imgurls"]=arr_img
        return JsonResponse(response)

#获取帖子的评论
@csrf_exempt
def getpostcomment(request):
    response={}
    response["msg"]="true"
    if request.method=="POST":
        req=simplejson.loads(request.body)
        postid=req["postid"]
        post=SecondHandTrade.objects.get(id=postid)
        comments=list(Comment.objects.filter(to_which_post=post).order_by("created_time"))
        response["comments"]=[]
        for comment in comments:
            com={}
            com["content"]=comment.content
            com["sendername"]=""
            com["senderimg"] = ""
            com["receivername"] = ""
            com["receiverimg"] = ""
            #拿到发送者的姓名和头像
            user = User.objects.get(id=comment.user.id)
            stu_profile = list(User_Profile_Stu.objects.filter(user=user))
            c_profile = list(User_Profile_Company.objects.filter(user=user))
            g_profile = list(User_Profile_Graduate.objects.filter(user=user))
            if len(stu_profile)>0:
                com["sendername"] = stu_profile[0].name
            if len(c_profile) > 0:
                com["sendername"] = c_profile[0].name
            if len(g_profile) > 0:
                com["sendername"] = g_profile[0].name
            img=list(ImageProfile.objects.filter(user=user))
            if len(img)>0:
                com["senderimg"]=img[0].imgurl

            #拿到接受者的姓名和头像
            user = User.objects.get(id=comment.user.id)
            stu_profile = list(User_Profile_Stu.objects.filter(user=user))
            c_profile = list(User_Profile_Company.objects.filter(user=user))
            g_profile = list(User_Profile_Graduate.objects.filter(user=user))
            if len(stu_profile) > 0:
                com["receivername"] = stu_profile[0].name
            if len(c_profile) > 0:
                com["receivername"] = c_profile[0].name
            if len(g_profile) > 0:
                com["receivername"] = g_profile[0].name
            com["commentid"]=comment.id
            com["senderid"]=comment.user.id
            com["created_time"]=comment.created_time
            response["comments"].append(com)

        return JsonResponse(response)

#点赞
@csrf_exempt
def add_likecount(request):
    if(request.method=="POST"):
        response={}
        req=simplejson.loads(request.body)
        postid=req["post_id"]
        post_lostf=SecondHandTrade.objects.get(id=postid)
        post_lostf.like_count+=1
        post_lostf.save()
        response["msg"] = "true"
        return JsonResponse(response)









