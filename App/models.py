from django.db import models
from django.shortcuts import render,redirect
from django.contrib.auth.models import AbstractUser,User
from datetime import datetime
from django.utils import timezone
from django.utils.text import slugify

# Create your models here.

class Tag(models.Model):
    name=models.CharField(max_length=100)
    def __str__(self):
        return self.name


#  For profile of user (CustomUser)
class BlogUser(models.Model):
    user=models.OneToOneField(User, verbose_name="user", on_delete=models.CASCADE)
    profileImg=models.ImageField("Profile Image", upload_to='App/profileimg/', default='profile.jpg')
    Bio=models.CharField( max_length=5000 ,default="",null=True,blank=True)
    followers=models.IntegerField(default=0)
    following=models.IntegerField(default=0)
    # test=models.CharField( max_length=50,dea)
    session_data=models.JSONField(default=dict,blank=True)
    def __str__(self) -> str:
        return self.user.username

class Post(models.Model):
    title=models.CharField( max_length=200)
    content=models.TextField()
    publish_time=models.DateField(default=datetime.today)
    read_count=models.IntegerField(default=0,db_index=True)
    author=models.ForeignKey(BlogUser, related_name='author', on_delete=models.CASCADE)
    like=models.IntegerField(default=0)
    tags=models.ManyToManyField(Tag, related_name='tagPosts',blank=True)
    thImg=models.ImageField("Post Thumbnail", upload_to='App/thumbnail/', default='',blank=True ,null=True)
    slug = models.SlugField(unique=True, max_length=200, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            queryset = Post.objects.all()
            next_num = 1
            while queryset.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{next_num}"
                next_num += 1
        super().save(*args, **kwargs)  # This is necessary to actually save the instance

    def __str__(self) -> str:
        return self.title
    # def save(self):

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
        return f"{self.sno}"+" - "+ self.comment_text + "...  by   "+ self.user.username
    
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



