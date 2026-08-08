from src.parser import Parsing
import re
import sys

class ParsingError(Exception):
    """raise an error in with catch it in the parsing"""
    pass


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
        self.cost = 1
        if zone == "restricted":
            self.cost = 2

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

        """loop for each line in the file and parse it"""
        for line in lines:
            if line.startswith("nb_drones:"):
                self.nb_drones = self.parse_nb_drones(line)

            elif line.startswith("start_hub:"):
                hub = self.parse_hub(line)

                if hub.name in self.hubs:
                    raise ParsingError(f"Duplicate hub: {hub.name}")

                self.hubs[hub.name] = hub
                self.start_hub = hub

            elif line.startswith("end_hub:"):
                hub = self.parse_hub(line)

                if hub.name in self.hubs:
                    raise ParsingError(f"Duplicate hub: {hub.name}")

                self.hubs[hub.name] = hub
                self.end_hub = hub

            elif line.startswith("hub:"):
                hub = self.parse_hub(line)

                if hub.name in self.hubs:
                    raise ParsingError(f"Duplicate hub: {hub.name}")
                self.hubs[hub.name] = hub

            elif line.startswith("connection:"):
                connection = self.parse_connection(line)
                self.connections.append(connection)

        """validate the parsing is it everything good before building the graph"""

        self.validate()

        """transforming the parsed to data into a graph"""

        for connect in self.connections:
            hub1 = self.hubs[connect.hub1]
            hub2 = self.hubs[connect.hub2]

            hub1.neighbors.append((hub2, connect.max_link_capacity))
            hub2.neighbors.append((hub1, connect.max_link_capacity))



    def validate(self):
        duplicate_connection = set()

        if self.nb_drones <= 0:
            raise ParsingError("ERROR: the number of the drones should be positive")

        if self.start_hub is None:
            raise ParsingError("ERROR: No start hub found")

        if self.end_hub is None:
            raise ParsingError("ERROR: No end hub found")

        for connection in self.connections:
            if connection.hub1 not in self.hubs or connection.hub2 not in self.hubs:
                raise ParsingError(f"Unknown hub in connection: {connection.hub1}-{connection.hub2}")

            key = tuple(sorted([connection.hub1, connection.hub2]))
            if key in duplicate_connection:
                raise ParsingError(f"ERROR: there's a duplicate connection {key}")
            
            duplicate_connection.add(key)





# path = "maps/challenger/01_the_impossible_dream.txt"
# loader = Loading()
# loader.processing(path)
# for hub in loader.hubs.values():
#     print(hub.name, hub.zone, hub.cost)
