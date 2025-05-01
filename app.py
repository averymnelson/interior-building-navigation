from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from navigation_system.models.node import NavigationGraph
from navigation_system.algorithms.pathfinding import a_star
from navigation_system.algorithms.pathfinding import find_restroom
from navigation_system.models.decision_points import DecisionPointManager
from navigation_system.utils.wifi_scanner import scan_wifi, get_dummy_wifi_data
from navigation_system.algorithms.step_instructions import get_navigation_instructions
from PIL import Image
from supabase import create_client, Client

from dotenv import load_dotenv
import os
import sqlite3
import json
import csv
import supabase

# Load environment variables from .env file
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for flash messages

# Initialize Supabase client
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

# Dummy credentials
USER_CREDENTIALS = {
    "admin": "password123"
}

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'navigation.db')

# Initialize graph
graph = NavigationGraph()

# Load graph from CSV files
url = "https://rbuwdtslfurengikxkcm.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJidXdkdHNsZnVyZW5naWt4a2NtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzg5NDQ1NjQsImV4cCI6MjA1NDUyMDU2NH0.uQ5XQ2om0Jvy4vhY3g1SKTUfDlE6Y3uMgiiyp3slD5k"

supabase: Client = create_client(url, key)

nodes = supabase.table("Point Table").select("*").execute()

edges = supabase.table("Edge Table").select("*").execute()

keycard_edges = supabase.table("Keycard Edge Table").select("*").execute()
# Load graph from CSV files
# Modified load_graph_from_csv function to debug hallway information
def load_graph_from_csv():
    # Load nodes
    for data in nodes.data:
        graph.add_node(data['pointnum'], data['type'], 1, data['x_position'], data['y_position'])
   
    # Debug: Print the first few edge records to verify hallway column
    # print("Checking Edge Table data structure:")
    # if edges.data and len(edges.data) > 0:
    #     sample_edge = edges.data[0]
        # print(f"Sample edge data: {sample_edge}")
        # print(f"Hallway field exists: {'hallway' in sample_edge}")
        # if 'hallway' in sample_edge:
        #     print(f"Hallway value: {sample_edge['hallway']}")
    
    # Load edges
    for data in edges.data:
        try:
            graph.add_edge(data['pointnum1'], data['pointnum2'])
        except KeyError:
            print(f"Warning: Could not add edge between {data['pointnum1']} and {data['pointnum2']} - nodes not found")
    
    for data in keycard_edges.data:
        try:
            graph.add_edge(data['pointnum1'], data['pointnum2'])
        except KeyError:
            print(f"[Keycard Edge Warning] Could not add edge between {data['pointnum1']} and {data['pointnum2']} - nodes not found")

# If CSV files don't exist, create test data
def create_test_graph():
    # Add some test nodes
    graph.add_node("1", "entrance", 1, 100, 100)
    graph.add_node("2", "point", 1, 200, 100)
    graph.add_node("3", "point", 1, 300, 100)
    graph.add_node("4", "point", 1, 300, 200)
    graph.add_node("5", "room", 1, 400, 200)
    
    # Add connections
    graph.add_edge("1", "2")
    graph.add_edge("2", "3")
    graph.add_edge("3", "4")
    graph.add_edge("4", "5")

# Try loading from CSV, fallback to test data
try:
    load_graph_from_csv()
    if not graph.nodes:
        create_test_graph()
except Exception as e:
    print(f"Error loading graph from CSV: {e}")
    create_test_graph()

# Decision points for WiFi fingerprinting
# In a real app, these would be loaded from a database
decision_points = {}  # Format: {node_id: {'description': str, 'fingerprint': {bssid: rssi}}}

# Function to get decision point info
def get_decision_point_info(node_id):
    if node_id in decision_points:
        return {
            'node_id': node_id,
            'description': decision_points[node_id]['description'],
            'is_decision_point': True
        }
    
    # If not a designated decision point, create generic info
    if node_id in graph.nodes:
        node = graph.nodes[node_id]
        return {
            'node_id': node_id,
            'description': f"{node.type_name} {node_id}",
            'is_decision_point': False
        }
    
    return None

