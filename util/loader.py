import torch
import numpy as np

def DataLoader(index_view, batch_size, open_corrupt = False):
    relation_num = len(index_view["relationship"]["index2name"])
    node_num = len(index_view["node"]["index2name"])

    indice = np.arange(relation_num)
    np.random.shuffle(indice)
    h_b = []
    t_b = []
    r_b = []

    for i in indice:
        rela_str = index_view["relationship"]["index2name"][str(i)]
        h_str, t_str = rela_str.split("->")
        h_index = index_view["node"]["name2index"][h_str]
        t_index = index_view["node"]["name2index"][t_str]
        r_index = index_view["relationship"]["name2index"][rela_str]
        h_b.append(h_index)
        t_b.append(t_index)
        r_b.append(r_index)

        if len(h_b) == batch_size:
            h = torch.LongTensor(h_b)
            t = torch.LongTensor(t_b)
            r = torch.LongTensor(r_b)
            if open_corrupt:
                n_h = torch.LongTensor(h_b)
                n_t = torch.LongTensor(t_b)

                n_h = (n_h + torch.randint(1, node_num, (len(n_h), ))) % node_num
                n_t = (n_t + torch.randint(1, node_num, (len(n_h), ))) % node_num
                
                yield h, t, r, n_h, n_t
            else:
                yield h, t, r

            h_b.clear()
            t_b.clear()
            r_b.clear()

    if len(h_b) > 0:
        h = torch.LongTensor(h_b)
        t = torch.LongTensor(t_b)
        r = torch.LongTensor(r_b)
        if open_corrupt:
            n_h = torch.LongTensor(h_b)
            n_t = torch.LongTensor(t_b)
            n_h = (n_h + torch.randint(1, node_num, (len(n_h), ))) % node_num
            n_t = (n_t + torch.randint(1, node_num, (len(n_h), ))) % node_num

            yield h, t, r, n_h, n_t

        else:
            yield h, t, r


if __name__ == "__main__":
    import json, math
    MAP_PATH = "data/map.full.json"
    # with open(MAP_PATH, "r", encoding="utf-8") as fp:
    #     index_view = json.load(fp=fp)
    # loader = DataLoader(index_view, 64)
