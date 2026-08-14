

class Drone():
    def __init__(self, drone_id, position, path):
        self.drone_id = drone_id
        self.position = position
        self.path = path


    def move_drone(self):
        current = self.path.index(self.position)

        if current + 1 < len(self.path):
            self.position = self.path[current + 1]























from src.loading import Loading
from src.algorithm import Dijkstra


path = "maps/challenger/01_the_impossible_dream.txt"

if __name__ == "__main__":
    drones = []

    loader = Loading()
    loader.processing(path)

    dj = Dijkstra(loader)
    dj.initialize()
    dj.run()
    path = dj.get_path()

    test = Drone(1, loader.start_hub, path)



    # for i in range(loader.nb_drones):
    #     drone = Drone(i + 1, loader.start_hub, path)
    #     drones.append(drone)

    # for turn in range(1, len(path)):
    #     print(f"Turn {turn}")

    #     for drone in drones:
    #         drone.move_drone()
    #         print(f"Drone {drone.drone_id} -> {drone.position.name}")

    current = loader.start_hub
    next_hub = path[1]

    connection = loader.get_connection(current, next_hub)

    print(connection.max_link_capacity)