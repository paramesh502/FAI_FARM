"""
Base Worker Agent implementation.

Provides common functionality for all specialized worker agents including
task reception, movement, and status reporting.
"""

from mesa import Agent
from typing import Optional, Tuple
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.cell_state import Task, AgentStatus, StatusReport, Message
from utils.message_bus import TOPIC_TASK_ASSIGNED, TOPIC_STATUS_UPDATE
from utils.pathfinding import calculate_path


class WorkerAgent(Agent):
    """
    Base class for all worker agents.
    
    Implements common behavior including task reception, pathfinding,
    movement, and status reporting. Subclasses implement specialized
    task execution logic.
    """
    
    def __init__(self, unique_id, model, agent_type: str):
        """
        Initialize the worker agent.
        
        Args:
            unique_id: Unique identifier for this agent
            model: Reference to the FarmModel
            agent_type: Type/role of this worker (e.g., "ploughing", "watering")
        """
        super().__init__(unique_id, model)
        
        self.agent_type = agent_type
        self.current_task: Optional[Task] = None
        self.status = AgentStatus.IDLE
        self.target_position: Optional[Tuple[int, int]] = None
        self.path: list = []
        
        # Subscribe to task assignments for this agent type
        self.model.message_bus.subscribe(TOPIC_TASK_ASSIGNED, self.receive_task)
    
    def step(self):
        """
        Execute one action cycle.
        
        Implements state machine: IDLE → MOVING → WORKING → COMPLETED
        ENHANCED: Faster execution with immediate task completion
        """
        if self.status == AgentStatus.IDLE:
            # Waiting for task assignment
            pass
        
        elif self.status == AgentStatus.MOVING:
            # ENHANCED: Move faster - take multiple steps if path is short
            steps_to_take = min(3, len(self.path)) if self.path else 0
            
            for _ in range(steps_to_take):
                if self.path:
                    next_pos = self.path.pop(0)
                    self.model.grid.move_agent(self, next_pos)
                    
                    # Check if reached target
                    if self.pos == self.target_position:
                        self.status = AgentStatus.WORKING
                        break
            
            # If no path or reached destination
            if not self.path or self.pos == self.target_position:
                self.status = AgentStatus.WORKING
        
        elif self.status == AgentStatus.WORKING:
            # Execute the assigned task immediately
            if self.current_task:
                self.execute_task()
                self.status = AgentStatus.COMPLETED
        
        elif self.status == AgentStatus.COMPLETED:
            # Report completion and return to idle immediately
            self.report_status()
            self.current_task = None
            self.target_position = None
            self.status = AgentStatus.IDLE
    
    def receive_task(self, message: Message):
        """
        Receive and accept a task assignment from the master agent.
        
        Args:
            message: Message containing task assignment
        """
        # Only accept tasks for this agent type
        payload = message.payload
        worker_type = payload.get('worker_type')
        
        if worker_type != self.agent_type:
            return
        
        # Only accept if currently idle
        if self.status != AgentStatus.IDLE:
            return
        
        task = payload.get('task')
        if not task:
            return
        
        self.current_task = task
        self.target_position = task.target_cell
        
        # Calculate path to target
        self.move_to_target(self.target_position)
    
    def move_to_target(self, target_pos: Tuple[int, int]):
        """
        Navigate to target grid cell using pathfinding.
        
        Args:
            target_pos: Target grid position (x, y)
        """
        if not target_pos:
            return
        
        # Calculate path from current position to target
        self.path = calculate_path(
            self.pos,
            target_pos,
            self.model.width,
            self.model.height,
            obstacles=set()  # Could add obstacle detection here
        )
        
        if self.path:
            # Remove current position from path
            if self.path and self.path[0] == self.pos:
                self.path.pop(0)
            self.status = AgentStatus.MOVING
        else:
            # No path found - report obstacle
            self.status = AgentStatus.IDLE
            self.current_task = None
    
    def execute_task(self):
        """
        Execute the assigned task.
        
        This method should be overridden by subclasses to implement
        specialized task execution logic.
        """
        raise NotImplementedError("Subclasses must implement execute_task()")
    
    def report_status(self):
        """Send status update to master agent via message bus."""
        if not self.current_task:
            return
        
        status_report = StatusReport(
            agent_id=self.unique_id,
            agent_type=self.agent_type,
            current_position=self.pos,
            status=self.status,
            current_task=self.current_task.task_id if self.current_task else None,
            message=f"{self.agent_type} agent completed task"
        )
        
        message = Message(
            topic=TOPIC_STATUS_UPDATE,
            sender_id=self.unique_id,
            timestamp=self.model.step_count,
            payload={
                'status_report': status_report,
                'task_id': self.current_task.task_id,
                'cell_position': self.current_task.target_cell
            }
        )
        
        self.model.message_bus.publish(TOPIC_STATUS_UPDATE, message)
