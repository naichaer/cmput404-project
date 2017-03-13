from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
import os
from .models import Profile, Post, friend_request, Comment
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import sys
import uuid

'''
def reg_complete(request):
    return render(request, 'registration/registration_complete.html' ,{'what':'Reg Completed!'})
'''

@login_required
def home(request):
    return HttpResponseRedirect(reverse('profile'))

@login_required
def profile(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
        user = User.objects.get(id=request.user.id)
    except (KeyError, Profile.DoesNotExist):
        # profile no found create new
        profile = Profile.create(request.user)
        profile.save()
    else:
        # print profile
        pass

    friend_requests = friend_request.objects.filter(request_receiver=request.user)

    friends = Profile.objects.get(user=request.user).friends.all()
    # print (friends)
    return render(request,'profile/profile.html',{'user':request.user, 'request_by':request.user,
        'friend_list':friends,'friend_request':friend_requests})

def view_profile(request, username):

    user = get_object_or_404(User, username=username)
    # profile = Profile.objects.get(user_id=user.id)

    # check if is anonymouse user request
    # print "\nDebug:", request.user.is_authenticated==False, "\n"
    if (request.user.is_authenticated==False):
        return render(request,'profile/profile.html', {'user':user})

    # is a logged in user
    else:
        friend_requests = friend_request.objects.filter(request_receiver=request.user)
        friends = Profile.objects.get(user=request.user).friends.all()
        isfriend = False
        for friend in friends:
            if (friend.user == user):
                isfriend = True

        return render(request,'profile/profile.html',
                        {
                            'user':user,
                            'isFriend':isfriend,
                            'request_by':request.user,
                            'friend_request':friend_requests
                        })


@login_required
def profile_edit(request):
    """
    Profile edit view
    """

    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except (KeyError, Profile.DoesNotExist):
        # profile no found create new
        profile = Profile.create(request.user)
        profile.save()
    else:
        # print profile
        pass

    return render(request,'profile/profile_edit.html',{'user':request.user})


@login_required
def profile_update(request):
    """
    POST handler for profile update
    """

    try:
        profile = Profile.objects.get(user_id=request.user.id)
        user = User.objects.get(id=request.user.id)
    except (KeyError, Profile.DoesNotExist):
        # profile no found create new
        profile = Profile.create(request.user)
    else:
        # print profile
        pass

    user.email = request.POST['user_email']
    user.save()
    profile.github = request.POST['github']
    profile.bio = request.POST['bio']
    profile.save()

    return HttpResponseRedirect(reverse('profile'))

@login_required
def create_post_html(request):
    return render(request,'post/create_post.html',{'user':request.user})

# @login_required
def view_all_posts(request):
    Posts = Post.objects.filter(can_view=0).order_by('-pub_datetime')
    context = { 'posts':Posts}
    return render(request,'post/view_all_posts.html',context)

@login_required
def create_post(request):
    """
    Create new post view
    """

    user = User.objects.get(id=request.user.id)
    can_view = request.POST['post_type']
    post_text = request.POST['POST_TEXT']
    post_type = request.POST['content_type']
    new_post = Post.create(request.user,post_text,can_view, post_type)
    #==========
       #image = request.FILES['file']
       #new_post = Post.create(request.user,post_text,can_view,image)
    #=========
    new_post.save()

    return HttpResponseRedirect(reverse('profile'))

    # new_post = Post.create(request.user,"a new one")
    # new_post.save()

    # return HttpResponseRedirect(reverse('profile'))
@login_required
def manage_post(request):
    """
    post edit view
    """

    post = Post.objects.get(post_id=request.GET['post_id'])

    post_type = request.GET['post_type']

    return render(request,'post/manage_post.html',{'post':post, 'post_type2':post_type})


@login_required
def update_post(request):
    post = Post.objects.get(post_id=request.POST['post_id'])
    new_post_text = request.POST['post_text']
    new_can_view = request.POST['post_type']
    new_post_type = request.POST['content_type']
    post.post_text = new_post_text
    post.can_view = new_can_view
    post.post_type = new_post_type
    post.save()

    post_type2 = request.POST['post_type2']
    # print post_type2
    context = postContent(post_type2, request)
    return render(request, 'stream/mystream.html', context)
    #return HttpResponseRedirect(reverse('ViewMyStream'))

@login_required
def comment(request):
    author = User.objects.get(id = request.user.id)
    comment_text = request.GET['comment_text']
    post_id= request.GET['post_id']
    post = Post.objects.get(post_id = post_id)

    new_comment = Comment.create(author, comment_text, post)
    new_comment.save()

    post_type = request.GET['post_type']
    context= postContent(post_type,request)

    return render(request, 'stream/mystream.html', context)
    #return HttpResponseRedirect(reverse('ViewMyStream'), kwargs={'post_type':post_type})

def postContent(post_type,request):
    comments = Comment.objects.all()

    if str(post_type)== "my_post":
            post = Post.objects.filter(author = request.user).order_by('-pub_datetime')
    else:
        post= Post.objects.filter(can_view=0).order_by('-pub_datetime')
        #post2=Post.objects.filter(can_view=3).order_by('-pub_datetime')
        #print post

    context = { 'posts': post , 'comments': comments, 'post_type': post_type}

    return context

@login_required
def ViewMyStream(request):
    Posts = Post.objects.order_by('-pub_datetime')
    comments = Comment.objects.all()


    post_type = request.GET['post_type']
    context = postContent(post_type,request)
    return render(request, 'stream/mystream.html', context)

@login_required
def delete_post(request):
    myPost = request.GET['post_id']
    allPost = Post.objects.all()
    for i in allPost:
        if (str(i.post_id) == str(myPost)):
            i.delete()
    #return HttpResponseRedirect(reverse('ViewMyStream'))
    post_type = request.GET['post_type']
    context = postContent(post_type,request)
    return render(request, 'stream/mystream.html', context)


@login_required
def Add_friend(request):
    request_sender_id = request.POST['request_sender']
    request_receiver_id = request.POST['request_receiver']
    request_sender = User.objects.get(id=request_sender_id)
    request_receiver = User.objects.get(id=request_receiver_id)
    status = False
    new_request = friend_request.create(request_sender,request_receiver,status)
    new_request.save()


    return HttpResponseRedirect(reverse('profile'))
@login_required
def list_my_friend_request(request):
    friend_requests = friend_request.objects.get(request_receiver=request.user)
    #friend_requests = friend_request.objects.all()

    return JsonResponse(friend_requests,safe=False)

@login_required
def accept_friend(request):
    request_f = friend_request.objects.get(request_id=request.POST['request_id'])
    request_f.status = True
    request_f.save()
    profile_for_requester = Profile.objects.get(user=request_f.request_sender)
    profile_for_requestee = Profile.objects.get(user=request_f.request_receiver)
    profile_for_requester.friends.add(profile_for_requestee)
    profile_for_requestee.friends.add(profile_for_requester)
    profile_for_requester.save()
    profile_for_requestee.save()
    #profile.friends.add(request.request_sender)



    return HttpResponseRedirect(reverse('profile'))


def viewUnlistedPost(request, post_id):
    post = get_object_by_uuid_or_404(Post, post_id)

    # post_id = request.GET['post_id']
    unlistedPost = Post.objects.get(pk=post_id)
    context = { 'post': unlistedPost }

    return render(request, 'post/shared_post.html', context)

### reference by: http://brainstorm.it/snippets/get_object_or_404-for-uuids/
def get_object_by_uuid_or_404(model, uuid_pk):
    """
    Calls get_object_or_404(model, pk=uuid_pk)
    but also prevents "badly formed hexadecimal UUID string" unhandled exception
    """
    try:
        uuid.UUID(uuid_pk)
    except Exception, e:
        raise Http404(str(e))
    return get_object_or_404(model, pk=uuid_pk)