from py2neo import Graph, Node, Relationship
import json
from data.schema import EventGraph

LOG_CONFIG_FILE = "./config/k.json"

with open(LOG_CONFIG_FILE, "r", encoding="utf-8") as fp:
    c = json.load(fp)

g = Graph(**c)
event_graph = EventGraph(g)
event_graph.load_data("./data/data_step2.json")