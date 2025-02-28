# utils/distance.py
from typing import Dict, Tuple

def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate Euclidean distance between two points"""
    return ((float(x1) - float(x2))**2 + (float(y1) - float(y2))**2)**0.5

def calculate_wifi_similarity(current_signals: Dict[str, float], 
                              reference_signals: Dict[str, float]) -> float:
    """
    Calculate similarity between two WiFi fingerprints.
    Lower score means higher similarity.
    
    Args:
        current_signals: Dictionary of {bssid: signal_strength} for current location
        reference_signals: Dictionary of {bssid: signal_strength} for reference point
    
    Returns:
        float: Similarity score (lower is better)
    """
    common_bssids = set(current_signals.keys()) & set(reference_signals.keys())
    
    # If no common access points, return a large value
    if not common_bssids:
        return float('inf')
    
    # Root mean square error of signal strengths
    sum_squared_diff = 0
    for bssid in common_bssids:
        diff = current_signals[bssid] - reference_signals[bssid]
        sum_squared_diff += diff * diff
        
    return (sum_squared_diff / len(common_bssids)) ** 0.5

def estimate_distance_from_rssi(rssi: float, reference_rssi: float = -50, 
                               reference_distance: float = 1.0) -> float:
    """
    Estimate distance from RSSI value using log-distance path loss model.
    
    Args:
        rssi: Signal strength in dBm
        reference_rssi: RSSI at reference distance (typically -50 dBm at 1m)
        reference_distance: Reference distance in meters (typically 1m)
    
    Returns:
        float: Estimated distance in meters
    """
    # Path loss exponent (typically 2-4 for indoor environments)
    path_loss_exponent = 3.0
    
    # Convert RSSI to distance using log-distance path loss model
    if rssi >= reference_rssi:
        return reference_distance
    
    ratio = (reference_rssi - rssi) / (10 * path_loss_exponent)
    distance = reference_distance * (10 ** ratio)
    
    return distance

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
