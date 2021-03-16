from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenObtainSerializer

from .models import Post, UserSocial, Emotion


# Serializer for user creation
class CreateUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']

    def validate_password(self, value):
        validate_password(value)
        return value


# Serializer for processing blog posts
# init method removes field if create post
class PostSerializer(ModelSerializer):
    user_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'created', 'user_by']

    def __init__(self, *args, **kwargs):
        if kwargs['context']['view'].action == 'create':
            del self.fields['user_by']
        super().__init__(*args, **kwargs)


# Override TokenObtainPairSerializer for processing user login
class MyTokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        login(self.context['request'], self.user)
        return data


# Serializer for 'like-dislike' creation
class EmotionSerializer(ModelSerializer):
    class Meta:
        model = Emotion
        fields = ['kind']


# Serializer for user statistic creation
class UserStatisticSerializer(ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = UserSocial
        fields = '__all__'


# Serializer for user emotions analytics creation
class AnalyticsSerializer(serializers.Serializer):
    date = serializers.DateField(source='created__date')
    quantity = serializers.IntegerField(source='count')




