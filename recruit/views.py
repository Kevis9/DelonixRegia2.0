
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import RecruitPost # Picture,Comment
from django.http import JsonResponse
from django.conf import settings
import simplejson
from django.core.cache import cache
#注意导入这个应用的时候
from user.models import User_Profile_Graduate,User_Profile_Stu,User_Profile_Company
from django.forms.models import model_to_dict
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
        try:
            user=User.objects.get(username=username)
            post=RecruitPost(user=user)
            del(req["sessionid"])
            post.update(**req)
            post.save()
            response["msg"]="true"
            response["post_id"]=post.id
            response["post_time"]=post.time_lab
        except Exception as e:
            response["msg"]="false"
            print(e)
            return JsonResponse(response)
        return JsonResponse(response)
    else:
        return JsonResponse({"msg":"WM"})

# #发布评论
# @csrf_exempt
# def uploadcomment(request):
#     if(request.method=="POST"):
#         response = {"msg":"true"}
#         req=simplejson.loads(request.body)
#         to_which_post=RecruitPost.objects.get(id=req["postid"])
#         to_which_user=None
#         try:
#             touserid=req.get("touserid",None)
#             if touserid is not None:
#                 # 回复评论的id
#                 to_which_user = User.objects.get(id=req["receiverid"])
#             user=User.objects.get(id=req["senderid"])
#             content=req["content"]
#             comment=Comment(user=user,content=content,to_which_user=to_which_user,to_which_post=to_which_post)
#             comment.save()
#         except Exception as e:
#             response["msg"]="false"
#         return JsonResponse(response)

@csrf_exempt
#获取所有帖子的信息
def getpost(request):
    if(request.method=="POST"):
        req=simplejson.loads(request.body)
        response={}
        response["msg"]="true"
        dic=cache.get(req["sessionid"])
        if dic is None:
            return JsonResponse({"msg":"false"})
        posts=list(RecruitPost.objects.all().order_by("-time_lab"))
        response["allposts"]=[]
        try:
            for post in posts:
               #time_lab对于auto_now字段好像无效
               dic=model_to_dict(post)
               #获取发布者(企业)的昵称和头像
               user=User.objects.get(id=post.user.id)
               com_profile=User_Profile_Company.objects.get(user=user)
               dic["name_lab"]=com_profile.name
               dic["img_url"]=com_profile.imgurl
               dic["time_lab"]=post.time_lab
               dic["cid"]=user.id
               response["allposts"].append(dic)
        except Exception as e:
            print(e)
            return JsonResponse({"msg":"false"})
        return JsonResponse(response)
    else:
        return JsonResponse({"msg":"WM"})

#
# #点赞
# @csrf_exempt
# def add_likecount(request):
#     if(request.method=="POST"):
#         response={}
#         req=simplejson.loads(request.body)
#         postid=req["post_id"]
#         post_lostf=RecruitPost.objects.get(id=postid)
#         post_lostf.like_count+=1
#         post_lostf.save()
#         response["msg"] = "true"
#         return JsonResponse(response)









