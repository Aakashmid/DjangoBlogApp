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
# Create your views here.
def home(request):    #fname is filter name
    filters=[{'name':'All'},{'name':'Latest'},{'name':'Following'}] if 'FollowedAuthor' in request.session and len(request.session['FollowedAuthor']) > 0 else [{'name':'All'},{'name':'Latest'}]
    postTags=Tag.objects.all()
    for tag in postTags:
        # getting those tag whose post exists
        if len(tag.name) >0 and Post.objects.filter(tags=tag).exists():
            filters.append({'name':str(tag.name)})
            
    allposts=Post.objects.all()
    params={'allPosts':allposts,'filters':filters,'activeFilter':{'name':'All'}}

    # for filtering posts
    filter=request.GET.get('filter','')
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
                    # print(request.session['FollowedAuthor'])
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
            return redirect('/')
        else:
            user=User.objects.create_user(username=username,email=email,password=password)
            user.first_name=fname
            user.last_name=lname
            user.save()
            request.session.set_expiry(2592000)  # user is logged in for 30 days
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
            print(request.session.items())
            messages.success(request,"Successsfully logged in user !!")
            return redirect('/')
        else:
            messages.error(request,"Username or Password is incorrect !!")
            return redirect('/')
    else:
         return redirect('/')
def Logout_hand(request):
    user=BlogUser.objects.get(user=request.user)
    user.session_data= serialize_session(request.session)
    user.save()
    print(user.session_data)
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
    else :
        categories=PostCategory.objects.all()
        params={'Categories':categories}
        return render(request,'App/createPost.html',params)

def detail_post(request,slug=None,author_username=None):
    if request.method=="POST":
        action=request.POST.get('action')
        post=Post.objects.get(pk=id)
        # Liked post login goes here

        #If click like button of comment
        if action=='CommentlikeIncrease':
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
    if Post.objects.filter(slug=slug).exists():
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

 # this is for profile  for author profile  # we have pass the same name in parameters as we passed in url    
 # here user_id is bloguser object's id 
def profile(request,text=None,username=None):
    # whole view function has to update 


    # For showing followers following  page
    if username !=None and text !=None:
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
    
    # for liked post by users
    elif request.method=="POST":
        print("Post id is none")
        post_id=request.POST.get('post_id')
        print(f"Post id is {post_id}")
        post=Post.objects.get(id=post_id)
        if "LikedPosts" in request.session:
            if int(post_id) not in request.session['LikedPosts']:
                request.session['LikedPosts'].append(int(post_id))
                request.session.modified=True
                # PostLike.objects.create(post=post,user=request.user)
                post.like+=1
                post.save()
                return JsonResponse({'Success':"Successfull","like_count":post.like})
            else:
                request.session.modified=True
                request.session['LikedPosts'].remove(int(post_id))
                post.like-=1
                post.save()
                return JsonResponse({'Success':"Successfull ","like_count":post.like})
        else:
            request.session['LikedPosts']=[int(post_id)]
            request.session.modified=True
            post.like+=1
            return JsonResponse({'Success':"Successfull ","like_count":post.like})

    # for follow a author or unfollow 
    elif request.method=="PATCH": 
        data=json.loads(request.body)  # get author_userid of author   
        if 'FollowedAuthor' not in request.session : 
            request.session['FollowedAuthor']=[]
        author_id=data['author_id']
        print(author_id)
        Author=BlogUser.objects.get(pk=author_id)
        follower=BlogUser.objects.get(user=request.user)  # follower user bloguser object
        if AuthorFollower.objects.filter(Author=Author,follower=request.user).exists():
            print(True)
            AuthorFollower.objects.get(Author=Author,follower=request.user).delete()
            Author.followers-=1
            follower.following-=1
            Author.save()
            follower.save()
            if int(author_id) in request.session['FollowedAuthor']:
                request.session['FollowedAuthor'].remove(int(author_id))
                request.session.modified=True
            params={'btnText':'Follow','follower_count':Author.followers}
        else:
            AuthorFollower.objects.create(Author=Author,follower=request.user)
            Author.followers+=1
            follower.following+=1
            Author.save()
            follower.save()
            request.session['FollowedAuthor'].append(int(author_id))
            request.session.modified=True
            params={'btnText':'Following','follower_count':Author.followers}
        print(request.session['FollowedAuthor'])
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
            return HttpResponseRedirect(reverse('App:User Profile',args=(request.user.username,)))

def update_post(request,post_id=None):
    if post_id is not None:
        # for delete post
        if request.method=="DELETE":
            post=get_object_or_404(Post,id=post_id)
            print(f'Post id is {post.id}')
            post.delete()
            if post_id in request.session['LikedPosts'] :
                request.session['LikedPosts'].remove(post_id) 
            if post_id in request.session['SavedPosts'] :
                request.session['SavedPosts'].remove(post_id) 
            print(request.session)
            return JsonResponse({'Message':"Deleted post"})
        
        # for update post
        elif request.method=="POST":
            post=Post.objects.get(id=post_id)
            title=request.POST.get('post_title')
            content=request.POST.get('blog_content')
            cat=request.POST.get('category')
            Tags=request.POST.get('tags')
            thumImg=request.FILES.get('thumbnail')
            if cat !="":
                category=PostCategory.objects.get(name=cat)
            else:
                category=None   

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
            post.category=category
            post.tags.add(*Tags)
            post.save()
            if thumImg is not None:
                post.thImg=thumImg
                post.save()
            messages.success(request,'Updated post successully ')
            return HttpResponseRedirect(reverse('App:Update post',args=(post_id,)))
        post=Post.objects.get(id=post_id)
        categories=PostCategory.objects.all()
        params={'post':post,'Categories':categories}
        return render(request,'App/updatePost.html',params)

# function for serailize session data
def serialize_session(session):
    serialized_data = {}
    for key, value in session.items():
        serialized_data[key] = value
    return json.dumps(serialized_data)

# for saving post (adding in reading list of user)
def SavePost(request):
    print("post")
    if request.method=="POST":
        post_id=request.POST.get('Post_id') 
        if post_id :
            post_id=int(post_id)
            if 'SavedPosts' in request.session:
                if post_id not in request.session['SavedPosts']:
                    request.session['SavedPosts'].append(post_id)
                    response=JsonResponse({'Result':'Post_saved'})
                    request.session.modified=True
                    return response
                else:
                    request.session['SavedPosts'].remove(post_id)
                    request.session.modified=True
                    response=JsonResponse({'Result':'Post_unsaved'})
                    return response
            else:
                request.session['SavedPosts']=[post_id]
                request.session.modified=True
                return JsonResponse({'Result':'Post_saved'})
        else:
            # return HttpResponseRedirect(reverse('App:Author profile',args=(,)))
            return HttpResponse('testingdslf')
    else:
        return redirect('/')
