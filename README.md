*This project has been created as part of the 42 curriculum by aidbrm.*

# Fly-in

## Description

**Fly-in** is a Python project that simulates a fleet of drones navigating through a network of hubs and connections from a starting point to a destination.

The main goal of the project is to design an algorithm capable of finding efficient routes through a graph while respecting different constraints such as:

- Hub capacity.
- Connection/link capacity.
- Restricted zones.
- Priority zones.
- Multiple possible paths.
- Dead ends and loops.
- Congestion between drones.
- Drones already travelling between hubs.
- Synchronization of multiple drones.
- Turn-by-turn movement.

The project combines **graph algorithms**, **path finding**, and **simulation**.

The map describes a graph where:

- Hubs represent nodes.
- Connections represent edges.
- Drones travel from the `start_hub` to the `end_hub`.
- Each hub can have a maximum number of drones.
- Each connection can have a maximum number of drones using it simultaneously.
- Zones can modify the cost or behavior of a route.

The program first analyzes the map and calculates possible routes. It then assigns drones to these routes and simulates their movements turn by turn until every drone reaches the destination.

---

## Features

- Custom map parser.
- Graph representation using hubs and connections.
- Dijkstra shortest-path algorithm.
- Alternative path generation.
- Path penalization to discover different routes.
- Priority-zone handling.
- Restricted-zone handling.
- Hub capacity management.
- Connection capacity management.
- Reservation system for drones in transit.
- Multi-drone scheduling.
- Turn-by-turn simulation.
- Dead-end and loop avoidance.
- Colored terminal output.
- Support for different map difficulties.
- Optimized drone distribution across available paths.

---

## Algorithm

### Graph Representation

The map is represented as a graph.

Each `Hub` represents a node and stores information such as:

- Name.
- Coordinates.
- Zone.
- Color.
- Maximum drone capacity.
- Neighboring hubs.

Connections represent edges between hubs and can have their own capacity.

Conceptually, the graph looks like:

```text
             ┌── hub A ──┐
start ───────┤            ├── destination
             └── hub B ──┘