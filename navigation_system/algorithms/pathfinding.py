from typing import Dict, List, Set, Tuple
import heapq
from navigation_system.models.node import NavigationGraph, Node

def heuristic(node: Node, goal: Node) -> float:
    return ((float(node.x) - float(goal.x))**2 + (float(node.y) - float(goal.y))**2)**0.5

def a_star(graph: NavigationGraph, start_id: str, goal_id: str, edges_data=None, prefer_hallways: bool = True) -> List[str]:
    """
    A* pathfinding algorithm that prioritizes hallway paths without changing edge weights.
    
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
    
    # First, try to find a path using only hallway connections
    if prefer_hallways and hallway_lookup:
        # Print info about hallway edges
        hallway_count = sum(1 for v in hallway_lookup.values() if v)
        print(f"Found {hallway_count} hallway edges out of {len(hallway_lookup)} total")
        
        # Create a filtered graph with only hallway connections
        hallway_graph = NavigationGraph()
        
        # Add all nodes to the hallway graph
        for node_id, node in graph.nodes.items():
            hallway_graph.add_node(node_id, node.type_name, node.layer, node.x, node.y)
        
        # Add only hallway edges to the hallway graph
        edges_added = 0
        for node_id, node in graph.nodes.items():
            for neighbor_id, weight in node.connections:
                edge_key = f"{node_id}-{neighbor_id}"
                hallway_value = hallway_lookup.get(edge_key, False)
                print(f"Edge {edge_key}: hallway={hallway_value}")
                if hallway_value:
                    # This is a hallway connection, add it to the hallway graph
                    try:
                        hallway_graph.add_edge(node_id, neighbor_id)
                        edges_added += 1
                    except KeyError:
                        pass
        
        print(f"Created hallway-only graph with {edges_added} hallway edges")
        
        # Try to find a path in the hallway-only graph
        hallway_path = standard_a_star(hallway_graph, start_id, goal_id, hallway_lookup)
        
        if hallway_path:
            print(f"Found hallway-only path: {hallway_path}")
            # Verify and print hallway status for each edge in the path
            print("Hallway status for each edge in path:")
            for i in range(len(hallway_path) - 1):
                edge_key = f"{hallway_path[i]}-{hallway_path[i+1]}"
                hallway_value = hallway_lookup.get(edge_key, "not found")
                print(f"  {edge_key}: hallway={hallway_value}")
            return hallway_path
        
        print("No hallway-only path found, falling back to regular graph with hallway preference")
    
    # If we couldn't find a hallway-only path or prefer_hallways is False,
    # fall back to the regular graph but still prefer hallway connections
    return standard_a_star(graph, start_id, goal_id, hallway_lookup)

def standard_a_star(graph: NavigationGraph, start_id: str, goal_id: str, hallway_lookup=None) -> List[str]:
    """
    Standard A* algorithm that prefers hallway connections when possible.
    """
    start = graph.nodes[start_id]
    goal = graph.nodes[goal_id]
    
    # Priority queue with 3 components: (f_score, is_not_hallway, node_id)
    # - f_score: lower is better
    # - is_not_hallway: 0 for hallway connections, 1 for non-hallway connections
    # - node_id: used for tiebreaking
    open_set = [(0, 0, start_id)]
    
    came_from = {}
    
    g_score = {start_id: 0}
    f_score = {start_id: heuristic(start, goal)}
    
    open_set_hash = {start_id}
    
    while open_set:
        current = heapq.heappop(open_set)
        current_id = current[2]
        open_set_hash.remove(current_id)
        
        if current_id == goal_id:
            path = []
            while current_id in came_from:
                path.append(current_id)
                current_id = came_from[current_id]
            path.append(start_id)
            path = path[::-1]
            
            # Print hallway status for each edge in the final path
            if hallway_lookup:
                print("Final path with hallway status:")
                for i in range(len(path) - 1):
                    edge_key = f"{path[i]}-{path[i+1]}"
                    hallway_value = hallway_lookup.get(edge_key, "not found")
                    print(f"  {edge_key}: hallway={hallway_value}")
            
            return path
        
        current_node = graph.nodes[current_id]
        
        for neighbor_id, weight in current_node.connections:
            # Use actual distance for weight calculation
            tentative_g_score = g_score[current_id] + weight
            
            if tentative_g_score < g_score.get(neighbor_id, float('inf')):
                neighbor = graph.nodes[neighbor_id]
                came_from[neighbor_id] = current_id
                g_score[neighbor_id] = tentative_g_score
                f = tentative_g_score + heuristic(neighbor, goal)
                f_score[neighbor_id] = f
                
                if neighbor_id not in open_set_hash:
                    # Check if this connection is a hallway
                    is_not_hallway = 1  # Default to non-hallway
                    
                    if hallway_lookup:
                        edge_key = f"{current_id}-{neighbor_id}"
                        hallway_value = hallway_lookup.get(edge_key, False)
                        print(f"Considering edge {edge_key}: hallway={hallway_value}, f_score={f}")
                        if hallway_value:
                            is_not_hallway = 0  # This is a hallway connection
                    
                    # The sorting is by (f_score, is_not_hallway, node_id)
                    # This ensures hallway connections are preferred when f_scores are equal
                    heapq.heappush(open_set, (f, is_not_hallway, neighbor_id))
                    open_set_hash.add(neighbor_id)
    
    return []  # No path found

def find_restroom(graph: NavigationGraph, room_id: str, edges_data=None):
    """Find the nearest restroom from a given room"""
    restrooms = [1162, 1166, 1265, 1261, 2513, 2517, 4407, 4405, 4721, 4725]
    shortest_path = None
    shortest_restroom_id = None
    shortest_path_length = float('inf')

    for restroom_id in restrooms:
        path = a_star(graph, room_id, str(restroom_id), edges_data)
    
        if path:
            path_length = len(path) 
            
            if path_length < shortest_path_length:
                shortest_path_length = path_length
                shortest_path = path
                shortest_restroom_id = restroom_id

    print(f"Path from Room {room_id} to Restroom {shortest_restroom_id}: {shortest_path}")
    return str(shortest_restroom_id)
