from navigation_system.models.node import NavigationGraph
from navigation_system.algorithms.pathfinding import a_star
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

    room1 = "4824"
    room2 = "1004"

    path = a_star(graph, room1, room2)
    print(f"Path from Room {room1} to Room {room2}: {path}")
    

if __name__ == "__main__":
    main()
    
