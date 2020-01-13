import os
import time

import pandas as pd
import vk
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

API_KEY = os.getenv("API_KEY")
session = vk.Session(API_KEY)
api = vk.API(session, v="5.103", lang="ru", timeout=10)


def get_user_group(id):
    return api.users.getSubscriptions(user_id=id, extended=1, count=199)


def parse_group():
    top_groups = {}
    members_counts = api.groups.getMembers(group_id="ic_tpu", offset=4000)["count"]
    print(members_counts)
    chunks = members_counts // 1000 + 1
    for chunk in range(chunks):
        print(f"Data chunk №{chunk + 1}")
        members = api.groups.getMembers(group_id="ic_tpu", offset=chunk * 1000)
        for item in tqdm(members["items"]):
            try:
                items = get_user_group(item)["items"]
                user_groups = []
                for item in items:
                    if item["type"] != "profile":
                        user_groups.append(item["screen_name"])
            except vk.exceptions.VkAPIError as e:
                continue

            top_keys = top_groups.keys()
            for group in user_groups:
                if group in top_keys:
                    top_groups[group] += 1
                else:
                    top_groups[group] = 1
    return top_groups


if __name__ == "__main__":
    print("Start parsing:")
    groups = parse_group()
    df = pd.DataFrame()
    df["count"] = pd.Series(groups).nlargest(10)
    print("Top 10:")
    print(df)
    print("Save to CSV")
    df.to_csv("groups.csv")