# Function to determine if a node is a decision point
def is_decision_point(node_id):
    return node_id in decision_points

# Function to locate user based on WiFi signals
def locate_user(wifi_signals):
    if not wifi_signals or not decision_points:
        # If no fingerprints yet or no signals, return first entrance
        for node_id, node in graph.nodes.items():
            if node.type_name == "entrance":
                return node_id
        # If no entrance found, return first node
        return next(iter(graph.nodes)) if graph.nodes else None
    
    # Find the closest match in our fingerprint database
    best_match = None
    best_score = float('inf')
    
    for node_id, data in decision_points.items():
        fingerprint = data['fingerprint']
        
        # Calculate similarity (lower is better)
        common_bssids = set(wifi_signals.keys()) & set(fingerprint.keys())
        if not common_bssids:
            continue
        
        sum_squared_diff = 0
        for bssid in common_bssids:
            diff = wifi_signals[bssid] - fingerprint[bssid]
            sum_squared_diff += diff * diff
            
        score = (sum_squared_diff / len(common_bssids)) ** 0.5
        
        if score < best_score:
            best_score = score
            best_match = node_id
    
    # Only return a match if the similarity is good enough
    threshold = 10.0  # dBm
    if best_score <= threshold:
        return best_match
    
    return None

# Function to get next decision point along a path
def get_next_decision_point(current_node, path):
    if current_node not in path:
        return None
        
    current_index = path.index(current_node)
    for i in range(current_index + 1, len(path)):
        if path[i] in decision_points:
            return path[i]
            
    # If no more decision points, return the destination
    return path[-1] if path else None
    
# API Endpoints for navigation
@app.route('/api/locate', methods=['POST'])
def api_locate_user():
    """API endpoint to locate user based on WiFi signals"""
    data = request.json
    
    # In a web context, we might not have direct WiFi access,
    # so either use signals from client or dummy data for testing
    wifi_signals = data.get('wifi_signals')
    if not wifi_signals:
        # For testing in browsers where WiFi scanning is restricted
        wifi_signals = get_dummy_wifi_data()
    
    # Find the closest decision point
    node_id = locate_user(wifi_signals)
    
    # For testing - if no match, use manually selected location if provided
    if not node_id and data.get('manual_location'):
        node_id = data.get('manual_location')
    
    # For testing - if still no match, return the first entrance
    if not node_id:
        for id, node in graph.nodes.items():
            if node.type_name == "entrance":
                node_id = id
                break
    
    # If still no node found, use first node
    if not node_id and graph.nodes:
        node_id = next(iter(graph.nodes))
    
    if node_id and node_id in graph.nodes:
        node = graph.nodes[node_id]
        node_info = get_decision_point_info(node_id)
        
        return jsonify({
            'node_id': node_id,
            'x': node.x,
            'y': node.y,
            'description': node_info['description'] if node_info else f"Node {node_id}",
            'success': True
        })
    
    return jsonify({'success': False, 'error': 'Unable to locate user'})

@app.route('/get-room-descriptions')
def get_room_descriptions():
    try:
        # Fetch space descriptions from the 'Room Info' table
        response = supabase_client.from_('Room Info Table').select('room_number,space_description').execute()
        
        # Return the response data directly - we'll handle combining with nodes in the frontend
        if response:
            return jsonify(response.data)
        else:
            return jsonify({'success': False, "error": "Unable to fetch data"}), 400
    except Exception as e:
        print(f"Error getting room descriptions: {e}")
        return jsonify({'success': False, "error": f"Unable to fetch data: {str(e)}"}), 400
    
