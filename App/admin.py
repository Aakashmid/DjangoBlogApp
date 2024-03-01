from django.contrib import admin
from .models import Post,Comment,PostLike,CommentLike,BlogUser,AuthorFollower,PostCategory,Tag
from django_summernote.admin import SummernoteModelAdmin
from django.contrib.admin import AdminSite
from .models import User
# import django
# Register your models here.



class BlogAdminArea(admin.AdminSite):
    site_header="Blog admin area"
    site_title="Blog adminstrations | Admin panel"


# class postAdmin(admin.ModelAdmin):
    
blog_site=BlogAdminArea()

# class SummerAdmin(SummernoteModelAdmin):
#     summernote_fields='content'
    

# registering models
# blog_site.register(Post, SummerAdmin)
blog_site.register(Post)
blog_site.register(Comment)
blog_site.register(User)
blog_site.register(PostLike)
blog_site.register(CommentLike)
blog_site.register(BlogUser)
blog_site.register(AuthorFollower)
blog_site.register(PostCategory)
blog_site.register(Tag)
