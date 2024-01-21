from django.contrib import admin
from .models import Post,Comment
from django_summernote.admin import SummernoteModelAdmin
from django.contrib.admin import AdminSite
# Register your models here.


class BlogAdminArea(admin.AdminSite):
    site_header="Blog admin area"
    site_title="Blog adminstrations | Admin panel"

blog_site=BlogAdminArea()

class SummerAdmin(SummernoteModelAdmin):
    summernote_fields='content'
    
# blog_site.register(Post, SummerAdmin)
blog_site.register(Post)
blog_site.register(Comment)