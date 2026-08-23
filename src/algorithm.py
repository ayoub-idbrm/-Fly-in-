from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from loading import Hub, Loading


class Dijkstra:

    def __init__(self, loader: "Loading") -> None:
        self.loader: "Loading" = loader
        self.distance: dict[str, float] = {}
        self.previous: dict[str, Optional["Hub"]] = {}
        self.visited: set[str] = set()

        self.add_cost: dict[tuple[str, str], float] = {}

    def get_edge_key(self, hub1: "Hub", hub2: "Hub") -> tuple[str, str]:
        # Sort names to ensure the key is identical regardless of order
        sorted_names = sorted([hub1.name, hub2.name])
        return (sorted_names[0], sorted_names[1])

    def initialize(self) -> None:
        self.distance = {}
        self.previous = {}
        self.visited = set()

        for hub in self.loader.hubs.values():
            self.distance[hub.name] = float("inf")
            self.previous[hub.name] = None

        if self.loader.start_hub:
            self.distance[self.loader.start_hub.name] = 0

    def get_next_hub(self, visited: set[str]) -> Optional[str]:
        small_distance: float = float("inf")
        next_hub: Optional[str] = None

        for hub in self.distance:
            if hub in visited:
                continue

            distance = self.distance[hub]

            if distance < small_distance:
                small_distance = distance
                next_hub = hub

            elif distance == small_distance:
                place = self.loader.hubs[hub]

                if place.zone == "priority":
                    next_hub = hub

        return next_hub

    def relax_neighbors(self, current: "Hub") -> None:
        for neighbor, capacity in current.neighbors:
            if neighbor.zone == "blocked":
                continue
            cost: float = 1.0

            if neighbor.zone == "restricted":
                cost = 2.0

            key = self.get_edge_key(current, neighbor)

            penalty = self.add_cost.get(key, 0.0)

            new_distance = self.distance[current.name] + cost + penalty

            if new_distance < self.distance[neighbor.name]:
                self.distance[neighbor.name] = new_distance
                self.previous[neighbor.name] = current

    def mark_visited(self, current: "Hub") -> None:
        self.visited.add(current.name)

    def run(self) -> list["Hub"]:
        while True:
            current_name = self.get_next_hub(self.visited)

            if current_name is None:
                break

            current_hub = self.loader.hubs[current_name]

            self.relax_neighbors(current_hub)

            self.mark_visited(current_hub)

            if current_hub == self.loader.end_hub:
                break

        return self.get_path()

    def get_path(self) -> list["Hub"]:
        path: list["Hub"] = []
        current: Optional["Hub"] = self.loader.end_hub

        if current is None or self.previous.get(current.name) is None:
            return []

        path.append(current)

        while current != self.loader.start_hub:
            if current is None:
                return []

            current = self.previous.get(current.name)

            if current is None:
                return []

            path.append(current)

        path.reverse()

        return path

    def penalize_path(self, path: list["Hub"]) -> None:
        for i in range(len(path) - 1):
            hub1 = path[i]
            hub2 = path[i + 1]

            key = self.get_edge_key(hub1, hub2)

            self.add_cost[key] = self.add_cost.get(key, 0.0) + 0.01

    def same_path(self, path1: list["Hub"], path2: list["Hub"]) -> bool:
        if len(path1) != len(path2):
            return False

        for i in range(len(path1)):
            if path1[i].name != path2[i].name:
                return False

        return True
