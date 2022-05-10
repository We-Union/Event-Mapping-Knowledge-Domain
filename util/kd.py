import json
import torch
from fuzzywuzzy import fuzz, process
import typing
import joblib

class KnowledgeGraph:
    def __init__(self) -> None:
        pass

    def load_everything(self, index_view_path : str, emb_model_path : str) -> None:
        with open(index_view_path, "r", encoding="utf-8") as fp:
            view_json = json.load(fp=fp)

        self.node_view = view_json["node"]
        self.rel_view = view_json["relationship"]

        self.nodes = list(self.node_view["name2index"].keys())

        self.node_num = len(self.node_view["index2name"])
        self.rel_num = len(self.rel_view["index2name"])

        state_dict = torch.load(emb_model_path, map_location="cpu")
        self.node_emb = state_dict["ent_emb.weight"]         # torch.Size([35741, 128])
        self.rel_emb = state_dict["rel_emb.weight"]         # torch.Size([67485, 128])

    def safe_predict_relation(self, n1_idx : int, n2_idx : int, thred = 1e-1) -> typing.Tuple[int]:
        # you should ensure inputs are in the range and we only receive integer in this function
        # return -1 if no rel is mathced

        n1_vec = self.node_emb[n1_idx]
        n2_vec = self.node_emb[n2_idx]
        r12_vec = n2_vec - n1_vec
        r21_vec = n1_vec - n2_vec

        # r12 : n1 --r12--> n2
        # r21 : n2 --r21--> n1
        r12_candidate = -1
        r12_min_distance = 10000000
        r21_candidate = -1
        r21_min_distance = 10000000
        
        for i in range(self.rel_num):
            dis_12_others = torch.norm(r12_vec - self.rel_emb[i]).item()
            dis_21_others = torch.norm(r21_vec - self.rel_emb[i]).item()

            if dis_12_others < thred:
                if dis_12_others < r12_min_distance:
                    r12_min_distance = dis_12_others
                    r12_candidate = i

            if dis_21_others < thred:
                if dis_21_others < r21_min_distance:
                    r21_min_distance = dis_21_others
                    r21_candidate = i

        return r12_candidate, r21_candidate
    
    def align_entity(self, entity : str, align_thred) -> typing.List[str]:
        res : typing.List[typing.Tuple[str, int]] = process.extract(entity, choices=self.nodes, limit=5)
        res : typing.List[str] = [match[0] for match in res if match[1] >= align_thred]
        return res

    def predict_relation(self, entity1 : str, entity2 : str, align_thred = 95, min_dis_thred = 1) -> typing.List[typing.Dict]:
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
    
    def one_jump(self, entity : str, align_thred : float, min_dis_thred : float = 1.0):
        # align the input to kb
        res = self.align_entity(entity, align_thred)
        
        for e in res:
            e_idx = self.node_view["name2index"][e]
            # match in the emb

            for other_e_idx in range(self.node_num):
                if other_e_idx == e_idx:
                    continue
                r12_idx, r21_idx = self.safe_predict_relation(e_idx, other_e_idx, thred=min_dis_thred)
                # if r12_idx > -1:
                #     r12 = self.rel_view["index2name"][str(r12_idx)]
                #     r12_type = self.rel_view["index2type"][str(r12_idx)]
                #     results.append({
                #         "start" : align_e1,
                #         "start_type" : n1_type,
                #         "relation" : r12_type,
                #         "end" : align_e2,
                #         "end_type" : n2_type,
                #         "evidence" : r12
                #     })
                # if r21_idx > -1:
                #     r21 = self.rel_view["index2name"][str(r21_idx)]
                #     r21_type = self.rel_view["index2type"][str(r21_idx)]
                #     results.append({
                #         "start" : align_e2,
                #         "start_type" : n2_type,
                #         "relation" : r21_type,
                #         "end" : align_e1,
                #         "end_type" : n1_type,
                #         "evidence" : r21
                #     })



if __name__ == "__main__":
    kg = KnowledgeGraph()
    kg.load_everything(
        index_view_path="./data/map.full.json",
        emb_model_path="model/2022-05-09 19-30-10.pth"
    )
    res = kg.predict_relation("Winter Olympics", "China")

    for r in res:
        print(r)