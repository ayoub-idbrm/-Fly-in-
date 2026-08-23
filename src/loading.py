from typing import Optional
from parser import Parsing


class ParsingError(Exception):
    """Raise an error to catch during parsing."""

    pass


class Hub:

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        hub_type: str,
        zone: str = "normal",
        color: str = "none",
        max_drones: int = 1,
    ) -> None:
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.hub_type: str = hub_type
        self.zone: str = zone
        self.color: str = color
        self.max_drones: int = max_drones
        self.neighbors: list[tuple["Hub", int]] = []
        self.cost: int = 1
        if zone == "restricted":
            self.cost = 2
        self.flag: bool = False


class Connection:

    def __init__(
        self, hub1: str, hub2: str, max_link_capacity: int = 1
    ) -> None:
        self.hub1: str = hub1
        self.hub2: str = hub2
        self.max_link_capacity: int = max_link_capacity


class Loading(Parsing):

    def __init__(self) -> None:
        super().__init__()
        self.nb_drones: int = 0
        self.hubs: dict[str, Hub] = {}
        self.start_hub: Optional[Hub] = None
        self.end_hub: Optional[Hub] = None
        self.connections: list[Connection] = []
        self.flag: bool = False

    def parse_nb_drones(self, line: str) -> int:
        try:
            return int(line.split(":")[1].strip())
        except Exception as d:
            raise ParsingError(f"Invalid nb_drones format: {d}")

    def parse_hub(self, line: str) -> Hub:
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
        try:
            x = int(tokens[1])
            y = int(tokens[2])
        except Exception:
            raise ParsingError("ERROR: invalid conrdinates")

        for item in meta.split():
            key, value = item.split("=")

            if key == "zone":
                zone = value
                if self.flag and value == "blocked":
                    self.flag = False
                    raise ParsingError(
                        "ERROR: You cannot set 'start_hub' "
                        "or 'end_hub' as blocked zone"
                    )
            elif key == "color":
                color = value
            elif key == "max_drones":
                try:
                    max_drones = int(value)
                    if max_drones <= 0:
                        raise ParsingError(
                            "ERROR: max_drones should be a "
                            f"positive int not '{max_drones}'"
                        )
                except Exception as d:
                    raise ParsingError(f"Invalid max_drones value: {d}")

        return Hub(
            name=name,
            x=x,
            y=y,
            hub_type=hub_type.strip(),
            zone=zone,
            color=color,
            max_drones=max_drones,
        )

    def parse_connection(self, line: str) -> Connection:
        _, rest = line.split(": ", 1)
        if "[" in rest:
            hub, cap = rest.split(" [", 1)
            max_link_capacity = cap.rstrip("]")
            _, nb = max_link_capacity.split("=", 1)

            con1, con2 = hub.split("-")
            if con1 == con2:
                raise ParsingError(
                    f"ERROR: there's self connection ({con1}-{con2})"
                )

            try:
                nb_val = int(nb)
            except BaseException:
                raise ParsingError("ERROR: max_link_capacity should be int")
            if nb_val <= 0:
                raise ParsingError(
                    "ERROR: max_link_capacity should be valid "
                    f"positive int not '{nb_val}'"
                )
        else:
            hub = rest.strip()
            nb_val = 1

        hub1, hub2 = hub.split("-")

        return Connection(hub1=hub1, hub2=hub2, max_link_capacity=nb_val)

    def processing(self, path: str) -> None:
        self.hubs = {}
        self.start_hub = None
        self.end_hub = None
        self.connections = []

        lines = self.read_file(path)

        for line in lines:
            if line.startswith("nb_drones:"):
                self.nb_drones = self.parse_nb_drones(line)

            elif line.startswith("start_hub:"):
                self.flag = True
                hub = self.parse_hub(line)

                if hub.name in self.hubs:
                    raise ParsingError(f"Duplicate start_hub: {hub.name}")

                self.hubs[hub.name] = hub
                self.start_hub = hub

            elif line.startswith("end_hub:"):
                self.flag = True
                hub = self.parse_hub(line)

                if hub.name in self.hubs:
                    raise ParsingError(f"Duplicate end_hub: {hub.name}")

                self.hubs[hub.name] = hub
                self.end_hub = hub

            elif line.startswith("hub:"):
                self.flag = False
                hub = self.parse_hub(line)

                if hub.name in self.hubs:
                    raise ParsingError(f"Duplicate hub: {hub.name}")
                self.hubs[hub.name] = hub

            elif line.startswith("connection:"):
                connection = self.parse_connection(line)
                self.connections.append(connection)

        self.validate()

        for connect in self.connections:
            h1 = self.hubs[connect.hub1]
            h2 = self.hubs[connect.hub2]

            h1.neighbors.append((h2, connect.max_link_capacity))
            h2.neighbors.append((h1, connect.max_link_capacity))

    def get_connection(self, hub1: Hub, hub2: Hub) -> Optional[Connection]:
        for connection in self.connections:
            match_direct = (
                connection.hub1 == hub1.name
                and connection.hub2 == hub2.name
            )
            match_reverse = (
                connection.hub1 == hub2.name
                and connection.hub2 == hub1.name
            )
            if match_direct or match_reverse:
                return connection

        return None

    def validate(self) -> None:
        duplicate_connection: set[tuple[str, str]] = set()

        if self.nb_drones <= 0:
            raise ParsingError(
                "ERROR: the number of the drones should be positive"
            )

        if self.start_hub is None:
            raise ParsingError("ERROR: No start hub found")

        if self.end_hub is None:
            raise ParsingError("ERROR: No end hub found")

        for connection in self.connections:
            h1, h2 = connection.hub1, connection.hub2
            if h1 not in self.hubs or h2 not in self.hubs:
                raise ParsingError(
                    f"Unknown hub in connection: {h1}-{h2}"
                )

            key = (min(h1, h2), max(h1, h2))
            if key in duplicate_connection:
                raise ParsingError(
                    f"ERROR: there's a duplicate connection {key}"
                )

            duplicate_connection.add(key)
