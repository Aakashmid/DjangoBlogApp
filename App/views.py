from django.db.models import Count
from django.shortcuts import render,redirect,HttpResponse,HttpResponseRedirect,get_object_or_404
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
from django.core.paginator import Paginator
from django.contrib import sessions
import json
from django.http import QueryDict
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

# # Cache the view for 15 minutes
# @cache_page(60 * 15)
def home(request):    #fname is filter name
    filters=[{'name':'All'},{'name':'Latest'},{'name':'Following'}] if 'FollowedAuthor' in request.session and len(request.session['FollowedAuthor']) > 0 else [{'name':'All'},{'name':'Latest'}]

    postTags = Tag.objects.annotate(post_count=Count('tagPosts')).filter(post_count__gt=0)  # posts is related name of  # tag in post model ,get tag whose posts are more than 0
    for tag in postTags:
        filters.append({'name':str(tag.name)})

    allposts=Post.objects.all()
    # allposts=Post.objects.all().order_by('?')  

    # Get the page number from the request
    page = request.GET.get('page', 1)

    # Create a Paginator object with 10 posts per page
    paginator = Paginator(allposts, 10)
    posts=paginator.page(page)
    params={'allPosts':posts,'filters':filters,'activeFilter':{'name':'All'}}

    # for filtering posts
    filter=request.GET.get('tag','')
    if filter:
        filteredPosts=[]
        if filter!='Following' and filter!='All' and filter!='Latest':
            try :
                activefilter=Tag.objects.get(name=filter)
                filteredPosts=Post.objects.filter(tags=activefilter)
                params={'allPosts':filteredPosts,'filters':filters,'activeFilter':activefilter}
            except Exception as e:
                pass
        elif filter=='Following':
            if not request.user.is_anonymous:
                followedAuthorPosts=[]
                for post in allposts:
                    if 'FollowedAuthor' in request.session and post.author.pk in request.session['FollowedAuthor']:
                        followedAuthorPosts.append(post) 
            else:
                # handle when user in not logged in 
                return render(request,'signup.html')
            activefilter={'name':'Following'} 
            params={'allPosts':followedAuthorPosts,'filters':filters,'activeFilter':activefilter }
        elif filter=='Latest':
            activefilter={'name':'Latest'} 
            latest_posts=Post.objects.filter(publish_time__gte=timezone.now()-timedelta(days=3))
            # latest_posts=Post.objects.filter(publish_time__gte=timezone.now()-timedelta(days=3)).order_by('-read_count')
            params={'allPosts':latest_posts,'filters':filters,'activeFilter':activefilter }
        else:
            params={'allPosts':allposts,'filters':filters,'activeFilter':{'name':'All'} }
    return render(request,'App/index.html',params)


def Create_account(request):
    if request.method=="POST":
        fname=request.POST.get('first_name')
        lname=request.POST.get('last_name')
        username=request.POST.get('username')
        password=request.POST.get('password')
        email=request.POST.get('email')
        if User.objects.filter(username=username).exists():
            messages.error(request,"This username is taken !!")
            return HttpResponseRedirect(reverse('App:Home'))
        else:
            user=User.objects.create_user(username=username,email=email,password=password)
            user.first_name=fname
            user.last_name=lname
            user.save()
            request.session.set_expiry(2592000)  # user is logged in for 30 days
            login(request,user=user)
            messages.success(request,"Account is created successfully")
            return HttpResponseRedirect(reverse('App:Home'))
    else:
        return render(request,'signup.html')
def Login_hand(request):
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        authenticated_user=authenticate(username=username,password=password)
        if authenticated_user:
            login(request,authenticated_user)
            request.session.set_expiry(2592000)  # user is logged in for 30 days
            user=BlogUser.objects.get(user=authenticated_user)
            if user.session_data=={} :
                user.session_data=serialize_session(request.session)
            else:
                deserialize_data=json.loads(user.session_data)  #deserialize
                request.session.clear()
                for key,value in deserialize_data.items():
                    request.session[key] =value
                    request.session.modified=True
            messages.success(request,"Successsfully logged in user !!")
            return HttpResponseRedirect(reverse('App:Home'))
        else:
            messages.error(request,"Username or Password is incorrect !!")
            return HttpResponseRedirect(reverse('App:Home'))
    else:
         return redirect('/')
