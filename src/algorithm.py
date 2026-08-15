from src.loading import Hub
import heapq


class Dijkstra:
    def __init__(self, loader):
        self.loader = loader
        self.distance = {}
        self.previous = {}
        self.visited = set()


    def initialize(self):
        for hub in self.loader.hubs.values():
            self.distance[hub.name] = float("inf")
            self.previous[hub.name] = None

        self.distance[self.loader.start_hub.name] = 0


    def get_next_hub(self, visited):
        small_distance = float("inf")
        next_hub = None

        for hub in self.distance:

            if hub in visited:
                continue

            if self.distance[hub] < small_distance:
                small_distance = self.distance[hub]
                next_hub = hub

        return next_hub


    def relax_neighbors(self, current):
        
        for neighbor , capacity in current.neighbors:

            new_distance = self.distance[current.name] + 1

            if new_distance < self.distance[neighbor.name]:
                self.distance[neighbor.name] = new_distance
                self.previous[neighbor.name] = current


    def mark_visited(self, current):
        self.visited.add(current.name)


    def run(self):
        while True:
            current = self.get_next_hub(self.visited)

            if current is None:
                break
            
            current = self.loader.hubs[current]

            self.relax_neighbors(current)

            self.mark_visited(current)

            if current == self.loader.end_hub:
                break
        
        return self.get_path()



    def get_path(self):
        path = []
        current = self.loader.end_hub
        path.append(current)
        dis = 0

        while True:
            current = self.previous[current.name]

            if current == None:
                break
            dis = dis + self.distance[current.name]
            path.append(current)
        path.reverse()
        return path

