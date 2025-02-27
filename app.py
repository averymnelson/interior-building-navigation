from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from PIL import Image
import os
import sqlite3
import json

from navigation_system.models.node import NavigationGraph
from navigation_system.algorithms.pathfinding import a_star

# Import new modules - ADD THESE LINES
from navigation_system.models.decision_points import DecisionPointManager
from navigation_system.utils.wifi_scanner import scan_wifi, get_dummy_wifi_data

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for flash messages

# Dummy credentials
USER_CREDENTIALS = {
    "admin": "password123"
}

@app.route('/')
def home():
    return render_template('home.html', title="Home")

@app.route('/wayfinding')
def wayfinding():
    return render_template('wayfinding.html', title="Wayfinding")

@app.route('/settings')
def settings():
    return render_template('settings.html', title="Settings")

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
        flash("Login successful!", "success")
        return redirect(url_for('home'))
    else:
        flash("Invalid credentials!", "danger")
        return redirect(url_for('settings'))
    
if __name__ == '__main__':
    app.run(debug=True)
