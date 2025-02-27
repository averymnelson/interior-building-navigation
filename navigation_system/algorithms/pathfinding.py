from typing import Dict, List, Set, Tuple
import heapq
from models.node import NavigationGraph, Node

def heuristic(node: Node, goal: Node) -> float:
    return ((float(node.x) - float(goal.x))**2 + (float(node.y) - float(goal.y))**2)**0.5

def a_star(graph: NavigationGraph, start_id: str, goal_id: str) -> List[str]:
    if start_id not in graph.nodes or goal_id not in graph.nodes:
        return []

    start = graph.nodes[start_id]
    goal = graph.nodes[goal_id]

    # print(f"Start node: {start_id}, Goal node: {goal_id}")
    
    open_set: List[Tuple[float, str]] = [(0, start_id)]
    came_from: Dict[str, str] = {}
    
    g_score: Dict[str, float] = {start_id: 0}
    f_score: Dict[str, float] = {start_id: heuristic(start, goal)}
    
    open_set_hash: Set[str] = {start_id}
    
    while open_set:
        current_id = heapq.heappop(open_set)[1]
        # print(f"Current node: {current_id}")
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

            #print(f"Checking neighbor {neighbor_id}, tentative_g_score: {tentative_g_score}")
            
            if tentative_g_score < g_score.get(neighbor_id, float('inf')):
                neighbor = graph.nodes[neighbor_id]
                came_from[neighbor_id] = current_id
                g_score[neighbor_id] = tentative_g_score
                f_score[neighbor_id] = tentative_g_score + heuristic(neighbor, goal)
                
                if neighbor_id not in open_set_hash:
                    heapq.heappush(open_set, (f_score[neighbor_id], neighbor_id))
                    open_set_hash.add(neighbor_id)
    
    return []  # No path found
