from typing import Optional
import argparse
from algorithm import Dijkstra
from drones import Drone
from loading import Hub, Loading, ParsingError

FILE_PATH = (
    "/home/aidbrm/Desktop/fly/maps/challenger/01_the_impossible_dream.txt"
)

COLORS = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "reset": "\033[0m",
    "purple": "\033[38;5;129m",
    "brown": "\033[38;5;130m",
    "orange": "\033[38;5;208m",
    "maroon": "\033[38;5;88m",
    "gold": "\033[38;5;220m",
    "darkred": "\033[38;5;52m",
    "violet": "\033[38;5;177m",
    "crimson": "\033[38;5;196m",
    "rainbow": "\033[38;5;201m",
}


class make_colors:
    @staticmethod
    def color_hub(hub: Hub) -> str:
        color = COLORS.get(hub.color, "")
        return f"{color}{hub.name}{COLORS['reset']}"


def all_finished(drones: list[Drone], end: Optional[Hub]) -> bool:
    for drone in drones:
        if drone.position != end:
            return False

    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capacity-info", action="store_true")
    parser.add_argument("map_file")

    return parser.parse_args()


def main() -> None:
    try:
        args = parse_args()

        loader = Loading()
        loader.processing(args.map_file)

        if loader.start_hub is None or loader.end_hub is None:
            print("ERROR: Missing start or end hub")
            return

        start_hub: Hub = loader.start_hub
        end_hub: Hub = loader.end_hub

        dijkstra = Dijkstra(loader)

        paths: list[list[Hub]] = []

        for _ in range(3):
            dijkstra.initialize()
            dijkstra.run()

            path = dijkstra.get_path()

            if len(path) <= 1 or path[0] != start_hub:
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
                print(make_colors.color_hub(hub), end=" -> ")

            print()

        drones: list[Drone] = []

        if not paths:
            print("No valid path found")
            return

        for i in range(loader.nb_drones):
            path = paths[i % len(paths)]

            drone = Drone(i + 1, start_hub, path)

            drones.append(drone)

        reserved: dict[str, int] = {}
        turn = 0

        for hub in loader.hubs.values():
            reserved[hub.name] = 0

        while not all_finished(drones, end_hub):
            turn += 1

            used_connections: dict[tuple[str, str], int] = {}
            movements: list[str] = []
            hub_occ: dict[str, int] = {}  # How many drones occupy each hub

            # -----------------------------
            # Count drones in every hub
            # -----------------------------
            for hub in loader.hubs.values():
                hub_occ[hub.name] = 0

            for drone in drones:
                if not drone.in_flight and drone.position != end_hub:
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

                    if not drone.in_flight and destination is not None:
                        reserved[destination.name] -= 1
                        hub_occ[destination.name] += 1

                        movements.append(
                            f"D{drone.drone_id}-{drone.position.name}"
                        )

                    continue

                # Already at goal
                if drone.position == end_hub:
                    continue

                current = drone.position
                current_index = drone.path.index(current)

                if current_index + 1 >= len(drone.path):
                    continue

                next_hub = drone.path[current_index + 1]

                connection = loader.get_connection(current, next_hub)

                if connection is None:
                    continue

                key = (
                    min(connection.hub1, connection.hub2),
                    max(connection.hub1, connection.hub2),
                )

                used = used_connections.get(key, 0)

                # -------------------------
                # Restricted destination
                # -------------------------
                if next_hub.zone == "restricted":
                    has_link_cap = used < connection.max_link_capacity
                    has_hub_cap = (
                        hub_occ[next_hub.name] + reserved[next_hub.name]
                        < next_hub.max_drones
                    )

                    if has_link_cap and has_hub_cap:
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
                    has_link_cap = used < connection.max_link_capacity

                    has_hub_cap = hub_occ[next_hub.name] < next_hub.max_drones

                    if has_link_cap and has_hub_cap:
                        drone.move_drone()

                        used_connections[key] = used + 1

                        hub_occ[current.name] -= 1
                        hub_occ[next_hub.name] += 1

                        movements.append(
                            f"D{drone.drone_id}-"
                            f"{make_colors.color_hub(drone.position)}"
                        )

            # -----------------------------
            # Print this turn
            # -----------------------------
            if movements:
                print(" ".join(movements))

        print(f"Total turns: {turn}")
    except Exception as e:
        raise ParsingError(f"{e}")


if __name__ == "__main__":
    try:
        main()
    except BaseException as e:
        print(e)
        import sys
        sys.exit(1)
