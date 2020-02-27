#!/usr/bin/python
#coding=utf-8
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.db.models.signals import post_init,post_save
from django.dispatch import receiver

#用户的身份
user_identity= (
        ('1', '毕业生'),
        ('2', '在校生'),
        ('3', '企业账号'),
        ('4', '管理员')
    )

class USER(AbstractUser):
    identity = models.CharField('用户身份',choices=user_identity,max_length=128,default="1")
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
    def __str__(self):
        return "{}".format(self.username)
    def get_absolute_url(self):
        return reverse('用户', args=[self.id])

#消息类
class Message(models.Model):
    msgfrom=models.ForeignKey(USER,verbose_name="发信人",on_delete=models.CASCADE,related_name="mysendmsg")
    msgto=models.ForeignKey(USER,verbose_name="收信人",on_delete=models.CASCADE,related_name="myreceivemsg")
    text=models.CharField("文本内容",max_length=200,null=False)
    headline=models.CharField("文本内容",max_length=200,null=False)
    class Meta:
        verbose_name = '消息表'
        verbose_name_plural = verbose_name
    def __str__(self):
        return "{}".format(self.msgfrom)
    def get_absolute_url(self):
        return reverse('工作经历', args=[self.msgfrom])

#职业经历
class JobExperience(models.Model):
    #user作为外键
    user=models.ForeignKey(USER,verbose_name="用户",on_delete=models.CASCADE,related_name="myjobexp",null=True)
    job_place = models.CharField("工作单位", max_length=128, null=True)
    job = models.CharField("职业",max_length=128,null=True)
    job_period_start=models.DateField("就职时间",null=True)
    job_period_end=models.DateField("离职时间",null=True)
    job_city = models.CharField("工作城市", max_length=128, null=True)
    job_salary=models.CharField("年薪", max_length=128,null=True)
    job_province=models.CharField("省份", max_length=128,null=True)
    class Meta:
        verbose_name = '工作经历'
        verbose_name_plural = verbose_name
    def __str__(self):
        return "{}".format(self.user)
    def get_absolute_url(self):
        return reverse('工作经历', args=[self.user.id])

#好友列表
#可以认为这个Friend是一个friendship,相当于一条有向线,改为关注
class Friends(models.Model):
    #朋友的id是唯一的，对应于一个User，一个User也相当于一个朋友
    user=models.OneToOneField(USER,verbose_name="朋友的id",on_delete=models.CASCADE,related_name="fid",null=True)
    #一个User同时也有多个friends
    followedby=models.ManyToManyField(USER, verbose_name="谁的朋友",related_name="myfollows",null=True)
    class Meta:
        verbose_name = '关注对象表'
        verbose_name_plural = verbose_name
    def __str__(self):
        return "{}".format(self.user)
    def get_absolute_url(self):
        return reverse('关注对象表', args=[self.user.id])


class EducationExperience(models.Model):
    user=models.ForeignKey(USER, verbose_name="用户教育经历", on_delete=models.CASCADE, related_name="myeducationexp",null=True)
    startime=models.DateField("教育开始时间",null=True)
    endtime = models.DateField("教育结束时间", null=True)
    school=models.CharField("学校",max_length=128,null=True)
    major=models.CharField("专业",max_length=128,null=True)
    educationbackground=models.CharField("教育背景",max_length=128,null=True)
    class Meta:
        verbose_name = '教育经历'
        verbose_name_plural = verbose_name
    def __str__(self):
        return "{}".format(self.user)
    def get_absolute_url(self):
        return reverse('教育经历', args=[self.user.id])


#毕业生
class User_Profile_Graduate(models.Model):
    #user作为主键
    user = models.OneToOneField(USER,on_delete=models.CASCADE,primary_key=True)
    education_backgroud_choices=(
        ('U','本科生'),
        ('M','硕士'),
        ('P','博士'),
    )
    #基本信息
    identity=models.CharField("用户身份",max_length=128,choices=user_identity,default='1')
    imgurl = models.CharField("头像url", max_length=1000, null=True)
    phonenum=models.CharField('电话号码', max_length=128, null=True)
    name=models.CharField('姓名', max_length=128,null=True)
    gender = models.SmallIntegerField(verbose_name='性别',null=True)      #0 for male . 1 for female
    major = models.CharField("专业", max_length=128,null=True)
    email = models.EmailField("邮件",max_length=128,null=True)
    birth_date=models.DateField("出生日期", null=True)
    # education_background=models.CharField("学历",max_length=128,choices=education_backgroud_choices,null=True)
    # university=models.CharField("所在学校", max_length=128,null=True)
    #对于城市这一块要搞一个城市的选择器
    # living_city = models.CharField("居住城市", max_length=128,null=True)
    # living_province= models.DateField("居住省份",max_length=128,null=True)
    # 时间选择
    admission_date = models.DateField("入校时间", null=True)
    graduate_date = models.DateField("毕业时间", null=True)
    # honour=models.TextField("荣誉",max_length=1000,null=True)
    # self_judgement=models.TextField("自我评价",max_length=1000,null=True)
    stunum = models.CharField("学号",max_length=15,null=True)
    institute = models.CharField("学院",max_length=20,null=True)
    gpa = models.FloatField("gpa总评",null=True)
    coin = models.IntegerField('硬币',null=True)       #积分硬币
    #下面都是模型的元数据设置,方便管理
    class Meta:
        verbose_name = "毕业生信息"
        verbose_name_plural = verbose_name
    def __str__(self):
        return "{}".format(self.user)

    def get_absolute_url(self):
        return reverse('get_profile_graduate', args=[self.user.id])
        #但是推荐用上面的


