from django.core.management.base import BaseCommand, CommandError

from django.core.management.base import BaseCommand, CommandError
from user.models import User_Profile_Graduate
from django.contrib.auth.models import User
from user.models import FurtherEducation,Employment
import random


class Command(BaseCommand):
    help = '向指定数据库累添加数据'

    # 每一个自定义的命令，都要自己实现handle()
    # 方法，这个方法是命令的核心业务处理代码，你的命令功能要通过它来实现。而add_arguments()
    # 则用于帮助处理命令行的参数，如果没有参数，可以不写这个方法。
    def add_arguments(self, parser):
        parser.add_argument('intergers', nargs='+', type=int)

    def handle(self, *args, **options):
        word_range = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz1234567890'
        schoollist = ['哈佛大学', '牛津大学', '麻省理工学院', '斯坦福大学', '哈佛大学', '牛津大学', '加州理工学院', '清华大学', '深圳大学', '清华大学']
        countrylist = ['美国', '英国', '美国', '美国', '美国', '英国', '美国', '中国', '中国', '中国']
        majorlist = ['软件工程', '信息安全', '网络工程', '微电子学', '计算机科学与技术', '土木工程', '建筑学', '车辆工程', '软件工程', '土木工程']
        institute = ['工学院', '理学院']
        salary=[1,2,3,4,5,6,7,8,9,10]
        companyname=['沃尔玛','中国石油','国家电网','英国石油','大众公司','苹果公司','沃尔玛','中国石油','国家电网','英国石油','大众公司','苹果公司']
        for i in range(0, 10):
            six_letter_1 = random.sample(word_range, 6)  # 这里得到的应该是一个序列而不是6个字符串
            six_letter_2 = ''.join(six_letter_1)  # 把六个得到的随机字符连接起来
            u1 = User.objects.create_user(username=six_letter_2, password='123456')
            u1.save()
            fe1 = FurtherEducation.objects.create(uid=u1.id, major=majorlist[i], country=countrylist[i],
                                                  uvty_name=schoollist[i])
            fe1.save()
            ep = Employment.objects.create(uid=u1.id, salary=salary[i], istop500=True, company_name=companyname[i])
            ep.save()
            upg1 = User_Profile_Graduate.objects.create(user=u1, institute=institute[i % 2], major=majorlist[i])
            upg1.save()
# 没有表
        u1 = User.objects.create_user(username='777', password='123456')
        u1.save()
        upg1 = User_Profile_Graduate.objects.create(user=u1)
        u1 = User.objects.create_user(username='888', password='123456')
        u1.save()
        upg1 = User_Profile_Graduate.objects.create(user=u1)
        u1 = User.objects.create_user(username='999', password='123456')
        u1.save()
        upg1 = User_Profile_Graduate.objects.create(user=u1)
#有两张表
        u1 = User.objects.create_user(username='1010', password='123456')
        u1.save()
        fe11 = FurtherEducation.objects.create(uid=u1.id, major=majorlist[0], country=countrylist[i],
                                               uvty_name=schoollist[0])
        fe11 = FurtherEducation.objects.create(uid=u1.id, major=majorlist[0], country=countrylist[i],
                                               uvty_name=schoollist[1])
        upg1 = User_Profile_Graduate.objects.create(user=u1, institute=institute[0], major=majorlist[0])

    # self.stdout.write(upg1.FurEduForm.major)

    # 在manage.py目录下运行python manage.py adddata 1
