from django.contrib import admin

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import JobExperience,\
    User_Profile_Graduate,\
    User_Profile_Stu,\
    User_Profile_Company,\
    EduExperience,\
    Friends,Message,Company_Resume,Graduate_Resume,User_Admin,USER


class USERAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (('Identity'), {'fields': ('identity',)}),
    )
    add_fieldsets = (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2','identity'),
        }),

# Register your models here.
admin.site.register(JobExperience)
admin.site.register(User_Profile_Graduate)
admin.site.register(User_Profile_Stu)
admin.site.register(User_Profile_Company)
admin.site.register(EduExperience)
admin.site.register(Friends)
admin.site.register(Message)
admin.site.register(Company_Resume)
admin.site.register(Graduate_Resume)
admin.site.register(User_Admin)
admin.site.register(USER,USERAdmin)




