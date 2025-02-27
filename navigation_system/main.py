from models.node import NavigationGraph
from algorithms.pathfinding import a_star

def main():
    # Create sample graph
    graph = NavigationGraph()
    
    # Add some test nodes
    graph.add_node(1, "room", 1, 0, 0)    # Room 1
    graph.add_node(2, "point", 1, 5, 0)    # Hallway point
    graph.add_node(3, "room", 1, 10, 0)    # Room 2
    
    # Add connections
    graph.add_edge(1, 2)
    graph.add_edge(2, 3)
    
    # Find path
    path = a_star(graph, 1, 3)
    print(f"Path from Room 1 to Room 2: {path}")
    
    # When you later add database:
    # Just modify NavigationGraph to load nodes from SQL
    # The pathfinding algorithm won't need to change

if __name__ == "__main__":
    main()
    