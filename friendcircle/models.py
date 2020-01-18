
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

'''
朋友圈
'''
# 帖子
class FriendPost(models.Model):
    # objects = models.Manager()
    title = models.CharField("标题",max_length=254,null=False)  # 标题
    user = models.ForeignKey(User, related_name='myposts', verbose_name='创建人', on_delete=models.CASCADE,null=False)
    content = models.TextField(max_length=4000, verbose_name='帖子内容',null=False)
    created_time = models.DateTimeField(auto_now_add=True,null=False)
    like_count = models.BigIntegerField("点赞数", null=True, default=0)
    # image
    class Meta:
        verbose_name = '朋友圈帖子表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.title)

    def get_absolute_url(self):
        return reverse('fpost', args=[self.user.id])


# 评论
class Comment(models.Model):
    content = models.TextField(max_length=4000, verbose_name='评论内容')
    # 父帖
    post = models.ForeignKey(FriendPost, on_delete=models.CASCADE, null=False,verbose_name="父帖",related_name="postcomments")
    # 父评论
    to_which_user = models.ForeignKey(User,on_delete=models.DO_NOTHING,verbose_name="回复的人",related_name="responsecomment",null=False)
    user= models.ForeignKey(User,related_name='mycomments', verbose_name='创建人', on_delete=models.CASCADE,null=False)
    #auto_now_add 自动更新为创建时的时间,以后都不能再更改
    #auto_now 自动更新为最后一次修改的时间，不能手动修改
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')
    class Meta:
        verbose_name = '朋友圈评论表'
        verbose_name_plural = verbose_name
    def __str__(self):
        return "{}".format(self.content)
    def get_absolute_url(self):
        return reverse('fcommemt', args=[self.user.id])

#图片
class Picture(models.Model):
    post = models.ForeignKey(FriendPost,verbose_name="所在帖子", on_delete=models.CASCADE, null=False,related_name="myimgs")
    imgurl = models.CharField(verbose_name="图片链接",max_length=1000, null=False)
    class Meta:
        verbose_name = '朋友圈照片表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.post)

    def get_absolute_url(self):
        return reverse('fimg', args=[self.post.id])

