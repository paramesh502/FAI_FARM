"""
CSP-based task scheduler for FAI-Farm.

Solves resource allocation and scheduling constraints using CSP techniques.
Can integrate with OR-Tools CP-SAT solver for production use.
"""

from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.cell_state import TaskType


class ResourceType(Enum):
    """Types of resources that can be constrained."""
    WATER = "water"
    FUEL = "fuel"
    TOOLS = "tools"
    TIME = "time"


@dataclass
class Resource:
    """Represents a constrained resource."""
    type: ResourceType
    available: float
    max_capacity: float
    
    def consume(self, amount: float) -> bool:
        """
        Attempt to consume resource.
        
        Args:
            amount: Amount to consume
        
        Returns:
            True if consumption successful, False if insufficient
        """
        if self.available >= amount:
            self.available -= amount
            return True
        return False
    
    def replenish(self, amount: float):
        """Replenish resource up to max capacity."""
        self.available = min(self.max_capacity, self.available + amount)


@dataclass
class TaskAssignment:
    """Represents an assignment of a task to an agent at a time slot."""
    task_id: str
    agent_id: int
    agent_type: str
    time_slot: int
    duration: int
    target_cell: Tuple[int, int]
    resource_requirements: Dict[ResourceType, float]
    priority: int


class CSPScheduler:
    """
    Constraint Satisfaction Problem solver for task scheduling.
    
    Handles:
    - Resource constraints (water, fuel, tools)
    - Time window constraints
    - Agent availability constraints
    - Task dependencies
    - Priority-based assignment
    """
    
    def __init__(self, time_horizon: int = 100):
        """
        Initialize the CSP scheduler.
        
        Args:
            time_horizon: Number of time slots to schedule over
        """
        self.time_horizon = time_horizon
        self.resources: Dict[ResourceType, Resource] = {}
        self.assignments: List[TaskAssignment] = []
        self.agent_schedules: Dict[int, List[int]] = {}  # agent_id -> occupied time slots
        
        # Initialize default resources
        self.resources[ResourceType.WATER] = Resource(ResourceType.WATER, 1000.0, 1000.0)
        self.resources[ResourceType.FUEL] = Resource(ResourceType.FUEL, 500.0, 500.0)
        self.resources[ResourceType.TOOLS] = Resource(ResourceType.TOOLS, 5.0, 5.0)
    
    def add_resource(self, resource_type: ResourceType, capacity: float):
        """
        Add or update a resource constraint.
        
        Args:
            resource_type: Type of resource
            capacity: Maximum capacity
        """
        self.resources[resource_type] = Resource(resource_type, capacity, capacity)
    
    def is_agent_available(self, agent_id: int, time_slot: int, duration: int) -> bool:
        """
        Check if an agent is available for a time window.
        
        Args:
            agent_id: Agent identifier
            time_slot: Start time slot
            duration: Duration in time slots
        
        Returns:
            True if agent is available for entire duration
        """
        if agent_id not in self.agent_schedules:
            self.agent_schedules[agent_id] = []
        
        occupied = set(self.agent_schedules[agent_id])
        required = set(range(time_slot, time_slot + duration))
        
        return len(occupied.intersection(required)) == 0
    
    def check_resource_availability(
        self, 
        requirements: Dict[ResourceType, float]
    ) -> bool:
        """
        Check if resources are available for a task.
        
        Args:
            requirements: Resource requirements
        
        Returns:
            True if all resources available
        """
        for resource_type, amount in requirements.items():
            if resource_type not in self.resources:
                return False
            if self.resources[resource_type].available < amount:
                return False
        return True
    
    def assign_task(
        self,
        task_id: str,
        agent_id: int,
        agent_type: str,
        time_slot: int,
        duration: int,
        target_cell: Tuple[int, int],
        resource_requirements: Dict[ResourceType, float],
        priority: int
    ) -> bool:
        """
        Attempt to assign a task to an agent.
        
        Args:
            task_id: Task identifier
            agent_id: Agent to assign to
            agent_type: Type of agent
            time_slot: Start time
            duration: Task duration
            target_cell: Target location
            resource_requirements: Required resources
            priority: Task priority
        
        Returns:
            True if assignment successful
        """
        # Check agent availability
        if not self.is_agent_available(agent_id, time_slot, duration):
            return False
        
        # Check resource availability
        if not self.check_resource_availability(resource_requirements):
            return False
        
        # Create assignment
        assignment = TaskAssignment(
            task_id=task_id,
            agent_id=agent_id,
            agent_type=agent_type,
            time_slot=time_slot,
            duration=duration,
            target_cell=target_cell,
            resource_requirements=resource_requirements,
            priority=priority
        )
        
        # Reserve agent time slots
        if agent_id not in self.agent_schedules:
            self.agent_schedules[agent_id] = []
        self.agent_schedules[agent_id].extend(range(time_slot, time_slot + duration))
        
        # Consume resources
        for resource_type, amount in resource_requirements.items():
            self.resources[resource_type].consume(amount)
        
        # Add assignment
        self.assignments.append(assignment)
        
        return True
    
    def schedule_tasks(
        self,
        tasks: List[Dict],
        agents: Dict[str, List[int]]
    ) -> List[TaskAssignment]:
        """
        Schedule a list of tasks to available agents.
        
        Args:
            tasks: List of task dictionaries with keys:
                   task_id, task_type, target_cell, priority, duration, resources
            agents: Dictionary mapping agent_type to list of agent_ids
        
        Returns:
            List of successful task assignments
        """
        # Sort tasks by priority (highest first)
        sorted_tasks = sorted(tasks, key=lambda t: t.get('priority', 0), reverse=True)
        
        successful_assignments = []
        
        for task in sorted_tasks:
            task_id = task['task_id']
            task_type = task['task_type']
            target_cell = task['target_cell']
            priority = task.get('priority', 50)
            duration = task.get('duration', 1)
            resources = task.get('resources', {})
            
            # Determine agent type needed
            agent_type = self._get_agent_type_for_task(task_type)
            
            if agent_type not in agents:
                continue
            
            # Try to assign to any available agent of the correct type
            assigned = False
            for agent_id in agents[agent_type]:
                # Try different time slots
                for time_slot in range(self.time_horizon - duration + 1):
                    if self.assign_task(
                        task_id=task_id,
                        agent_id=agent_id,
                        agent_type=agent_type,
                        time_slot=time_slot,
                        duration=duration,
                        target_cell=target_cell,
                        resource_requirements=resources,
                        priority=priority
                    ):
                        successful_assignments.append(self.assignments[-1])
                        assigned = True
                        break
                
                if assigned:
                    break
        
        return successful_assignments
    
    def _get_agent_type_for_task(self, task_type: str) -> str:
        """Map task type to agent type."""
        mapping = {
            "PLOUGH": "ploughing",
            "SOW": "sowing",
            "WATER": "watering",
            "HARVEST": "harvesting",
            "MONITOR": "drone"
        }
        return mapping.get(task_type, "")
    
    def get_schedule_metrics(self) -> Dict:
        """
        Calculate scheduling metrics.
        
        Returns:
            Dictionary of metrics
        """
        if not self.assignments:
            return {
                'total_tasks': 0,
                'makespan': 0,
                'resource_utilization': {},
                'agent_utilization': {}
            }
        
        makespan = max(a.time_slot + a.duration for a in self.assignments)
        
        # Calculate resource utilization
        resource_util = {}
        for res_type, resource in self.resources.items():
            utilization = (resource.max_capacity - resource.available) / resource.max_capacity
            resource_util[res_type.value] = utilization
        
        # Calculate agent utilization
        agent_util = {}
        for agent_id, slots in self.agent_schedules.items():
            utilization = len(set(slots)) / self.time_horizon
            agent_util[agent_id] = utilization
        
        return {
            'total_tasks': len(self.assignments),
            'makespan': makespan,
            'resource_utilization': resource_util,
            'agent_utilization': agent_util
        }
    
    def reset(self):
        """Reset the scheduler to initial state."""
        self.assignments = []
        self.agent_schedules = {}
        
        # Replenish all resources
        for resource in self.resources.values():
            resource.available = resource.max_capacity
    
    def export_schedule(self, filename: str):
        """
        Export the schedule to a file.
        
        Args:
            filename: Output file path
        """
        with open(filename, 'w') as f:
            f.write("# FAI-Farm CSP Schedule\n\n")
            f.write("## Task Assignments\n\n")
            
            for assignment in sorted(self.assignments, key=lambda a: a.time_slot):
                f.write(f"Time {assignment.time_slot}: ")
                f.write(f"Agent {assignment.agent_id} ({assignment.agent_type}) -> ")
                f.write(f"Task {assignment.task_id} at {assignment.target_cell}\n")
            
            f.write("\n## Metrics\n\n")
            metrics = self.get_schedule_metrics()
            for key, value in metrics.items():
                f.write(f"{key}: {value}\n")
