from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from .models import Post,Comment
from .templatetags import extraFilter
from django.db.models import Q
from django.http import JsonResponse
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
        trending=request.POST.get('trending')
        if search:
            allPosts=Post.objects.all()
            Posts=[]
            for post in allPosts:
                if search in  post.title.lower() or search in post.content.lower():
                    Posts.append(post)
            params={"allPosts":Posts}
            return render(request,'App/blog_posts.html',params)
        elif trending:
            return render(request,'App/blog_posts.html',params)
    
    elif filterOrder : 
            ids=['trend','new','old']
            if filterOrder==ids[0]:
                #write query for selecting trending posts
                allPosts=Post.objects.filter(read_count__gte=20)
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
    else:
        allPosts=Post.objects.all()
        params={'allPosts':allPosts}
        return render(request,'App/blog_posts.html',params)

         

        
    
def Create_post(request):
    if request.method=="POST":
        title=request.POST.get('post_title')
        content=request.POST.get('blog_content')
        author=request.user.username
        post=Post(author=author,title=title,content=content)
        post.save()
        messages.success(request,"Blog is posted successfuly !!")
        return redirect('/')
    return render(request,'App/createPost.html')

def Read_post(request,id):
    post=Post.objects.get(id=id)    
    if request.method=="PATCH":
        post.read_count+=1
        post.save()
        response = JsonResponse({'message': 'data is deleted successfully'})
        return response
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
    
def profile(request):
    return render(request,'App/profile.html')