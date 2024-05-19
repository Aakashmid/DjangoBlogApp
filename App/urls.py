

from django.contrib import admin
from django.urls import path
from . import views

app_name = 'App'

urlpatterns = [
    # Home page
    path('', views.home, name="Home"),
    path('', views.home, name="filter_posts"),
    
    # Authentication
    path('sign-up/', views.Create_account, name="Create user"),
    path('login-user/', views.Login_hand, name="login_user"),
    path('logout-user/', views.Logout_hand, name="Logout user"),
    
    # Search and filter
    path('search/', views.SearchResult, name="Search Posts"),
    path('readinglist/', views.SearchResult, name="Reading_list"),

    #-------------have to modify----------------
    # path('post-blogs/<str:filterOrder>/', views.SearchResult, name="Blogs filter"),
    path('search/category/<str:category>/', views.SearchResult, name="Blogs By Category"),
    path('search/tag/<str:tagName>/', views.SearchResult, name="Blogs by tag"),
    # ----------------------------

    # Post-related
    path('new-post/', views.Create_post, name="Create Post"),
    path('<str:author_username>/<str:slug>/', views.detail_post, name="Detail Post"),
    # path('<str:author_username>/<str:slug>/', views.detail_post, name="Blog Post"),
    path('post-comment/', views.post_comment, name="Post Comment"),
    path('savepost/', views.SavePost, name='Save Post'),
    path('edit-post/post-id-<int:post_id>/', views.update_post, name="Update post"),
    
    # Profile and settings
    path('settings/', views.Change_profile, name="Profile Change"),
    path('follow-author/', views.profile, name="Follow Author"),
    path('<str:username>/<str:text>/', views.profile, name="Followers Following"),
    path('<str:username>/', views.profile, name="Profile"),  # Specific profile view last
]


# This part is not needed as it is already covered by the above line
# path('<str:username>/', views.profile, name="Author Profile"),
