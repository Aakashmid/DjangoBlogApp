from django.db import models
from django.shortcuts import render,redirect
from django.contrib.auth.models import AbstractUser,User
from datetime import datetime
from django.utils import timezone

# Create your models here.

class PostCategory(models.Model):
    name=models.CharField(max_length=100)
    def __str__(self):
        return self.name
class Tag(models.Model):
    name=models.CharField(max_length=100)
    def __str__(self):
        return self.name


#  For profile of user 
class BlogUser(models.Model):
    user=models.OneToOneField(User, verbose_name="User", on_delete=models.CASCADE)
    profileImg=models.ImageField("Profile Image", upload_to='App/profileimg/', default='profile.jpg')
    Bio=models.CharField( max_length=5000 ,default="",null=True)
    followers=models.IntegerField(default=0)
    following=models.IntegerField(default=0)
    def __str__(self) -> str:
        return self.user.username

class Post(models.Model):
    title=models.CharField( max_length=500)
    content=models.TextField()
    publish_time=models.DateField(default=datetime.today)
    read_count=models.IntegerField(default=0)
    author=models.ForeignKey(BlogUser, on_delete=models.CASCADE)
    like=models.IntegerField(default=0)
    category=models.ForeignKey(PostCategory, verbose_name="Post_Categories", on_delete=models.SET_NULL,null=True,blank=True)
    tags=models.ManyToManyField(Tag, verbose_name="Post_Tags",blank=True)
    def __str__(self) -> str:
        return self.title
    class Meta:
        verbose_name_plural="Blog posts"


class Comment(models.Model):
    sno=models.AutoField(primary_key=True)
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    post=models.ForeignKey(Post, on_delete=models.CASCADE)
    parent=models.ForeignKey('self', on_delete=models.CASCADE,null=True)
    timeStamp=models.DateTimeField(default=timezone.now)
    comment_text=models.TextField()
    like=models.IntegerField(default=0)
    # isLiked=models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.comment_text + "...  by   "+ self.user.username
    
#store which user like which post
class PostLike(models.Model):
    user=models.ForeignKey(User, verbose_name="user who liked", on_delete=models.CASCADE)
    post=models.ForeignKey(Post, verbose_name="post which is liked", on_delete=models.CASCADE)

#store which user like which comment
class CommentLike(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    comment=models.ForeignKey(Comment, on_delete=models.CASCADE)

# for informations who read a specific post
class PostReadedUser(models.Model):
    user=models.ForeignKey(User, verbose_name="user", on_delete=models.CASCADE)
    post=models.ForeignKey(Post, verbose_name="Readed post", on_delete=models.CASCADE)


class AuthorFollower(models.Model):
    Author=models.ForeignKey(BlogUser, verbose_name="Author", on_delete=models.CASCADE)
    follower=models.ForeignKey(User, verbose_name="Follower", on_delete=models.CASCADE)
    
class SavedPost(models.Model):
    saved_post=models.ForeignKey(Post, on_delete=models.CASCADE)
    user=models.ForeignKey(BlogUser, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return self.saved_post.title+ "  "+ self.user.user.first_name
