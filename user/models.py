#!/usr/bin/python
# coding=utf-8
# import os

# import django
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


# os.environ.setdefault('DJANGO_SETTING_MODULE', 'delonixregia.settings')
# django.setup()

# 消息类
class Message(models.Model):
    msgfrom = models.ForeignKey(User, verbose_name="发信人", on_delete=models.CASCADE, related_name="mysendmsg")
    msgto = models.ForeignKey(User, verbose_name="收信人", on_delete=models.CASCADE, related_name="myreceivemsg")
    text = models.CharField("文本内容", max_length=200, null=False)
    headline = models.CharField("文本内容", max_length=200, null=False)

    class Meta:
        verbose_name = '消息表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.msgfrom)

    def get_absolute_url(self):
        return reverse('工作经历', args=[self.msgfrom])


# 职业经历
class JobExperience(models.Model):
    # user作为外键
    user = models.ForeignKey(User, verbose_name="用户", on_delete=models.CASCADE, related_name="myjobexp", null=True,
                             blank=True)
    job_place = models.CharField("工作单位", max_length=128, null=True, blank=True)
    job = models.CharField("职业", max_length=128, null=True, blank=True)
    job_period_start = models.DateField("就职时间", null=True, blank=True)
    job_period_end = models.DateField("离职时间", null=True, blank=True)
    job_city = models.CharField("工作城市", max_length=128, null=True, blank=True)
    job_salary = models.CharField("年薪", max_length=128, null=True, blank=True)
    job_province = models.CharField("省份", max_length=128, null=True, blank=True)

    class Meta:
        verbose_name = '工作经历'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.user)

    def get_absolute_url(self):
        return reverse('工作经历', args=[self.user.id])


# 好友列表
# 可以认为这个Friend是一个friendship,相当于一条有向线,改为关注
class Friends(models.Model):
    # 朋友的id是唯一的，对应于一个User，一个User也相当于一个朋友
    user = models.OneToOneField(User, verbose_name="朋友的id", on_delete=models.CASCADE, related_name="fid", blank=True,
                                null=True)
    # 一个User同时也有多个friends
    followedby = models.ManyToManyField(User, verbose_name="谁的朋友", related_name="myfollows", null=True)

    class Meta:
        verbose_name = '关注对象表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.user)

    def get_absolute_url(self):
        return reverse('关注对象表', args=[self.user.id])


class EducationExperience(models.Model):
    user = models.ForeignKey(User, verbose_name="用户教育经历", on_delete=models.CASCADE, related_name="myeducationexp",
                             null=True, blank=True)
    startime = models.DateField("教育开始时间", null=True, blank=True)
    endtime = models.DateField("教育结束时间", null=True, blank=True)
    school = models.CharField("学校", max_length=128, null=True, blank=True)
    major = models.CharField("专业", max_length=128, null=True, blank=True)
    educationbackground = models.CharField("教育背景", max_length=128, null=True, blank=True)

    class Meta:
        verbose_name = '教育经历'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.user)

    def get_absolute_url(self):
        return reverse('教育经历', args=[self.user.id])


# 毕业生
class User_Profile_Graduate(models.Model):
    # user作为主键
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mygraduateproflie')
    # # 一个毕业生有多个深造表
    # furduform = models.ForeignKey('FurtherEducation', on_delete=models.CASCADE, blank=True, null=True,
    #                               related_name='FurtherEducationform')
    # # 一个毕业生有多个就业表
    # emplfrom = models.ForeignKey('Employment', on_delete=models.CASCADE, blank=True, null=True,
    #                              related_name='Employmentform')
    # 用uid表示
    male_choices = (
        ('M', '男'),
        ('F', '女')
    )
    education_backgroud_choices = (
        ('U', '本科生'),
        ('M', '硕士'),
        ('P', '博士'),
    )
    user_identity = (
        ('1', '毕业生'),
        ('2', '在校生'),
        ('3', '企业账号'),
    )
    # 基本信息
    identity = models.CharField("用户身份", max_length=128, choices=user_identity, default='1')
    imgurl = models.CharField("头像url", max_length=1000, null=True, blank=True)
    phonenum = models.CharField('电话号码', max_length=128, null=True, blank=True)
    name = models.CharField('姓名', max_length=128, null=True, blank=True)
    gender = models.CharField('性别', max_length=128, choices=male_choices, null=True, blank=True)
    # age = models.CharField("年龄", max_length=128,null=True,blank=True)
    major = models.CharField("专业", max_length=128, null=True, blank=True)
    email = models.EmailField("邮件", max_length=128, null=True, blank=True)
    birth_date = models.DateField("出生日期", null=True, blank=True)
    # education_background=models.CharField("学历",max_length=128,choices=education_backgroud_choices,null=True,blank=True)
    # university=models.CharField("所在学校", max_length=128,null=True,blank=True)
    # 对于城市这一块要搞一个城市的选择器
    # living_city = models.CharField("居住城市", max_length=128,null=True,blank=True)
    # living_province= models.DateField("居住省份",max_length=128,null=True,blank=True)
    # 时间选择
    admission_date = models.DateField("入校时间", null=True, blank=True)
    graduate_date = models.DateField("毕业时间", null=True, blank=True)
    # honour=models.TextField("荣誉",max_length=1000,null=True, blank=True)
    # self_judgement=models.TextField("自我评价",max_length=1000,null=True, blank=True)
    stunum = models.CharField("学号", max_length=15, null=True, blank=True)
    institute = models.CharField("学院", max_length=20, null=True, blank=True)
    gpa = models.FloatField("gpa总评", null=True, blank=True)
    coin = models.IntegerField(null=True, blank=False)  # 积分硬币

    # 下面都是模型的元数据设置,方便管理
    class Meta:
        verbose_name = "毕业生信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.user)

    def get_absolute_url(self):
        return reverse('get_profile_graduate', args=[self.user.id])
        # 但是推荐用上面的


