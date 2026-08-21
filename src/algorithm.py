from src.loading import Hub

class Dijkstra:
    def __init__(self, loader):
        self.loader = loader
        self.distance = {}
        self.previous = {}
        self.visited = set()

        self.add_cost = {}


    def get_edge_key(self, hub1, hub2):
        return tuple(sorted([hub1.name, hub2.name]))


    def initialize(self):
        self.distance = {}
        self.previous = {}
        self.visited = set()

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

            distance = self.distance[hub]

            if distance < small_distance:
                small_distance = distance
                next_hub = hub
            
            elif self.distance[hub] == small_distance:
                place = self.loader.hubs[hub]

                if place.zone == "priority":
                    next_hub = hub

        return next_hub


    def relax_neighbors(self, current):

        for neighbor , capacity in current.neighbors:
            
            if neighbor.zone == "blocked":
                continue
            
            cost = 1

            if neighbor.zone == "restricted":
                cost = 2

            key = self.get_edge_key(current, neighbor)

            penalty = self.add_cost.get(key, 0)



            new_distance = self.distance[current.name] + cost + penalty

            if new_distance < self.distance[neighbor.name]:
                self.distance[neighbor.name] = new_distance
                self.previous[neighbor.name] = current


    def mark_visited(self, current):
        self.visited.add(current.name)


    def run(self):
        paths = []
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

        if self.previous[current.name] is None:
            return []

        path.append(current)

        while current != self.loader.start_hub:
            current = self.previous[current.name]

            if current is None:
                return []

            path.append(current)

        path.reverse()

        return path


    def penalize_path(self, path):

        for i in range(len(path) - 1):

            hub1 = path[i]
            hub2 = path[i + 1]

            key = self.get_edge_key(hub1, hub2)

            self.add_cost[key] = self.add_cost.get(key, 0) + 0.01


    def same_path(self, path1, path2):
        if len(path1) != len(path2):
            return False
        
        for i in range(len(path1)):
            if path1[i].name != path2[i].name:
                return False
        
        return True