from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_pic = models.ImageField(upload_to="profile_pics",default="static/images/profilepic.png",null=True,blank=True)
    name = models.CharField(max_length=100, null=True)
    bio = models.TextField(max_length=250, blank=True)
    address = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=20, null=True)
    dob = models.DateField(null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    following = models.ManyToManyField("self", related_name="followed_by", null=True, symmetrical=False)
    block = models.ManyToManyField("self", related_name="blocked", symmetrical=False, null=True)

    def __str__(self):
        return self.user.username


class Posts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userpost")
    title = models.CharField(max_length=200)
    content = models.FileField(upload_to="posts", null=True, blank=True)
    likes = models.ManyToManyField(User, related_name="post_like", blank=True)
    saves = models.ManyToManyField(User, related_name="postsave", blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    

class Comments(models.Model):
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name="post_comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment")
    text = models.CharField(max_length=200)
    # comment_reply = models.ForeignKey('self',null=True, blank=True, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.text


class Stories(models.Model):
    user = models.ForeignKey(User, related_name="userstories", on_delete=models.CASCADE)
    post_content = models.FileField(upload_to="stories", null=True, blank=True)
    text_content = models.CharField(max_length=200, null=True, blank=True)
    # story_reply = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    #exp = created_date + timezone.timedelta(days=1)

    def __str__(self):
        return self.user.username
    
    def save(self, *args, **kwargs):
        if not self.expiry_date:
            self.expiry_date = timezone.now()+timezone.timedelta(days=1)
        super().save(*args, **kwargs)


def create_profile(sender,instance,created,**kwargs):
    if created:
        UserProfile.objects.create(user=instance)
post_save.connect(sender=User, receiver=create_profile)



    


    






