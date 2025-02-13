from typing import Dict, List, Set, Tuple
import heapq
from models.node import NavigationGraph, Node

def heuristic(node: Node, goal: Node) -> float:
    return ((node.x - goal.x)**2 + (node.y - goal.y)**2)**0.5

def a_star(graph: NavigationGraph, start_id: int, goal_id: int) -> List[int]:
    if start_id not in graph.nodes or goal_id not in graph.nodes:
        return []

    start = graph.nodes[start_id]
    goal = graph.nodes[goal_id]
    
    open_set: List[Tuple[float, int]] = [(0, start_id)]
    came_from: Dict[int, int] = {}
    
    g_score: Dict[int, float] = {start_id: 0}
    f_score: Dict[int, float] = {start_id: heuristic(start, goal)}
    
    open_set_hash: Set[int] = {start_id}
    
    while open_set:
        current_id = heapq.heappop(open_set)[1]
        open_set_hash.remove(current_id)
        
        if current_id == goal_id:
            path = []
            while current_id in came_from:
                path.append(current_id)
                current_id = came_from[current_id]
            path.append(start_id)
            return path[::-1]
            
        current = graph.nodes[current_id]
        
        for neighbor_id, weight in current.connections:
            tentative_g_score = g_score[current_id] + weight
            
            if tentative_g_score < g_score.get(neighbor_id, float('inf')):
                neighbor = graph.nodes[neighbor_id]
                came_from[neighbor_id] = current_id
                g_score[neighbor_id] = tentative_g_score
                f_score[neighbor_id] = tentative_g_score + heuristic(neighbor, goal)
                
                if neighbor_id not in open_set_hash:
                    heapq.heappush(open_set, (f_score[neighbor_id], neighbor_id))
                    open_set_hash.add(neighbor_id)
    
    return []  # No path found
