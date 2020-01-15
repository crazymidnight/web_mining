import os
import time

import numpy as np
import pandas as pd
import seaborn as sns
import networkx
import vk
from tqdm import tqdm_notebook as tqdm

load_dotenv()

API_KEY = os.getenv("API_KEY")
session = vk.Session(API_KEY)
api = vk.API(session, v="5.103", lang="ru", timeout=10)
from datetime import datetime

def get_user_friends(id):
    friends = api.friends.get(user_id=id)
    return friends
    


def parse_group():
    users_friends = {}
    members_counts = api.groups.getMembers(group_id="ic_tpu", offset=4000)["count"]
    print(members_counts)
    chunks = members_counts // 1000 + 1
    data = {}
    for chunk in range(chunks):
        print(f"Data chunk №{chunk + 1}")
        members = api.groups.getMembers(group_id="ic_tpu", offset=chunk * 1000)["items"]
        for member in members:
            try:
                data[member] = get_user_friends(member)
            except vk.exceptions.VkAPIError as e:
                data[member] = "Private account"
                continue
            
    return data

if __name__ == "__main__":
    print("Start parsing:")
    data = parse_group()
    print(data)
