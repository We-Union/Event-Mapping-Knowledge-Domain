# -*- encoding: utf-8 -*-
# purpose: make vocab to view.json
# please run the script in the neo4j server

from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher
import json

LOG_CONFIG_FILE = "./config/k.json"

with open(LOG_CONFIG_FILE, "r", encoding="utf-8") as fp:
    c = json.load(fp)

g = Graph(**c)
matcher = NodeMatcher(g)
r_matcher = RelationshipMatcher(g)

nodes = {
    "event" : [],
    "country" : [],
    "group" : [],
    "person" : [],
    "place" : [],
    "time" : [],
}

for node_name in nodes:
    target_nodes = matcher.match(node_name.upper()).all()
    nodes[node_name] = list(map(lambda x : x['name'], target_nodes))
    print("[{}] ready".format(node_name))

relations = {
    "happen_in" : [],
    "join" : [],
    "link" : [],
    "locate_at" : []
}

for r_name in relations:
    target_r = r_matcher.match(r_type=r_name.upper()).all()
    relations[r_name] = list(map(lambda x : "{}->{}".format(x.nodes[0]["name"], x.nodes[1]["name"]), target_r))
    print("[{}] ready".format(r_name))

view = {
    "node" : nodes,
    "relationship" : relations
}

with open("./data/view.json", "w", encoding="utf-8") as fp:
    json.dump(obj=view, fp=fp, ensure_ascii=False)