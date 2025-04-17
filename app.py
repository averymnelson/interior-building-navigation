from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from navigation_system.models.node import NavigationGraph
from navigation_system.algorithms.pathfinding import a_star
from navigation_system.algorithms.pathfinding import find_restroom
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

# Load graph from CSV files
def load_graph_from_csv():
    # Load nodes
    for data in nodes.data:
        graph.add_node(data['pointnum'], data['type'],1, data['x_position'],data['y_position'])
   
    # Load edges
    for data in edges.data:
        try:
            graph.add_edge(data['pointnum1'], data['pointnum2'])
        except KeyError:
            print(f"Warning: Could not add edge between {data['pointnum1']} and {data['pointnum2']} - nodes not found")
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

@app.route('/get-room-descriptions')
def get_room_descriptions():
    # Fetch space descriptions from the 'Room Info' table
    response = supabase_client.from_('Room Info Table').select('space_description').execute()

    if response:
        return jsonify(response.data)
    else:
        return jsonify({'success': False, "error": "Unable to fetch data"}), 400

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
            'type_name': f"{node.type_name} {node_id}"
        }
    return jsonify(nodes_data)

@app.route('/api/route', methods=['POST'])
def api_calculate_route():
    """Calculate route between two points"""
    data = request.json
    start_id = data.get('start')
    end_id = data.get('end')
    print(start_id)
    print(end_id)
    
    if start_id not in graph.nodes or end_id not in graph.nodes:
        return jsonify({'success': False, 'error': 'Invalid start or end node'})
    
    path = a_star(graph, start_id, end_id)
    
    instructions = get_navigation_instructions(graph, path)
    print("\nNavigation Instructions:")
    for i, instruction in enumerate(instructions, 1):
        print(f"Step {i}: {instruction}")
    
    if not path:
        return jsonify({'success': False, 'error': 'No path found'})
    
    # Convert to coordinates for display
    path_details = []
    for node_id in path:
        node = graph.nodes[node_id]
        
        node_info = {
            'node_id': node_id,
            'x': node.x,
            'y': node.y
        }
            
        path_details.append(node_info)
    
    return jsonify({
        'success': True,
        'path': path,
        'path_details': path_details,
        'instructions': instructions
    })

@app.route('/api/get-restroom', methods=['POST'])
def api_get_restroom():
    """Get restroom room ID for destination ID"""
    data = request.json
    start_id = data.get('startId')
    
    if start_id not in graph.nodes:
        return jsonify({'success': False, 'error': 'Invalid start node'})
    
    end = find_restroom(graph, start_id)
    if not end:
        return jsonify({'success': False, 'error': 'No restroom found'})
    return jsonify({
        'success': True,
        'end': end
    })

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
