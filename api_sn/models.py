from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# User dependent model created for convenience
# 'last_login' - date and time when user got both tokens url='user_login'
# 'last_request' - last not anonymous request (update token - anonymous request)
class UserSocial(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_login = models.DateTimeField(verbose_name='Last user login')
    last_request = models.DateTimeField(verbose_name='Last user request to service')

    def __str__(self):
        return self.user.username


# Blog post model
class Post(models.Model):
    user_by = models.ForeignKey(UserSocial, blank=False, null=False, on_delete=models.CASCADE,
                                verbose_name='Post created by user')
    title = models.CharField(max_length=64, blank=False, verbose_name='Post title')
    body = models.CharField(max_length=256, blank=False, verbose_name='Post body')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# Model for processing 'like-dislike options'
# 'created' with default for convenient development and testing (changeable)
# 'unique_together' for condition processing: one user can provide only one emotion for post
class Emotion(models.Model):
    KIND = (
        ('like', 'like'),
        ('dislike', 'dislike'),
    )
    kind = models.CharField(max_length=8, choices=KIND, verbose_name='Like or Dislike')
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_by = models.ForeignKey(UserSocial, blank=False, null=False, on_delete=models.CASCADE,
                                   verbose_name='Emotion created by user')
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '{} for {}'.format(self.kind, self.post.title)

    class Meta:
        unique_together = [['post', 'created_by']]
