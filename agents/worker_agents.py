"""
Specialized Worker Agent implementations.

This module contains all specialized worker agents including Ploughing, Sowing,
Watering, Harvesting, and Drone Monitoring agents.
"""

import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import WorkerAgent
from model.cell_state import CellState, Message
from utils.message_bus import TOPIC_TASK_COMPLETED, TOPIC_ALERT_DISEASE


class PloughingAgent(WorkerAgent):
    """
    Ploughing agent that prepares soil for planting.
    
    Transitions grid cells from INITIAL state to PLOUGHED state.
    """
    
    def __init__(self, unique_id, model):
        """Initialize the ploughing agent."""
        super().__init__(unique_id, model, "ploughing")
    
    def execute_task(self):
        """
        Execute ploughing task at current position.
        
        Validates cell is in INITIAL state before ploughing and updates
        cell state to PLOUGHED.
        """
        if not self.current_task:
            return
        
        target_cell = self.current_task.target_cell
        current_state = self.model.get_cell_state(target_cell)
        
        # Validate cell is in correct state for ploughing
        if current_state == CellState.INITIAL:
            # Transition to PLOUGHED state
            self.model.set_cell_state(target_cell, CellState.PLOUGHED)
            
            # Publish task completion message
            message = Message(
                topic=TOPIC_TASK_COMPLETED,
                sender_id=self.unique_id,
                timestamp=self.model.step_count,
                payload={
                    'task_id': self.current_task.task_id,
                    'cell_position': target_cell,
                    'action': 'ploughed'
                }
            )
            self.model.message_bus.publish(TOPIC_TASK_COMPLETED, message)


class SowingAgent(WorkerAgent):
    """
    Sowing agent that plants seeds in prepared soil.
    
    Transitions grid cells from PLOUGHED state to SOWN state and initializes
    growth parameters.
    """
    
    def __init__(self, unique_id, model):
        """Initialize the sowing agent."""
        super().__init__(unique_id, model, "sowing")
    
    def execute_task(self):
        """
        Execute sowing task at current position.
        
        Validates cell is in PLOUGHED state before sowing and updates
        cell state to SOWN with initial growth parameters.
        """
        if not self.current_task:
            return
        
        target_cell = self.current_task.target_cell
        current_state = self.model.get_cell_state(target_cell)
        
        # Validate cell is in correct state for sowing
        if current_state == CellState.PLOUGHED:
            # Transition to SOWN state
            self.model.set_cell_state(target_cell, CellState.SOWN)
            
            # Initialize growth parameters
            self.model.update_cell_attributes(
                target_cell,
                growth_progress=0,
                water_level=0.5,
                disease_probability=0.0
            )
            
            # Publish task completion message
            message = Message(
                topic=TOPIC_TASK_COMPLETED,
                sender_id=self.unique_id,
                timestamp=self.model.step_count,
                payload={
                    'task_id': self.current_task.task_id,
                    'cell_position': target_cell,
                    'action': 'sown'
                }
            )
            self.model.message_bus.publish(TOPIC_TASK_COMPLETED, message)


class WateringAgent(WorkerAgent):
    """
    Watering agent that irrigates crops.
    
    Transitions cells from SOWN or NEED_WATER states to GROWING or HEALTHY
    states and increases water level.
    """
    
    def __init__(self, unique_id, model):
        """Initialize the watering agent."""
        super().__init__(unique_id, model, "watering")
    
    def execute_task(self):
        """
        Execute watering task at current position.
        
        Handles cells in SOWN, NEED_WATER, or DISEASED states by increasing
        water level and transitioning to appropriate growth state.
        
        Weather-aware: Skips watering if rain is forecasted.
        """
        if not self.current_task:
            return
        
        target_cell = self.current_task.target_cell
        current_state = self.model.get_cell_state(target_cell)
        attrs = self.model.get_cell_attributes(target_cell)
        
        # Check weather - skip watering if rain is coming
        if self.model.weather.get('rain_forecast_24h', False):
            # Publish task completion with weather delay message
            message = Message(
                topic=TOPIC_TASK_COMPLETED,
                sender_id=self.unique_id,
                timestamp=self.model.step_count,
                payload={
                    'task_id': self.current_task.task_id,
                    'cell_position': target_cell,
                    'action': 'watering_delayed',
                    'reason': 'rain_forecast'
                }
            )
            self.model.message_bus.publish(TOPIC_TASK_COMPLETED, message)
            return
        
        # Handle different cell states
        if current_state == CellState.SOWN:
            # Transition newly sown seeds to growing
            self.model.set_cell_state(target_cell, CellState.GROWING)
            new_water_level = min(1.0, attrs.get('water_level', 0.0) + 0.3)
            self.model.update_cell_attributes(
                target_cell,
                water_level=new_water_level,
                last_watered=self.model.step_count
            )
        
        elif current_state == CellState.NEED_WATER:
            # Water crops that need it
            growth_progress = attrs.get('growth_progress', 0)
            new_water_level = min(1.0, attrs.get('water_level', 0.0) + 0.3)
            
            # Transition based on growth progress
            if growth_progress > 50 and new_water_level > 0.5:
                self.model.set_cell_state(target_cell, CellState.HEALTHY)
            else:
                self.model.set_cell_state(target_cell, CellState.GROWING)
            
            self.model.update_cell_attributes(
                target_cell,
                water_level=new_water_level,
                last_watered=self.model.step_count
            )
        
        elif current_state == CellState.DISEASED:
            # Water diseased crops (treatment)
            new_water_level = min(1.0, attrs.get('water_level', 0.0) + 0.3)
            self.model.update_cell_attributes(
                target_cell,
                water_level=new_water_level,
                last_watered=self.model.step_count,
                disease_probability=max(0.0, attrs.get('disease_probability', 0.0) - 0.2)
            )
            # Transition back to growing if water helps
            if new_water_level > 0.6:
                self.model.set_cell_state(target_cell, CellState.GROWING)
        
        # Publish task completion message
        message = Message(
            topic=TOPIC_TASK_COMPLETED,
            sender_id=self.unique_id,
            timestamp=self.model.step_count,
            payload={
                'task_id': self.current_task.task_id,
                'cell_position': target_cell,
                'action': 'watered'
            }
        )
        self.model.message_bus.publish(TOPIC_TASK_COMPLETED, message)


