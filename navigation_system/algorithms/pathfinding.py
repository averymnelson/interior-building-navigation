from typing import Dict, List, Set, Tuple
import heapq
from navigation_system.models.node import NavigationGraph, Node

def heuristic(node: Node, goal: Node) -> float:
    """Distance heuristic for A* algorithm"""
    return ((float(node.x) - float(goal.x))**2 + (float(node.y) - float(goal.y))**2)**0.5

def a_star(graph: NavigationGraph, start_id: str, goal_id: str, edges_data=None, prefer_hallways: bool = True) -> List[str]:
    """
    A* pathfinding algorithm that prioritizes minimizing non-hallway segments first,
    then considers path length as a secondary criterion.
    
    Args:
        graph: The navigation graph
        start_id: Starting node ID
        goal_id: Destination node ID
        edges_data: Edge data from the database containing hallway information
        prefer_hallways: Whether to prefer hallway paths when possible
    
    Returns:
        List of node IDs representing the path from start to goal
    """
    if start_id not in graph.nodes or goal_id not in graph.nodes:
        print(f"Start node {start_id} or goal node {goal_id} not in graph")
        return []

    start = graph.nodes[start_id]
    goal = graph.nodes[goal_id]
    
    # Create a dictionary to quickly lookup hallway status for an edge
    hallway_lookup = {}
    if edges_data and prefer_hallways:
        for edge in edges_data:
            # Create keys for both directions of the edge
            key1 = f"{edge['pointnum1']}-{edge['pointnum2']}"
            key2 = f"{edge['pointnum2']}-{edge['pointnum1']}"
            is_hallway = edge.get('hallway', False)
            hallway_lookup[key1] = is_hallway
            hallway_lookup[key2] = is_hallway
    
    # Print info about hallway edges for debugging
    # hallway_count = sum(1 for v in hallway_lookup.values() if v)
    # print(f"Found {hallway_count} hallway edges out of {len(hallway_lookup)} total")

    # Priority queue with components: (non_hallway_count, distance, node_id)
    # This makes non-hallway segment count the primary sorting criterion
    open_set = [(0, 0, start_id)]
    
    came_from = {}
    
    # Track both distance and non-hallway count
    g_score = {start_id: 0}  # Regular distance
    non_hallway_count = {start_id: 0}  # Count of non-hallway segments
    
    # Estimate to goal
    f_score = {start_id: heuristic(start, goal)}
    
    open_set_hash = {start_id}
    
    while open_set:
        # Unpack the current node (non_hallway_count, distance, node_id)
        current = heapq.heappop(open_set)
        current_id = current[2]
        current_non_hallway_count = current[0]
        
        open_set_hash.remove(current_id)
        
        # Check if we've reached the goal
        if current_id == goal_id:
            path = []
            while current_id in came_from:
                path.append(current_id)
                current_id = came_from[current_id]
            path.append(start_id)
            path = path[::-1]
            
            # Print hallway status for debugging
            # print("Final path with hallway status:")
            non_hallway_segments = 0
            for i in range(len(path) - 1):
                edge_key = f"{path[i]}-{path[i+1]}"
                hallway_value = hallway_lookup.get(edge_key, False)
                if not hallway_value:
                    non_hallway_segments += 1
                # print(f"  {edge_key}: hallway={hallway_value}")
            
            # print(f"Path has {non_hallway_segments} non-hallway segments out of {len(path)-1} total segments")
            return path
        
        current_node = graph.nodes[current_id]
        
        for neighbor_id, weight in current_node.connections:
            # Check if this connection is a hallway
            edge_key = f"{current_id}-{neighbor_id}"
            is_hallway = hallway_lookup.get(edge_key, False)
            
            # Increment non-hallway count if this is not a hallway
            new_non_hallway_count = current_non_hallway_count
            if not is_hallway:
                new_non_hallway_count += 1
            
            # Calculate regular distance
            tentative_g_score = g_score[current_id] + weight
            
            # We update if either:
            # 1. This path has fewer non-hallway segments, or
            # 2. Same number of non-hallway segments but shorter distance
            update_needed = False
            if neighbor_id not in non_hallway_count:
                update_needed = True
            elif new_non_hallway_count < non_hallway_count[neighbor_id]:
                update_needed = True
            elif new_non_hallway_count == non_hallway_count[neighbor_id] and tentative_g_score < g_score.get(neighbor_id, float('inf')):
                update_needed = True
            
            if update_needed:
                neighbor = graph.nodes[neighbor_id]
                came_from[neighbor_id] = current_id
                g_score[neighbor_id] = tentative_g_score
                non_hallway_count[neighbor_id] = new_non_hallway_count
                
                # Estimate to goal using distance
                f = tentative_g_score + heuristic(neighbor, goal)
                f_score[neighbor_id] = f
                
                if neighbor_id not in open_set_hash:
                    # Add to priority queue with non-hallway count as primary key
                    # This ensures paths with fewer non-hallway segments are explored first
                    heapq.heappush(open_set, (new_non_hallway_count, f, neighbor_id))
                    open_set_hash.add(neighbor_id)
    
    print("No path found")
    return []  # No path found

def find_restroom(graph: NavigationGraph, room_id: str, edges_data=None):
    """Find the nearest restroom from a given room"""
    restrooms = [1162, 1166, 1265, 1261, 2513, 2517, 4407, 4405, 4721, 4725]
    shortest_path = None
    shortest_restroom_id = None
    shortest_path_length = float('inf')
    fewest_non_hallways = float('inf')

    for restroom_id in restrooms:
        path = a_star(graph, room_id, str(restroom_id), edges_data)
        
        if path:
            # Count non-hallway segments
            non_hallway_segments = 0
            for i in range(len(path) - 1):
                edge_key = f"{path[i]}-{path[i+1]}"
                is_hallway = False
                for edge in edges_data:
                    if (edge['pointnum1'] == path[i] and edge['pointnum2'] == path[i+1]) or \
                       (edge['pointnum1'] == path[i+1] and edge['pointnum2'] == path[i]):
                        is_hallway = edge.get('hallway', False)
                        break
                if not is_hallway:
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