# 毕业生的深造表
class FurtherEducation(models.Model):
    uid = models.IntegerField("唯一标识", null=True, blank=True)
    # primary_key=True implies blank=False ,null=False and unique=True
    # 深造国家筛选的时候只有两类：中国和其他国家
    country = models.CharField("深造的国家", max_length=20, null=True, blank=True)
    major = models.CharField("深造的专业", max_length=20, null=True, blank=True)
    uvty_name = models.CharField("深造的学校的名称", max_length=20, null=True, blank=True)
    # FurEdu_time = models.DateField("深造的时间", max_length=128, null=True, blank=True)#以年为单位
    admission_date = models.IntegerField("深造的时间",null=True, blank=True)  # 以年为单位

    class Meta:
        verbose_name = '毕业生简历表'


# 毕业生就业表
class Employment(models.Model):
    uid = models.IntegerField("唯一标识", null=True, blank=True)
    salary = models.FloatField("月薪", null=True, blank=True)
    major_professional = models.BooleanField("专业对口", null=True, blank=True)
    istop500 = models.BooleanField("500强企业", null=True, blank=True)
    company_name = models.CharField("企业名称", max_length=30, null=True, blank=True)
    country = models.CharField("就业国家", max_length=20, null=True, blank=True)
    province = models.CharField("就业省份", max_length=20, null=True, blank=True)
    city = models.CharField("就业城市", max_length=20, null=True, blank=True)
    birth_data = models.IntegerField("就业时间", blank=True)


# 在校生
class User_Profile_Stu(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mystuprofile')
    male_choices = (
        ('M', '男'),
        ('F', '女')
    )
    # user_identity = (
    #     ('1', '毕业生'),
    #     ('2', '管理员'),
    #     ('3', '企业账号'),
    # )
    education_backgroud_choices = (
        ('U', '本科生'),
        ('M', '硕士'),
        ('P', '博士'),
    )
    education_background = models.CharField("学历", max_length=128, choices=education_backgroud_choices, null=True,
                                            blank=True)
    university = models.CharField("所在学校", max_length=128, null=True, blank=True)
    imgurl = models.CharField("头像url", max_length=1000, null=True, blank=True)
    living_province = models.CharField("居住省份", max_length=128, null=True, blank=True)
    living_city = models.CharField("居住城市", max_length=128, null=True, blank=True)
    # identity=models.CharField("用户身份",max_length=128,choices=user_identity,default='2')
    phonenumber = models.CharField('电话号码', max_length=128, null=True, blank=True)
    name = models.CharField('姓名', max_length=128, null=True, blank=True)
    gender = models.CharField('性别', max_length=128, choices=male_choices, null=True, blank=True)
    age = models.CharField("年龄", max_length=128, null=True, blank=True)
    major = models.CharField("专业", max_length=128, null=True, blank=True)
    email = models.EmailField("邮件", max_length=128, null=True, blank=True)
    birth_data = models.DateField("出生日期", null=True, blank=True)
    institution = models.CharField("学院", max_length=128, null=True, blank=True)
    self_sign = models.CharField("个性签名", max_length=128, null=True, blank=True)
    self_judgement = models.TextField("自我评价", null=True, blank=True)

    class Meta:
        verbose_name = '在校生个人信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.user)

    def get_absolute_url(self):
        return reverse('get_profile_stu', args=[self.user.id])


# 企业
class User_Profile_Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mycompanyprofile')
    user_identity = (
        ('1', '毕业生'),
        ('2', '在校生'),
        ('3', '企业账号'),
    )
    imgurl = models.CharField("头像url", max_length=1000, null=True, blank=True)
    identity = models.CharField("用户身份", max_length=128, choices=user_identity, default='3')
    phonenumber = models.CharField('电话号码', max_length=128, null=True, blank=True)
    name = models.CharField('公司名', max_length=128, null=True, blank=True)
    email = models.EmailField("邮件", max_length=128, null=True, blank=True)

    class Meta:
        verbose_name = '企业个人信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.user)


# 毕业生个人的简历
class Graduate_Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="myresume", verbose_name="毕业生的简历")
    url = models.CharField("简历所在的路径", max_length=200, null=False)
    name = models.CharField("简历的名字", max_length=50, null=False)

    class Meta:
        verbose_name = '毕业生简历表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.user)


# 企业用户收到的简历表
class Company_Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="resumefrom", verbose_name="毕业生的简历")
    company = models.ForeignKey(User, on_delete=models.CASCADE, related_name="resumeto", verbose_name="投递到的公司")
    url = models.CharField("简历所在的路径", max_length=200, null=False)
    name = models.CharField("简历的名字", max_length=50, null=False)

    class Meta:
        verbose_name = '企业用户简历表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.user)
