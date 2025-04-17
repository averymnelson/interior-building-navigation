# utils/distance.py
from typing import Dict, Tuple

def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate Euclidean distance between two points"""
    return ((float(x1) - float(x2))**2 + (float(y1) - float(y2))**2)**0.5

def find_nearest_node(x: float, y: float, nodes: Dict) -> Tuple[str, float]:
    """
    Find the node nearest to the given coordinates
    
    Args:
        x: X coordinate
        y: Y coordinate
        nodes: Dictionary of node objects
        
    Returns:
        Tuple of (node_id, distance)
    """
    nearest_id = None
    min_distance = float('inf')
    
    for node_id, node in nodes.items():
        dist = calculate_distance(x, y, node.x, node.y)
        if dist < min_distance:
            min_distance = dist
            nearest_id = node_id
            
    return nearest_id, min_distance
