from django.contrib import admin
from .models import CustomUser,Course ,UserProfile


admin.site.register(Course)
admin.site.register(UserProfile)
admin.site.register(CustomUser)