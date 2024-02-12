from django.db import models
from django.shortcuts import render,redirect
from django.contrib.auth.models import AbstractUser,User
from datetime import datetime
from django.utils import timezone

# Create your models here.


class Post(models.Model):
    author=models.CharField(max_length=100)
    title=models.CharField( max_length=500)
    content=models.TextField()
    publish_time=models.DateField(default=datetime.today)
    read_count=models.IntegerField(default=0)
    # isReaded=models.BooleanField(default=False)
    like=models.IntegerField(default=0)
    # isLiked=models.BooleanField(default=False)

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
class PostReadedUser(models.Model):
    user=models.ForeignKey(User, verbose_name="user", on_delete=models.CASCADE)
    post=models.ForeignKey(Post, verbose_name="Readed post", on_delete=models.CASCADE)

class BlogUser(models.Model):
    user=models.OneToOneField(User, verbose_name="User", on_delete=models.CASCADE)
    Bio=models.CharField( max_length=5000 ,default=None)
    followers=models.IntegerField(default=0)
    following=models.IntegerField(default=0)

    