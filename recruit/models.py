from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
'''
招聘信息发布
'''
# 帖子
class RecruitPost(models.Model):
    title = models.CharField(max_length=254,null=False,verbose_name="标题")
    user = models.ForeignKey(User, related_name='myrecruitpost', verbose_name='创建人', on_delete=models.CASCADE,null=False,)
    content = models.TextField(max_length=4000, verbose_name='帖子内容',null=False)
    time_lab = models.DateTimeField(auto_now_add=True,null=False)
    like_count = models.BigIntegerField("点赞数",default=0)
    detail_url = models.CharField(max_length=254,null=True,blank=True,verbose_name="公司链接")
    description = models.TextField(max_length=2000,null=False,blank=False,verbose_name="职位描述",default="")
    salary_lo = models.CharField(max_length=300,null=True,blank=True,verbose_name="最低薪水",default="")
    salary_hi= models.CharField(max_length=300,null=True,blank=True,verbose_name="最高薪水",default="")
    edu_require= models.TextField(max_length=2000,null=True,blank=True,verbose_name="学历要求",default="")
    exp_require=models.TextField(max_length=2000,null=True,blank=True,verbose_name="经历要求",default="")
    place = models.CharField(max_length=300,null=False,blank=False,verbose_name="地点",default="")
    want_num=models.CharField(max_length=300,null=False,blank=False,verbose_name="招聘人数",default="")
    class Meta:
        verbose_name = '招聘帖子'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.title)

    def get_absolute_url(self):
        return reverse('rpost', args=[self.user.id])


# # 评论
# class Comment(models.Model):
#     content = models.TextField(max_length=4000, verbose_name='评论内容')
#     # 父帖
#     post = models.ForeignKey(RecruitPost, on_delete=models.CASCADE, verbose_name="父帖", related_name="postcomments",blank=False)
#     # 父评论
#     to_which_user = models.ForeignKey(User, verbose_name="回复的人",related_name='recruitresponse',on_delete=models.DO_NOTHING,null=True)
#     user= models.ForeignKey(User, verbose_name='招聘评论者', related_name='myrecruitcomments', on_delete=models.CASCADE,null=False)
#     created_time = models.DateField(auto_now_add=True, null=False, verbose_name='创建时间')
#     class Meta:
#         verbose_name = '招聘评论'
#         verbose_name_plural = verbose_name
#
#     def __str__(self):
#         return "{}".format(self.content)
#
#     def get_absolute_url(self):
#         return reverse('rcommemt', args=[self.user.id])


# class Picture(models.Model):
#     post = models.ForeignKey(RecruitPost, on_delete=models.CASCADE, null=False,related_name="myimgs")
#     imgurl = models.CharField(max_length=1000, null=True, blank=True)
#     class Meta:
#         verbose_name = '招聘照片'
#         verbose_name_plural = verbose_name
#     def __str__(self):
#         return "{}".format(self.post)
#
#     def get_absolute_url(self):
#         return reverse('fimg', args=[self.post.id])


