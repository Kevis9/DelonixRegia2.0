#!python
#coding:utf-8
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import FriendPost,Picture,Comment
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
import simplejson
from user.models import Friends,User_Profile_Graduate,User_Profile_Stu,User_Profile_Company
from operator import attrgetter

#获取朋友的所有帖子
@csrf_exempt
def getallpost(request):
    response = {}
    if(request.method=="POST"):
        response["msg"]="true"
        req=simplejson.loads(request.body)
        #用户的id
        sessionid=req["sessionid"]
        dic = cache.get(sessionid)
        if dic is None:
            return JsonResponse({"msg":"expire"})
        username=dic["username"]
        all_posts=[]
        response["allpost"]=[]
        #获取用户所有的朋友
        user=User.objects.get(username=username)
        try:
            myfollows=list(user.followedby.all())
        except Exception as e:
            print(e)
            myfollows=[]
        for f in myfollows:
            try:
                all_my_friend_post=list(f.myposts.all())
            except Exception as e:
                all_my_friend_post=[]
            for post in all_my_friend_post:
                all_posts.append(post)
        #按照时间顺序降序
        try:
            sorted(all_posts,key=attrgetter("created_time"),reverse=False)
        except Exception as e:
            print(e)

        for post in all_posts:
            #将帖子里面的信息放入字典
            dic={}
            #发帖人的基本信息
            gra_user_profile=User_Profile_Graduate.objects.get(user=post.user)
            dic["img_url"]=gra_user_profile.imgurl
            dic["name_lab"]=gra_user_profile.name
            dic["time_lab"]=post.created_time
            dic["title"]=post.title
            dic["content"]=post.content
            dic["post_id"]=post.id
            dic["owner"]=post.user.username
            try:
                imgs=list(post.myimgs.all())
            except Exception as e:
                print(e)
                imgs=[]
            try:
                comments=list(post.postcomments.all())
            except Exception as e:
                print(e)
                comments=[]
            dic["pics_url"] = []
            dic["comments"]=[]
            dic["mycomments"] = []
            for i in imgs:
                dic["pics_url"].append(i.imgurl)
            for c in comments:
                tmp={}
                gra_profile=list(User_Profile_Graduate.objects.filter(user=c.user))
                com_profile =list(User_Profile_Company.objects.filter(user=c.user))
                if(len(gra_profile)>0):
                    tmp["from"]=gra_profile[0].name
                if(len(com_profile)>0):
                    tmp["from"] = com_profile[0].name
                gra_profile = list(User_Profile_Graduate.objects.filter(user=c.to_which_user))
                com_profile = list(User_Profile_Company.objects.filter(user=c.to_which_user))
                if (len(gra_profile) > 0):
                    tmp["to"] = gra_profile[0].name
                if (len(com_profile) > 0):
                    tmp["to"] = com_profile[0].name
                tmp["fromusername"]=c.user.username
                tmp["content"]=c.content
                tmp["time_lab"]=c.created_time
                tmp["commentid"]=c.id
                dic["comments"].append(tmp)
            response["allpost"].append(dic)
        return JsonResponse(response)
    else:
        return JsonResponse({"msg":"WM"})

#发布评论
@csrf_exempt
def uploadcomment(request):
    if (request.method == "POST"):
        response = {"msg": "true"}
        req = simplejson.loads(request.body)
        sessionid = req["sessionid"]
        dic = cache.get(sessionid)
        if dic is None:
            return JsonResponse({"msg": "expire"})
        username = dic["username"]
        to_which_post = FriendPost.objects.get(id=req["postid"])
        try:
            poster_name = req.get("poster_name", None)
            to_which_user = User.objects.get(username=poster_name)
            user = User.objects.get(username=username)
            content = req["content"]
            comment = Comment(user=user, content=content, to_which_user=to_which_user, post=to_which_post)
            comment.save()
            response["commentid"] = comment.id
        except Exception as e:
            response["msg"] = "false"
        return JsonResponse(response)
    else:
        return JsonResponse({"msg":"WM"})

@csrf_exempt
#删除评论
def deletecomment(request):
    if (request.method == "POST"):
        response = {"msg": "true"}
        req = simplejson.loads(request.body)
        sessionid = req["sessionid"]
        dic = cache.get(sessionid)
        if dic is None:
            return JsonResponse({"msg": "expire"})
        username = dic["username"]
        cid=req["commentid"]
        try:
            comment = Comment.objects.get(id=cid)
            comment.delete()
        except Exception as e:
            response["msg"] = "false"
        return JsonResponse(response)
    else:
        return JsonResponse({"msg":"WM"})

#点赞
@csrf_exempt
def add_likecount(request):
    if(request.method=="POST"):
        response={}
        req=simplejson.loads(request.body)
        postid=req["post_id"]
        post_lostf=FriendPost.objects.get(id=postid)
        post_lostf.like_count+=1
        post_lostf.save()
        response["msg"] = "true"
        return JsonResponse(response)

#发布帖子
@csrf_exempt
def uploadpost(request):
    response={}
    response["msg"]="true"
    if(request.method=="POST"):
        req=simplejson.loads(request.body)
        dic=cache.get(req["sessionid"])
        if dic is None:
            response["msg"]="expire"
            return JsonResponse(response)
        is_login=dic["is_login"]
        if is_login:
            title=req["title"]
            content=req["content"]
            imgurls=req["imgurls"]
            try:
                user=User.objects.get(username=dic["username"])
                post=FriendPost(user=user, title=title, content=content, like_count=0)
                post.save()
                for i in range(len(imgurls)):
                    img=Picture(imgurl=imgurls[i],post=post)
                    img.save()
                response["msg"]="true"
                response["post_lostf_id"]=post.id
            except Exception as e:
                response["msg"]=e
                print(e)
        else:
            response["msg"]="false"
        return JsonResponse(response)

# 获取帖子的评论
@csrf_exempt
def getpostcomment(request):
    response={}
    response["msg"]="true"
    if request.method=="POST":
        req=simplejson.loads(request.body)
        dic=cache.get(req["sessionid"])
        if dic is None:
            return JsonResponse({"msg":"expire"})
        postid=req["postid"]
        post=FriendPost.objects.get(id=postid)
        try:
            comments=list(post.postcomments.all().order_by("-created_time"))
        except Exception as e:
            comments=[]
        response["comments"]=[]
        for comment in comments:
            com={}
            com["content"]=comment.content
            com["from"]=""
            com["fromimg"] = ""
            com["to"] = ""
            # 拿发送者的姓名和头像
            user = User.objects.get(id=comment.user.id)
            gra_profile = list(User_Profile_Graduate.objects.filter(user=user))
            com_profile = list(User_Profile_Company.objects.filter(user=user))
            if len(gra_profile)>0:
                com["from"] = gra_profile[0].name
                com["fromimg"]=gra_profile[0].imgurl
            if len(com_profile) > 0:
                com["from"] = com_profile[0].name
                com["fromimg"] = com_profile[0].imgurl
            #拿接受者的姓名
            if comment.to_which_user is not None:
                user = User.objects.get(id=comment.to_which_user.id)
                com_profile = list(User_Profile_Company.objects.filter(user=user))
                gra_profile = list(User_Profile_Graduate.objects.filter(user=user))
                if len(gra_profile) > 0:
                    com["to"] = gra_profile[0].name
                if len(com_profile) > 0:
                    com["to"] = com_profile[0].name
            com["commentid"]=comment.id
            com["fromusername"]=comment.user.username
            com["created_time"]=comment.created_time
            response["comments"].append(com)
        return JsonResponse(response)
    else:
        return JsonResponse({"msg":"WM"})
