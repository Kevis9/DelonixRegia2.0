from django.contrib import admin

from django.contrib import admin
from .models import JobExperience,\
    User_Profile_Graduate,\
    User_Profile_Stu,\
    User_Profile_Company,\
    EducationExperience,\
    Friends,Message,Company_Resume,Graduate_Resume


# Register your models here.
admin.site.register(JobExperience)
admin.site.register(User_Profile_Graduate)
admin.site.register(User_Profile_Stu)
admin.site.register(User_Profile_Company)
admin.site.register(EducationExperience)
admin.site.register(Friends)
admin.site.register(Message)
admin.site.register(Company_Resume)
admin.site.register(Graduate_Resume)



