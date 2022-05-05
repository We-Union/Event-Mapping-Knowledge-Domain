from py2neo import Graph, Node, Relationship
import json

LOG_CONFIG_FILE = "./config/k.json"

with open(LOG_CONFIG_FILE, "r", encoding="utf-8") as fp:
    c = json.load(fp)

g = Graph(**c)
