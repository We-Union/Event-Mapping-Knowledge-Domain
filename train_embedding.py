from torchkge.models import TransEModel
from torchkge.utils import MarginLoss

import torch
import os
import json
from util.out import *
from util.loader import DataLoader
from util.time import now_str
from tqdm import tqdm
import math
import matplotlib.pyplot as plt

MAP_PATH = "data/map.full.json"

if not os.path.exists(MAP_PATH):
    error_out("{} is not a valid path to read map json!".format(MAP_PATH))
    exit(-1)

with open(MAP_PATH, "r", encoding="utf-8") as fp:
    index_view = json.load(fp=fp)

#################################################
###########     main parameter       ############
#################################################
NODE_NUM = len(index_view["node"]["index2name"])
RELATION_NUM = len(index_view["relationship"]["index2name"])
LEARNING_RATE = 1e-3
BATCH_SIZE = 128
MARGIN = 0.5
EPOCH = 3

DEVICE = "cuda"

def main():
    if not os.path.exists("model"):
        os.mkdir("model")

    model = TransEModel(
        emb_dim=128,
        n_entities=NODE_NUM,
        n_relations=RELATION_NUM,
        dissimilarity_type='L2'
    )
    model = model.to(DEVICE)

    criterion = MarginLoss(MARGIN)
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=1e-5)

    iterator = range(math.ceil(RELATION_NUM / BATCH_SIZE))
    losses = []

    for epoch in range(EPOCH):
        loader = DataLoader(
            index_view=index_view,
            batch_size=BATCH_SIZE,
            open_corrupt=True
        )
        note_iter = tqdm(iterator)
        note_iter.set_description_str("loss : unknown")

        cur_losses = []
        for i in note_iter:
            h, t, r, n_h, n_t = next(loader)
            h = h.to(DEVICE)
            t = t.to(DEVICE)
            r = r.to(DEVICE)
            n_h = n_h.to(DEVICE)
            n_t = n_t.to(DEVICE)

            optimizer.zero_grad()
            pos, neg = model(h, t, r, n_h, n_t)
            loss : torch.Tensor = criterion(pos, neg)
            loss.backward()
            optimizer.step()
            loss_value = loss.item()
            cur_losses.append(loss_value)
            note_iter.set_description_str("loss : {}".format(round(loss_value, 3)))

        for i in range(0, len(cur_losses), 50):
            losses.append(cur_losses[i])

    # if epoch % 2 == 0:
    #     torch.save(
    #         model.state_dict(),
    #         "model/" + now_str() + ".pth"
    #     )

    torch.save(model.state_dict(), "model/" + now_str() + ".pth")
    
    plt.figure(dpi=120)
    plt.style.use("gadfly")
    plt.plot(losses, label="loss")
    plt.legend()
    plt.show()



if __name__ == "__main__":
    main()