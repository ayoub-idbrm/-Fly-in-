

class Dijkstra:
    def __init__(self, loader):
        self.loader = loader
        self.distance = {}
        self.previous = {}


    def initialize(self):
        for hub in self.loader.hubs.values():
            self.distance[hub.name] = float("inf")
            self.previous[hub.name] = None

        self.distance[self.loader.start_hub.name] = 0



from src.loading import Loading
from src.algorithm import Dijkstra

path = "maps/challenger/01_the_impossible_dream.txt"

loader = Loading()
loader.processing(path)

dijkstra = Dijkstra(loader)
dijkstra.initialize()

print(dijkstra.distance)
print(dijkstra.previous)