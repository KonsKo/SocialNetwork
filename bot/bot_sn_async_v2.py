import random
import requests
import asyncio
from aiohttp import ClientSession
import datetime
import json

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

# count time
start_time = datetime.datetime.now()

# function for create random user and password
def create_random_user():
    username = 'user_{}_{}'.format(random.choice(WORDS).decode('utf-8'), str(random.randrange(100)))
    password = '{}{}'.format(
        random.choice([word for word in WORDS if len(word) > 8]).decode('utf-8'),
        str(random.randrange(100))
    )
    data_user = {'username': username, 'password': password}
    return data_user

# function for create random post title and body
def create_random_post():
    post_title = 'Post title {}'.format(
        random.choice(WORDS).decode('utf-8')
    )
    post_body = 'Three random words: {} {} {} '.format(
        random.choice(WORDS).decode('utf-8'),
        random.choice(WORDS).decode('utf-8'),
        random.choice(WORDS).decode('utf-8')
    )
    data_post = {'title': post_title, 'body': post_body}
    return data_post

##########################################################################################################3

# function for get existing post ids for like processing
async def get_posts_ids(session, headers):
      async with session.get(url_post_all, headers=headers) as response:
            ids = [int(post['id']) for post in await response.json()]
            return ids


# 'like' processing, we wait until post creating process is ended
async def fetch_like(session, headers):
    ids = await get_posts_ids(session, headers)
    try:
        post_id = random.choice(ids)
    except:
        post_id = random.randint(1, 100)
    url_like = r'{}{}/'.format(url_post_do, post_id)
    data_emotion = {'kind': 'like'}
    async with session.post(url_like, headers=headers, data=data_emotion) as response:
        print('fetch4', response.status)


# 'post' processing, we wait until all users logged in
async def fetch_post(session, headers):
    async with session.post(url_post_new, headers=headers, data=create_random_post()) as response:
        print('fetch3', response.status)


# user logging in, we wait until all users were created
async def fetch_user_log(session, data_user, tasks_user_create):
    async with session.post(url_user_login, data=data_user) as response:
        print(response.status)
        access_token = (await response.json())["access"]
        headers = {'Authorization': f'Bearer {access_token}'}

        for _ in range(max_posts_per_user):
            task3 = asyncio.ensure_future(fetch_post(session, headers))
            tasks_user_create.append(task3)

        for _ in range(max_likes_per_user):
            task4 = asyncio.ensure_future(fetch_like(session, headers))
            tasks_user_create.append(task4)

# user creation
async def fetch_user_create(session, data_user, tasks_user_create):
    async with session.post(url_user_create, data=data_user) as response:
        print(response.status)
        task2 = asyncio.ensure_future(fetch_user_log(session, data_user, tasks_user_create))
        tasks_user_create.append(task2)

async def run():
    tasks_user_create = []
    async with ClientSession() as session:
        for i in range(number_of_user):
            data_user = create_random_user()
            task = asyncio.ensure_future(fetch_user_create(session, data_user, tasks_user_create))
            tasks_user_create.append(task)

        while tasks_user_create:
            old_cnt = len(tasks_user_create)
            await asyncio.gather(*tasks_user_create)
            del tasks_user_create[:old_cnt]

    print('finish time', datetime.datetime.now() - start_time)

loop = asyncio.get_event_loop()
future = asyncio.ensure_future(run())
loop.run_until_complete(future)
loop.close()

