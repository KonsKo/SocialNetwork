import pandas as pd

import requests
import json
import random
import time

# load settings
with open('settings.json', 'r') as settings_file:
    settings = json.load(settings_file)

url_user_create = settings["url_user_create"]
url_user_login = settings["url_user_login"]
url_post_new = settings["url_post_new"]
url_post_do = settings["url_post_do"]
url_post_all = settings["url_post_all"]

# load config
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

number_of_user = config["number_of_users"]
max_posts_per_user = config["max_posts_per_user"]
max_likes_per_user = config["max_likes_per_user"]

# load list of words for random data generation
word_site = "https://www.mit.edu/~ecprice/wordlist.10000"
response = requests.get(word_site)
WORDS = response.content.splitlines()

df_users = pd.DataFrame(columns=['username', 'status', 'info'])
df_posts = pd.DataFrame(columns=['username', 'post_name', 'status'])
df_likes = pd.DataFrame(columns=['username', 'post_id', 'status'])

# main cycle
for user in range(number_of_user):

    # create random user
    username = 'user_{}_{}'.format(random.choice(WORDS).decode('utf-8'), str(random.randrange(100)))
    password = '{}{}'.format(
        random.choice([word for word in WORDS if len(word) > 8]).decode('utf-8'),
        str(random.randrange(100))
    )
    data_user = {'username': username, 'password': password}
    response_create = requests.post(url_user_create, data=data_user)

    # write data about user to df
    df_users = df_users.append(
        {
            'username': username,
            'status': response_create.status_code},
        ignore_index=True
    )

    # if user was created successfully than log in user and get token
    # else go to nest user
    if response_create.status_code == 201:
        response_login = requests.post(url_user_login, data=data_user)
        access_token = (json.loads(response_login.content))["access"]
    else:
        continue

    # if user was logged in than write token
    if response_login.status_code == 200:
        headers = {'Authorization': f'Bearer {access_token}'}
    else:
        continue

    # user has to make particular quantity of posts
    for post in range(max_posts_per_user):
        post_title = f'Post title {post+1} from {username}'
        post_body = 'Three random words: {} {} {} '.format(
            random.choice(WORDS).decode('utf-8'),
            random.choice(WORDS).decode('utf-8'),
            random.choice(WORDS).decode('utf-8')
        )
        data_post = {'title': post_title, 'body': post_body}
        response_post = requests.post(url_post_new, headers=headers, data=data_post)

        # write info about post creation process
        df_posts = df_posts.append(
            {
                'username': username,
                'status': response_post.status_code,
                'post_name': post_title
            },
            ignore_index=True
        )

    # get id's of existing post for emotions process
    response_post_all = requests.get(url_post_all, headers=headers)
    post_all = json.loads(response_post_all.content)
    post_ids = [post["id"] for post in post_all]

    # if quantity of available post less 'max_likes_per_user'
    # we can not process all likes
    if len(post_ids) < max_likes_per_user:
        df_users.at[df_users['username'] == username, 'info'] = 'Not maximum likes'
        like_marker = len(post_ids)
    else:
        like_marker = max_likes_per_user

    # process 'likes', do it while make all likes
    while like_marker > 0:
        post_id = random.choice(post_ids)
        url_to_emotion = r'{}{}/'.format(url_post_do, post_id)
        data_emotion = {'kind': 'like'}
        response_emotion = requests.post(url_to_emotion, headers=headers, data=data_emotion)

        if response_emotion.status_code == 201:
            like_marker -= 1
            post_ids.remove(post_id)

        df_likes = df_likes.append(
            {
                'username': username,
                'post_id': post_id,
                'status': response_emotion.status_code
            },
            ignore_index=True
        )

    time.sleep(1)


print(df_users)
print(df_posts)
print(df_likes)
