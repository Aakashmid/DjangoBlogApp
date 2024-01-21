from django.db import models
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
# Create your models here.

class Post(models.Model):
    author=models.CharField(max_length=100)
    title=models.CharField( max_length=500)
    content=models.TextField()
    publish_time=models.DateTimeField(default=datetime.now())
    read_count=models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.title
    
class Comment(models.Model):
    sno=models.AutoField(primary_key=True)
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    post=models.ForeignKey(Post, on_delete=models.CASCADE)
    parent=models.ForeignKey('self', on_delete=models.CASCADE,null=True)
    timeStamp=models.DateTimeField(default=timezone.now)
    comment_text=models.TextField()

    def __str__(self) -> str:
        return self.comment_text + "...  by   "+ self.user.username