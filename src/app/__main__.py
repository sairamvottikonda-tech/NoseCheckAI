# -*- coding: utf-8 -*-
"""
Entry point for running the NoseCheck Flask application.

Run with: python -m src.app
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
        host="0.0.0.0",  # Allow connections from other devices on network
        port=5001,  # Using 5001 to avoid conflict with macOS AirPlay
        debug=True
    )
