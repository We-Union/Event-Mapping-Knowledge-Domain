import json
from util.kd import KnowledgeGraph
from py2neo import Graph
from util.out import dump_json

import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    '-i', help="input event"
)

args = vars(parser.parse_args())

EVENT = args["i"]

if __name__ == "__main__":
    LOG_CONFIG_FILE = "./config/k.json"
    with open(LOG_CONFIG_FILE, "r", encoding="utf-8") as fp:
        c = json.load(fp)

    kg = KnowledgeGraph(c)
    kg.load_view("data/map.full.json")

    kg.one_jump(entity=EVENT)