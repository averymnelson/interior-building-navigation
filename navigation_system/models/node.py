from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class Node:
    id: int
    type_name: str
    layer: int
    x: float
    y: float
    connections: List[Tuple[int, float]] = field(default_factory=list)

    def add_connection(self, node_id: int, weight: float):
        self.connections.append((node_id, weight))

class NavigationGraph:
    def __init__(self):
        self.nodes = {}

    def add_node(self, id: int, type_name: str, layer: int, x: float, y: float) -> None:
        self.nodes[id] = Node(id, type_name, layer, x, y)

    def add_edge(self, node1_id: int, node2_id: int) -> None:
        node1 = self.nodes[node1_id]
        node2 = self.nodes[node2_id]
        weight = self._calculate_distance(node1, node2)
        
        node1.add_connection(node2_id, weight)
        node2.add_connection(node1_id, weight)

    def _calculate_distance(self, node1: Node, node2: Node) -> float:
        return ((node1.x - node2.x)**2 + (node1.y - node2.y)**2)**0.5
    