#在校生
class User_Profile_Stu(models.Model):
    user = models.OneToOneField(USER,on_delete=models.CASCADE, related_name='mystuprofile')
    male_choices = (
        ('M', '男'),
        ('F', '女')
    )
    education_backgroud_choices = (
        ('U', '本科生'),
        ('M', '硕士'),
        ('P', '博士'),
    )
    education_background = models.CharField("学历", max_length=128, choices=education_backgroud_choices, null=True,
                                                blank=True)
    university = models.CharField("所在学校", max_length=128, null=True)
    imgurl = models.CharField("头像url", max_length=1000, null=True)
    living_province = models.CharField("居住省份", max_length=128, null=True)
    living_city = models.CharField("居住城市", max_length=128, null=True)
    # identity=models.CharField("用户身份",max_length=128,choices=user_identity,default='2')
    phonenumber=models.CharField('电话号码', max_length=128,null=True)
    name=models.CharField('姓名', max_length=128,null=True)
    gender = models.CharField('性别', max_length=128,choices=male_choices,null=True)
    age = models.CharField("年龄", max_length=128,null=True)
    major = models.CharField("专业", max_length=128,null=True)
    email = models.EmailField("邮件",max_length=128,null=True)
    birth_data=models.DateField("出生日期",null=True)
    institution=models.CharField("学院",max_length=128,null=True)
    self_sign=models.CharField("个性签名",max_length=128,null=True)
    self_judgement=models.TextField("自我评价",null=True)
    class Meta:
        verbose_name = '在校生个人信息'
        verbose_name_plural = verbose_name
    def __str__(self):
        return "{}".format(self.user)

    def get_absolute_url(self):
        return reverse('get_profile_stu', args=[self.user.id])

#企业
class User_Profile_Company(models.Model):
    user = models.OneToOneField(USER, on_delete=models.CASCADE)
    imgurl = models.CharField("头像url", max_length=1000, null=True)
    identity = models.CharField("用户身份", max_length=128, choices=user_identity, default='3')
    phonenumber = models.CharField('电话号码', max_length=128, null=True)
    name = models.CharField('公司名', max_length=128, null=True)
    email = models.EmailField("邮件", max_length=128, null=True)
    class Meta:
        verbose_name = '企业信息'
        verbose_name_plural = verbose_name
    def __str__(self):
        return "{}".format(self.user)

#管理员信息
class User_Admin(models.Model):
    user = models.OneToOneField(USER,on_delete=models.CASCADE)
    email = models.EmailField("邮件", max_length=128, null=True)
    name = models.CharField('管理员名称', max_length=128, null=True)
    class Meta:
        verbose_name = '管理员信息'
        verbose_name_plural = verbose_name
    def __str__(self):
        return "{}".format(self.name)
    def get_absolute_url(self):
        return reverse('用户', args=[self.id])

#毕业生个人的简历
class Graduate_Resume(models.Model):
    user=models.ForeignKey(USER,on_delete=models.CASCADE,related_name="myresume",verbose_name="毕业生的简历")
    url=models.CharField("简历所在的路径",max_length=200,null=False)
    name=models.CharField("简历的名字",max_length=50,null=False)
    class Meta:
        verbose_name = '毕业生简历表'
        verbose_name_plural = verbose_name
    def __str__(self):
        return "{}".format(self.user)

#企业用户收到的简历表
class Company_Resume(models.Model):
    user = models.ForeignKey(USER, on_delete=models.CASCADE, related_name="resumefrom",verbose_name="毕业生的简历")
    company=models.ForeignKey(USER,on_delete=models.CASCADE,related_name="resumeto",verbose_name="投递到的公司")
    url = models.CharField("简历所在的路径", max_length=200, null=False)
    name = models.CharField("简历的名字", max_length=50, null=False)
    class Meta:
        verbose_name = '企业用户简历表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.user)


#利用django的signal机制实现类似触发器的效果
#创建好了用户后，自动创建用户的profile
@receiver(post_save,sender=USER)
def create_profile(sender,**kwargs):
    user = kwargs["instance"]
    g_name = user.identity
    if g_name == "4":
        profile = User_Admin(user=user)
        profile.save()
    if g_name == "1":
        profile = User_Profile_Graduate(user=user)
        profile.save()
    if g_name == "3":
        profile = User_Profile_Company(user=user)
        profile.save()