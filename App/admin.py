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

# modelAdmin define how form of class is represented
# class postAdmin(admin.ModelAdmin):

blog_site=BlogAdminArea()
# class SummerAdmin(SummernoteModelAdmin):
#     summernote_fields='content'
    

# registering models
# blog_site.register(Post, SummerAdmin)
blog_site.register([Comment,User,AuthorFollower,PostCategory,CommentLike,PostLike,Tag])

@admin.register(Post,site=blog_site)
class PostAdmin(admin.ModelAdmin):
    search_fields=('author__user__first_name','author__user__last_name','author__user__username')
    list_display=['author','title','category','publish_time']
    list_filter=['publish_time','category','author']
    # def author_name(self,obj):
    #     return obj.author.first_name+" "+obj.author.last_name

@admin.register(BlogUser,site=blog_site)
class UserAdmin(admin.ModelAdmin):
    list_display=['Username','Full_Name','followers','following','bio']
    list_filter=('followers',)
    def Username(self,obj): #obj is Bloguser object
        return obj.user.username
    def Full_Name(self,obj):
        return obj.user.first_name+" "+obj.user.last_name
    def bio(self,obj):
        return obj.Bio[:50]+"..."