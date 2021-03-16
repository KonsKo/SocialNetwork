from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView
from rest_framework import permissions
from rest_framework.exceptions import ValidationError as s_ValidationError

from rest_framework_simplejwt.views import TokenObtainPairView

from django_filters.rest_framework import DjangoFilterBackend

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Count

from .models import Post, UserSocial, Emotion
from .filters import AnalyticsFilter
from .serializers import (CreateUserSerializer,
                          PostSerializer,
                          MyTokenSerializer,
                          EmotionSerializer,
                          UserStatisticSerializer,
                          AnalyticsSerializer)


# New user creation and connect with our user dependent model
# we have to process 'set_password' for password creating
class CreateUserView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer

    def perform_create(self, serializer):
        user = User.objects.create(username=serializer.data['username'])
        user.set_password(serializer.data['password'])
        user.save()
        user_social = UserSocial(user=user, last_login=timezone.now(), last_request=timezone.now())
        user_social.save()


# Post processing
# There is 'list' point with url 'posts_all': if we want make 'like-dislike'
# we want get list of posts. There is no limit for list size.
# There is 'create' point for creation purpose
class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        user_social = UserSocial.objects.get(user=self.request.user)
        serializer.save(user_by=user_social)


# Override TokenObtainPairView because override TokenObtainPairSerializer
class MyToken(TokenObtainPairView):
    serializer_class = MyTokenSerializer


# 'like-dislike' creation
# 'perform_create' for convenience (we can do it in serializer)
# 'full_clean' because DRF does nor processing model exceptions
class EmotionViewSet(ModelViewSet):
    queryset = Emotion.objects.all()
    serializer_class = EmotionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        kind = serializer.data['kind']
        user_social = UserSocial.objects.get(user=self.request.user.id)
        emotion = Emotion(post=post, kind=kind, created_by=user_social)
        try:
            emotion.full_clean()
            emotion.save()
        except ValidationError as e:
            raise s_ValidationError(e.messages)


class UserStatisticViewSet(ModelViewSet):
    queryset = UserSocial.objects.all()
    serializer_class = UserStatisticSerializer
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser,)


# 'like-dislike' analytics by date
# There is no separation 'likes' and 'dislikes'
# There is no limits for data
class AnalyticsViewSet(ModelViewSet):
    serializer_class = AnalyticsSerializer
    filterset_class = AnalyticsFilter
    filter_backends = (DjangoFilterBackend,)
    search_fields = ['date_from', 'date_to',]
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser,)

    def get_queryset(self):
        self.queryset = Emotion.objects.values('created__date').\
            annotate(count=Count('created__date')).\
            order_by('created__date')
        return self.queryset


