"""
Visualization server configuration for FAI-Farm simulation.

This module configures the Mesa visualization server including grid rendering,
agent portrayal, charts, and the web interface.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from model.farm_model import FarmModel
from model.cell_state import CellState
from agents.master_agent import MasterAgent
from agents.base_agent import WorkerAgent


# Professional color scheme for cell states
CELL_COLORS = {
    CellState.INITIAL: "#E8E8E8",        # Light gray
    CellState.PLOUGHED: "#8B4513",       # Saddle brown
    CellState.SOWN: "#D2B48C",           # Tan
    CellState.GROWING: "#90EE90",        # Light green
    CellState.NEED_WATER: "#FFD700",     # Gold (warning)
    CellState.HEALTHY: "#228B22",        # Forest green
    CellState.DISEASED: "#DC143C",       # Crimson
    CellState.READY_TO_HARVEST: "#FFA500" # Orange
}

# Professional color scheme for agents
AGENT_COLORS = {
    "master": "#000000",          # Black
    "ploughing": "#8B4513",       # Brown
    "sowing": "#F4A460",          # Sandy brown
    "watering": "#4169E1",        # Royal blue
    "drone": "#708090",           # Slate gray
    "harvesting": "#FF8C00"       # Dark orange
}


def agent_portrayal(agent):
    """
    Define how agents are rendered on the grid.
    
    Master Agent is rendered as a black rectangle, Worker Agents as
    colored circles with distinct colors per agent type.
    
    Args:
        agent: Agent instance to render
    
    Returns:
        Dictionary of portrayal properties for Mesa visualization
    """
    if agent is None:
        return None
    
    portrayal = {
        "Filled": "true",
        "Layer": 1
    }
    
    if isinstance(agent, MasterAgent):
        # Master Agent: Black rectangle
        portrayal["Shape"] = "rect"
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8
        portrayal["Color"] = AGENT_COLORS["master"]
        portrayal["Layer"] = 2
    
    elif isinstance(agent, WorkerAgent):
        # Worker Agents: Colored circles
        portrayal["Shape"] = "circle"
        portrayal["r"] = 0.5
        portrayal["Color"] = AGENT_COLORS.get(agent.agent_type, "#808080")
        portrayal["Layer"] = 1
    
    return portrayal


def get_cell_color(model, x, y):
    """
    Get the background color for a grid cell based on its state.
    
    Args:
        model: FarmModel instance
        x: Grid x-coordinate
        y: Grid y-coordinate
    
    Returns:
        Hex color string for the cell
    """
    cell_state = model.get_cell_state((x, y))
    return CELL_COLORS.get(cell_state, "#FFFFFF")


# Custom JavaScript for cell coloring
def create_grid_with_colors():
    """
    Create a CanvasGrid with custom cell coloring.
    
    Returns:
        Configured CanvasGrid instance
    """
    grid = CanvasGrid(agent_portrayal, 20, 20, 500, 500)
    
    # Override the render method to include cell background colors
    original_render = grid.render
    
    def render_with_colors(model):
        # Get the standard rendering
        grid_state = original_render(model)
        
        # Add cell colors
        for x in range(model.width):
            for y in range(model.height):
                cell_state = model.get_cell_state((x, y))
                color = CELL_COLORS.get(cell_state, "#FFFFFF")
                
                # Add color information to grid state
                if "layers" not in grid_state:
                    grid_state["layers"] = []
                
                # Create a background layer for cell colors
                grid_state.setdefault("cell_colors", {})
                grid_state["cell_colors"][f"{x},{y}"] = color
        
        return grid_state
    
    grid.render = render_with_colors
    return grid


def create_server():
    """
    Create and configure the Mesa visualization server.
    
    Returns:
        Configured ModularServer instance ready to launch
    """
    # Create grid visualization
    grid = CanvasGrid(agent_portrayal, 20, 20, 500, 500)
    
    # Create chart for tracking cell state counts over time
    chart = ChartModule([
        {"Label": "Ploughed", "Color": CELL_COLORS[CellState.PLOUGHED]},
        {"Label": "Sown", "Color": CELL_COLORS[CellState.SOWN]},
        {"Label": "Growing", "Color": CELL_COLORS[CellState.GROWING]},
        {"Label": "Healthy", "Color": CELL_COLORS[CellState.HEALTHY]},
        {"Label": "Harvested", "Color": "#FFA500"},
        {"Label": "Diseased", "Color": CELL_COLORS[CellState.DISEASED]},
    ])
    
    # Model parameters for user configuration
    model_params = {
        "width": 20,
        "height": 20,
        "num_workers": 6
    }
    
    # Create the server
    server = ModularServer(
        FarmModel,
        [grid, chart],
        "FAI-Farm Multi-Agent System",
        model_params
    )
    
    server.port = 8521
    
    return server
