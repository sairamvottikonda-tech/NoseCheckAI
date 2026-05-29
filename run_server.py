#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convenience script to start the NoseCheck Flask server.

Usage:
    python run_server.py
    
Or simply:
    ./run_server.py (if made executable with: chmod +x run_server.py)
"""

from src.app import app

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting NoseCheck Flask Server")
    print("=" * 60)
    print("📱 iOS App: Configure server URL in Settings")
    print("   - Simulator: http://localhost:5001")
    print("   - Real Device: http://YOUR_MAC_IP:5001")
    print()
    print("🌐 Web Interface: http://localhost:5001")
    print("=" * 60)
    print()
    
    app.run(
        host="0.0.0.0",  # Allow connections from iPhone on same network
        port=5001,  # Using 5001 to avoid conflict with macOS AirPlay
        debug=True
    )
