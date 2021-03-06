import json
import torch
from fuzzywuzzy import process
import typing
from py2neo import Graph
from util.out import dump_json

class KnowledgeGraph:
    NODE_TYPE = ('EVENT', 'COUNTRY', 'GROUP', 'PERSON', 'PLACE', 'TIME')

    def __init__(self, config) -> None:
        self.graph = Graph(**config)
    
    def load_view(self, index_view_path):
        with open(index_view_path, "r", encoding="utf-8") as fp:
            view_json = json.load(fp=fp)
        self.node_view = view_json["node"]
        self.rel_view = view_json["relationship"]
        self.nodes = list(self.node_view["name2index"].keys())
        self.node_num = len(self.node_view["index2name"])
        self.rel_num = len(self.rel_view["index2name"])
    
    def load_emb(self, emb_model_path):
        state_dict = torch.load(emb_model_path, map_location="cpu")
        self.node_emb = state_dict["ent_emb.weight"]         # torch.Size([35741, 128])
        self.rel_emb = state_dict["rel_emb.weight"]         # torch.Size([67485, 128])

    def load_everything(self, index_view_path : str, emb_model_path : str) -> None:
        self.load_view(index_view_path)
        self.load_emb(emb_model_path)

    def match_rel(self, rel_vec, thred) -> int:
        r_candidate = -1
        r_min_distance = 10000000
        for i in range(self.rel_num):
            dis_others = torch.norm(rel_vec - self.rel_emb[i]).item()
            if dis_others < thred:
                if dis_others < r_min_distance:
                    r_min_distance = dis_others
                    r_candidate = i

        return r_candidate
    
    def cal_cos_sim(self, vec1, vec2):
        ...
    
    def binary_match_rel(self, rel_vec) -> int:
        ...

    def safe_predict_relation(self, n1_idx : int, n2_idx : int, thred = 1e-1) -> typing.Tuple[int]:
        # you should ensure inputs are in the range and we only receive integer in this function
        # return -1 if no rel is mathced

        n1_vec = self.node_emb[n1_idx]
        n2_vec = self.node_emb[n2_idx]
        r12_vec = n2_vec - n1_vec
        r21_vec = n1_vec - n2_vec

        # r12 : n1 --r12--> n2
        # r21 : n2 --r21--> n1
        r12_candidate = self.match_rel(r12_vec, thred)
        r21_candidate = self.match_rel(r21_vec, thred)

        return r12_candidate, r21_candidate
    
    def align_entity(self, entity : str, align_thred = 95, limit=5) -> typing.List[str]:
        res : typing.List[typing.Tuple[str, int]] = process.extract(entity, choices=self.nodes, limit=limit)
        res : typing.List[str] = [match[0] for match in res if match[1] >= align_thred]
        return res

    def local_predict_relation(self, entity1 : str, entity2 : str, align_thred = 95, min_dis_thred = 1) -> typing.List[typing.Dict]:
        res1 = self.align_entity(entity1, align_thred)
        res2 = self.align_entity(entity2, align_thred)

        results = []

        for align_e1 in res1:
            for align_e2 in res2:

                n1_idx = self.node_view["name2index"][align_e1]
                n2_idx = self.node_view["name2index"][align_e2]
                n1_type = self.node_view["index2type"][str(n1_idx)]
                n2_type = self.node_view["index2type"][str(n2_idx)]

                r12_idx, r21_idx = self.safe_predict_relation(n1_idx, n2_idx, thred=min_dis_thred)
                if r12_idx > -1:
                    r12 = self.rel_view["index2name"][str(r12_idx)]
                    r12_type = self.rel_view["index2type"][str(r12_idx)]
                    results.append({
                        "start" : align_e1,
                        "start_type" : n1_type,
                        "relation" : r12_type,
                        "end" : align_e2,
                        "end_type" : n2_type,
                        "evidence" : r12
                    })
                if r21_idx > -1:
                    r21 = self.rel_view["index2name"][str(r21_idx)]
                    r21_type = self.rel_view["index2type"][str(r21_idx)]
                    results.append({
                        "start" : align_e2,
                        "start_type" : n2_type,
                        "relation" : r21_type,
                        "end" : align_e1,
                        "end_type" : n1_type,
                        "evidence" : r21
                    })
        
        return results
    
    def predict_relation(self, entity1 : str, entity2 : str, align_thred = 95, min_dis_thred = 1):
        res1 = self.align_entity(entity1, align_thred)
        res2 = self.align_entity(entity2, align_thred)

        results = {"edge" : []}
        all_nodes = {}

        for align_e1 in res1:
            if align_e1 not in all_nodes:
                all_nodes[align_e1] = {}
            
            n1_idx = self.node_view["name2index"][align_e1]
            n1_type = self.node_view["index2type"][str(n1_idx)]
            all_nodes[align_e1]["type"] = n1_type

            for align_e2 in res2:
                if align_e2 not in all_nodes:
                    all_nodes[align_e2] = {}

                n2_idx = self.node_view["name2index"][align_e2]
                n2_type = self.node_view["index2type"][str(n2_idx)]
                all_nodes[align_e2]["type"] = n2_type

                query1 = self.graph.run(f'MATCH (h:COUNTRY{{name:"{align_e1}"}})-[a]->(t:EVENT{{name:"{align_e2}"}}) RETURN h, type(a) as r, t LIMIT 10').data()
                query2 = self.graph.run(f'MATCH (h:COUNTRY{{name:"{align_e1}"}})<-[a]-(t:EVENT{{name:"{align_e2}"}}) RETURN h, type(a) as r, t LIMIT 10').data()
                
                for q in query1 + query2:
                    if "desc" not in all_nodes[q["h"]["name"]]:
                        all_nodes[q["h"]["name"]]["desc"] = q["h"]["desc"]
                    if "desc" not in all_nodes[q["t"]["name"]]:
                        all_nodes[q["t"]["name"]]["desc"] = q["t"]["desc"]
                    results["edge"].append({
                        "from" : q["h"]["name"],
                        "to" : q["t"]["name"],
                        "name" : q["r"]
                    })
        
        results["all_nodes"] = []
        true_all_nodes = set()

        for edge in results["edge"]:
            true_all_nodes.add(edge["from"])
            true_all_nodes.add(edge["to"])
        
        for node_name in true_all_nodes:
            results["all_nodes"].append({
                "name" : node_name,
                "type" : all_nodes[node_name]["type"],
                "desc" : all_nodes[node_name]["desc"]
            })

        return results

    def one_jump(self, entity : str, align_thred : float = 95, min_dis_thred : float = 1.0, limit : int = 10):
        res = self.align_entity(entity, align_thred, limit=1)
        results = {}

        for r in res:
            results[r] = {}
            r_idx = self.node_view["name2index"][r]
            r_type = self.node_view["index2type"][str(r_idx)].upper()

            query = self.graph.run(f"MATCH (h:{r_type}{{name:\"{r}\"}})  RETURN h LIMIT {limit}").data()[0]["h"]
            results[r]["desc"] = query["desc"]
            results[r]["type"] = r_type
            
            results[r]["to"] = []
            results[r]["from"] = []

            results[r]["all_nodes"] = [{
                "name" : r,
                "desc" : query["desc"],
                "type" : r_type
            }]

            all_nodes = {}

            for node_type in self.NODE_TYPE:
                query = self.graph.run(f"MATCH (h:{r_type}{{name:\"{r}\"}})-[n]->(t:{node_type})  RETURN t, type(n) as r LIMIT {limit}").data()
                for q in query:
                    node_name = q["t"]["name"]
                    results[r]["to"].append({
                        "name" : node_name,
                        "rel" : q["r"]
                    })
                    if q["t"]["name"] not in all_nodes:
                        all_nodes[node_name] = {}
                    all_nodes[node_name]["desc"] = q["t"]["desc"]
                    all_nodes[node_name]["type"] = node_type
                
                query = self.graph.run(f"MATCH (h:{r_type}{{name:\"{r}\"}})<-[n]-(t:{node_type})  RETURN t, type(n) as r LIMIT {limit}").data()
                for q in query:
                    node_name = q["t"]["name"]
                    results[r]["from"].append({
                        "name" : q["t"]["name"],
                        "rel" : q["r"]
                    })
                    if q["t"]["name"] not in all_nodes:
                        all_nodes[node_name] = {}
                    all_nodes[node_name]["desc"] = q["t"]["desc"]
                    all_nodes[node_name]["type"] = node_type
            
            
            for node_name in all_nodes:
                results[r]["all_nodes"].append({
                    "name" : node_name,
                    "desc" : all_nodes[node_name]["desc"],
                    "type" : all_nodes[node_name]["type"]
                })

        return results
    
    def local_one_jump(self, entity : str, align_thred : float = 95, min_dis_thred : float = 1.0, limit : int = 25):
        # this method can do query without database
        # align the input to kb
        res = self.align_entity(entity, align_thred)
        
        results = []

        for e in res:
            e_idx = self.node_view["name2index"][e]
            e_type = self.node_view["index2type"][str(e_idx)]
            # match in the emb
            for other_e_idx in range(self.node_num):
                if other_e_idx == e_idx:
                    continue
                r12_idx, r21_idx = self.safe_predict_relation(e_idx, other_e_idx, thred=min_dis_thred)
                other_e = self.node_view["index2name"][str(other_e_idx)]
                other_e_type = self.node_view["index2type"][str(other_e_idx)]
                if r12_idx > -1:
                    r12 = self.rel_view["index2name"][str(r12_idx)]
                    r12_type = self.rel_view["index2type"][str(r12_idx)]
                    results.append({
                        "start" : e,
                        "start_type" : e_type,
                        "relation" : r12_type,
                        "end" : other_e,
                        "end_type" : other_e_type,
                        "evidence" : r12
                    })
                if r21_idx > -1:
                    r21 = self.rel_view["index2name"][str(r21_idx)]
                    r21_type = self.rel_view["index2type"][str(r21_idx)]
                    results.append({
                        "start" : other_e,
                        "start_type" : other_e_type,
                        "relation" : r21_type,
                        "end" : e,
                        "end_type" : e_type,
                        "evidence" : r21
                    })

        return results

if __name__ == "__main__":
    import json
    LOG_CONFIG_FILE = "./config/k.json"
    with open(LOG_CONFIG_FILE, "r", encoding="utf-8") as fp:
        c = json.load(fp)
    kg = KnowledgeGraph(c)
    kg.load_everything(
        index_view_path="./data/map.full.json",
        emb_model_path="model/2022-05-09 19-30-10.pth"
    )
    res = kg.predict_relation("Winter Olympics", "China")

    for r in res:
        print(r)
    