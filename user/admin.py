from django.contrib import admin

from django.contrib import admin
from .models import jobexperience,\
    user_profile_graduate,\
    user_profile_stu,\
    user_profile_company,\
    imageprofile,\
    educationexperice,\
    friends


# Register your models here.
admin.site.register(jobexperience)
admin.site.register(user_profile_graduate)
admin.site.register(user_profile_stu)
admin.site.register(user_profile_company)
admin.site.register(imageprofile)
admin.site.register(educationexperice)
admin.site.register(friends)

