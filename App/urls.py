from django.contrib import admin
from django.urls import path,include
from .import views

app_name='App'
urlpatterns = [
    path('',views.home,name="Home"),
    path('',views.home,name="filter_posts"),
    path('sign-up/',views.Create_account,name="Create user"),
    path('login-user/',views.Login_hand,name="login_user"),
    path('logout-user/',views.Logout_hand,name="Logout user"),


    path('search/',views.SearchResult,name="Search Posts"),
    path('search/',views.SearchResult,name="Reading_list"),
    path('post-blogs/<str:filterOrder>',views.SearchResult,name="Blogs filter"),
    path('search/?category=<str:category>',views.SearchResult,name="Blogs By Category"),
    path('search/?tag=<str:tagName>/',views.SearchResult,name="Blogs by tag"),


    path('create-post/',views.Create_post,name="Create Post"),
    path('post-blogs/<int:id>/',views.Read_post,name="Blog Post"),
    path('post-comment/',views.post_comment,name="Post Comment"),
    path('profile/',views.profile,name="User Profile"),
    path('Author/profile/<int:user_id>/',views.profile,name="Author Profile"),
    path('profile/change-profile/',views.Change_profile,name="Profile Change"),
    path('profile/update-post/<int:post_id>',views.update_post,name="Update post"),
    path('<str:text>/<str:username>/<int:user_id>/',views.profile,name="Followers Following"),#<str:text>/<str:username>/<int:user_id>/
    # path('<str:username>/<int:user_id>/<str:text>/',views.profile,name="Followers Following"),#<str:text>/<str:username>/<int:user_id>/
]