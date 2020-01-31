from django.contrib import admin
from .models import Comment,FriendPost,Picture
# Register your models here.

admin.site.register(Comment)
admin.site.register(FriendPost)
admin.site.register(Picture)
