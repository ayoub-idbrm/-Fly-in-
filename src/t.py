"""
Matplotlib visualization for the drone delivery simulation.

Drop this file next to your existing `main.py` (so the `src` package
is importable) and run:

    pip install matplotlib
    python visualize.py
"""

from collections import namedtuple

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.lines as mlines

from src.loading import Loading
from src.algorithm import Dijkstra
from src.drones import Drone


MAP_FILE = "/home/aidbrm/Desktop/fly/maps/easy/03_basic_capacity.txt"

SUBSTEPS = 10        # animation smoothness per turn
TURN_DURATION_MS = 20 # how long one simulation turn takes to animate
MAX_PATHS = 3         # matches main.py: up to 3 Dijkstra paths, penalized in turn

START_COLOR = "#3cc85a"
END_COLOR = "#dc4646"
RESTRICTED_COLOR = "#e6a028"
PRIORITY_COLOR = "#c060e0"
BLOCKED_COLOR = "#555560"
HUB_COLOR = "#4682b4"
CONNECTION_COLOR = "#5a5a64"
BG_COLOR = "#121218"
TEXT_COLOR = "white"

# A movement describes, for one drone during one turn, the hub-to-hub
# segment it travels along and which portion of that segment (start_t
# to end_t, both in [0, 1]) it covers during this turn.
Movement = namedtuple("Movement", ["drone_id", "from_hub", "to_hub", "start_t", "end_t"])


# ----------------------------------------------------------------------
# Simulation (same rules as main(), refactored to yield per-turn drone
# movements instead of printing them)
#
# Notes on timing:
# Drone.flight() sets turns = 2, and finish_flight() only decrements
# `turns` - it is not called on the turn flight() itself is invoked.
# So a restricted-hub crossing actually spans 3 turns end to end:
#   turn T   -> drone.flight(next_hub) is called (departure)
#   turn T+1 -> finish_flight(): turns 2 -> 1 (still in flight)
#   turn T+2 -> finish_flight(): turns 1 -> 0 (lands, position updates)
# main.py only prints a movement on the landing turn; here we animate
# smoothly across all three turns so the drone doesn't appear to jump.
# ----------------------------------------------------------------------

def all_finished(drones, end):
    return all(drone.position == end for drone in drones)


def compute_paths(loader, dijkstra, max_paths=MAX_PATHS):
    """Compute up to `max_paths` distinct Dijkstra paths, penalizing
    each one before computing the next (mirrors main.py)."""
    paths = []
    for _ in range(max_paths):
        dijkstra.initialize()
        dijkstra.run()
        path = dijkstra.get_path()

        if len(path) <= 1 or path[0] != loader.start_hub:
            break

        paths.append(path)
        dijkstra.penalize_path(path)

    return paths


def simulate_turns(loader, drones):
    """Run the delivery simulation turn by turn, yielding a list of
    Movement objects for each turn."""

    reserved = {hub.name: 0 for hub in loader.hubs.values()}
    flights = {}  # drone_id -> {"origin", "destination", "elapsed", "total"}

    while not all_finished(drones, loader.end_hub):
        used_connections = {}
        hub_occ = {hub.name: 0 for hub in loader.hubs.values()}

        for drone in drones:
            if not drone.in_flight and drone.position != loader.end_hub:
                hub_occ[drone.position.name] += 1

        movements = []
        for drone in drones:
            movement = process_drone(drone, loader, hub_occ, used_connections, reserved, flights)
            if movement:
                movements.append(movement)

        yield movements


def process_drone(drone, loader, hub_occ, used_connections, reserved, flights):
    if drone.in_flight:
        return continue_drone_flight(drone, hub_occ, reserved, flights)

    if drone.position == loader.end_hub:
        return None

    current_index = drone.path.index(drone.position)
    if current_index + 1 >= len(drone.path):
        return None

    next_hub = drone.path[current_index + 1]
    connection = loader.get_connection(drone.position, next_hub)
    key = tuple(sorted([connection.hub1, connection.hub2]))
    used = used_connections.get(key, 0)

    if used >= connection.max_link_capacity:
        return None

    if next_hub.zone == "restricted":
        # NOTE: mirrors main.py exactly - `reserved` is only ever
        # decremented (on landing), never incremented on departure.
        if hub_occ[next_hub.name] + reserved[next_hub.name] >= next_hub.max_drones:
            return None

        used_connections[key] = used + 1
        return start_drone_flight(drone, next_hub, hub_occ, flights)

    if hub_occ[next_hub.name] >= next_hub.max_drones:
        return None

    used_connections[key] = used + 1
    return move_drone(drone, next_hub, hub_occ)