@app.route('/api/get-room_number', methods=['POST'])
def get_room_number():
    data = request.json
    room_description = data.get('destinationText')
    response = supabase_client.from_('Room Info Table') \
        .select('room_number') \
        .eq('space_description', room_description) \
        .execute()
    if response.data:
        return jsonify({"success": True, "end": str(response.data[0]['room_number'])})
    else:
        return jsonify({"success": False, "message": f"No room found for description '{room_description}'"})

@app.route('/api/nodes')
def api_get_nodes():
    """Get all nodes in the graph"""
    nodes_data = {}
    for node_id, node in graph.nodes.items():
        nodes_data[node_id] = {
            'id': node_id,
            'x': node.x,
            'y': node.y,
            'type': node.type_name,
            'type_name': f"{node.type_name} {node_id}",  # For display
            'is_decision_point': is_decision_point(node_id)
        }
    return jsonify(nodes_data)

@app.route('/api/edges')
def api_get_edges():
    """Get all regular edges in the graph"""
    try:
        edges_response = supabase.table("Edge Table").select("*").execute()
        return jsonify(edges_response.data)
    except Exception as e:
        print(f"Error fetching edge data: {e}")
        return jsonify([])

@app.route('/api/keycard-edges')
def api_get_keycard_edges():
    """Get all keycard-protected edges in the graph"""
    try:
        keycard_edges_response = supabase.table("Keycard Edge Table").select("*").execute()
        print("=== KEYCARD EDGES TABLE CONTENT ===")
        for i, edge in enumerate(keycard_edges_response.data):
            print(f"Edge {i+1}: {edge}")
        print("=== END KEYCARD EDGES TABLE CONTENT ===")
        return jsonify(keycard_edges_response.data)
    except Exception as e:
        print(f"Error fetching keycard edge data: {e}")
        return jsonify([])
    
@app.route('/api/route', methods=['POST'])
def api_calculate_route():
    data = request.json
    start_id = data.get('start')
    end_id = data.get('end')
    prefer_hallways = data.get('prefer_hallways', True)
    has_keycard = data.get('has_keycard', False)

    print(f"Calculating route from {start_id} to {end_id}, prefer_hallways={prefer_hallways}, has_keycard={has_keycard}")

    if start_id not in graph.nodes or end_id not in graph.nodes:
        return jsonify({'success': False, 'error': 'Invalid start or end node'})

    try:
        # Load regular edges
        regular_edges_response = supabase.table("Edge Table").select("*").execute()
        all_edges = list(regular_edges_response.data)  # start with regular edges only

        # If user has keycard, add keycard edges too
        if has_keycard:
            keycard_edges = supabase.table("Keycard Edge Table").select("*").execute()
            all_edges.extend(keycard_edges.data)
            # print(f"✔ Added {len(keycard_edges)} keycard edges to edge list")

    except Exception as e:
        print(f"❌ Error fetching edge data: {e}")
        return jsonify({'success': False, 'error': 'Edge fetch error'})

    # ✅ Now pass combined edge list to a_star
    path = a_star(graph, start_id, end_id, all_edges, prefer_hallways)

    if not path:
        return jsonify({'success': False, 'error': 'No path found'})

    instructions = get_navigation_instructions(graph, path)

    # Construct path details
    path_details = []
    for node_id in path:
        node = graph.nodes[node_id]
        path_details.append({
            'node_id': node_id,
            'x': node.x,
            'y': node.y,
            'is_decision_point': is_decision_point(node_id),
            'description': get_decision_point_info(node_id)['description']
                           if get_decision_point_info(node_id) else f"{node.type_name} {node_id}"
        })

    return jsonify({
        'success': True,
        'path': path,
        'path_details': path_details,
        'instructions': instructions
    })

# Replace the existing api_get_restroom route with this improved version:

