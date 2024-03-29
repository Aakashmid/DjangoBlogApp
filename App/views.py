from django.shortcuts import render,redirect,HttpResponse,HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from .models import Post,Comment,PostLike,CommentLike,PostReadedUser ,BlogUser,AuthorFollower,Tag,PostCategory,SavedPost
from .templatetags import extraFilter
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
# Create your views here.
def home(request):
    # incomplet , write logic for showing recent posts
    allPosts=Post.objects.filter(publish_time__gte=timezone.now()-timedelta(days=5)).order_by('-read_count')[:10]
    postTags=Tag.objects.all()[:8]
    postCats=PostCategory.objects.all()[:10]
    if request.session.get('postList'):
        print(request.session['postList'])
    else:
        print([])

    parms={"allPosts":allPosts,'postTags':postTags,'Categories':postCats,}
    return render(request,'App/index.html',parms)


def Create_account(request):
    if request.method=="POST":
        fname=request.POST.get('first_name')
        lname=request.POST.get('last_name')
        username=request.POST.get('username')
        password=request.POST.get('password')
        email=request.POST.get('email')
        if User.objects.filter(username=username).exists():
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
    
def Show_post_blogs(request,filterOrder=None,category=None,tagName=None):
    # Handling search query 
    if request.method=="POST":
        if request.POST['SearchQuery']:
            search=request.POST.get('SearchQuery')
            allPosts=Post.objects.all()
            Posts=[]
            for post in allPosts:
                if search.lower() in  post.title.lower() or search.lower() in post.content.lower() :
                    Posts.append(post)
                if post.category is not None:
                    if post.category.name.lower()==search.lower():
                        Posts.append(post)
            params={"allPosts":Posts,'Search':"Search_result_page"}
            return render(request,'App/blog_posts.html',params)
    elif category is not  None:
        cat=PostCategory.objects.get(name=category)
        Posts=Post.objects.filter(category=cat)
        params={"allPosts":Posts}
        return render(request,'App/blog_posts.html',params)
        
    elif tagName is not None:
        allPosts=Post.objects.all()
        Posts=[]
        for post in allPosts:
            for tag in post.tags.all():
                if tagName==tag.name:
                    Posts.append(post)
                    break
        return render(request,'App/blog_posts.html',{'allPosts':Posts})
    elif filterOrder : 
        ids=['trend','new','old','mostreaded']
        if filterOrder==ids[0]:
            #write query for selecting trending posts
            allPosts=Post.objects.filter(Q(read_count__gte=0)& Q(publish_time__gte=timezone.now()-timedelta(days=6)))[:20]
            # allPosts=Post.objects.filter(publish_time__gte=timezone.now()-timedelta(days=3)).order_by('-read_count')[:4]
        elif filterOrder==ids[1]:
            allPosts=Post.objects.all().order_by('-publish_time')
        elif filterOrder==ids[2]:
            allPosts=Post.objects.all().order_by('publish_time')
        elif filterOrder==ids[3]:
            allPosts=Post.objects.all().order_by('-read_count')[:20]
            # allPosts=Post.objects.filter(Q())
        if request.user.is_anonymous:
            user=""
        else:
            user=BlogUser.objects.get(user=request.user)  #user is current user
        params={'allPosts':allPosts,'User':user}
        return render(request,'App/blog_posts.html',params)
    else:
        if request.user.is_anonymous:
            user=""
        else:
            user=BlogUser.objects.get(user=request.user)  #user is current user
        allPosts=Post.objects.all()
        params={'allPosts':allPosts,'User':user}
        return render(request,'App/blog_posts.html',params)

def Create_post(request):
    if request.method=="POST":
        title=request.POST.get('post_title')
        content=request.POST.get('blog_content')
        cat=request.POST.get('category')
        Tags=request.POST.get('tags')
        thumImg=request.FILES.get('thumbnail')
        if cat!="":
            category=PostCategory.objects.get(name=cat)
        else:
            category=None   

        # Adding tags
        Tagnames=[]
        for tag in Tags.split():
            if tag[0]=='#':
                Tagnames.append(tag[1:])
            else:
                Tagnames.append(tag[0:])
        
        Tags=[]  
        for tagname in Tagnames:
            if not Tag.objects.filter(name=tagname).exists():
                tag=Tag.objects.create(name=tagname)
                Tags.append(tag)
            else:
                tag=Tag.objects.get(name=tagname)
                Tags.append(tag)
    
            
        author=BlogUser.objects.get(user=request.user)
        author.save()
        # Create post 
        post=Post.objects.create(author=author,title=title,content=content,category=category)
        post.tags.add(*Tags)
        if thumImg is not None:
            post.thImg=thumImg
            post.save()
        messages.success(request,"Blog is posted successfuly !!")
        return redirect('/')
    categories=PostCategory.objects.all()
    params={'Categories':categories}
    return render(request,'App/createPost.html',params)

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
        related_posts=Post.objects.filter(category=post.category)[:4]
        # Author=BlogUser.objects.get(user=post.author)
        CommentsDict={}
        replyDict={}
        for reply in replies:
            if reply.parent.sno not in replyDict.keys():
                replyDict[reply.parent.sno]=[reply]
            else:
                replyDict[reply.parent.sno].append(reply)
        for comment in comments:
            CommentsDict[comment]=BlogUser.objects.get(user=comment.user)
        return render(request,'App/postView.html',{"post":post,"CommentsDict":CommentsDict,'replies':replyDict,'Related_posts':related_posts})  #User is logged in user or current user
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
    