def start_drone_flight(drone, next_hub, hub_occ, flights):
    origin = drone.position

    drone.flight(next_hub)
    hub_occ[origin.name] -= 1

    total_turns = drone.turns + 1  # departure turn + `turns` finish_flight() calls
    flights[drone.drone_id] = {
        "origin": origin,
        "destination": next_hub,
        "elapsed": 1,
        "total": total_turns,
    }

    return Movement(drone.drone_id, origin, next_hub, 0.0, 1 / total_turns)


def continue_drone_flight(drone, hub_occ, reserved, flights):
    info = flights[drone.drone_id]
    origin, destination = info["origin"], info["destination"]
    total = info["total"]

    drone.finish_flight()

    start_t = info["elapsed"] / total
    info["elapsed"] += 1
    end_t = min(info["elapsed"] / total, 1.0)

    if not drone.in_flight:
        reserved[destination.name] -= 1
        hub_occ[destination.name] += 1
        del flights[drone.drone_id]

    return Movement(drone.drone_id, origin, destination, start_t, end_t)


def move_drone(drone, next_hub, hub_occ):
    origin = drone.position

    drone.move_drone()
    hub_occ[origin.name] -= 1
    hub_occ[next_hub.name] += 1

    return Movement(drone.drone_id, origin, next_hub, 0.0, 1.0)


# ----------------------------------------------------------------------
# Turn-by-turn movements -> smooth per-frame drone positions
# ----------------------------------------------------------------------

def build_frames(loader, drones, turns):
    layout = {name: (hub.x, hub.y) for name, hub in loader.hubs.items()}
    positions = {drone.drone_id: layout[loader.start_hub.name] for drone in drones}

    frames = []
    for movements in turns:
        for step in range(1, SUBSTEPS + 1):
            progress = step / SUBSTEPS

            for m in movements:
                t = m.start_t + (m.end_t - m.start_t) * progress
                fx, fy = layout[m.from_hub.name]
                tx, ty = layout[m.to_hub.name]
                positions[m.drone_id] = (fx + (tx - fx) * t, fy + (ty - fy) * t)

            frames.append(dict(positions))

    return layout, frames


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------
"""
Matplotlib visualization for the drone delivery simulation.

Drop this file next to your existing `main.py` (so the `src` package
is importable) and run:

    pip install matplotlib
    python visualize.py
"""

from collections import namedtuple

import matplotlib.pyplot as plt
import matplotlib.animation as animation

from src.loading import Loading
from src.algorithm import Dijkstra
from src.drones import Drone


MAP_FILE = "/home/aidbrm/Desktop/fly/maps/hard/01_maze_nightmare.txt"

SUBSTEPS = 10        # animation smoothness per turn
TURN_DURATION_MS = 2 # how long one simulation turn takes to animate

START_COLOR = "#3cc85a"
END_COLOR = "#dc4646"
RESTRICTED_COLOR = "#e6a028"
HUB_COLOR = "#4682b4"
CONNECTION_COLOR = "#5a5a64"
BG_COLOR = "#121218"
TEXT_COLOR = "white"

# A movement describes, for one drone during one turn, the hub-to-hub
# segment it travels along and which portion of that segment (start_t
# to end_t, both in [0, 1]) it covers during this turn.
Movement = namedtuple("Movement", ["drone_id", "from_hub", "to_hub", "start_t", "end_t"])


# ----------------------------------------------------------------------
# Simulation (same rules as the original main(), refactored to yield
# per-turn drone movements instead of printing them)
# ----------------------------------------------------------------------

def all_finished(drones, end):
    return all(drone.position == end for drone in drones)