@app.route('/api/get-restroom', methods=['POST'])
def api_get_restroom():
    """Get restroom room ID for destination ID"""
    data = request.json
    start_id = data.get('startId')
    has_keycard = data.get('has_keycard', False)  # Default to no keycard access
    
    if start_id not in graph.nodes:
        return jsonify({'success': False, 'error': 'Invalid start node'})
    
    print(f"Finding nearest restroom from {start_id} with keycard access: {has_keycard}")
    
    # Get regular edges
    try:
        regular_edges = supabase.table("Edge Table").select("*").execute()
        all_edges_data = regular_edges.data
    except Exception as e:
        print(f"Error fetching regular edge data: {e}")
        return jsonify({'success': False, 'error': 'Could not fetch edges'})
    
    # Add keycard edges if the user has keycard access
    keycard_edges_data = None
    if has_keycard:
        try:
            keycard_edges = supabase.table("Keycard Edge Table").select("*").execute()
            keycard_edges_data = keycard_edges.data
            
            print(f"Using {len(keycard_edges_data)} keycard edges for restroom search")
        except Exception as e:
            print(f"Error fetching keycard edge data: {e}")
    
    # Call find_restroom with the corrected parameters
    end = find_restroom(graph, start_id, all_edges_data, keycard_edges_data, has_keycard)

    if not end:
        return jsonify({'success': False, 'error': 'No restroom found'})
    
    print(f"Found nearest restroom: {end}")
    return jsonify({
        'success': True,
        'end': end
    })
    
@app.route('/api/next-decision-point', methods=['POST'])
def api_get_next_decision_point():
    """Get the next decision point along a path"""
    data = request.json
    current_id = data.get('current')
    path = data.get('path')
    
    if not current_id or not path:
        return jsonify({'success': False, 'error': 'Missing parameters'})
    
    next_dp = get_next_decision_point(current_id, path)
    
    if next_dp:
        dp_info = get_decision_point_info(next_dp)
        return jsonify({
            'success': True,
            'node_id': next_dp,
            'description': dp_info['description'] if dp_info else f"Node {next_dp}"
        })
    
    # If no next decision point, use the destination
    if path:
        dest_id = path[-1]
        dest_info = get_decision_point_info(dest_id)
        return jsonify({
            'success': True,
            'node_id': dest_id,
            'description': dest_info['description'] if dest_info else f"Destination ({dest_id})"
        })
    
    return jsonify({'success': False, 'error': 'No next decision point found'})

@app.route('/api/fingerprint', methods=['POST'])
def api_add_fingerprint():
    """Add or update a WiFi fingerprint for a location"""
    data = request.json
    node_id = data.get('node_id')
    description = data.get('description')
    wifi_signals = data.get('wifi_signals')
    
    if not node_id or not wifi_signals or node_id not in graph.nodes:
        return jsonify({'success': False, 'error': 'Invalid parameters'})
    
    decision_points[node_id] = {
        'description': description or f"{graph.nodes[node_id].type_name} {node_id}",
        'fingerprint': wifi_signals
    }
    
    return jsonify({'success': True})

@app.route('/')
def home():
    return render_template('home.html', title="Home")

@app.route('/wayfinding')
def wayfinding():
    return render_template('wayfinding.html', title="Wayfinding")

@app.route('/get_directions', methods=['POST'])
def get_directions():
    start = request.form.get('start')
    destination = request.form.get('destination')

    if start and destination:
        flash(f"Finding route from {start} to {destination}...", "info")
        return redirect(url_for('wayfinding'))
    else:
        flash("Please enter both a starting point and a destination!", "danger")
        return redirect(url_for('wayfinding'))
    
@app.route('/settings')
def settings():
    return render_template('settings.html', title="Settings")

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    try:
        response = supabase_client.auth.sign_in_with_password({"email": email, "password": password})
    
        print(f"[INFO] Login successful for {email}")
        flash("Login successful!", "success")
        return redirect(url_for('home'))

    except Exception as e:
        print(f"[WARNING] Login failed for: {email}")
        flash("Invalid credentials!", "danger")
        return redirect(url_for('settings'))

if __name__ == '__main__':
    app.run(debug=True)
