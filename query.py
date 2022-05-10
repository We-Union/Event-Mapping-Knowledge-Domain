import json
from util.kd import KnowledgeGraph
from util.out import dump_json

import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    '-i', help="input event"
)

parser.add_argument(
    '-v', default="data/map.full.json",
    help="map view path"
)

parser.add_argument(
    '-c', default="config/k.json",
    help="config path"
)

parser.add_argument(
    '-o', default="default.json",
    help="output_path"
)

args = vars(parser.parse_args())

EVENT = args["i"]
VIEW_PATH = args["v"]
CONFIG_PATH = args["c"]
OUT_PATH = args["o"]

if __name__ == "__main__":
    with open(CONFIG_PATH, "r", encoding="utf-8") as fp:
        c = json.load(fp)

    kg = KnowledgeGraph(c)
    kg.load_view(VIEW_PATH)

    result = kg.one_jump(entity=EVENT)
    dump_json(
        obj=result,
        path=OUT_PATH
    )