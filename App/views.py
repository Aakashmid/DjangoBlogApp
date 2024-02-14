from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from .models import Post,Comment,PostLike,CommentLike,PostReadedUser ,BlogUser
from .templatetags import extraFilter
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
# Create your views here.
def home(request):
    allPosts=Post.objects.filter(Q(read_count__gte=10))
    parms={"allPosts":allPosts}
    return render(request,'App/index.html',parms)


def Create_account(request):
    if request.method=="POST":
        fname=request.POST.get('first_name')
        lname=request.POST.get('last_name')
        username=request.POST.get('username')
        password=request.POST.get('password')
        email=request.POST.get('email')
        if User.objects.filter(username=username):
            messages.error(request,"This username is taken !!")
            return redirect('/')
        else:
            user=User.objects.create_user(username=username,email=email,password=password)
            user.first_name=fname
            user.last_name=lname
            user.save()
            bloguser=BlogUser.objects.create(user=user)
            bloguser.save()
            login(request,user=user)
            
            messages.success(request,"Account is created successfully")
            return redirect('/')
    else:
        return render(request,'signup.html')
def Login_hand(request):
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        authenticated_user=authenticate(username=username,password=password)
        if authenticated_user:
            login(request,authenticated_user)
            # print(f"First name of user is {authenticated_user.username} ")
            # print(authenticated_user.first_name)
            messages.success(request,"Successsfully logged in user !!")
            return redirect('/')
        else:
            messages.error(request,"Username or Password is incorrect !!")
            return redirect('/')
    else:
         return redirect('/')
def Logout_hand(request):
    # user=request.user
    # print(user)
    logout(request)
    messages.success(request,"Successsfully logout !!")
    return redirect('/')
    
def Show_post_blogs(request,filterOrder=None):

    if request.method=="POST":
        search=request.POST.get('SearchQuery')
        if search:
            allPosts=Post.objects.all()
            Posts=[]
            for post in allPosts:
                if search in  post.title.lower() or search in post.content.lower():
                    Posts.append(post)
            params={"allPosts":Posts}
            return render(request,'App/blog_posts.html',params)

    elif filterOrder : 
            ids=['trend','new','old','mostreaded']
            if filterOrder==ids[0]:
                #write query for selecting trending posts
                allPosts=Post.objects.filter(Q(read_count__gte=50)& Q(publish_time__gte=timezone.now()-timedelta(days=3)))[:20]
                params={"allPosts":allPosts}
                return render(request,'App/blog_posts.html',params)
            elif filterOrder==ids[1]:
                allPosts=Post.objects.all().order_by('-publish_time')
                params={"allPosts":allPosts}
                return render(request,'App/blog_posts.html',params)
            
            elif filterOrder==ids[2]:
                allPosts=Post.objects.all().order_by('publish_time')
                params={"allPosts":allPosts}
                return render(request,'App/blog_posts.html',params)
            elif filterOrder==ids[3]:
                allPosts=Post.objects.all().order_by('-read_count')[:20]
                # allPosts=Post.objects.filter(Q())
                params={"allPosts":allPosts}
                return render(request,'App/blog_posts.html',params)
    else:
        allPosts=Post.objects.all()
        params={'allPosts':allPosts}
        return render(request,'App/blog_posts.html',params)

def Create_post(request):
    if request.method=="POST":
        title=request.POST.get('post_title')
        content=request.POST.get('blog_content')
        # author=request.user.first_name+" "+request.user.last_name
        post=Post(author=request.user,title=title,content=content)
        post.save()
        messages.success(request,"Blog is posted successfuly !!")
        return redirect('/')
    return render(request,'App/createPost.html')

