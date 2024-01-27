from django.contrib import admin
from django.urls import path,include
from .import views
urlpatterns = [
    path('',views.home,name="Home"),
    path('sign-up/',views.Create_account,name="Create user"),
    path('login-user/',views.Login_hand,name="Login user"),
    path('logout-user/',views.Logout_hand,name="Logout user"),
    path('post-blogs/',views.Show_post_blogs,name="Blogs"),
    path('post-blogs/<str:filterOrder>',views.Show_post_blogs,name="Blogs"),
    path('create-post/',views.Create_post,name="Create Post"),
    path('post-blogs/<int:id>/',views.Read_post,name="Blog post"),
    path('post-comment/',views.post_comment,name="Post Comment"),
]