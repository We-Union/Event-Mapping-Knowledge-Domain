# import en_core_web_sm
# nlp = en_core_web_sm.load()
# doc = nlp(u"The Winter Olympic Games (French: Jeux olympiques d'hiver)[note 1] is a major international multi-sport event held once every four years for sports practiced on snow and ice. The first Winter Olympic Games, the 1924 Winter Olympics, were held in Chamonix, France. The modern Olympic Games were inspired by the ancient Olympic Games, which were held in Olympia, Greece, from the 8th century BC to the 4th century AD. Baron Pierre de Coubertin founded the International Olympic Committee (IOC) in 1894, leading to the first modern Summer Olympic Games in Athens, Greece in 1896. The IOC is the governing body of the Olympic Movement, with the Olympic Charter defining its structure and authority.")
# for token in doc:
#     print(token.text, token.pos_)
text1 = "The Winter Olympic Games (French: Jeux olympiques d'hiver)[note 1] is a major international multi-sport event held once every four years for sports practiced on snow and ice. The first Winter Olympic Games, the 1924 Winter Olympics, were held in Chamonix, France. The modern Olympic Games were inspired by the ancient Olympic Games, which were held in Olympia, Greece, from the 8th century BC to the 4th century AD. Baron Pierre de Coubertin founded the International Olympic Committee (IOC) in 1894, leading to the first modern Summer Olympic Games in Athens, Greece in 1896. The IOC is the governing body of the Olympic Movement, with the Olympic Charter defining its structure and authority."
from pprint import pprint

from stanfordcorenlp import StanfordCoreNLP

model = StanfordCoreNLP("./lib/stanford-corenlp-4.4.0")
res = model.ner(text1)
pprint(res)