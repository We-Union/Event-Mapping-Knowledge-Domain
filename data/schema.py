from py2neo import Graph, Node, Relationship
from tqdm import tqdm
import json

class EventGraph:
    notation2name = {
        "GPE" : "COUNTRY",
        "NORP" : "GROUP",
        "PERSON" : "PERSON"
    }
    # predefined relationship
    JOIN = Relationship.type("JOIN")
    HAPPEN_IN = Relationship.type("HAPPEN_IN")
    LOCATE_AT = Relationship.type("LOCATE_AT")
    LINK = Relationship.type("LINK")

    def __init__(self, neo4j_graph: Graph) -> None:
        self.graph = neo4j_graph

    def upload_data(self):
        ...
    
    def add_one_item(self, item_dict):
        """
        one item_dict is like:
        {
            "title": "Winter Olympic Games", 
            "url": "https://en.wikipedia.org/wiki/Winter_Olympic_Games", 
            "content": "The Winter Olympic Games (French: Jeux olympiques d'hiver)[note 1] is a major international multi-sport event held once every four years for sports practiced on snow and ice. The first Winter Olympic Games, the 1924 Winter Olympics, were held in Chamonix, France. The modern Olympic Games were inspired by the ancient Olympic Games, which were held in Olympia, Greece, from the 8th century BC to the 4th century AD. Baron Pierre de Coubertin founded the International Olympic Committee (IOC) in 1894, leading to the first modern Summer Olympic Games in Athens, Greece in 1896. The IOC is the governing body of the Olympic Movement, with the Olympic Charter defining its structure and authority.", 
            "joiner": []
        },
        """
        try:
            event_node = Node("EVENT", name=item_dict["title"].strip(), desc=item_dict["desc"].strip())

            for time in item_dict["time"]:
                time_node = Node("TIME", name=time.strip())
                self.graph.merge(self.HAPPEN_IN(event_node, time_node), "EVENT", "name")

            for place in item_dict["place"]:
                place_node = Node("PLACE", name=place.strip())
                self.graph.merge(self.LOCATE_AT(event_node, place_node), "EVENT", "name")
                
            for joiner in item_dict["joiner"]:
                j_type = joiner["type"].strip()
                j_name = joiner["content"].strip()
                joiner_node = Node(self.notation2name[j_type], name=j_name)    
                self.graph.merge(self.JOIN(joiner_node, event_node), self.notation2name[j_type], "name")
                

            for link in item_dict["link"]:
                link_event_node = Node("EVENT", name=link.strip())
                self.graph.merge(
                    self.LINK(event_node, link_event_node) | self.LINK(link_event_node, event_node),
                    "EVENT", "name"
                )
        
        except Exception as e:
            print("[ERROR] ", e)
            print("one error at title {}".format(item_dict.get("title", "Unknown")))
    
    def check_item(self, item_dict, key):
        return bool(key in item_dict and len(item_dict[key]) > 0)

    def load_data(self, file):
        all_data = [json.loads(line.strip()) for line in open(file, "r", encoding="utf-8")]
        for i in tqdm(range(len(all_data))):
            self.add_one_item(all_data[i])