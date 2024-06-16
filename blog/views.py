from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from blog.forms import RegistrationForm, LoginForm, UserProfileForm, PostForm, CommentForm, StoryForm, UserSearchForm
from django.contrib.auth import authenticate, login, logout
from blog.models import Posts, UserProfile, Stories, User, Comments
from django.utils import timezone
from django.urls import reverse
from blog.decorators import signin_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib import messages

#decorator :
decs = [signin_required,never_cache]


# Create your views here.

#url: localhost:8000/register/
#method: get, post

class SignUpView(View):

    def get(self, request, *args, **kwargs):
        form = RegistrationForm()
        return render(request, "register.html", {"form":form})
    
    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("signin")
        return render(request, "login.html", {"form":form})
    

#url: localhost:8000/
#method: get, post
    
class SignInView(View):

    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return render(request, "login.html", {"form":form})
    
    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            uname = form.cleaned_data.get("username")
            pwd = form.cleaned_data.get("password")
            user_object = authenticate(request, username=uname, password=pwd)
            if user_object:
                login(request, user_object)
                return redirect("home")
            
        messages.error(request,"Failed to login invalid credentials")
        return render(request, "login.html", {"form":form})
    

#url: localhost:8000/home/
#method: get, post
    
@method_decorator(decs, name='dispatch')
class HomeView(View):

    def get(self, request, *args, **kwargs):

        # Fetch the following users and their IDs     
        following_users = request.user.profile.following.all()
        following_user_ids = [user.user_id for user in following_users]

        # Fetch posts of the logged-in user and the users they are following
        qs= Posts.objects.filter(user__in=following_user_ids) | Posts.objects.filter(user=request.user).order_by("-created_date")
        
        current_date=timezone.now()

        # Filter stories to include only stories of the logged-in user and the users they are following
        stories = Stories.objects.filter(user_id__in=following_user_ids, expiry_date__gte=current_date) | Stories.objects.filter(user=request.user, expiry_date__gte=current_date).order_by("-created_date")
    
        context = {
            'data': qs,
            'stories': stories,
        }
        return render(request, 'home.html', context)

    def post(self, request, *args, **kwargs):

        # Handle post uploading form submission
        form = PostForm(request.POST, files=request.FILES)
        if form.is_valid():
            form.instance.user=request.user
            form.save()    
            return redirect('home')
        return render(request, 'home.html', {'form':form})
    

#url: localhost:8000/signout/
#method: get
    
