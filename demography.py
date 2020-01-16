import os
import time
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import vk
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

API_KEY = os.getenv("API_KEY")
session = vk.Session(API_KEY)
api = vk.API(session, v="5.103", lang="ru", timeout=10)


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
        data += get_user_data(members)
    return data


def get_age(bdate):
    bdate = list(map(lambda x: int(x), bdate.split(".")))
    bdate = datetime(bdate[2], bdate[1], bdate[0])
    return (datetime.now() - bdate).days // 365


if __name__ == "__main__":
    print("Start parsing:")
    data = pd.DataFrame(parse_group())

    data["country"] = data["country"].apply(
        lambda x: x["title"] if type(x) == dict else x
    )
    data["city"] = data["city"].apply(lambda x: x["title"] if type(x) == dict else x)

    data["age"] = data["bdate"].apply(
        lambda x: get_age(x) if type(x) == str and len(x) > 7 else np.nan
    )

    data["sex"] = data["sex"].apply(lambda x: "Не указан" if x == 0 else x)
    data["sex"] = data["sex"].apply(lambda x: "Жен" if x == 1 else x)
    data["sex"] = data["sex"].apply(lambda x: "Муж" if x == 2 else x)

    data = data.loc[:, ["age", "sex", "country", "city"]]

    print("\nВозраст участников сообщества:")
    print(f"Средний возраст: {data['age'].dropna().mean()}")
    print(f"Медиана возраста: {data['age'].dropna().median()}")
    print(
        f"Количество людей с неуказанным возрастом: {data['age'].isna().value_counts()[1]}"
    )

    data.loc[data["age"] <= 18, "age_cat"] = "Младше 18"
    data.loc[(data["age"] > 18) & (data["age"] <= 25), "age_cat"] = "От 18 до 25"
    data.loc[(data["age"] > 25) & (data["age"] <= 40), "age_cat"] = "От 25 до 40"
    data.loc[(data["age"] > 40) & (data["age"] <= 65), "age_cat"] = "От 40 до 65"
    data.loc[data["age"] > 65, "age_cat"] = "Старше 65"
    data["age_cat"].value_counts().plot(
        title="Распределение возрастов", kind="pie", autopct="%1.1f%%"
    )
    plt.show()

    print("\nРаспределение полов в сообществе:")
    print(data["sex"].value_counts())
    data["sex"].value_counts().plot(
        title="Распределение полов", kind="pie", autopct="%1.1f%%"
    )
    plt.show()

    print("\n5 распространенных стран участников:")
    print(data["country"].dropna().value_counts().head(5))
    print(
        f"Количество людей с неуказанной страной: {data['country'].isna().value_counts()[1]}"
    )
    data.loc[:, "Популярные страны",] = data["country"]
    data.loc[
        ~data["country"].isin(data["country"].dropna().value_counts().head(5).index),
        "Популярные страны",
    ] = "Остальные страны"
    data["Популярные страны"].value_counts().plot(
        title="Распределение стран", kind="pie", autopct="%1.1f%%"
    )
    plt.show()

    print("\n5 распространенных городов участников:")
    print(data["city"].dropna().value_counts().head(5))
    print(
        f"Количество людей с неуказанным городом: {data['city'].isna().value_counts()[1]}"
    )
    data.loc[:, "Популярные города",] = data["city"]
    data.loc[
        ~data["city"].isin(data["city"].dropna().value_counts().head(5).index),
        "Популярные города",
    ] = "Остальные города"
    data["Популярные города"].value_counts().plot(
        title="Распределение городов", kind="pie", autopct="%1.1f%%"
    )
    plt.show()
