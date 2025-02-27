# utils/distance.py
from typing import Dict

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
