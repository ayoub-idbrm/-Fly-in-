
from loading import Hub


class Drone():
    def __init__(
            self, drone_id: int, position: "Hub", path: list["Hub"]) -> None:
        self.drone_id = drone_id
        self.position = position
        self.path = path

        self.in_flight = False
        self.destination = None
        self.turns = 0

    def move_drone(self) -> None:
        current = self.path.index(self.position)

        if current + 1 < len(self.path):
            self.position = self.path[current + 1]

    def flight(self, destination: "Hub") -> None:
        self.in_flight = True
        self.destination = destination
        self.turns = 2

    def finish_flight(self) -> None:
        self.turns -= 1

        if self.turns == 0:
            self.in_flight = False
            self.position = self.destination
            self.destination = None