def Logout_hand(request):
    try:
        user=BlogUser.objects.get(user=request.user)
        user.session_data= serialize_session(request.session)
        user.save()
    except Exception as e :
        pass
    logout(request)
    messages.success(request,"Successsfully logout !!")
    return redirect('/')
    
def SearchResult(request,filterOrder=None,category=None,tagName=None):
    # Handling search query 
    if request.method=="GET" and 'q' in  request.GET:
        query=request.GET.get('q')
        allPosts=Post.objects.all()
        Posts=[]
        for post in allPosts:
            if query.lower() in  post.title.lower() :
                Posts.append(post)
            if post.category is not None:
                if post.category.name.lower()==query.lower():
                    Posts.append(post)
        params={"allPosts":Posts,'Search':"Search_result_page"}

# --------------------------- handle later
    elif category is not  None:
        cat=PostCategory.objects.get(name=category)
        Posts=Post.objects.filter(category=cat)
        params={"allPosts":Posts}

    elif tagName is not None:
        allPosts=Post.objects.all()
        Posts=[]
        for post in allPosts:
            for tag in post.tags.all():
                if tagName==tag.name:
                    Posts.append(post)
                    break
        params={'allPosts':Posts}

    # FOR FILTERING POST SERRCHRESULT PAGE
    elif filterOrder : 
        ids=['trend','new','old','mostreaded']
        if filterOrder==ids[0]:
            #write query for selecting trending posts
            allPosts=Post.objects.filter(Q(read_count__gte=0)& Q(publish_time__gte=timezone.now()-timedelta(days=6)))[:20]
        elif filterOrder==ids[1]:
            allPosts=Post.objects.all().order_by('-publish_time')
        elif filterOrder==ids[2]:
            allPosts=Post.objects.all().order_by('publish_time')
        elif filterOrder==ids[3]:
            allPosts=Post.objects.all().order_by('-read_count')[:20]
        params={'allPosts':allPosts}
   
#----------------------------- 
    # FOR SHOWING READING LIST 
    else:
        SavedPosts=[]
        postIds=request.session['SavedPosts'] if 'SavedPosts' in request.session else []
        if len(postIds)>0:
            for id in postIds:
                try:
                    SavedPosts.append(Post.objects.get(id=id))
                except Exception as e:
                    request.session['SavedPosts'].remove(id)
                    request.session.modified=True
        params={'readingList':True, 'readingListPosts':SavedPosts}
    return render(request,'App/SearchedPosts.html',params)

def Create_post(request):
    if request.method=="POST":
        title=request.POST.get('post_title')
        content=request.POST.get('blog_content')
        Tags=request.POST.get('tags')
        thumImg=request.FILES.get('thumbnail')

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
        post=Post.objects.create(author=author,title=title,content=content)
        post.tags.add(*Tags)
        if thumImg is not None:
            post.thImg=thumImg
            post.save()
        messages.success(request,"Blog is posted successfuly !!")
        return HttpResponseRedirect(reverse('App:Home'))
    else :
        categories=PostCategory.objects.all()
        params={'Categories':categories}
        return render(request,'App/createPost.html',params)

@csrf_exempt   # when use handling post request
def detail_post(request,slug=None,author_username=None):

    # for change like count of a comment on post
    if request.method=="POST":
        try:
            likedComments= request.session.get('likedComments',[])
            data=json.loads(request.body)
            comment_sno=int(data.get('comment_sno')) 
            comment=Comment.objects.get(sno=comment_sno)
            if CommentLike.objects.filter(comment=comment,user=request.user).exists():
                CommentLike.objects.get(comment=comment,user=request.user).delete()
                comment.like-=1
                comment.save()
                if comment_sno in  likedComments:
                    likedComments.remove(comment_sno)
                response_context={'likeCount':comment.like,'status':'unliked'}
            else:
                CommentLike.objects.create(comment=comment,user=request.user)
                comment.like+=1
                comment.save()
                if comment_sno not in likedComments:
                    likedComments.append(comment_sno)
                response_context={'likeCount':comment.like,'status':'liked'}

            request.session['likedComments']=likedComments
            request.session.modified=True
            return JsonResponse(response_context)
        except Exception as e:
             return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    ###  Fitler comments and replies of a post 
    elif Post.objects.filter(slug=slug).exists():
        post=Post.objects.get(slug=slug)
        comments=Comment.objects.filter(Q(parent=None) & Q(post=post))
        replies=Comment.objects.filter(post=post).exclude(parent=None)
        related_posts=Post.objects.filter(category=post.category)
        # Author=BlogUser.objects.get(user=post.author)
        CommentsDict={}
        replyDict={}
        for reply in replies:
            replyUser=BlogUser.objects.get(user=reply.user)
            if reply.parent.sno not in replyDict.keys():
                replyDict[reply.parent.sno]=[{replyUser:reply}]
            else:
                replyDict[reply.parent.sno].append({replyUser:reply})
        for comment in comments:
            CommentsDict[comment]=BlogUser.objects.get(user=comment.user)
        return render(request,'App/postView.html',{"post":post,"CommentsDict":CommentsDict,'replies':replyDict,'Related_posts':related_posts})  #User is logged in user or current user
    else:
        return redirect('/')

