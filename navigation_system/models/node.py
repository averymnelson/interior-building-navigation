from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class Node:
    id: str
    type_name: str
    layer: int
    x: float
    y: float
    connections: List[Tuple[str, float]] = field(default_factory=list)

    def add_connection(self, node_id: str, weight: float):
        self.connections.append((node_id, weight))
    def print(self):
        print(f"ID: {self.id}, Type: {self.type_name}, Layer: {self.layer}, X: {self.x}, Y: {self.y}, Connections: {self.connections}")


class NavigationGraph:
    def __init__(self):
        self.nodes = {}

    def add_node(self, id: str, type_name: str, layer: int, x: float, y: float) -> None:
        self.nodes[id] = Node(id, type_name, layer, x, y)

    def add_edge(self, node1_id: str, node2_id: str) -> None:
        node1 = self.nodes[node1_id]
        node2 = self.nodes[node2_id]
        weight = self._calculate_distance(node1, node2)
        
        node1.add_connection(node2_id, weight)
        node2.add_connection(node1_id, weight)

    def print_Nodes(self) -> None:
        for node in self.nodes.values():
            node.print()

    def _calculate_distance(self, node1: Node, node2: Node) -> float:
        return ((float(node1.x) - float(node2.x))**2 + (float(node1.y) - float(node2.y))**2)**0.5
    