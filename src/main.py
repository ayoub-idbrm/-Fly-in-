from src.loading import Loading
from src.algorithm import Dijkstra
from src.drones import Drone


file = "/home/aidbrm/Desktop/fly/maps/challenger/01_the_impossible_dream.txt"


def all_finished(drones, end):
    for drone in drones:
        if drone.position != end:
            return False

    return True


def main():
    loader = Loading()
    loader.processing(file)

    dijkstra = Dijkstra(loader)

    paths = []

    for i in range(3):
        dijkstra.initialize()
        dijkstra.run()

        path = dijkstra.get_path()
    
        if len(path) <= 1 or path[0] != loader.start_hub:
            break
        
        already_exists = False


        for old in paths:
            if dijkstra.same_path(path, old):
                already_exists = True
                break
        
        if already_exists:
            break

        paths.append(path)

        dijkstra.penalize_path(path)

    for i, path in enumerate(paths):
        print(f"Path {i + 1}")

        for hub in path:
            print(hub.name, end=" -> ")

        print()
    drones = []

    if not paths:
        print("No valid path found")
        return
    
    for i in range(loader.nb_drones):
        path = paths[i % len(paths)]

        drone = Drone(i + 1, loader.start_hub, path)

        drones.append(drone)

    reserved = {}
    turn = 0

    for hub in loader.hubs.values():
        reserved[hub.name] = 0


    while not all_finished(drones, loader.end_hub):
        turn += 1

        used_connections = {}
        movements = []
        hub_occ = {} #How many drones are currently occupying each hub

        # -----------------------------
        # Count drones in every hub
        # -----------------------------
        for hub in loader.hubs.values():
            hub_occ[hub.name] = 0

        for drone in drones:
            if not drone.in_flight and drone.position != loader.end_hub:
                hub_occ[drone.position.name] += 1

        # -----------------------------
        # Process drones
        # -----------------------------
        for drone in drones:

            # -------------------------
            # Drone is already flying
            # -------------------------
            if drone.in_flight:
                destination = drone.destination

                drone.finish_flight()

                if not drone.in_flight:
                    reserved[destination.name] -= 1
                    hub_occ[destination.name] += 1

                    movements.append(
                        f"D{drone.drone_id}-{drone.position.name}"
                    )

                continue

            """ Already at goal"""
            if drone.position == loader.end_hub:
                continue

            current = drone.position
            current_index = drone.path.index(current)

            if current_index + 1 >= len(drone.path):
                continue

            next_hub = drone.path[current_index + 1]

            connection = loader.get_connection(
                current,
                next_hub
            )

            key = tuple(
                sorted([connection.hub1, connection.hub2])
            )

            used = used_connections.get(key, 0)

            # -------------------------
            # Restricted destination
            # -------------------------
            if next_hub.zone == "restricted":

                if (used < connection.max_link_capacity and hub_occ[next_hub.name] + reserved[next_hub.name] < next_hub.max_drones):
                    drone.flight(next_hub)

                    used_connections[key] = used + 1

                    # Drone leaves current hub
                    hub_occ[current.name] -= 1

                    movements.append(
                        f"D{drone.drone_id}-"
                        f"{connection.hub1}-"
                        f"{connection.hub2}"
                    )

            # -------------------------
            # Normal / priority
            # -------------------------
            else:

                if (used < connection.max_link_capacity and hub_occ[next_hub.name] < next_hub.max_drones):
                    drone.move_drone()

                    used_connections[key] = used + 1

                    hub_occ[current.name] -= 1
                    hub_occ[next_hub.name] += 1

                    movements.append(
                        f"D{drone.drone_id}-"
                        f"{drone.position.name}"
                    )

        # -----------------------------
        # Print this turn
        # -----------------------------
        if movements:
            print(" ".join(movements))
            print(f"Total turns: {turn}")


if __name__ == "__main__":
    main()