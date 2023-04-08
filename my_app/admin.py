from django.contrib import admin
from django.db import models
from .models import Post, Comment
from django_summernote.admin import SummernoteModelAdmin
from datetime import datetime

@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):

    list_display = ('title', 'slug', 'status', 'created_on')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('status', 'published_on')
    summernote_fields = ('content',)
    actions = ['publish_posts']

    def publish_posts(self, request, queryset):
        queryset.update(status=2)
        queryset.update(published_on=datetime.utcnow())


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):

    list_display = ('name', 'body', 'post', 'created_on', 'approved')
    list_filter = ('approved', 'created_on')
    search_fields = ('name', 'email', 'body')
    actions = ['approve_comments']  

    def approve_comments(self, request, queryset):
        queryset.update(approved=True)