def CommentReplyHandler(request):
    if request.method=="POST":
        postSno=request.POST.get('postSno')
        parentSno=request.POST.get('parentSno')
        comment_text=request.POST.get('comment')
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
        return HttpResponseRedirect(reverse('App:Detail Post',args=(post.author.user.username,post.slug,)))
    else:
        # next_url=request.GET.get('')
        return redirect('/')
 
 # this is for profile  for author profile  # we have pass the same name in parameters as we passed in url    
def profile(request,text=None,username=None):
    # For showing followers following  page
    if username is not None and  text is not None:
        user=User.objects.get(username=username)
        Author=BlogUser.objects.get(user=user)
        if text=='following':
            following=True
            follower=False
            AuthorFollowerObjs=AuthorFollower.objects.filter(follower=Author.user)  # follower is user object
        else:
            AuthorFollowerObjs=AuthorFollower.objects.filter(Author=Author)
            following=False
            follower=True
        AllUsers=[]
        for i in AuthorFollowerObjs:
            
            if following==True:
                if i.Author != Author:
                    AllUsers.append(i.Author)
            else:
                follower=BlogUser.objects.get(user=i.follower)
                if follower != Author:
                    AllUsers.append(follower)
        params={'following':following,'follower':follower,'Author':Author,'AllUsers':AllUsers}
        return render(request,'App/followersFollowings.html',params)
    
    # for changing post likes
    elif request.method=="POST":
        try:
            likedPosts= request.session['likedPosts'] if 'likedPosts' in request.session  else []
            data=json.loads(request.body)
            post_id=int(data['post_id']) 
            # get post of that id
            post=Post.objects.get(id=post_id)
            if PostLike.objects.filter(post=post,user=request.user).exists():
                PostLike.objects.get(post=post, user=request.user).delete()
                post.like-=1
                post.save()
                likedPosts = [pid for pid in likedPosts if pid != post_id]
                response_context={'likeCount':post.like,'status':'unliked'}
            else:
                PostLike.objects.create(post=post,user=request.user)
                post.like+=1
                post.save()
                likedPosts.append(post_id) if post_id not in likedPosts else None
                response_context={'likeCount':post.like,'status':'liked'}
            request.session['likedPosts']=likedPosts
            request.session.modified=True
            
            return JsonResponse(response_context)
        except PostLike.MultipleObjectsReturned:
            PostLike.objects.filter(post=post, user=request.user).delete()
            post.like-=1
            post.save()
            likedPosts = [pid for pid in likedPosts if pid != post_id]
            response_context={'likeCount':post.like,'status':'unliked'}
        except Exception as e:
             print(request.session.items())
             return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    # for follow a author or unfollow 
    elif request.method=="PATCH": 
        data=json.loads(request.body)  # get author_userid of author   
        if 'FollowedAuthor' not in request.session : 
            request.session['FollowedAuthor']=[]
        author_id=int(data['author_id'])
        Author=BlogUser.objects.get(pk=author_id)
        follower=BlogUser.objects.get(user=request.user)  # follower user bloguser object
        if AuthorFollower.objects.filter(Author=Author,follower=request.user).exists():
            AuthorFollower.objects.get(Author=Author,follower=request.user).delete()
            Author.followers-=1
            follower.following-=1
            Author.save()
            follower.save()
            if author_id in request.session['FollowedAuthor']:
                request.session['FollowedAuthor'].remove(author_id)
                request.session.modified=True
            params={'btnText':'Follow','follower_count':Author.followers}
        else:
            AuthorFollower.objects.create(Author=Author,follower=request.user)
            Author.followers+=1
            follower.following+=1
            Author.save()
            follower.save()
            request.session['FollowedAuthor'].append(author_id)
            request.session.modified=True
            params={'btnText':'Following','follower_count':Author.followers}
        return JsonResponse(params)
    
    # for show profile page of user 
    elif username is not None:
        # for showing current user profile
        if not request.user.is_anonymous and  username==request.user.username:
            bloguser=BlogUser.objects.get(user=request.user)
            SavedPosts=[]
            postIds=request.session['SavedPosts'] if 'SavedPosts' in request.session else []
            if len(postIds)>0:
                for id in postIds:
                    try:
                        SavedPosts.append(Post.objects.get(id=id))
                    except Exception as e:
                        request.session['SavedPosts'].remove(id)
                        request.session.modified=True
            CurrentUser=BlogUser.objects.get(user=request.user)
            UsersPosts=Post.objects.filter(author=CurrentUser) if Post.objects.filter(author=CurrentUser).exists() else []
            context={"User":bloguser,'saved_posts':SavedPosts,'UsersPosts':UsersPosts}
            return render(request,'App/profile.html',context=context)
        
        # for showing  author profile
        elif User.objects.filter(username=username).exists():
            user=User.objects.get(username=username)
            bloguser=BlogUser.objects.get(user=user)
            allPosts=Post.objects.filter(author=bloguser)
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
            return redirect('/')
    else:
        return redirect('/')


    
