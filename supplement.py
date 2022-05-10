from util.kd import KnowledgeGraph
import json
from py2neo import Graph
from tqdm import tqdm

LOG_CONFIG_FILE = "./config/k.json"

with open(LOG_CONFIG_FILE, "r", encoding="utf-8") as fp:
    c = json.load(fp)

kg = KnowledgeGraph(c)
kg.load_everything(
    index_view_path="data/map.full.json",
    emb_model_path="model/2022-05-09 19-30-10.pth"
)

r12, r21 = kg.safe_predict_relation(0, 1)
print(r12)
print(r21)

# for i in tqdm(range(kg.node_num)):
#     for j in range(i + 1, kg.node_num):
        

