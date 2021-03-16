from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from .views import PostViewSet, CreateUserView, MyToken, EmotionViewSet, UserStatisticViewSet, AnalyticsViewSet


# All urls in one place because it is test project
# In real project best way is divide some urls
# (for example: user processing, statistic processing, app processing)
urlpatterns = [

    path('user/new/', CreateUserView.as_view(), name='user_create'),
    path('user/login/', MyToken.as_view(), name='user_login'),
    path('user/refresh/', TokenRefreshView.as_view(), name='user_refresh'),

    path('user/stat/<int:pk>/', UserStatisticViewSet.as_view({'get': 'retrieve'}), name='user_stat'),
    path('user/stat/all/', UserStatisticViewSet.as_view({'get': 'list'}), name='users_list'),
    path('analytics/', AnalyticsViewSet.as_view({'get': 'list'}), name='analytics'),

    path('post/all/', PostViewSet.as_view({'get': 'list'}), name='posts_all'),
    path('post/new/', PostViewSet.as_view({'post': 'create'}), name='post_create'),

    path('post/<int:pk>/', EmotionViewSet.as_view({'post': 'create'}), name='like_dislike'),

]
