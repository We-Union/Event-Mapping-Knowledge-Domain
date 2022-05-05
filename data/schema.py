from py2neo import Graph, Node, Relationship
from tqdm import tqdm

class EventGraph:
    def __init__(self, neo4j_graph: Graph) -> None:
        self.graph = neo4j_graph
        # nodes define
        self.event = []
        self.time = []
        self.place = []
        self.joiner = []
        
        # relationship
        self.belongsTo = []
        self.cause = []
        self.join = []
        self.happenIn = []
        self.locateAt = []

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
            event_node = Node(item_dict["title"], desc=item_dict["content"])
            joiner = Node(item_dict["joiner"])
            
            if "time" in item_dict and len(item_dict["time"] > 0):
                time_node = Node(item_dict["time"])
            
            if "place" in item_dict and len(item_dict["place"] > 0):
                place_node = Node(item_dict["place"])
            

        except:
            print("one error at title {}".format(item_dict.get("title", "Unknown")))

    def push(self):
        self.graph.merge()
