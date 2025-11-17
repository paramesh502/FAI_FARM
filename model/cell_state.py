"""
Cell state definitions and data models for the FAI-Farm simulation.

This module defines the core data structures used throughout the simulation including
cell states, tasks, messages, and status reports.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Tuple


class CellState(Enum):
    """Enumeration of all possible farm cell states."""
    INITIAL = 0
    PLOUGHED = 1
    SOWN = 2
    GROWING = 3
    NEED_WATER = 4
    HEALTHY = 5
    DISEASED = 6
    READY_TO_HARVEST = 7


class TaskType(Enum):
    """Enumeration of task types that can be assigned to worker agents."""
    PLOUGH = "plough"
    SOW = "sow"
    WATER = "water"
    MONITOR = "monitor"
    HARVEST = "harvest"


class TaskStatus(Enum):
    """Enumeration of task execution states."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentStatus(Enum):
    """Enumeration of agent operational states."""
    IDLE = "idle"
    MOVING = "moving"
    WORKING = "working"
    COMPLETED = "completed"


@dataclass
class Task:
    """
    Represents a work task to be executed by a worker agent.
    
    Attributes:
        task_id: Unique identifier for the task
        task_type: Type of agricultural operation to perform
        target_cell: Grid coordinates (x, y) where task should be executed
        priority: Priority score for task scheduling (higher = more urgent)
        assigned_to: Agent ID of the worker assigned to this task
        status: Current execution status of the task
        created_at: Simulation step when task was created
        completed_at: Simulation step when task was completed
    """
    task_id: str
    task_type: TaskType
    target_cell: Tuple[int, int]
    priority: int
    assigned_to: Optional[int] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: int = 0
    completed_at: Optional[int] = None


@dataclass
class Message:
    """
    Represents a message passed through the message bus between agents.
    
    Attributes:
        topic: Message topic/channel for routing
        sender_id: Agent ID of the message sender
        timestamp: Simulation step when message was created
        payload: Dictionary containing message-specific data
    """
    topic: str
    sender_id: int
    timestamp: int
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StatusReport:
    """
    Represents a status update from a worker agent to the master agent.
    
    Attributes:
        agent_id: Unique identifier of the reporting agent
        agent_type: Type/role of the agent (e.g., "ploughing", "watering")
        current_position: Current grid coordinates of the agent
        status: Current operational status of the agent
        current_task: ID of the task currently being executed
        message: Human-readable status message
    """
    agent_id: int
    agent_type: str
    current_position: Tuple[int, int]
    status: AgentStatus
    current_task: Optional[str] = None
    message: str = ""


@dataclass
class CellKnowledge:
    """
    Represents the master agent's knowledge about a specific grid cell.
    
    Attributes:
        position: Grid coordinates of the cell
        state: Current agricultural state of the cell
        water_level: Water content level (0.0 to 1.0)
        growth_progress: Crop growth percentage (0 to 100)
        disease_probability: Probability of disease presence (0.0 to 1.0)
        last_updated: Simulation step when knowledge was last updated
        pending_tasks: List of task IDs scheduled for this cell
    """
    position: Tuple[int, int]
    state: CellState
    water_level: float
    growth_progress: int
    disease_probability: float
    last_updated: int
    pending_tasks: list = field(default_factory=list)
