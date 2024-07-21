from django.db.models import Count
from django.shortcuts import render,redirect,HttpResponse,HttpResponseRedirect,get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from .models import Post,Comment,PostLike,CommentLike,BlogUser,AuthorFollower,Tag
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
def home(request):    #fname is filter name
    filters=[{'name':'All'},{'name':'Latest'},{'name':'Following'}] if 'FollowedAuthor' in request.session and len(request.session['FollowedAuthor']) > 0 else [{'name':'All'},{'name':'Latest'}]

    postTags = Tag.objects.annotate(post_count=Count('tagPosts')).filter(post_count__gt=1)  # posts is related name of  # tag in post model ,get tag whose posts are more than 0

    for tag in postTags:
        filters.append({'name':str(tag.name)})

    # allposts= Post.objects.select_related('author__user').annotate(comment_count=Count('comment', filter=Q(comment__parent=None))).order_by('?')  
    allposts= Post.objects.select_related('author__user').annotate(comment_count=Count('comment', filter=Q(comment__parent=None))).order_by('?')
    params={'allPosts':allposts,'filters':filters,'activeFilter':{'name':'All'}}

    # for filtering posts
    filter=request.GET.get('tag','')
    if filter:
        filteredPosts=[]
        if filter!='Following' and filter!='All' and filter!='Latest':
            try :
                activefilter=Tag.objects.get(name=filter)
                filteredPosts=Post.objects.select_related('author__user').filter(tags=activefilter).annotate(comment_count=Count('comment', filter=Q(comment__parent=None))).order_by('?')
                # filteredPosts=Post.objects.filter(tags=activefilter)
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
            latest_posts=Post.objects.filter(publish_time__gte=timezone.now()-timedelta(days=3)).select_related('author__user').annotate(comment_count=Count('comment',filter=Q(comment__parent=None))).order_by('?')
            # latest_posts=Post.objects.filter(publish_time__gte=timezone.now()-timedelta(days=3)).order_by('-read_count')
            params={'allPosts':latest_posts,'filters':filters,'activeFilter':activefilter }
        else:
            params={'allPosts':allposts,'filters':filters,'activeFilter':{'name':'All'} }
    

    # for pagination
    # paginator=Paginator(params['allPosts'],2)
    # page_number = request.GET.get('page')
    # posts = paginator.get_page(page_number)
    # params['allPosts']=posts
    params['home']=True
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
    
def SearchResult(request,tagName=None):
    # Handling search query 
    if request.method=="GET" and 'q' in  request.GET:
        query=request.GET.get('q')
        allPosts=Post.objects.select_related('author__user').annotate(comment_count=Count('comment', filter=Q(comment__parent=None))).filter(title__icontains=query)
        params={"allPosts":allPosts,'Search':"Search_result_page",'query':query}
        if 'filter' in request.GET:
            filter=request.GET.get('filter')
            allPosts=params['allPosts']
            if filter=='most_readed':
                filltered_posts=allPosts.order_by('read_count')
                params['allPosts']=filltered_posts
            elif filter=='newest':
                filltered_posts=allPosts.order_by('-publish_time')
                params['allPosts']=filltered_posts
            elif filter=='oldest':
                filltered_posts=allPosts.order_by('publish_time')
                params['allPosts']=filltered_posts
            params['filter']=filter
        
    elif 'tag' in request.GET:
        tagName=request.GET.get('tag')
        tag=Tag.objects.get(name=tagName)
        allPosts=Post.objects.select_related('author__user').annotate(comment_count=Count('comment', filter=Q(comment__parent=None))).filter(tags=tag)
        params={"allPosts":allPosts,'Search':"Search_result_page",'tag':tag.name}
        if 'filter' in request.GET:
            filter=request.GET.get('filter')
            allPosts=params['allPosts']
            if filter=='most_readed':
                filltered_posts=allPosts.order_by('read_count')
                params['allPosts']=filltered_posts
            elif filter=='newest':
                filltered_posts=allPosts.order_by('-publish_time')
                params['allPosts']=filltered_posts
            elif filter=='oldest':
                filltered_posts=allPosts.order_by('publish_time')
                params['allPosts']=filltered_posts
            params['filter']=filter

    # FOR SHOWING READING LIST 
    else:
        SavedPosts=[]
        postIds=request.session['SavedPosts'] if 'SavedPosts' in request.session else []
        if len(postIds)>0:
            posts = Post.objects.filter(id__in=postIds).select_related('author__user').annotate(comment_count=Count('comment', filter=Q(comment__parent=None)))
            for post in posts:
                SavedPosts.append(post)
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
        return render(request,'App/createPost.html')

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
        post=Post.objects.select_related('author__user').get(slug=slug)
        comments=Comment.objects.filter(Q(parent=None) & Q(post=post)).order_by('-timeStamp')
        replies=Comment.objects.filter(post=post).exclude(parent=None).order_by('-timeStamp')
        # related_posts=Post.objects.filter(category=post.category)
        tags=post.tags.all()
        related_posts=Post.objects.filter(tags__in=tags).select_related('author__user').exclude(id=post.id).distinct().annotate(same_tag_count=Count('tags')).annotate(comment_count=Count('comment', filter=Q(comment__parent=None))).order_by('-same_tag_count')[:5]
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
        else:
            parent=Comment.objects.get(sno=parentSno)
            comment=Comment(user=user,post=post,comment_text=comment_text,parent=parent)
            comment.save()
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
            CurrentUser=BlogUser.objects.get(user=request.user)
            UsersPosts=Post.objects.filter(author=CurrentUser).select_related('author__user').annotate(comment_count=Count('comment', filter=Q(comment__parent=None))) if Post.objects.filter(author=CurrentUser).exists() else []
            # context={'saved_posts':SavedPosts,'UsersPosts':UsersPosts}
            context={'UsersPosts':UsersPosts}
            return render(request,'App/profile.html',context=context)
        
        # for showing  author profile
        elif User.objects.filter(username=username).exists():
            user=User.objects.get(username=username)
            author=BlogUser.objects.select_related('user').get(user=user)
            allPosts=Post.objects.filter(author=author).select_related('author__user').annotate(comment_count=Count('comment', filter=Q(comment__parent=None))) if Post.objects.filter(author=author).exists() else []
            if not request.user.is_anonymous:
                if AuthorFollower.objects.filter(follower=request.user,Author=author).exists():
                    userFollower=True
                else:
                    userFollower=False
            else:
                userFollower=False
            # here Author is author of post
            return render(request,'App/author.html',{"Author":author,'Posts':allPosts,'userFollower':userFollower})
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
    if slug is not None and Post.objects.select_related('author__user').get(slug=slug).author.user==request.user:
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
            post.title=title
            post.content=content
            post.tags.set(Tags)
            post.save()
            if thumImg is not None:
                post.thImg=thumImg
            post.save()
            messages.success(request,'Updated post successully ')
            # return HttpResponseRedirect(reverse('App:Update post',args=(post.slug,)))
            return HttpResponseRedirect(reverse('App:Detail Post',args=(request.user.username,slug)))
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


def About(request):
    return render(request,'App/about.html')    