from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Image, Comment, Like
# Register your models here.

@admin.register(Image)
class Image_Admin(admin.ModelAdmin):
    list_display_links = (
        'location',
    )

    list_display = (
        'id',
        'file',
        'location',
        'caption',
        'creator',
        'created_at',
        'updated_at'
    )

@admin.register(Comment)
class Comment_Admin(admin.ModelAdmin):
    pass

@admin.register(Like)
class Like_Admin(admin.ModelAdmin):

    list_display = (
        'creator',
        'image',
    )
