

from django.contrib import admin
from django.urls import path
from . import views

app_name = 'App'

urlpatterns = [
    # Home page
    path('', views.home, name="Home"),
    # Authentication
    path('sign-up/', views.Create_account, name="Create user"),
    path('login-user/', views.Login_hand, name="login_user"),
    path('logout-user/', views.Logout_hand, name="Logout user"),
    # path('load_more_posts/', views.loadMorePosts, name="load-more-posts"),
    
    # Search and filter
    path('search/', views.SearchResult, name="Search Posts"),
    path('readinglist/', views.SearchResult, name="Reading_list"),

    #-------------have to modify----------------
    # path('post-blogs/<str:filterOrder>/', views.SearchResult, name="Blogs filter"),
    path('search/category/<str:category>/', views.SearchResult, name="Blogs By Category"),
    path('search/tag/<str:tagName>/', views.SearchResult, name="Blogs by tag"),
    # ----------------------------

    path('post-comment-reply/', views.CommentReplyHandler, name="comment-reply"),
    path('savepost/', views.SavePost, name='Save Post'),
    path('delete-post/post-<int:post_id>/', views.update_post, name="delete post"),
    path('edit-post/post-<str:slug>/', views.update_post, name="Update post"),
    
    # Post-related
    path('<str:author_username>/post-<str:slug>/', views.detail_post, name="Detail Post"),
    path('new-post/', views.Create_post, name="Create Post"),

    # Profile and settings
    path('settings/', views.Change_profile, name="Profile Change"),
    path('follow-author/', views.profile, name="Follow Author"),
    path('<str:username>/<str:text>/', views.profile, name="Followers Following"),
    path('<str:username>/', views.profile, name="Profile"),  # Specific profile view last
]


# This part is not needed as it is already covered by the above line
# path('<str:username>/', views.profile, name="Author Profile"),
