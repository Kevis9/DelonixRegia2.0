from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import FriendCircle,Picture,Comment
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
        myfriends=list(Friends.objects.filter(whosfriend=user))
        for myfriend in myfriends:
            my=User.objects.get(id=myfriend.user.id)
            all_my_friend_post=FriendCircle.objects.filter(user=my)
            for post in all_my_friend_post:
                all_posts.append(post)
        #按照时间顺序降序

        try:
            for i in all_posts:
                print(i.created_time)
            sorted(all_posts,key=attrgetter("created_time"),reverse=False)
        except Exception as e:
            print(e)
        i=1
        for post in all_posts:
            postname="post"+str(i)
            j = 1
            i=i+1

            postins={}
            postins["content"]=post.content
            postins["postid"] = post.id
            postins["userid_p"] =post.user.id
            postins["like_count"] = post.like_count
            postins["created_time"]=post.created_time
            postins["title"]=post.title
            imgs=Picture.objects.filter(post=post)
            arr_img=[]
            for i in range(len(imgs)):
                arr_img.append(imgs[i].img_url)
            postins["imgurls"]=arr_img
            # 获取发布者的昵称
            user = User.objects.get(id=post.user.id)
            stu_profile = list(User_Profile_Stu.objects.filter(user=user))
            c_profile = list(User_Profile_Company.objects.filter(user=user))
            g_profile = list(User_Profile_Graduate.objects.filter(user=user))
            if len(stu_profile) > 0:
                postins["postername"] = stu_profile[0].name
            if len(c_profile) > 0:
                postins["postername"] = c_profile[0].name
            if len(g_profile) > 0:
                postins["postername"] = g_profile[0].name
            # 获取发布者的头像
            try:
                user = User.objects.get(id=post.user.id)
            except Exception as e:
                print(e)
            img = list(ImageProfile.objects.filter(user=user))
            if len(img) > 0:
                postins["userimg"] = img[0].imgurl
            response["allpost"].append(postins)
        return JsonResponse(response)


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
        sendername = dic["username"]

        to_which_post = FriendCircle.objects.get(id=req["postid"])
        to_which_user = None
        try:
            touserid = req.get("receiverid", None)
            if touserid != '':
                # 回复评论的id
                to_which_user = User.objects.get(id=req["receiverid"])
            user = User.objects.get(username=sendername)
            content = req["content"]
            comment = Comment(user=user, content=content, to_which_user=to_which_user, to_which_post=to_which_post)
            comment.save()
            response["commentid"] = comment.id
        except Exception as e:
            response["msg"] = "false"
        return JsonResponse(response)

#点赞
@csrf_exempt
def add_likecount(request):
    if(request.method=="POST"):
        response={}
        req=simplejson.loads(request.body)
        postid=req["post_id"]
        post_lostf=FriendCircle.objects.get(id=postid)
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
                post=FriendCircle(user=user,title=title,content=content,like_count=0)
                post.save()
                for i in range(len(imgurls)):
                    img=Picture(img_url=imgurls[i],post=post)
                    img.save()
                response["msg"]="true"
                response["post_lostf_id"]=post.id
            except Exception as e:
                response["msg"]=e
                print(e)
        else:
            response["msg"]="false"
        return JsonResponse(response)

#获取帖子的评论
@csrf_exempt
def getpostcomment(request):
    response={}
    response["msg"]="true"
    if request.method=="POST":
        req=simplejson.loads(request.body)
        postid=req["postid"]
        post=FriendCircle.objects.get(id=postid)
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
            if comment.to_which_user is not None:
                user = User.objects.get(id=comment.to_which_user.id)
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