def Read_post(request,id):
    post=Post.objects.get(id=id)
    if request.method=="POST":
        action=request.POST.get('action')
        post=Post.objects.get(pk=id)
        if action=="PostLikeIncrease":
            if not PostLike.objects.filter(user=request.user,post=post).exists():
                post.like+=1
                post.save()
                Like=PostLike.objects.create(user=request.user,post=post)
                Like.save()
                response=JsonResponse({'likeCount':post.like})
                return response
            else:
                response=JsonResponse({'likeCount':post.like})
                return response
                
        elif action=="PostLikeDecrease":
            post=Post.objects.get(id=id)
            if PostLike.objects.filter(user=request.user,post=post).exists():
                post.like-=1
                post.save()
                Like=PostLike.objects.get(user=request.user,post=post)
                Like.delete()
                response=JsonResponse({'likeCount':post.like})
                return response
            else:
                response=JsonResponse({'likeCount':post.like})
                return response   
            
        #If click like button of comment
        elif action=='CommentlikeIncrease':
            comment_sno=int(request.POST.get('commentNo'))
            comment=Comment.objects.get(sno=comment_sno)
            if not CommentLike.objects.filter(user=request.user,comment=comment).exists():
                comment.like+=1
                print("increase like by 1")
                comment.save()
                # Create object like and save it ,that keep detailw which user liked  comment
                Like=CommentLike.objects.create(user=request.user,comment=comment)
                Like.save()
                response=JsonResponse({'likeCount':comment.like})
                return response
            else:
                response=JsonResponse({'likeCount':comment.like})
                return response

        elif action=='CommentlikeDecrease': # Decrease like count
                comment_sno=int(request.POST.get('commentNo'))
                comment=Comment.objects.get(sno=comment_sno)
                if CommentLike.objects.filter(user=request.user,comment=comment).exists():
                    comment.like-=1
                    comment.save()
                    CommentLike.objects.get(user=request.user,comment=comment).delete()
                    response=JsonResponse({'likeCount':comment.like})
                    return response
                response=JsonResponse({'likeCount':comment.like})
                return response
        
    # for increase readcount when user visit blog for sometime check also user is new or old
    if request.method=="PATCH":    
        if not PostReadedUser.objects.filter(user=request.user,post=post).exists():
            post.read_count+=1
            post.save()
            reader=PostReadedUser.objects.create(user=request.user,post=post)
            reader.save()
            response = JsonResponse({'message': 'post read count is increased successfully'})
            return response  
        response = JsonResponse({'message': 'read count is alerdyincreased '})
        return response

###  Fitler comments and replies of a post 
    if post:
        comments=Comment.objects.filter(Q(parent=None) & Q(post=post))
        replies=Comment.objects.filter(post=post).exclude(parent=None)
        replyDict={}
        for reply in replies:
            if reply.parent.sno not in replyDict.keys():
                replyDict[reply.parent.sno]=[reply]
            else:
                replyDict[reply.parent.sno].append(reply)
        return render(request,'App/postView.html',{"post":post,"comments":comments,'replies':replyDict})
    else:
        return redirect('/post-blogs/')

def post_comment(request):
    if request.method=="GET":
        postSno=request.GET.get('postSno')
        parentSno=request.GET.get('parentSno')
        comment_text=request.GET.get('comment')
        user=request.user
        post=Post.objects.get(id=postSno)
        if parentSno=="":
            comment=Comment(user=user,post=post,comment_text=comment_text)
            comment.save()
            messages.success(request,"Comment is posted successfully ")
        else:
            parent=Comment.objects.get(sno=parentSno)
            comment=Comment(user=user,post=post,comment_text=comment_text,parent=parent)
            comment.save()
            messages.success(request," Reply posted successfully ")
        return redirect(f'/post-blogs/{post.id}/')
    
def profile(request,author_id=None):
    if author_id:
        # here author id is user.id of user
        bloguser=BlogUser.objects.get(user=author_id)
        allPosts=Post.objects.filter(author=author_id)
        return render(request,'App/author.html',{"User":bloguser,'Posts':allPosts})
    else:
        return render(request,'App/profile.html')