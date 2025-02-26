from models.node import NavigationGraph
from algorithms.pathfinding import a_star
import csv

def import_nodes(graph = NavigationGraph()):
    filename = "point_table.csv"
    entries = []
    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            entries.append(row)

    del entries[0]

    for entry in entries:
        graph.add_node(entry[0], entry[1], 1, entry[2],entry[3])

def import_edges(graph = NavigationGraph()):
    filename = "edge_table.csv"
    entries = []
    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            entries.append(row)

    del entries[0]

    for entry in entries:
        node_1_id = entry[1]
        node_2_id = entry[2]
        graph.add_edge(node_1_id, node_2_id)

def main():
    # Create sample graph
    graph = NavigationGraph()
    
    import_nodes(graph)
    import_edges(graph)

    # # Add some test nodes
    # graph.add_node(1, "room", 1, 0, 0)    # Room 1
    # graph.add_node(2, "point", 1, 5, 0)    # Hallway point
    # graph.add_node(3, "room", 1, 10, 0)    # Room 2
    
    # # Add connections
    # graph.add_edge(1, 2)
    # graph.add_edge(2, 3)
    
    # # Find path
    # path = a_star(graph, 1, 3)
    # print(f"Path from Room 1 to Room 2: {path}")

    path = a_star(graph, "1", "100")
    print(f"Path from Room 1 to Room 100: {path}")
    

if __name__ == "__main__":
    main()
    