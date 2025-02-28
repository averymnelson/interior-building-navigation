# utils/wifi_scanner.py
import platform
import subprocess
import re
import json
from typing import Dict

def scan_wifi() -> Dict[str, float]:
    """
    Scan for WiFi networks and return signal strengths
    Returns: dict of {bssid: signal_strength_in_dbm}
    """
    system = platform.system()
    
    if system == "Windows":
        return _scan_windows()
    elif system == "Linux":
        return _scan_linux()
    elif system == "Darwin":  # macOS
        return _scan_macos()
    else:
        print(f"WiFi scanning not implemented for {system}")
        return {}

def _scan_windows() -> Dict[str, float]:
    """Scan WiFi networks on Windows using netsh"""
    try:
        # Run netsh command to get networks
        output = subprocess.check_output(
            "netsh wlan show networks mode=bssid", 
            shell=True
        ).decode('utf-8', errors='ignore')
        
        # Parse output to extract BSSIDs and signal strengths
        networks = {}
        current_bssid = None
        
        for line in output.split('\n'):
            line = line.strip()
            if "BSSID" in line:
                parts = line.split(":")
                if len(parts) > 1:
                    current_bssid = parts[1].strip()
            elif "Signal" in line and current_bssid:
                parts = line.split(":")
                if len(parts) > 1:
                    # Convert percentage to dBm (approximate)
                    signal_percent = int(parts[1].strip().replace('%', ''))
                    signal_dbm = -100 + (signal_percent / 2)  # Rough conversion
                    networks[current_bssid] = signal_dbm
                
        return networks
    except Exception as e:
        print(f"Error scanning WiFi on Windows: {e}")
        return {}

def _scan_linux() -> Dict[str, float]:
    """Scan WiFi networks on Linux using iwlist"""
    try:
        # Get list of wireless interfaces
        interfaces = subprocess.check_output(
            "iwconfig 2>/dev/null | grep -o '^[a-zA-Z0-9]*'", 
            shell=True
        ).decode('utf-8').strip().split('\n')
        
        # Find first wireless interface that's up
        wireless_if = None
        for iface in interfaces:
            if not iface:
                continue
            try:
                output = subprocess.check_output(f"iwconfig {iface}", shell=True)
                wireless_if = iface
                break
            except:
                continue
        
        if not wireless_if:
            print("No wireless interface found")
            return {}
            
        # Scan networks
        output = subprocess.check_output(
            f"sudo iwlist {wireless_if} scan", 
            shell=True
        ).decode('utf-8')
        
        # Parse output
        networks = {}
        current_bssid = None
        
        for line in output.split('\n'):
            line = line.strip()
            if "Address:" in line:
                bssid_match = re.search(r'([0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2})', line, re.I)
                if bssid_match:
                    current_bssid = bssid_match.group(1)
            elif "Signal level" in line and current_bssid:
                level_match = re.search(r'Signal level=(-\d+) dBm', line)
                if level_match:
                    signal_dbm = float(level_match.group(1))
                    networks[current_bssid] = signal_dbm
        
        return networks
    except Exception as e:
        print(f"Error scanning WiFi on Linux: {e}")
        return {}

def _scan_macos() -> Dict[str, float]:
    """Scan WiFi networks on macOS using airport utility"""
    try:
        # Use airport utility to scan networks
        output = subprocess.check_output(
            "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s", 
            shell=True
        ).decode('utf-8')
        
        networks = {}
        
        # Skip header line
        lines = output.strip().split('\n')[1:]
        for line in lines:
            parts = re.split(r'\s+', line.strip())
            if len(parts) >= 2:
                bssid = parts[1]
                try:
                    rssi = float(parts[2])
                    networks[bssid] = rssi
                except:
                    pass
                    
        return networks
    except Exception as e:
        print(f"Error scanning WiFi on macOS: {e}")
        return {}
        
def get_dummy_wifi_data():
    """
    Get dummy WiFi data for testing or when real scanning is not available
    Useful in web application context where direct scanning may not be possible
    """
    return {
        "00:11:22:33:44:55": -65,
        "AA:BB:CC:DD:EE:FF": -72,
        "11:22:33:44:55:66": -83
    }
    