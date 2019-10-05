import os
import time

import vk
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
print(API_KEY)
session = vk.Session(API_KEY)
api = vk.API(session, v='5.101', lang='ru', timeout=10)

groups = api.groups.getMembers(group_id="weirdreparametrizationtrick")

def get_user_group(id):
    return api.users.getSubscriptions(user_id=id)

for item in groups["items"]:
    try:
        print(get_user_group(item))
    except vk.exceptions.VkAPIError as e:
        print(e)
    time.sleep(1)

print(groups)

print(get_user_group(449))
