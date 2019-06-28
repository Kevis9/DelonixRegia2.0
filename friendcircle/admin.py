from django.contrib import admin
from .models import Comment,FriendCircle,Picture
# Register your models here.

admin.site.register(Comment)
admin.site.register(FriendCircle)
admin.site.register(Picture)
