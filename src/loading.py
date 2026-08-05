from src.parser import Parsing
import re
import sys


class Hub:
    def __init__(self, name, x, y, hub_type, zone="normal", color="none", max_drones=1):
        self.name = name
        self.x = x
        self.y = y
        self.hub_type = hub_type
        self.zone = zone
        self.color = color
        self.max_drones = max_drones
        self.neighbors = []


class Connection:
    def __init__(self, hub1, hub2, max_link_capacity=1):
        self.hub1 = hub1
        self.hub2 = hub2
        self.max_link_capacity = max_link_capacity


class Loading(Parsing):

    def parse_nb_drones(self, line):
        try:
            nb_drones = int(line.split(":")[1].strip())
        except BaseException as d:
            print(f"ERROR: {d}")

        return nb_drones


    def parse_hub(self, line):
        zone = "normal"
        color = "none"
        max_drones = 1

        if "[" in line:
            left, meta = line.split("[", 1)
            meta = meta.rstrip("]")
        else:
            left = line
            meta = ""

        hub_type, values = left.split(":", 1)

        tokens = values.split()

        name = tokens[0]
        try :
            x = int(tokens[1])
            y = int(tokens[2])
        except BaseException as d:
            print(f"ERROR: {d}")

        for item in meta.split():
            key, value = item.split("=")

            if key == "zone":
                zone = value
            elif key == "color":
                color = value
            elif key == "max_drones":
                try:
                    max_drones = int(value)
                except BaseException as d:
                    print (f"ERROR: {d}")

        return Hub(
            name=name,
            x=x,
            y=y,
            hub_type=hub_type.strip(),
            zone=zone,
            color=color,
            max_drones=max_drones,
        )


    def parse_connection(self, line):

        _, rest = line.split(": ", 1)
        if "[" in rest:
            hub, cap = rest.split(" [", 1)
            max_link_capacity = cap.rstrip("]")
            _ , nb = max_link_capacity.split("=", 1)
            nb = int(nb)
        else:
            hub = rest.strip()
            nb = 1
        
        hub1, hub2 = hub.split("-")
        
        return Connection(
            hub1=hub1,
            hub2=hub2,
            max_link_capacity=nb
        )


    def processing(self, path):
        self.hubs = {}
        self.start_hub = None
        self.end_hub = None

        self.connections = []

        lines = self.read_file(path)

        for line in lines:
            if line.startswith("nb_drones:"):
                self.nb_drones = self.parse_nb_drones(line)

            elif line.startswith("start_hub:"):
                hub = self.parse_hub(line)
                self.hubs[hub.name] = hub
                self.start_hub = hub

            elif line.startswith("end_hub:"):
                hub = self.parse_hub(line)
                self.hubs[hub.name] = hub
                self.end_hub = hub

            elif line.startswith("hub:"):
                hub = self.parse_hub(line)
                self.hubs[hub.name] = hub

            elif line.startswith("connection:"):
                connection = self.parse_connection(line)
                self.connections.append(connection)
        for connect in self.connections:
            hub.neighbors
        

path = "maps/challenger/01_the_impossible_dream.txt"
loader = Loading()
loader.processing(path)
print(loader.connections[0].hub1)
print(loader.connections[0].hub2)
print(loader.connections[0].max_link_capacity)