def profile(request,user_id=None):     
    if user_id:
        if request.method=="POST":
            action=request.POST.get('action',None)
            post_id=request.POST.get('Post_id',None)  # for saving post in reading list
            if action is not None:
                if action=='IncreaseFollower':
                    Author=BlogUser.objects.get(user=user_id)
                    Follower=request.user 
                    # AuthFollRel is object storing AuthorFollower object which keeps information of author and follower data
                    
                    if not AuthorFollower.objects.filter(Author=Author,follower=Follower).exists():
                        Author.followers+=1
                        Author.save()
                        AuthFollRel=AuthorFollower.objects.create(Author=Author,follower=Follower)
                        AuthFollRel.save()
                        response=JsonResponse({'btnText':"Following",'followerCount':Author.followers})
                        return response
                    else:
                        response=JsonResponse({'btnText':"Following",'followerCount':Author.followers})
                        return response   
                elif action=="DecreaseFollower":
                    Author=BlogUser.objects.get(user=user_id)
                    Follower=request.user
                    if AuthorFollower.objects.filter(Author=Author,follower=Follower).exists():
                        Author.followers-=1
                        Author.save()
                        AuthFollRel=AuthorFollower.objects.get(Author=Author,follower=Follower)
                        AuthFollRel.delete()
                        response=JsonResponse({'btnText':"Follow",'followerCount':Author.followers})
                        return response
                    else:
                        response=JsonResponse({'btnText':"Follow",'followerCount':Author.followers})
                        return response

                else:
                    Author=BlogUser.objects.get(user=user_id)
                    # if not request.user.is_anonymous
                    Follower=request.user
                    if AuthorFollower.objects.filter(Author=Author,follower=Follower).exists():
                        response=JsonResponse({'btnText':"Following"})
                        return response
                    else:
                        response=JsonResponse({'btnText':"Follow"})
                        return response
            elif post_id is not None:
                # post_id=int(post_id)
                if 'postList' in request.session:
                    if int(post_id) not in request.session['postList']:
                        request.session['postList'].append(int(post_id))
                        response=JsonResponse({'Result':'Post_saved'})
                        request.session.modified=True
                        return response
                    else:
                        request.session['postList'].remove(int(post_id))
                        request.session.modified=True
                        response=JsonResponse({'Result':'Post_unsaved'})
                        return response
                else:
                    request.session['postList']=[int(post_id)]
                    request.session.modified=True
                    return JsonResponse({'Result':'Post_saved'})
            else:
                return HttpResponseRedirect(reverse('App:Author profile',args=(user_id)))

        # If user  want to see author page
        else:
            # here author id is blogser object pk 
            bloguser=BlogUser.objects.get(pk=user_id)
            allPosts=Post.objects.filter(author=user_id)
            if not request.user.is_anonymous:
                if AuthorFollower.objects.filter(follower=request.user,Author=bloguser).exists():
                    userFollower=True
                else:
                    userFollower=False
            else:
                userFollower=False
            # here Author is author of post
            return render(request,'App/author.html',{"Author":bloguser,'Posts':allPosts,'userFollower':userFollower})
            # return render(request,'App/author.html',{'Posts':allPosts})
    else:
        bloguser=BlogUser.objects.get(user=request.user)
        SavedPosts=[]
        postIds=request.session['postList'] if 'postList' in request.session else []
        if len(postIds)>0:
            for id in postIds:
                SavedPosts.append(Post.objects.get(id=id))
        return render(request,'App/profile.html',{"User":bloguser,'saved_posts':SavedPosts})
    
def Change_profile(request):
    if request.method=="POST":
        username=request.POST.get('username')
        name=request.POST.get('fullname')
        email=request.POST.get('Email')
        bio=request.POST.get('Bio')
        profilImage=request.FILES.get('imageInput')
        if User.objects.filter(username=username).exclude(username=request.user.username):
            messages.error(request,'This username is taken !!')
            return HttpResponseRedirect(reverse('App:User Profile'))
        else:
            firstname=name.split(' ')[0]
        # here length is storing how many word is list name is
            length= len(name.split(' '))
            lastname=""
            for i in range(1,length):
                if i!=1:
                    lastname+=" "+name.split(' ')[i]
                else:
                    lastname+=name.split(' ')[i]
            user=request.user
            user.first_name=firstname
            user.last_name=lastname
            user.username=username
            user.email=email
            user.save()
            bloguser=BlogUser.objects.get(user=user)
            if profilImage is not None:
                bloguser.profileImg=profilImage
            bloguser.Bio=bio
            bloguser.save()
            messages.success(request,"Changed profile successfully !!")
            return HttpResponseRedirect(reverse('App:User Profile'))

