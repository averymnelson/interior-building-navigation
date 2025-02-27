# models/decision_points.py
import json
import sqlite3
from typing import Dict, Optional, List, Tuple
from models.node import NavigationGraph

class DecisionPointManager:
    """Manages decision points with WiFi fingerprints for indoor positioning"""
    
    def __init__(self, db_path: str, graph: NavigationGraph):
        self.db_path = db_path
        self.graph = graph
        self.decision_points = {}  # Cache of decision points
        self.load_decision_points()
        
    def load_decision_points(self) -> None:
        """Load decision points from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS decision_points (
                id INTEGER PRIMARY KEY,
                node_id INTEGER UNIQUE,
                description TEXT,
                fingerprint TEXT,
                timestamp TEXT
            )
            ''')
            conn.commit()
            
            # Load existing decision points
            cursor.execute("SELECT node_id, description, fingerprint FROM decision_points")
            rows = cursor.fetchall()
            
            for row in cursor.fetchall():
                node_id, description, fingerprint_json = row
                self.decision_points[node_id] = {
                    'description': description,
                    'fingerprint': json.loads(fingerprint_json)
                }
            
            conn.close()
        except Exception as e:
            print(f"Error loading decision points: {e}")
    
    def locate_user(self, wifi_signals: Dict[str, float]) -> Optional[int]:
        """Find the most likely decision point based on WiFi signals"""
        if not wifi_signals or not self.decision_points:
            return None
            
        best_match = None
        best_score = float('inf')
        
        for node_id, data in self.decision_points.items():
            fingerprint = data['fingerprint']
            score = self._calculate_similarity(wifi_signals, fingerprint)
            
            if score < best_score:
                best_score = score
                best_match = node_id
        
        # Only return a match if the similarity is good enough
        similarity_threshold = 8.0  # dBm threshold (adjust based on testing)
        if best_score <= similarity_threshold:
            return best_match
            
        return None
    
    def _calculate_similarity(self, current_signals: Dict[str, float], 
                              fingerprint: Dict[str, float]) -> float:
        """Calculate similarity between WiFi scans (lower is better)"""
        common_bssids = set(current_signals.keys()) & set(fingerprint.keys())
        
        # If no common access points, return a large value
        if not common_bssids:
            return float('inf')
        
        # Calculate root mean square error of signal strengths
        sum_squared_diff = 0
        for bssid in common_bssids:
            diff = current_signals[bssid] - fingerprint[bssid]
            sum_squared_diff += diff * diff
            
        return (sum_squared_diff / len(common_bssids)) ** 0.5
    
    def get_next_decision_point(self, current_node: int, path: List[int]) -> Optional[int]:
        """Find the next decision point along a path"""
        if current_node not in path:
            return None
            
        current_index = path.index(current_node)
        for i in range(current_index + 1, len(path)):
            if path[i] in self.decision_points:
                return path[i]
                
        # If no more decision points, return the destination
        return path[-1] if path else None
    
    def get_decision_point_info(self, node_id: int) -> Optional[Dict]:
        """Get information about a decision point"""
        if node_id in self.decision_points:
            return {
                'node_id': node_id,
                'description': self.decision_points[node_id]['description'],
                'is_decision_point': True
            }
        return None
    
    def is_decision_point(self, node_id: int) -> bool:
        """Check if a node is a decision point"""
        return node_id in self.decision_points
    