def simulate_turns(loader, drones):
    """Run the delivery simulation turn by turn, yielding a list of
    Movement objects for each turn."""

    while not all_finished(drones, loader.end_hub):
        used_connections = {}
        hub_occ = {hub.name: 0 for hub in loader.hubs.values()}

        for drone in drones:
            if not drone.in_flight and drone.position != loader.end_hub:
                hub_occ[drone.position.name] += 1

        movements = []
        for drone in drones:
            movement = process_drone(drone, loader, hub_occ, used_connections)
            if movement:
                movements.append(movement)

        yield movements


def process_drone(drone, loader, hub_occ, used_connections):
    if drone.in_flight:
        return finish_drone_flight(drone, hub_occ)

    if drone.position == loader.end_hub:
        return None

    current_index = drone.path.index(drone.position)
    if current_index + 1 >= len(drone.path):
        return None

    next_hub = drone.path[current_index + 1]
    connection = loader.get_connection(drone.position, next_hub)
    key = tuple(sorted([connection.hub1, connection.hub2]))
    used = used_connections.get(key, 0)

    if used >= connection.max_link_capacity or hub_occ[next_hub.name] >= next_hub.max_drones:
        return None

    used_connections[key] = used + 1

    if next_hub.zone == "restricted":
        return start_drone_flight(drone, next_hub, hub_occ)

    return move_drone(drone, next_hub, hub_occ)


def finish_drone_flight(drone, hub_occ):
    origin = drone.position
    destination = drone.destination

    drone.finish_flight()

    if drone.in_flight:
        return None  # flight not finished yet

    hub_occ[destination.name] += 1
    return Movement(drone.drone_id, origin, destination, 0.5, 1.0)


def start_drone_flight(drone, next_hub, hub_occ):
    origin = drone.position

    drone.flight(next_hub)
    hub_occ[origin.name] -= 1

    return Movement(drone.drone_id, origin, next_hub, 0.0, 0.5)


def move_drone(drone, next_hub, hub_occ):
    origin = drone.position

    drone.move_drone()
    hub_occ[origin.name] -= 1
    hub_occ[next_hub.name] += 1

    return Movement(drone.drone_id, origin, next_hub, 0.0, 1.0)


# ----------------------------------------------------------------------
# Turn-by-turn movements -> smooth per-frame drone positions
# ----------------------------------------------------------------------

def build_frames(loader, drones, turns):
    layout = {name: (hub.x, hub.y) for name, hub in loader.hubs.items()}
    positions = {drone.drone_id: layout[loader.start_hub.name] for drone in drones}

    frames = []
    for movements in turns:
        for step in range(1, SUBSTEPS + 1):
            progress = step / SUBSTEPS

            for m in movements:
                t = m.start_t + (m.end_t - m.start_t) * progress
                fx, fy = layout[m.from_hub.name]
                tx, ty = layout[m.to_hub.name]
                positions[m.drone_id] = (fx + (tx - fx) * t, fy + (ty - fy) * t)

            frames.append(dict(positions))

    return layout, frames


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------

def hub_color(loader, hub):
    if hub == loader.start_hub:
        return START_COLOR
    if hub == loader.end_hub:
        return END_COLOR
    if hub.zone == "restricted":
        return RESTRICTED_COLOR
    return HUB_COLOR


def draw_static_map(ax, loader, layout):
    for connection in loader.connections:
        x1, y1 = layout[connection.hub1]
        x2, y2 = layout[connection.hub2]
        ax.plot([x1, x2], [y1, y2], color=CONNECTION_COLOR, zorder=1)

    for hub in loader.hubs.values():
        x, y = layout[hub.name]
        ax.scatter(x, y, s=400, color=hub_color(loader, hub), zorder=2, edgecolors=BG_COLOR)
        ax.annotate(hub.name, (x, y), textcoords="offset points", xytext=(0, -22),
                    ha="center", color=TEXT_COLOR, fontsize=8)


