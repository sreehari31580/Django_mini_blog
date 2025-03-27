from django.contrib import admin
from .models import BlogAuthor, BlogPost, Comment

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'post_date')
    inlines = [CommentInline]

@admin.register(BlogAuthor)
class BlogAuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('blog_post', 'author', 'post_date', 'get_description')
    
    def get_description(self, obj):
        return obj.description[:75] + '...' if len(obj.description) > 75 else obj.description
    
    get_description.short_description = 'Description' 