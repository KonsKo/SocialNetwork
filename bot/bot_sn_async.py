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

# function for get existing post ids for like processing
async def get_posts_ids(session, headers):
    async with session.get(url_post_all, headers=headers) as response:
        return await response.read()

#def combine(response_user, response_token):
#    user_token_data = []
#    for i in range(len(response_user)):
#        user = json.loads(response_user[i])
#        token = json.loads(response_token[i])
#        user["access"] = token.get("access")
#        user_token_data.append(user)
#    return user_token_data

# 'like' processing, we wait until post creating process is ended
async def fetch_like(session, headers, post_id, tasks_user_log):
    await asyncio.wait(tasks_user_log)
    url_like = r'{}{}/'.format(url_post_do, post_id)
    data_emotion = {'kind': 'like'}
    async with session.post(url_like, headers=headers, data=data_emotion) as response:
        print('fetch4', response.status)
        return await response.read()

# 'post' processing, we wait until all users logged in
async def fetch_post(session, data_post, headers, tasks_user_log):
    await asyncio.wait(tasks_user_log)
    async with session.post(url_post_new, headers=headers, data=data_post) as response:
        print('fetch3', response.status)
        return await response.read()

# user logging in, we wait until all users were created
async def fetch_user_log(session, data_user, tasks_user_create):
    await asyncio.wait(tasks_user_create)
    async with session.post(url_user_login, data=data_user) as response:
        print(response.status)
        return await response.read()

# user creation
async def fetch_user_create(session, data_user):
    async with session.post(url_user_create, data=data_user) as response:
        print(response.status)
        return await response.read()

async def run():
    tasks_user_create = []
    tasks_user_log = []
    tasks_post_likes = []
    #tasks_like = []
    async with ClientSession() as session:
        for i in range(number_of_user):
            data_user = create_random_user()
            task = asyncio.ensure_future(fetch_user_create(session, data_user))
            tasks_user_create.append(task)
            task2 = asyncio.ensure_future(fetch_user_log(session, data_user, tasks_user_create))
            tasks_user_log.append(task2)
        responses = await asyncio.gather(*tasks_user_create)
        responses2 = await asyncio.gather(*tasks_user_log)

        for resp in responses2:
            access_token = (json.loads(resp))["access"]
            headers = {'Authorization': f'Bearer {access_token}'}

            task_all_posts = asyncio.ensure_future(get_posts_ids(session, headers))
            response_all_posts = await asyncio.gather(task_all_posts)
            post_ids_list = json.loads(response_all_posts[0])
            post_ids = [i.get('id') for i in post_ids_list]

            for p in range(max_posts_per_user):
                data_post = create_random_post()
                task3 = asyncio.ensure_future(fetch_post(session, data_post, headers, tasks_user_log))
                tasks_post_likes.append(task3)

            for l in range(max_likes_per_user):
                post_id = random.choice(post_ids)
                task4 = asyncio.ensure_future(fetch_like(session, headers, post_id, tasks_user_log))
                tasks_post_likes.append(task4)
                post_ids.remove(post_id)

        responses3 = await asyncio.gather(*tasks_post_likes)
        #responses4 = await asyncio.gather(*tasks_like)

        print('finish time', datetime.datetime.now() - start_time)

loop = asyncio.get_event_loop()
future = asyncio.ensure_future(run())
loop.run_until_complete(future)