class HarvestingAgent(WorkerAgent):
    """
    Harvesting agent that collects mature crops.
    
    Transitions cells from READY_TO_HARVEST state back to INITIAL state
    and resets cell attributes.
    """
    
    def __init__(self, unique_id, model):
        """Initialize the harvesting agent."""
        super().__init__(unique_id, model, "harvesting")
    
    def execute_task(self):
        """
        Execute harvesting task at current position.
        
        Validates cell is ready for harvest, collects crop, and resets
        cell to initial state.
        """
        if not self.current_task:
            return
        
        target_cell = self.current_task.target_cell
        current_state = self.model.get_cell_state(target_cell)
        
        # Validate cell is ready for harvest
        if current_state == CellState.READY_TO_HARVEST:
            # Transition back to INITIAL state
            self.model.set_cell_state(target_cell, CellState.INITIAL)
            
            # Reset cell attributes
            self.model.update_cell_attributes(
                target_cell,
                water_level=0.0,
                growth_progress=0,
                disease_probability=0.0,
                last_watered=0
            )
            
            # Increment harvest counter
            self.model.harvested_count += 1
            
            # Publish task completion message
            message = Message(
                topic=TOPIC_TASK_COMPLETED,
                sender_id=self.unique_id,
                timestamp=self.model.step_count,
                payload={
                    'task_id': self.current_task.task_id,
                    'cell_position': target_cell,
                    'action': 'harvested',
                    'yield': 1
                }
            )
            self.model.message_bus.publish(TOPIC_TASK_COMPLETED, message)


class DroneMonitoringAgent(WorkerAgent):
    """
    Drone monitoring agent that scans crops for disease.
    
    Periodically scans all grid cells, calculates disease probability,
    and alerts master agent when disease is detected.
    """
    
    def __init__(self, unique_id, model):
        """Initialize the drone monitoring agent."""
        super().__init__(unique_id, model, "drone")
        self.scan_interval = 15  # Scan every 15 steps (less frequent since disease is rare)
        self.last_scan_step = 0
        self.scan_index = 0  # Track which cells have been scanned
    
    def step(self):
        """
        Execute monitoring cycle.
        
        Overrides base step to implement periodic scanning behavior.
        """
        # Perform periodic scanning
        if self.model.step_count - self.last_scan_step >= self.scan_interval:
            self.scan_farm()
            self.last_scan_step = self.model.step_count
    
    def scan_farm(self):
        """
        Scan all grid cells for disease.
        
        Calculates disease probability for each cell and transitions
        cells to DISEASED state when probability exceeds threshold.
        """
        for x in range(self.model.width):
            for y in range(self.model.height):
                cell_pos = (x, y)
                self.scan_cell(cell_pos)
    
    def scan_cell(self, cell_pos):
        """
        Scan a single cell for disease.
        
        Args:
            cell_pos: Grid position to scan
        """
        current_state = self.model.get_cell_state(cell_pos)
        
        # Only scan growing or healthy crops
        if current_state not in [CellState.GROWING, CellState.HEALTHY, CellState.SOWN]:
            return
        
        attrs = self.model.get_cell_attributes(cell_pos)
        water_level = attrs.get('water_level', 0.5)
        growth_progress = attrs.get('growth_progress', 0)
        
        # Calculate disease probability
        # Base probability increases with low water and growth stage
        # Disease should be rare - only 2-5% of crops get diseased
        base_prob = 0.02  # Very low base (2%)
        water_factor = (1.0 - water_level) * 0.15  # Low water impact
        growth_factor = (growth_progress / 100.0) * 0.1  # Low growth impact
        random_factor = random.random() * 0.1  # Small random factor
        
        disease_probability = base_prob + water_factor + growth_factor + random_factor
        
        # Update disease probability in cell attributes
        self.model.update_cell_attributes(
            cell_pos,
            disease_probability=disease_probability
        )
        
        # Transition to diseased if probability exceeds threshold
        # High threshold means disease is rare
        if disease_probability > 0.85:  # Very high threshold - disease is rare
            self.model.set_cell_state(cell_pos, CellState.DISEASED)
            
            # Publish disease alert
            message = Message(
                topic=TOPIC_ALERT_DISEASE,
                sender_id=self.unique_id,
                timestamp=self.model.step_count,
                payload={
                    'cell_position': cell_pos,
                    'disease_probability': disease_probability,
                    'water_level': water_level
                }
            )
            self.model.message_bus.publish(TOPIC_ALERT_DISEASE, message)
    
    def execute_task(self):
        """
        Drone doesn't execute traditional tasks.
        
        Monitoring is done in the step method instead.
        """
        pass
