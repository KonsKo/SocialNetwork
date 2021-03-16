from rest_framework import status
from rest_framework.test import  APITestCase, APIClient

from django.contrib.auth.models import User
from django.utils import timezone

import datetime

from .models import UserSocial, Post, Emotion

class SocialNetworkTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User(username='testuser')
        self.user.set_password('testpassword')
        self.user.save()
        self.user_social = UserSocial.objects.create(
            user=self.user, last_login=timezone.now(), last_request=timezone.now()
        )
        self.post1 = Post.objects.create(user_by=self.user_social, title='title', body='body1')
        self.emotion1 = Emotion.objects.create(kind='like', post=self.post1, created_by=self.user_social)
        self.data = {'username': 'testuser', 'password': 'testpassword'}
        self.response_test = self.client.post('/api/user/login/', data=self.data)
        self.access_token = self.response_test.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

    def test_new_user_creation(self):
        data = {'username': 'new_user', 'password': 'newpassword1'}
        response = self.client.post('/api/user/new/', data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_user_getting_token(self):
        response = self.client.post('/api/user/login/', data=self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_token_refresh(self):
        response1 = self.client.post('/api/user/login/', data=self.data)
        refresh_token = response1.data.get('refresh')
        data2 = {'refresh': refresh_token }
        response2 = self.client.post('/api/user/refresh/', data=data2)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

    def test_no_token_no_data_check_urls(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ')
        response = self.client.get('/api/post/all/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.post('/api/post/new/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.post('/api/post/1/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_post_list(self):
        response = self.client.get('/api/post/all/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_creation(self):
        data = {'title': 'new', 'body':'new'}
        response = self.client.post('/api/post/new/', data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_like_dislike_processing(self):
        post = Post.objects.create(user_by=self.user_social, title='title2', body='body12')
        data1 = {'kind': 'lik'}
        url1 = '/api/post/' + str(post.id) + '/'
        response1 = self.client.post(url1, data=data1)
        self.assertNotEqual(response1.status_code, status.HTTP_201_CREATED)

        data2 = {'kind': 'like'}
        url2 = '/api/post/' + str(self.post1.id) + '/'
        response2 = self.client.post(url2, data=data2)
        self.assertNotEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertIn('already exists', response2.data[0])

        data3 = {'kind': 'like'}
        url3 = '/api/post/' + str(post.id) + '/'
        response3 = self.client.post(url3, data=data3)
        self.assertEqual(response3.status_code, status.HTTP_201_CREATED)

    def test_user_statistic(self):
        response = self.client.get('/api/user/stat/all/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.is_staff = True
        self.user.save()
        response = self.client.get('/api/user/stat/all/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/api/user/stat/' + str(self.user_social.id) + '/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_analytics(self):
        response = self.client.get('/api/analytics/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.is_staff = True
        self.user.save()
        response = self.client.get('/api/analytics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_analytics_range_by_dates(self):
        self.user.is_staff = True
        self.user.save()
        
        post = Post.objects.create(user_by=self.user_social, title='title2', body='body2')
        emotion1 = Emotion.objects.create(post=post, kind='like', created_by=self.user_social)
        response = self.client.get('/api/analytics/')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0].get('date'), str(timezone.now().date()))
        self.assertEqual(response.data[0].get('quantity'), 2)

        post2 = Post.objects.create(user_by=self.user_social, title='title22', body='body22')
        emotion2 = Emotion.objects.create(post=post2, kind='dislike', created_by=self.user_social, 
                                          created=datetime.datetime.strptime('10 March, 2020', '%d %B, %Y'))
        response = self.client.get('/api/analytics/')
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[1].get('date'), str(timezone.now().date()))
        self.assertEqual(response.data[0].get('date'), '2020-03-10')
        self.assertEqual(response.data[1].get('quantity'), 2)
        self.assertEqual(response.data[0].get('quantity'), 1)