def Change_profile(request):
    if request.method=="POST":
        username=request.POST.get('username')
        name=request.POST.get('fullname')
        email=request.POST.get('Email')
        bio=request.POST.get('Bio')
        profilImage=request.FILES.get('imageInput')
        if User.objects.filter(username=username).exclude(username=request.user.username):
            messages.error(request,'This username is taken !!')
            return HttpResponseRedirect(reverse('App:Profile'))
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
            return HttpResponseRedirect(reverse('App:Profile',args=(request.user.username,)))

def update_post(request,slug=None,post_id=None):
    if slug is not None and Post.objects.get(slug=slug).author.user==request.user:
        # for update post
        if request.method=="POST":
            post=Post.objects.get(slug=slug)
            title=request.POST.get('post_title')
            content=request.POST.get('blog_content')
            Tags=request.POST.get('tags')
            thumImg=request.FILES.get('thumbnail')

            # Collecting  tags
            Tagnames=[]
            for tag in Tags.split():
                if tag[0]=='#':
                    Tagnames.append(tag[1:])
                else:
                    Tagnames.append(tag[0:])
            Tags=[]  
            # Adding tags
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
            # post=Post.objects.create(author=author,title=title,content=content,category=category)
            post.title=title
            post.content=content
            post.tags.add(*Tags)
            post.save()
            if thumImg is not None:
                post.thImg=thumImg
            post.save()
            messages.success(request,'Updated post successully ')
            return HttpResponseRedirect(reverse('App:Update post',args=(post.slug,)))
        post=Post.objects.get(slug=slug)
        params={'post':post}
        return render(request,'App/updatePost.html',params)
        # when post.slug is wrong or another user is trying to access another user's post

    # for delete post
    elif post_id is not None and request.method=="DELETE" :
        post=get_object_or_404(Post,id=post_id)
        post.delete()
        if post_id in request.session['likedPosts'] :
            request.session['likedPosts'].remove(post_id) 
        if post_id in request.session['SavedPosts'] :
            request.session['SavedPosts'].remove(post_id) 
        return JsonResponse({'Message':"Deleted post"})
    
    else:
        return redirect('/')
# function for serailize session data
def serialize_session(session):
    serialized_data = {}
    for key, value in session.items():
        serialized_data[key] = value
    return json.dumps(serialized_data)


def SavePost(request):
    if request.method == "POST":
        post_id = request.POST.get('Post_id')
        if post_id:
            post_id = int(post_id)
            saved_posts = request.session.get('SavedPosts', [])
            
            if post_id in saved_posts:
                saved_posts.remove(post_id)
                result = 'Post_unsaved'
            else:
                saved_posts.append(post_id)
                result = 'Post_saved'
            
            request.session['SavedPosts'] = saved_posts
            request.session.modified = True
            return JsonResponse({'Result': result})
        else:
            return HttpResponse('Invalid Post ID', status=400)
    else:
        return redirect('/')