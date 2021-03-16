from django.contrib import admin

from .models import UserSocial, Post, Emotion

admin.site.register(UserSocial)
admin.site.register(Post)
admin.site.register(Emotion)

