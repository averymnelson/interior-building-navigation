# tools/fingerprint_collector.py
import time
import json
import sqlite3
import argparse
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.wifi_scanner import scan_wifi

class FingerprintCollector:
    """Tool for collecting WiFi fingerprints at decision points"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.setup_database()
        
    def setup_database(self):
        """Set up database tables if they don't exist"""
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS decision_points (
            id INTEGER PRIMARY KEY,
            node_id INTEGER UNIQUE,
            description TEXT,
            fingerprint TEXT,
            timestamp TEXT
        )''')
        self.conn.commit()
    
    def collect_fingerprint(self, node_id, description, samples=5, interval=1):
        """Collect multiple WiFi samples and average them"""
        print(f"Collecting fingerprint for node {node_id} ({description})...")
        print(f"Taking {samples} samples with {interval}s interval...")
        
        # Collect multiple samples
        all_samples = []
        for i in range(samples):
            print(f"Sample {i+1}/{samples}...")
            sample = scan_wifi()
            print(f"  Found {len(sample)} networks")
            all_samples.append(sample)
            if i < samples - 1:  # Don't sleep after the last sample
                print(f"  Waiting {interval}s...")
                time.sleep(interval)
            
        # Average the samples
        fingerprint = self._average_samples(all_samples)
        
        # Store in database
        cursor = self.conn.cursor()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        fingerprint_json = json.dumps(fingerprint)
        
        # Check if node already exists
        cursor.execute("SELECT id FROM decision_points WHERE node_id = ?", (node_id,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute(
                "UPDATE decision_points SET description = ?, fingerprint = ?, timestamp = ? WHERE node_id = ?",
                (description, fingerprint_json, timestamp, node_id)
            )
            print(f"Updated existing fingerprint for node {node_id}")
        else:
            cursor.execute(
                "INSERT INTO decision_points (node_id, description, fingerprint, timestamp) VALUES (?, ?, ?, ?)",
                (node_id, description, fingerprint_json, timestamp)
            )
            print(f"Added new fingerprint for node {node_id}")
            
        self.conn.commit()
        return fingerprint
    
    def _average_samples(self, samples):
        """Average multiple WiFi scans"""
        # Combine all BSSIDs from all samples
        all_bssids = set()
        for sample in samples:
            all_bssids.update(sample.keys())
            
        # Average the RSSI values
        avg_fingerprint = {}
        for bssid in all_bssids:
            values = [sample.get(bssid, -100) for sample in samples if bssid in sample]
            if values:
                avg_fingerprint[bssid] = sum(values) / len(values)
                
        return avg_fingerprint
        
    def list_decision_points(self):
        """List all decision points in the database"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT node_id, description, timestamp FROM decision_points ORDER BY node_id")
        points = cursor.fetchall()
        
        if not points:
            print("No decision points found in database")
            return
            
        print("\nDecision Points:")
        print("-" * 60)
        print(f"{'Node ID':<10} {'Description':<30} {'Timestamp':<20}")
        print("-" * 60)
        
        for node_id, description, timestamp in points:
            print(f"{node_id:<10} {description:<30} {timestamp:<20}")

def main():
    parser = argparse.ArgumentParser(description='Collect WiFi fingerprints for indoor positioning')
    parser.add_argument('--db', default='navigation.db', help='Database file path')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Collect command
    collect_parser = subparsers.add_parser('collect', help='Collect a new fingerprint')
    collect_parser.add_argument('node_id', type=int, help='Node ID in the navigation graph')
    collect_parser.add_argument('description', help='Description of the location (e.g., "North Hallway Intersection")')
    collect_parser.add_argument('--samples', type=int, default=5, help='Number of samples to take')
    collect_parser.add_argument('--interval', type=float, default=1, help='Interval between samples (seconds)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all collected fingerprints')
    
    args = parser.parse_args()
    
    collector = FingerprintCollector(args.db)
    
    if args.command == 'collect':
        collector.collect_fingerprint(args.node_id, args.description, args.samples, args.interval)
    elif args.command == 'list':
        collector.list_decision_points()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
    