from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

#职业经历
class jobexperience(models.Model):
    #user作为外键
    user=models.ForeignKey(User,verbose_name="用户",on_delete=models.CASCADE,related_name="user_jobexperiment",null=True,blank=True)
    job_place = models.CharField("工作单位", max_length=128, null=True, blank=True)
    job = models.CharField("职业",max_length=128,null=True,blank=True)
    job_period_start=models.DateField("就职时间",null=True, blank=True)
    job_period_end=models.DateField("离职时间",null=True, blank=True)
    job_city = models.CharField("工作城市", max_length=128, null=True, blank=True)
    job_salary=models.CharField("年薪", max_length=128,null=True,blank=True)
    job_province=models.CharField("省份", max_length=128,null=True,blank=True)
    class Meta:
        verbose_name = '工作经历'
        verbose_name_plural = verbose_name
    def __str__(self):
        return "{}".format(self.user)
    def get_absolute_url(self):
        return reverse('工作经历', args=[self.user.id])

#好友列表
class friends(models.Model):
    user=models.ForeignKey(User,verbose_name="朋友的id",on_delete=models.CASCADE,related_name="fuser",blank=True,null=True)
    whosfriend=models.ForeignKey(User,verbose_name="谁的朋友",on_delete=models.CASCADE,related_name="fwhosfriend",blank=True,null=True)
    is_friend=models.BooleanField("是否为好友",default=False)
    class Meta:
        verbose_name = '好友列表'
        verbose_name_plural = verbose_name
    def __str__(self):
        return "{}".format(self.user)
    def get_absolute_url(self):
        return reverse('好友列表', args=[self.user.id])

class educationexperice(models.Model):
    user=models.ForeignKey(User, verbose_name="用户教育经历", on_delete=models.CASCADE, related_name="user_educationexperience",null=True, blank=True)
    startime=models.DateField("教育开始时间",null=True,blank=True)
    endtime = models.DateField("教育结束时间", null=True, blank=True)
    school=models.CharField("学校",max_length=128,null=True,blank=True)
    major=models.CharField("专业",max_length=128,null=True,blank=True)
    educationbackground=models.CharField("教育背景",max_length=128,null=True,blank=True)
    class Meta:
        verbose_name = '教育经历'
        verbose_name_plural = verbose_name
    def __str__(self):
        return "{}".format(self.user)
    def get_absolute_url(self):
        return reverse('教育经历', args=[self.user.id])
#头像类
class imageprofile(models.Model):
    user = models.ForeignKey(User, verbose_name="用户头像", on_delete=models.CASCADE, related_name="user_imageprofile",null=True, blank=True)
    imgurl=models.CharField("头像路径",max_length=1000,null=True,blank=True)
    class Meta:
        verbose_name = '头像'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.user)

    def get_absolute_url(self):
        return reverse('头像', args=[self.user.id])
#毕业生
class user_profile_graduate(models.Model):
    #user作为主键
    user = models.OneToOneField(User,on_delete=models.CASCADE, related_name='user_profile_graduate',primary_key=True)
    male_choices=(
        ('M','男'),
        ('F','女')
    )

    education_backgroud_choices=(
        ('U','本科生'),
        ('M','硕士'),
        ('P','博士'),
    )
    user_identity=(
        ('1','毕业生'),
        ('2', '在校生'),
        ('3', '企业账号'),
    )
    #基本信息
    identity=models.CharField("用户身份",max_length=128,choices=user_identity,default='1')
    phonenumber=models.CharField('电话号码', max_length=128,null=True,blank=True)
    name=models.CharField('姓名', max_length=128,null=True,blank=True)
    gender = models.CharField('性别', max_length=128,choices=male_choices,null=True,blank=True)
    age = models.CharField("年龄", max_length=128,null=True,blank=True)
    major = models.CharField("专业", max_length=128,null=True,blank=True)
    email = models.EmailField("邮件",max_length=128,null=True,blank=True)
    birth_data=models.DateField("出生日期",null=True,blank=True)
    education_background=models.CharField("学历",max_length=128,choices=education_backgroud_choices,null=True,blank=True)
    university=models.CharField("所在学校", max_length=128,null=True,blank=True)
    #对于城市这一块要搞一个城市的选择器
    living_city = models.CharField("居住城市", max_length=128,null=True,blank=True)
    living_province= models.DateField("居住省份",max_length=128,null=True,blank=True)
    # 时间选择
    school_period_start = models.DateField("在校时间开始", null=True, blank=True)
    school_period_end = models.DateField("在校时间结束", null=True, blank=True)
    honour=models.TextField("荣誉",max_length=1000,null=True, blank=True)
    self_judgement=models.TextField("自我评价",max_length=1000,null=True, blank=True)

    #下面都是模型的元数据设置,方便管理
    class Meta:
        verbose_name = "毕业生个人信息"

    def __str__(self):
        return "{}".format(self.user)

    def get_absolute_url(self):

        return reverse('get_profile_graduate', args=[self.user.id])
        #但是推荐用上面的

#在校生
class user_profile_stu(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE, related_name='user_profile_stu',primary_key=True)
    male_choices = (
        ('M', '男'),
        ('F', '女')
    )
    user_identity = (
        ('1', '毕业生'),
        ('2', '在校生'),
        ('3', '企业账号'),
    )
    education_backgroud_choices = (
        ('U', '本科生'),
        ('M', '硕士'),
        ('P', '博士'),
    )
    education_background = models.CharField("学历", max_length=128, choices=education_backgroud_choices, null=True,
                                                blank=True)
    university = models.CharField("所在学校", max_length=128, null=True, blank=True)
    living_province = models.CharField("居住省份", max_length=128, null=True, blank=True)
    living_city = models.CharField("居住城市", max_length=128, null=True, blank=True)
    identity=models.CharField("用户身份",max_length=128,choices=user_identity,default='2')
    phonenumber=models.CharField('电话号码', max_length=128,null=True,blank=True)
    name=models.CharField('姓名', max_length=128,null=True,blank=True)
    gender = models.CharField('性别', max_length=128,choices=male_choices,null=True,blank=True)
    age = models.CharField("年龄", max_length=128,null=True,blank=True)
    major = models.CharField("专业", max_length=128,null=True,blank=True)
    email = models.EmailField("邮件",max_length=128,null=True,blank=True)
    birth_data=models.DateField("出生日期",null=True,blank=True)
    institution=models.CharField("学院",max_length=128,null=True,blank=True)
    self_sign=models.CharField("个性签名",max_length=128,null=True,blank=True)
    self_judgement=models.TextField("自我评价",null=True, blank=True)
    class Meta:
        verbose_name = '在校生个人信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}".format(self.user)

    def get_absolute_url(self):
        return reverse('get_profile_stu', args=[self.user.id])

#企业
class user_profile_company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile_company', primary_key=True)
    user_identity = (
        ('1', '毕业生'),
        ('2', '在校生'),
        ('3', '企业账号'),
    )
    identity = models.CharField("用户身份", max_length=128, choices=user_identity, default='3')
    phonenumber = models.CharField('电话号码', max_length=128, null=True, blank=True)
    name = models.CharField('公司名', max_length=128, null=True, blank=True)
    email = models.EmailField("邮件", max_length=128, null=True, blank=True)
    class Meta:
        verbose_name = '企业个人信息'
        verbose_name_plural = verbose_name
    def __str__(self):
        return "{}".format(self.user)