class SignOutView(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("signin")


#url: localhost:8000/profiles/{id}/change/
#method: get, post
    
@method_decorator(decs, name='dispatch')
class ProfileUpdateView(View):

    def get(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        userprofile_object = UserProfile.objects.get(id=id)
        form = UserProfileForm(instance=userprofile_object)
        return render(request, "profile_edit.html", {"form":form})
    
    def post(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        userprofile_object = UserProfile.objects.get(id=id)
        form = UserProfileForm(request.POST, files=request.FILES, instance=userprofile_object)

        if form.is_valid():
            form.save()
            return redirect("profile-detail", pk=id)
        return render(request, "profile_edit.html", {"form":form})


#url: localhost:8000/profiles/{id}/
#method: get
    
@method_decorator(decs, name='dispatch')
class ProfileDetailView(View):
    
    def get(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        qs = UserProfile.objects.get(id=id)
        post = Posts.objects.filter(user=qs.user).order_by("-created_date")
        
        # Check if the profile being viewed is the profile of the logged-in user
        is_own_profile = qs.user == request.user

        return render(request, "profile_detail.html", {"data":qs, "post":post, "is_own_profile":is_own_profile})
    

#url: localhost:8000/profiles/all/
#method: get
    
@method_decorator(decs, name='dispatch')
class ProfileListView(View):

    def get(self, request, *args, **kwargs):
        qs = UserProfile.objects.all().exclude(user=request.user)
        return render(request, "profile_list.html", {"data":qs})
    

#url: localhost:8000/profiles/{id}/follow/
#method: post
    
@method_decorator(decs, name='dispatch')
class FollowView(View):

    def post(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        user_object = UserProfile.objects.get(id=id)

        action = request.POST.get('action')

        if action == 'follow':
            request.user.profile.following.add(user_object)
        elif action== 'unfollow':
            request.user.profile.following.remove(user_object)

        return redirect('profile-detail',pk=id)


#url: localhost:8000/profiles/{id}/block/
#method: post
    
@method_decorator(decs, name='dispatch')
class ProfileBlockView(View):

    def post(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        user_object = UserProfile.objects.get(id=id)

        action = request.POST.get('action')

        if action == 'block':
            request.user.profile.block.add(user_object)

            # Automatically unfollow the user if they are being blocked
            request.user.profile.following.remove(user_object)
            # Automatically remove the user from your following list
            user_object.following.remove(request.user.profile)

        elif action== 'unblock':
            request.user.profile.block.remove(user_object)

        return redirect('home')


#url: localhost:8000/profiles/{id}/posts/
#method: get

@method_decorator(decs, name='dispatch')
class ProfilePostview(View):

    def get(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        post = Posts.objects.filter(id=id)
        return render(request, "profile_post.html", {"data":post})


#url: localhost:8000/post/{id}/like/
#method: post
@method_decorator(decs, name='dispatch')
class PostLikeView(View):

    def post(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        post_object = Posts.objects.get(id=id)

        action = request.POST.get('action')

        if action == 'like':
            post_object.likes.add(request.user)
        elif action == 'unlike':
            post_object.likes.remove(request.user)
        elif action == 'save':
            post_object.saves.add(request.user)
        elif action == 'unsave':
            post_object.saves.remove(request.user)

        return redirect('home')
    
#url: localhost:8000/post/{id}/comments/add/
#method: post
    
@method_decorator(decs, name='dispatch')
class CommentView(View):

    def post(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        post_object = Posts.objects.get(id=id)
        form = CommentForm(request.POST)

        if form.is_valid():
           form.instance.user = request.user
           form.instance.post= post_object
           form.save()
           return redirect('home')
        
        return render(request, 'home.html', {'form':form})


@method_decorator(decs, name='dispatch')
class CommentDeleteView(View):
    
    def post(self, request, *args, **kwargs):
        comment_id = kwargs.get('comment_id')  # Fetching comment_id from URL kwargs
        comment = get_object_or_404(Comments, id=comment_id)
        
        # Check if the logged-in user is the owner of the comment
        if request.user == comment.user:
            comment.delete()
        
        # Redirect to the homepage after deleting the comment
        return redirect('home')
    

#url: localhost:8000/post/{id}/remove/
#method: get
    
@method_decorator(decs, name='dispatch')
class PostDeleteView(View):

    def get(self, request, *args, **kwargs):
        id=kwargs.get('pk')
        Posts.objects.get(id=id).delete()
        return redirect('home')
    

#url: localhost:8000/stories/add/
#method: post
    
@method_decorator(decs, name='dispatch')
class StoryCreateView(View):

    def post(self, request, *args, **kwargs):
        form = StoryForm(request.POST, files=request.FILES)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            return redirect('home')
        return redirect('home')
    

@method_decorator(decs, name='dispatch')
class StoryDeleteView(View):

    def post(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        story_object = get_object_or_404(Stories, id=id)

        # Check if the user is authorized to delete the story
        if request.user == story_object.user:
            story_object.delete()

        return redirect('home')
    

#url: localhost:8000/profiles/posts/add/
#method: post
    
@method_decorator(decs, name='dispatch')
class PostCreateView(View):

    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST, files=request.FILES)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            return redirect(reverse('profile-detail', kwargs={'pk': request.user.profile.pk}))
        return redirect('profile-detail')
    

#url: localhost:8000/search/
#method: get, post
    
@method_decorator(decs, name='dispatch')
class SearchView(View):

    def get(self, request, *args, **kwargs):
        form = UserSearchForm()
        return render(request, 'search_results.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = UserSearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            users = User.objects.filter(username__icontains=query)
            return render(request, 'search_results.html', {'users': users, 'query': query})
        return redirect('home')
    







        


        

