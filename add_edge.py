import numpy as np
import datetime
from lshashpy3 import LSHash
import threading
import json
from util.kd import KnowledgeGraph
import torch

eus = list()
cnt = 0

def get_edge(es):
    zero = torch.zeros((128))
    print(zero.shape)
    print(es[0].shape)
    discs = list()

    for i in range(0,len(es)):
        disc = torch.norm(es[i] - zero)
        discs.append([disc,i])

    results = list()
    discs.sort(key=lambda x:x[0])
    num = (int)(len(es) * 0.025)
    for i in range(0,num):
        results.append(discs[i][1])

    for i in range(len(es)-num,len(es)):
        results.append(discs[i][1])

    return results


def get_two_neer_vs(e_num):

    e_name = kg.rel_view["index2name"][str(e_num)]
    start_node, end_node = e_name.split("->")
    start_node_idx = kg.node_view["name2index"][start_node]
    end_node_idx = kg.node_view["name2index"][end_node]
    v1,v2 = all_v[start_node_idx],all_v[end_node_idx]

    result = lshv.query(v1, 25)
    v1s = list()
    for i in range(0,len(result)):
        ((vec, extra_data), distance) = result[i]
        v1s.append([vec,extra_data])

    result = lshv.query(v2, 25)
    v2s = list()
    for i in range(0, len(result)):
        ((vec, extra_data), distance) = result[i]
        v2s.append([vec,extra_data])

    return v1s,v2s

def func(e,v1n,v2n):
    result = lsh.query(e, 1)
    if len(result):
        ((vec, extra_data), distance) = result[0]
        eus.append([extra_data,distance,v1n,v2n])



if __name__ == "__main__":
    dim = 128
    lsh = LSHash(14, dim)
    lshv = LSHash(14,dim)
    LOG_CONFIG_FILE = "./config/k.json"
    with open(LOG_CONFIG_FILE, "r", encoding="utf-8") as fp:
        c = json.load(fp)
    kg = KnowledgeGraph(c)
    kg.load_everything(
        index_view_path="./data/map.full.json",
        emb_model_path="model/2022-05-09 19-30-10.pth"
    )
    all_v = (kg.node_emb * 10000).int()
    all_e = (kg.rel_emb * 10000).int()
    print("index for all edge")
    for i in range(0, len(all_e)):
        lsh.index(all_e[i], extra_data=i)
    print("index for all v")
    for i in range(0,len(all_v)):
        lshv.index(all_v[i],extra_data=i)

    start = datetime.datetime.now()
    max_len = 100
    ts = list()
    # max_t = 10
    # lock1 = threading.Lock()
    # lock2 = threading.Lock()
    # for i in range(0, max_t):
    #     t = threading.Thread(target=func, args=(i * max_len // max_t, (i + 1) * max_len // max_t))
    #     t.start()
    #     ts.append(t)
    #
    # for i in range(0, max_t):
    #     ts[i].join()
    results = get_edge(all_e)
    for i in results:
        v1s,v2s = get_two_neer_vs(i)
        for [v1,v1n] in v1s:
            for [v2,v2n] in v2s:

                v1 = torch.tensor(list(v1)).int()
                v2 = torch.tensor(list(v2)).int()
                func(v1-v2,v1n,v2n)
    print(datetime.datetime.now() - start)

    eus.sort(key=lambda x:x[1])
    with open("add_edge1.txt","w") as f:
        i = 0
        for e in eus:
            edge_type = kg.rel_view["index2type"][str(e[0])]

            f.write("{},{},{}\n".format(e[2],e[3],edge_type))
            if i > 10000:
                break
    # plt.hist(eus)
    #
    # plt.title("data analyze")
    # plt.xlabel("disc")
    # plt.ylabel("count")
    #
    # plt.show()
