import os
import time

import numpy as np
import pandas as pd
import seaborn as sns
import vk
from tqdm import tqdm

load_dotenv()

API_KEY = os.getenv("API_KEY")
session = vk.Session(API_KEY)
api = vk.API(session, v="5.103", lang="ru", timeout=10)
from datetime import datetime


def get_user_data(ids):
    user = api.users.get(user_ids=ids, fields=["city", "country", "bdate", "sex"])
    return user
    


def parse_group():
    top_groups = {}
    members_counts = api.groups.getMembers(group_id="ic_tpu", offset=4000)["count"]
    print(members_counts)
    chunks = members_counts // 1000 + 1
    data = []
    for chunk in range(chunks):
        print(f"Data chunk №{chunk + 1}")
        members = api.groups.getMembers(group_id="ic_tpu", offset=chunk * 1000)["items"]
        data += (get_user_data(members))
    return data

def get_age(bdate):
    bdate = list(map(lambda x: int(x), bdate.split(".")))
    bdate = datetime(bdate[2], bdate[1], bdate[0])
    return (datetime.now() - bdate).days // 365



if __name__ == "__main__":
    print("Start parsing:")
    data = pd.DataFrame(parse_group())
    data['country'] = data['country'].apply(lambda x: x["title"] if type(x) == dict else x)
    data['city'] = data['city'].apply(lambda x: x["title"] if type(x) == dict else x)
    data['age'] = data['bdate'].apply(lambda x: get_age(x) if type(x) == str and len(x) > 7 else np.nan)
    data['sex'] = data['sex'].apply(lambda x: "Не указан" if x == 0 else x)
    data['sex'] = data['sex'].apply(lambda x: "Жен" if x == 1 else x)
    data['sex'] = data['sex'].apply(lambda x: "Муж" if x == 2 else x)
    data = data.loc[:, ["age", "sex", "country", "city"]]
    print("age")
    print(data["age"].dropna().mean())
    print(data["age"].dropna().median())
    print(data["age"].isna().value_counts()[1])
    print(data['sex'].value_counts())
    print(data['country'].dropna().value_counts())
    print(data["country"].isna().value_counts()[1])
    print(data['city'].dropna().value_counts())
    print(data["city"].isna().value_counts()[1])