def animate(loader, layout, frames):
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xticks([])
    ax.set_yticks([])

    draw_static_map(ax, loader, layout)

    drone_dots = ax.scatter([], [], s=60, color="white", zorder=3)
    turn_label = ax.text(0.02, 0.97, "", transform=ax.transAxes, color=TEXT_COLOR, va="top")

    def update(frame_index):
        drone_dots.set_offsets(list(frames[frame_index].values()))
        turn_label.set_text(f"Turn {frame_index // SUBSTEPS + 1}")
        return drone_dots, turn_label

    interval = TURN_DURATION_MS / SUBSTEPS
    ani = animation.FuncAnimation(
        fig, update, frames=len(frames), interval=interval, blit=False, repeat=False
    )
    plt.show()
    return ani  # keep a reference so it isn't garbage-collected mid-animation


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------

def main():
    loader = Loading()
    loader.processing(MAP_FILE)

    dijkstra = Dijkstra(loader)
    dijkstra.initialize()
    dijkstra.run()
    path = dijkstra.get_path()

    drones = [Drone(i + 1, loader.start_hub, path) for i in range(loader.nb_drones)]
    turns = list(simulate_turns(loader, drones))

    layout, frames = build_frames(loader, drones, turns)
    animate(loader, layout, frames)


if __name__ == "__main__":
    main()
def hub_color(loader, hub):
    if hub == loader.start_hub:
        return START_COLOR
    if hub == loader.end_hub:
        return END_COLOR
    if hub.zone == "restricted":
        return RESTRICTED_COLOR
    if hub.zone == "priority":
        return PRIORITY_COLOR
    if hub.zone == "blocked":
        return BLOCKED_COLOR
    return HUB_COLOR


def draw_static_map(ax, loader, layout):
    for connection in loader.connections:
        x1, y1 = layout[connection.hub1]
        x2, y2 = layout[connection.hub2]
        ax.plot([x1, x2], [y1, y2], color=CONNECTION_COLOR, zorder=1)

    for hub in loader.hubs.values():
        x, y = layout[hub.name]
        ax.scatter(x, y, s=400, color=hub_color(loader, hub), zorder=2, edgecolors=BG_COLOR)
        ax.annotate(hub.name, (x, y), textcoords="offset points", xytext=(0, -22),
                    ha="center", color=TEXT_COLOR, fontsize=8)

    legend_entries = [
        ("Start", START_COLOR),
        ("End", END_COLOR),
        ("Restricted", RESTRICTED_COLOR),
        ("Priority", PRIORITY_COLOR),
        ("Blocked", BLOCKED_COLOR),
        ("Normal", HUB_COLOR),
    ]
    handles = [
        mlines.Line2D([], [], color=color, marker="o", linestyle="None",
                       markersize=8, label=label)
        for label, color in legend_entries
    ]
    legend = ax.legend(handles=handles, loc="upper right", facecolor=BG_COLOR,
                        edgecolor=CONNECTION_COLOR, fontsize=8, labelcolor=TEXT_COLOR)
    legend.get_frame().set_alpha(0.85)


def animate(loader, layout, frames):
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xticks([])
    ax.set_yticks([])

    draw_static_map(ax, loader, layout)

    drone_dots = ax.scatter([], [], s=60, color="white", zorder=3)
    turn_label = ax.text(0.02, 0.97, "", transform=ax.transAxes, color=TEXT_COLOR, va="top")

    def update(frame_index):
        drone_dots.set_offsets(list(frames[frame_index].values()))
        turn_label.set_text(f"Turn {frame_index // SUBSTEPS + 1}")
        return drone_dots, turn_label

    interval = TURN_DURATION_MS / SUBSTEPS
    ani = animation.FuncAnimation(
        fig, update, frames=len(frames), interval=interval, blit=False, repeat=False
    )
    plt.show()
    return ani  # keep a reference so it isn't garbage-collected mid-animation


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------

def main():
    loader = Loading()
    loader.processing(MAP_FILE)

    dijkstra = Dijkstra(loader)
    paths = compute_paths(loader, dijkstra)

    if not paths:
        print("No valid path found")
        return

    drones = [
        Drone(i + 1, loader.start_hub, paths[i % len(paths)])
        for i in range(loader.nb_drones)
    ]

    turns = list(simulate_turns(loader, drones))

    layout, frames = build_frames(loader, drones, turns)
    animate(loader, layout, frames)


if __name__ == "__main__":
    main()