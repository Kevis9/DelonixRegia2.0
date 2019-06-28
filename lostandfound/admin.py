from django.contrib import admin
from .models import LostandFound,Comment,Picture

# Register your models here.
admin.site.register(LostandFound)
admin.site.register(Comment)
admin.site.register(Picture)
