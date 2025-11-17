"""
Farm Model implementation using Mesa framework.

This module contains the main simulation model that manages the grid environment,
agents, and simulation state.
"""

from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from typing import Dict, Tuple
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.cell_state import CellState
from utils.message_bus import MessageBus


class FarmModel(Model):
    """
    Main simulation model for the FAI-Farm multi-agent system.
    
    Manages the grid environment, agent scheduling, cell states, and
    simulation statistics collection.
    """
    
    def __init__(self, width=20, height=20, num_workers=6):
        """
        Initialize the farm model.
        
        Args:
            width: Grid width in cells
            height: Grid height in cells
            num_workers: Number of worker agents to create
        """
        super().__init__()
        
        self.width = width
        self.height = height
        self.num_workers = num_workers
        
        # Initialize grid (MultiGrid allows multiple agents per cell)
        self.grid = MultiGrid(width, height, torus=False)
        
        # Initialize scheduler for agent activation
        self.schedule = RandomActivation(self)
        
        # Initialize message bus for agent communication
        self.message_bus = MessageBus()
        
        # Track cell states for each grid position
        self.cell_states: Dict[Tuple[int, int], CellState] = {}
        
        # Track cell attributes (water level, growth progress, disease probability)
        self.cell_attributes: Dict[Tuple[int, int], Dict] = {}
        
        # Initialize all cells to INITIAL state
        for x in range(width):
            for y in range(height):
                self.cell_states[(x, y)] = CellState.INITIAL
                self.cell_attributes[(x, y)] = {
                    'water_level': 0.0,
                    'growth_progress': 0,
                    'disease_probability': 0.0,
                    'last_watered': 0
                }
        
        # Track simulation step
        self.step_count = 0
        
        # Initialize data collector for statistics
        self.datacollector = DataCollector(
            model_reporters={
                "Ploughed": lambda m: m.count_cells_by_state(CellState.PLOUGHED),
                "Sown": lambda m: m.count_cells_by_state(CellState.SOWN),
                "Growing": lambda m: m.count_cells_by_state(CellState.GROWING),
                "Healthy": lambda m: m.count_cells_by_state(CellState.HEALTHY),
                "Harvested": lambda m: m.harvested_count,
                "Diseased": lambda m: m.count_cells_by_state(CellState.DISEASED),
                "Temperature": lambda m: m.weather['temperature'],
                "Humidity": lambda m: m.weather['humidity'],
                "Estimated_Yield": lambda m: m.calculate_yield_prediction()['estimated_yield'],
                "Water_Stress": lambda m: m.get_stress_indicators()['water_stress_percentage'],
            }
        )
        
        # Track harvest count
        self.harvested_count = 0
        
        # Weather simulation
        self.weather = {
            'temperature': 25.0,
            'humidity': 60.0,
            'rain_forecast_24h': False,
            'wind_speed': 10.0
        }
        
        # Yield prediction tracking
        self.total_yield_estimate = 0.0
        self.estimated_harvest_date = 0
        
        # Agents will be created by create_agents method
        self.master_agent = None
        self.worker_agents = []
        
        # Create agents
        self.create_agents()
    
    def get_cell_state(self, pos: Tuple[int, int]) -> CellState:
        """
        Get the current state of a grid cell.
        
        Args:
            pos: Grid position (x, y)
        
        Returns:
            Current CellState of the cell
        """
        return self.cell_states.get(pos, CellState.INITIAL)
    
    def set_cell_state(self, pos: Tuple[int, int], state: CellState):
        """
        Update the state of a grid cell.
        
        Args:
            pos: Grid position (x, y)
            state: New CellState to set
        """
        if pos in self.cell_states:
            self.cell_states[pos] = state
    
    def get_cell_attributes(self, pos: Tuple[int, int]) -> Dict:
        """
        Get the attributes of a grid cell.
        
        Args:
            pos: Grid position (x, y)
        
        Returns:
            Dictionary of cell attributes
        """
        return self.cell_attributes.get(pos, {})
    
    def update_cell_attributes(self, pos: Tuple[int, int], **kwargs):
        """
        Update specific attributes of a grid cell.
        
        Args:
            pos: Grid position (x, y)
            **kwargs: Attribute key-value pairs to update
        """
        if pos in self.cell_attributes:
            self.cell_attributes[pos].update(kwargs)
    
    def count_cells_by_state(self, state: CellState) -> int:
        """
        Count the number of cells in a specific state.
        
        Args:
            state: CellState to count
        
        Returns:
            Number of cells in the specified state
        """
        return sum(1 for s in self.cell_states.values() if s == state)
    
    def update_weather(self):
        """
        Simulate weather changes over time.
        
        Updates temperature, humidity, rain forecast, and wind speed
        with realistic variations.
        """
        import random
        
        # Temperature variation (20-35°C)
        self.weather['temperature'] += random.uniform(-2, 2)
        self.weather['temperature'] = max(20, min(35, self.weather['temperature']))
        
        # Humidity variation (40-90%)
        self.weather['humidity'] += random.uniform(-5, 5)
        self.weather['humidity'] = max(40, min(90, self.weather['humidity']))
        
        # Rain forecast (10% chance of rain)
        self.weather['rain_forecast_24h'] = random.random() < 0.1
        
        # Wind speed variation (5-40 km/h)
        self.weather['wind_speed'] += random.uniform(-3, 3)
        self.weather['wind_speed'] = max(5, min(40, self.weather['wind_speed']))
    
    def calculate_yield_prediction(self) -> dict:
        """
        Calculate estimated crop yield based on current farm state.
        
        Returns:
            Dictionary with yield estimates and harvest timing
        """
        # Count crops at different stages
        growing = self.count_cells_by_state(CellState.GROWING)
        healthy = self.count_cells_by_state(CellState.HEALTHY)
        ready = self.count_cells_by_state(CellState.READY_TO_HARVEST)
        diseased = self.count_cells_by_state(CellState.DISEASED)
        
        # Calculate average growth progress
        total_growth = 0
        crop_count = 0
        for pos, state in self.cell_states.items():
            if state in [CellState.GROWING, CellState.HEALTHY, CellState.NEED_WATER]:
                attrs = self.cell_attributes[pos]
                total_growth += attrs.get('growth_progress', 0)
                crop_count += 1
        
        avg_growth = total_growth / crop_count if crop_count > 0 else 0
        
        # Estimate yield per cell based on health
        yield_per_healthy = 1.0
        yield_per_growing = 0.7
        yield_per_diseased = 0.3
        
        estimated_yield = (
            healthy * yield_per_healthy +
            growing * yield_per_growing +
            diseased * yield_per_diseased +
            ready * yield_per_healthy
        )
        
        # Estimate days until harvest (based on average growth)
        if avg_growth > 0:
            remaining_growth = 100 - avg_growth
            # Assuming 2% growth per step
            steps_to_harvest = remaining_growth / 2
            days_to_harvest = int(steps_to_harvest)
        else:
            days_to_harvest = 0
        
        self.total_yield_estimate = estimated_yield
        self.estimated_harvest_date = self.step_count + days_to_harvest
        
        return {
            'estimated_yield': round(estimated_yield, 2),
            'current_harvest': self.harvested_count,
            'potential_yield': estimated_yield + self.harvested_count,
            'days_to_harvest': days_to_harvest,
            'estimated_harvest_step': self.estimated_harvest_date,
            'average_growth_progress': round(avg_growth, 1),
            'healthy_crops': healthy,
            'at_risk_crops': diseased
        }
    
    def get_stress_indicators(self) -> dict:
        """
        Calculate crop stress indicators across the farm.
        
        Returns:
            Dictionary with stress metrics
        """
        water_stressed = 0
        temperature_stressed = 0
        total_crops = 0
        
        for pos, state in self.cell_states.items():
            if state in [CellState.GROWING, CellState.HEALTHY, CellState.NEED_WATER, CellState.SOWN]:
                total_crops += 1
                attrs = self.cell_attributes[pos]
                
                # Water stress
                if attrs.get('water_level', 0) < 0.3:
                    water_stressed += 1
                
                # Temperature stress (high temp + low water)
                if self.weather['temperature'] > 32 and attrs.get('water_level', 0) < 0.5:
                    temperature_stressed += 1
        
        return {
            'water_stressed_count': water_stressed,
            'temperature_stressed_count': temperature_stressed,
            'total_crops': total_crops,
            'water_stress_percentage': round(water_stressed / total_crops * 100, 1) if total_crops > 0 else 0,
            'temperature_stress_percentage': round(temperature_stressed / total_crops * 100, 1) if total_crops > 0 else 0,
            'overall_health_score': round((total_crops - water_stressed - temperature_stressed) / total_crops * 100, 1) if total_crops > 0 else 100
        }
    
    def create_agents(self):
        """
        Create and initialize all agents in the simulation.
        
        Creates one Master Agent and multiple specialized Worker Agents,
        places them on the grid, and registers them with the scheduler.
        """
        from agents.master_agent import MasterAgent
        from agents.worker_agents import (
            PloughingAgent, SowingAgent, WateringAgent,
            HarvestingAgent, DroneMonitoringAgent
        )
        
        # Create Master Agent at center of grid
        center_x = self.width // 2
        center_y = self.height // 2
        self.master_agent = MasterAgent(0, self)
        self.grid.place_agent(self.master_agent, (center_x, center_y))
        self.schedule.add(self.master_agent)
        
        # Create Worker Agents
        agent_id = 1
        
        # Ploughing Agent
        ploughing_agent = PloughingAgent(agent_id, self)
        self.grid.place_agent(ploughing_agent, (2, 2))
        self.schedule.add(ploughing_agent)
        self.worker_agents.append(ploughing_agent)
        self.master_agent.worker_registry["ploughing"] = ploughing_agent
        agent_id += 1
        
        # Sowing Agent
        sowing_agent = SowingAgent(agent_id, self)
        self.grid.place_agent(sowing_agent, (self.width - 3, 2))
        self.schedule.add(sowing_agent)
        self.worker_agents.append(sowing_agent)
        self.master_agent.worker_registry["sowing"] = sowing_agent
        agent_id += 1
        
        # Watering Agent
        watering_agent = WateringAgent(agent_id, self)
        self.grid.place_agent(watering_agent, (2, self.height - 3))
        self.schedule.add(watering_agent)
        self.worker_agents.append(watering_agent)
        self.master_agent.worker_registry["watering"] = watering_agent
        agent_id += 1
        
        # Harvesting Agent
        harvesting_agent = HarvestingAgent(agent_id, self)
        self.grid.place_agent(harvesting_agent, (self.width - 3, self.height - 3))
        self.schedule.add(harvesting_agent)
        self.worker_agents.append(harvesting_agent)
        self.master_agent.worker_registry["harvesting"] = harvesting_agent
        agent_id += 1
        
        # Drone Monitoring Agent
        drone_agent = DroneMonitoringAgent(agent_id, self)
        self.grid.place_agent(drone_agent, (center_x, 2))
        self.schedule.add(drone_agent)
        self.worker_agents.append(drone_agent)
        self.master_agent.worker_registry["drone"] = drone_agent
    
    def step_cells(self):
        """
        Update cell states based on automatic progression rules.
        
        Implements state transitions:
        - GROWING → NEED_WATER (water_level < 0.3)
        - GROWING → HEALTHY (growth_progress > 50 and water_level > 0.5)
        - HEALTHY → READY_TO_HARVEST (growth_progress >= 100)
        
        Also decreases water level and increases growth progress over time.
        """
        for pos, state in list(self.cell_states.items()):
            attrs = self.cell_attributes[pos]
            
            # Update growing and healthy cells
            if state in [CellState.GROWING, CellState.HEALTHY]:
                # Decrease water level over time
                new_water_level = max(0.0, attrs['water_level'] - 0.05)
                attrs['water_level'] = new_water_level
                
                # Increase growth progress if sufficient water
                if new_water_level > 0.3:
                    attrs['growth_progress'] = min(100, attrs['growth_progress'] + 2)
                
                # Check for state transitions
                if state == CellState.GROWING:
                    if new_water_level < 0.3:
                        # Needs water
                        self.cell_states[pos] = CellState.NEED_WATER
                    elif attrs['growth_progress'] > 50 and new_water_level > 0.5:
                        # Transition to healthy
                        self.cell_states[pos] = CellState.HEALTHY
                
                elif state == CellState.HEALTHY:
                    if new_water_level < 0.3:
                        # Needs water
                        self.cell_states[pos] = CellState.NEED_WATER
                    elif attrs['growth_progress'] >= 100:
                        # Ready to harvest
                        self.cell_states[pos] = CellState.READY_TO_HARVEST
    
    def step(self):
        """
        Execute one step of the simulation.
        
        Coordinates cell state updates, message processing, and agent steps.
        """
        self.step_count += 1
        
        # Update weather simulation
        if self.step_count % 5 == 0:  # Update weather every 5 steps
            self.update_weather()
        
        # Update cell states automatically
        self.step_cells()
        
        # Process pending messages
        self.message_bus.process_messages()
        
        # Execute all agent steps
        self.schedule.step()
        
        # Collect data
        self.datacollector.collect(self)
