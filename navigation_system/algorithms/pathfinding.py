from typing import Dict, List, Tuple
import heapq
from navigation_system.models.node import NavigationGraph, Node

def heuristic(node: Node, goal: Node) -> float:
    """Euclidean distance heuristic"""
    return ((float(node.x) - float(goal.x))**2 + (float(node.y) - float(goal.y))**2)**0.5

def a_star(
    graph: NavigationGraph,
    start_id: str,
    goal_id: str,
    edges_data: List[Dict],
    prefer_hallways: bool = True
) -> List[str]:
    """A* pathfinding with hallway preference. Assumes edges_data already includes all allowed edges."""
    
    if start_id not in graph.nodes or goal_id not in graph.nodes:
        print(f"Start node {start_id} or goal node {goal_id} not in graph")
        return []

    start = graph.nodes[start_id]
    goal = graph.nodes[goal_id]

    # Build edge lookup: edge_key => {'hallway': bool}
    edge_lookup = {}
    adjacency = {}
    for edge in edges_data:
        a, b = edge['pointnum1'], edge['pointnum2']
        is_hallway = edge.get('hallway', False)
        
        key_ab = f"{a}-{b}"
        key_ba = f"{b}-{a}"
        edge_lookup[key_ab] = {'hallway': is_hallway}
        edge_lookup[key_ba] = {'hallway': is_hallway}

        adjacency.setdefault(a, set()).add(b)
        adjacency.setdefault(b, set()).add(a)

    open_set = [(0, 0, start_id)]  # (non_hallway_count, f_score, node_id)
    open_set_hash = {start_id}
    came_from = {}

    g_score = {start_id: 0}
    non_hallway_count = {start_id: 0}
    f_score = {start_id: heuristic(start, goal)}

    while open_set:
        _, _, current_id = heapq.heappop(open_set)
        open_set_hash.remove(current_id)

        if current_id == goal_id:
            path = []
            while current_id in came_from:
                path.append(current_id)
                current_id = came_from[current_id]
            path.append(start_id)
            return path[::-1]

        current_node = graph.nodes[current_id]
        neighbors = adjacency.get(current_id, set())

        for neighbor_id in neighbors:
            if neighbor_id not in graph.nodes:
                continue
            neighbor = graph.nodes[neighbor_id]
            edge_key = f"{current_id}-{neighbor_id}"
            edge_info = edge_lookup.get(edge_key)
            if edge_info is None:
                continue  # skip unknown edge

            # Distance
            dx = float(current_node.x) - float(neighbor.x)
            dy = float(current_node.y) - float(neighbor.y)
            weight = (dx**2 + dy**2) ** 0.5

            # Handle hallway preference
            is_hallway = edge_info.get('hallway', False)
            new_non_hallway_count = non_hallway_count[current_id]
            if not is_hallway:
                new_non_hallway_count += 1

            tentative_g = g_score[current_id] + weight

            # Update if better path found
            better = False
            if neighbor_id not in g_score:
                better = True
            elif new_non_hallway_count < non_hallway_count[neighbor_id]:
                better = True
            elif new_non_hallway_count == non_hallway_count[neighbor_id] and tentative_g < g_score[neighbor_id]:
                better = True

            if better:
                came_from[neighbor_id] = current_id
                g_score[neighbor_id] = tentative_g
                non_hallway_count[neighbor_id] = new_non_hallway_count
                f = tentative_g + heuristic(neighbor, goal)
                f_score[neighbor_id] = f

                if neighbor_id not in open_set_hash:
                    heapq.heappush(open_set, (new_non_hallway_count, f, neighbor_id))
                    open_set_hash.add(neighbor_id)

    print("No path found")
    return []

# Correct implementation of find_restroom function that aligns with a_star parameters:

def find_restroom(graph: NavigationGraph, room_id: str, edges_data=None, keycard_edges_data=None, has_keycard=False):
    """Find the nearest restroom from a given room"""
    restrooms = [1162, 1166, 1265, 1261, 2513, 2517, 4407, 4405, 4721, 4725]
    shortest_path = None
    shortest_restroom_id = None
    shortest_path_length = float('inf')
    fewest_non_hallways = float('inf')

    if room_id in map(str, restrooms):
        return room_id  # If already at a restroom, return the same id

    # Prepare all edges for pathfinding
    all_edges = []
    if edges_data:
        all_edges.extend(edges_data)
    
    # Add keycard edges if user has keycard
    if has_keycard and keycard_edges_data:
        all_edges.extend(keycard_edges_data)
        print(f"✅ Added {len(keycard_edges_data)} keycard edges to restroom search")

    for restroom_id in restrooms:
        # Call a_star with the correct number of parameters
        path = a_star(graph, room_id, str(restroom_id), all_edges, True)
        
        if path:
            # Count non-hallway segments
            non_hallway_segments = 0
            
            # Create a dictionary for quick edge lookup
            edge_lookup = {}
            for edge in all_edges:
                key1 = f"{edge['pointnum1']}-{edge['pointnum2']}"
                key2 = f"{edge['pointnum2']}-{edge['pointnum1']}"
                is_hallway = edge.get('hallway', False)
                edge_lookup[key1] = {'hallway': is_hallway}
                edge_lookup[key2] = {'hallway': is_hallway}
            
            for i in range(len(path) - 1):
                edge_key = f"{path[i]}-{path[i+1]}"
                edge_info = edge_lookup.get(edge_key, {'hallway': False})
                if not edge_info.get('hallway', False):
                    non_hallway_segments += 1
            
            # First prioritize minimizing non-hallway segments, then path length
            if non_hallway_segments < fewest_non_hallways or \
               (non_hallway_segments == fewest_non_hallways and len(path) < shortest_path_length):
                fewest_non_hallways = non_hallway_segments
                shortest_path_length = len(path)
                shortest_path = path
                shortest_restroom_id = restroom_id

    if shortest_restroom_id:
        print(f"Path from Room {room_id} to Restroom {shortest_restroom_id}: {shortest_path}")
        print(f"Path has {fewest_non_hallways} non-hallway segments and {shortest_path_length} total segments")
    return str(shortest_restroom_id) if shortest_restroom_id else None
