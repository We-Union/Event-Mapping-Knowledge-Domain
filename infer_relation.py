import json
from util.kd import KnowledgeGraph
from util.out import dump_json

import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    '-s', help="start event"
)

parser.add_argument(
    '-e', help="end event"
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

START = args["s"].strip()
END   = args["e"].strip()
VIEW_PATH = args["v"].strip()
CONFIG_PATH = args["c"].strip()
OUT_PATH = args["o"].strip()

if __name__ == "__main__":
    with open(CONFIG_PATH, "r", encoding="utf-8") as fp:
        c = json.load(fp)

    kg = KnowledgeGraph(c)
    kg.load_view(VIEW_PATH)

    result = kg.predict_relation(
        entity1=START,
        entity2=END
    )
    dump_json(
        obj=result,
        path=OUT_PATH
    )