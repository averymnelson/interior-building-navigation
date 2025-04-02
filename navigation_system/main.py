from navigation_system.models.node import NavigationGraph
from navigation_system.algorithms.pathfinding import a_star
from navigation_system.algorithms.step_instructions import get_navigation_instructions
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

def find_restroom(graph: NavigationGraph, room_id: str):
    restrooms = [1162, 1166, 1265, 1261, 2513, 2517, 4407, 4405, 4721, 4725]
    shortest_path = None
    shortest_restroom_id = None
    shortest_path_length = float('inf')

    for restroom_id in restrooms:
        path = a_star(graph, room_id, str(restroom_id))
    
        if path:
            path_length = len(path) 
            
            if path_length < shortest_path_length:
                shortest_path_length = path_length
                shortest_path = path
                shortest_restroom_id = restroom_id

    print(f"Path from Room {room_id} to Restroom {shortest_restroom_id}: {shortest_path}")
    return shortest_path, shortest_restroom_id

def main():
    # Create sample graph
    graph = NavigationGraph()
    
    import_nodes(graph)
    import_edges(graph)

    room1 = "4824"
    room2 = "1004"

    path = a_star(graph, room1, room2)
    print(f"Path from Room {room1} to Room {room2}: {path}")

    instructions = get_navigation_instructions(graph, path)
    print("\nNavigation Instructions:")
    for i, instruction in enumerate(instructions, 1):
        print(f"Step {i}: {instruction}")

    path = find_restroom(graph, room1)

if __name__ == "__main__":
    main()
    
