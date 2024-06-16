from django.urls import path
from blog import views


urlpatterns = [
    
    path("register/", views.SignUpView.as_view(), name="signup"),
    path("", views.SignInView.as_view(), name="signin"),
    path("home/", views.HomeView.as_view(), name="home"),
    path("signout/", views.SignOutView.as_view(), name="signout"),
    path("profiles/<int:pk>/change/", views.ProfileUpdateView.as_view(), name="profile-update"),
    path("profiles/<int:pk>/", views.ProfileDetailView.as_view(), name="profile-detail"),
    path("profiles/all/", views.ProfileListView.as_view(), name="profile-list"),
    path("profiles/<int:pk>/follow/", views.FollowView.as_view(), name="follow"),
    path("profiles/<int:pk>/block/", views.ProfileBlockView.as_view(), name="block"),
    path("profiles/<int:pk>/posts/", views.ProfilePostview.as_view(), name="profile-post"),
    path("post/<int:pk>/like/", views.PostLikeView.as_view(), name="like"),
    path("post/<int:pk>/comments/add/", views.CommentView.as_view(), name="comment"),
    path("post/<int:pk>/remove/", views.PostDeleteView.as_view(), name="post-delete"),
    path("stories/add/", views.StoryCreateView.as_view(), name="story-create"),
    path("profiles/posts/add/", views.PostCreateView.as_view(), name="post-create"),
    path("search/", views.SearchView.as_view(), name="search"),   
    

]