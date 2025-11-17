"""
FAI-Farm Multi-Agent System Launcher

This script initializes and launches the Mesa visualization server for the
FAI-Farm agricultural simulation.

Usage:
    python run.py

The simulation will open in your default web browser at http://127.0.0.1:8521
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.visualization import create_server


def main():
    """
    Main entry point for the FAI-Farm simulation.
    
    Creates and launches the visualization server.
    """
    print("=" * 60)
    print("FAI-Farm Multi-Agent System")
    print("=" * 60)
    print("\nInitializing simulation...")
    
    # Create the visualization server
    server = create_server()
    
    print(f"\nServer configured on port {server.port}")
    print(f"Opening browser at http://127.0.0.1:{server.port}")
    print("\nSimulation Controls:")
    print("  - Start: Begin the simulation")
    print("  - Step: Execute one simulation step")
    print("  - Pause: Pause the simulation")
    print("  - Reset: Reset to initial state")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    # Launch the server
    server.launch()


if __name__ == "__main__":
    main()
