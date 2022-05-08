from py2neo import Graph, Node, Relationship
import json
from data.schema import EventGraph

LOG_CONFIG_FILE = "./config/k.json"

with open(LOG_CONFIG_FILE, "r", encoding="utf-8") as fp:
    c = json.load(fp)

g = Graph(**c)

transaction = g.begin()

a = Node("Person", name="Alice", age=33, desc="XXXXXXXXXXXXXXXXXXXXXXX")
c = Node("Good", name="House", price=300)
BUY = Relationship.type("BUY")
transaction.merge(BUY(a, c), "Person", "name")
g.commit(transaction)