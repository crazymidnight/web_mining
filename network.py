import os
import time
from datetime import datetime

import networkx as nx
import numpy as np
import pandas as pd
import vk
from dotenv import load_dotenv
from tqdm import tqdm

import matplotlib.pyplot as plt
import networkx.algorithms.centrality as nxa

load_dotenv()

API_KEY = os.getenv("API_KEY")
session = vk.Session(API_KEY)
api = vk.API(session, v="5.103", lang="ru", timeout=10)


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
        for member in tqdm(members):
            try:
                data[member] = [
                    (member, friend)
                    for friend in get_user_friends(member)["items"]
                    if friend in members
                ]
            except vk.exceptions.VkAPIError as e:
                # data[member] = (member, None)
                continue

    return data


def create_graph(data):
    G = nx.Graph()
    G.add_nodes_from(data.keys())
    for key in data.keys():
        G.add_edges_from(data[key])
    print(f"Number of nodes: {G.number_of_nodes()}")
    print(f"Number of edges: {G.number_of_edges()}")
    return G


def draw_graph(G):
    nx.draw(G, node_size=30)
    plt.show()


if __name__ == "__main__":
    print("Start parsing:")
    data = parse_group()
    G = create_graph(data)
    draw_graph(G)

    degree = pd.Series(nxa.degree_centrality(G)).idxmax()
    closeness = pd.Series(nxa.closeness_centrality(G)).idxmax()
    eigenvector = pd.Series(nxa.eigenvector_centrality(G)).idxmax()
    betweennes = pd.Series(nxa.betweenness_centrality(G)).idxmax()

    degree_user = api.users.get(user_ids=degree)[0]
    closeness_user = api.users.get(user_ids=closeness)[0]
    eigenvector_user = api.users.get(user_ids=eigenvector)[0]
    betweeness_user = api.users.get(user_ids=betweennes)[0]

    print("Most important user:")
    print(
        f"Degree centrality: id{degree} - {degree_user['first_name'] + ' ' + degree_user['last_name']}"
    )
    print(
        f"Closeness centrality: id{closeness} - {closeness_user['first_name'] + ' ' + closeness_user['last_name']}"
    )
    print(
        f"Eigenvector centrality: id{eigenvector} - {eigenvector_user['first_name'] + ' ' + eigenvector_user['last_name']}"
    )
    print(
        f"Betweenness centrality: id{betweennes} - {betweeness_user['first_name'] + ' ' + betweeness_user['last_name']}"
    )
