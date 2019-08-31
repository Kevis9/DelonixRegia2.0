from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
'''
招聘信息发布
'''
# 帖子
class Recruit(models.Model):
    # objects = models.Manager()
    title = models.CharField(max_length=254,null=True,blank=True)  # 标题
    user = models.ForeignKey(User, related_name='招聘发帖者', verbose_name='创建人', on_delete=models.CASCADE,null=True,blank=True)
    content = models.TextField(max_length=4000, verbose_name=u'帖子内容',null=True,blank=True)
    created_time = models.DateTimeField(auto_now_add=True,null=True)
    like_count = models.BigIntegerField("点赞数", null=True, default=0)
    companylink = models.CharField(max_length=254,null=True,blank=True,verbose_name="公司链接")  # 链接

    # image
    class Meta:
        verbose_name = '招聘帖子'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.user)

    def get_absolute_url(self):
        return reverse('rpost', args=[self.user.id])


# 评论
class Comment(models.Model):
    content = models.TextField(max_length=4000, verbose_name='评论内容')
    # 父帖
    to_which_post = models.ForeignKey(Recruit,on_delete=models.CASCADE,null=True,blank=True)
    # 父评论
    to_which_user = models.ForeignKey(User, blank=True, related_name='招聘发送给谁的评论', on_delete=models.CASCADE,null=True)
    user= models.ForeignKey(User, related_name='招聘评论者', verbose_name='创建人', on_delete=models.CASCADE,null=True,blank=True)
    created_time = models.DateField(auto_now_add=True, null=True, verbose_name='创建时间')
    class Meta:
        verbose_name = '招聘评论'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.user)

    def get_absolute_url(self):
        return reverse('rcommemt', args=[self.user.id])


class Picture(models.Model):
    post = models.ForeignKey(Recruit, on_delete=models.CASCADE, null=True)
    imgurl = models.CharField(max_length=1000, null=True, blank=True)
    class Meta:
        verbose_name = '招聘照片'
        verbose_name_plural = verbose_name
    def __str__(self):
        return "{}".format(self.post)

    def get_absolute_url(self):
        return reverse('fimg', args=[self.post.id])

