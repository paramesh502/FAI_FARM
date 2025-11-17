"""
Master Agent implementation for farm coordination.

The Master Agent maintains global knowledge of the farm state, plans tasks,
assigns work to worker agents, and adapts plans based on feedback.
"""

from mesa import Agent
from queue import PriorityQueue
from typing import Dict, Tuple
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.cell_state import CellState, CellKnowledge, Task, TaskType, TaskStatus, Message
from utils.message_bus import (
    TOPIC_STATUS_UPDATE,
    TOPIC_ALERT_DISEASE,
    TOPIC_ALERT_OBSTACLE,
    TOPIC_TASK_COMPLETED,
    TOPIC_TASK_ASSIGNED
)


class MasterAgent(Agent):
    """
    Master coordination agent that plans and assigns tasks to worker agents.
    
    Maintains global knowledge of farm state, implements rule-based reasoning
    for task prioritization, and adapts plans based on worker feedback.
    """
    
    def __init__(self, unique_id, model):
        """
        Initialize the Master Agent.
        
        Args:
            unique_id: Unique identifier for this agent
            model: Reference to the FarmModel
        """
        super().__init__(unique_id, model)
        
        # Global knowledge base mapping cell positions to knowledge
        self.knowledge_base: Dict[Tuple[int, int], CellKnowledge] = {}
        
        # Task queue with priority ordering
        self.task_queue = PriorityQueue()
        
        # Registry of worker agents by type
        self.worker_registry: Dict[str, Agent] = {}
        
        # Track assigned tasks
        self.assigned_tasks: Dict[str, Task] = {}
        
        # Task counter for unique IDs
        self.task_counter = 0
        
        # Initialize knowledge base for all cells
        self._initialize_knowledge_base()
        
        # Subscribe to worker feedback topics
        self.model.message_bus.subscribe(TOPIC_STATUS_UPDATE, self.handle_feedback)
        self.model.message_bus.subscribe(TOPIC_ALERT_DISEASE, self.handle_feedback)
        self.model.message_bus.subscribe(TOPIC_ALERT_OBSTACLE, self.handle_feedback)
        self.model.message_bus.subscribe(TOPIC_TASK_COMPLETED, self.handle_feedback)
    
    def _initialize_knowledge_base(self):
        """Initialize knowledge base with current farm state."""
        for x in range(self.model.width):
            for y in range(self.model.height):
                pos = (x, y)
                attrs = self.model.get_cell_attributes(pos)
                self.knowledge_base[pos] = CellKnowledge(
                    position=pos,
                    state=self.model.get_cell_state(pos),
                    water_level=attrs.get('water_level', 0.0),
                    growth_progress=attrs.get('growth_progress', 0),
                    disease_probability=attrs.get('disease_probability', 0.0),
                    last_updated=self.model.step_count,
                    pending_tasks=[]
                )
    
    def step(self):
        """
        Execute one planning cycle.
        
        Updates knowledge, plans tasks, and assigns work to available workers.
        """
        # Update knowledge from current farm state
        self.update_knowledge()
        
        # Plan new tasks based on current state
        self.plan_tasks()
        
        # Assign tasks to available workers
        self.assign_pending_tasks()
    
    def update_knowledge(self):
        """Update global knowledge base from current farm state."""
        for pos, knowledge in self.knowledge_base.items():
            current_state = self.model.get_cell_state(pos)
            attrs = self.model.get_cell_attributes(pos)
            
            knowledge.state = current_state
            knowledge.water_level = attrs.get('water_level', 0.0)
            knowledge.growth_progress = attrs.get('growth_progress', 0)
            knowledge.disease_probability = attrs.get('disease_probability', 0.0)
            knowledge.last_updated = self.model.step_count
    
    def plan_tasks(self):
        """
        Generate task assignments based on current farm state.
        
        Implements priority scoring: DISEASED > NEED_WATER > READY_TO_HARVEST > 
        SOWN > PLOUGHED > INITIAL
        
        Enhanced to be more aggressive in task generation and weather-aware.
        """
        # Count current tasks by type to balance workload
        task_counts = {}
        for task_id, task in self.assigned_tasks.items():
            task_type = task.task_type.value
            task_counts[task_type] = task_counts.get(task_type, 0) + 1
        
        # Limit tasks per type to avoid overwhelming agents
        max_tasks_per_type = 10
        
        # Check weather conditions
        rain_forecast = self.model.weather.get('rain_forecast_24h', False)
        high_temp = self.model.weather.get('temperature', 25) > 32
        
        for pos, knowledge in self.knowledge_base.items():
            # Skip if cell already has pending tasks
            if knowledge.pending_tasks:
                continue
            
            state = knowledge.state
            task_type = None
            priority = 0
            
            # Determine task type and priority based on cell state
            if state == CellState.DISEASED:
                # Highest priority: treat diseased crops with water
                task_type = TaskType.WATER
                priority = 100
            elif state == CellState.NEED_WATER:
                # High priority: water crops that need it
                # WEATHER-AWARE: Skip if rain is coming, unless high temp stress
                if rain_forecast and not high_temp:
                    continue  # Skip watering, rain will handle it
                task_type = TaskType.WATER
                priority = 95 if high_temp else 90  # Higher priority in heat
            elif state == CellState.READY_TO_HARVEST:
                # Medium-high priority: harvest ready crops
                task_type = TaskType.HARVEST
                priority = 80
            elif state == CellState.SOWN:
                # Medium priority: water newly sown seeds
                # WEATHER-AWARE: Reduce priority if rain is coming
                if rain_forecast:
                    priority = 50  # Lower priority, rain will help
                else:
                    priority = 70
                task_type = TaskType.WATER
            elif state == CellState.PLOUGHED:
                # Low-medium priority: sow seeds in ploughed soil
                task_type = TaskType.SOW
                priority = 60
            elif state == CellState.INITIAL:
                # Low priority: plough initial soil
                # ENHANCED: More aggressive ploughing
                task_type = TaskType.PLOUGH
                priority = 50
            
            # Create task if needed and not exceeding limits
            if task_type:
                task_type_str = task_type.value
                current_count = task_counts.get(task_type_str, 0)
                if current_count < max_tasks_per_type:
                    self.create_task(task_type, pos, priority)
                    task_counts[task_type_str] = current_count + 1
    
    def create_task(self, task_type: TaskType, target_cell: Tuple[int, int], priority: int):
        """
        Create a new task and add to queue.
        
        Args:
            task_type: Type of task to create
            target_cell: Grid position for task execution
            priority: Priority score (higher = more urgent)
        """
        self.task_counter += 1
        task_id = f"task_{self.task_counter}"
        
        task = Task(
            task_id=task_id,
            task_type=task_type,
            target_cell=target_cell,
            priority=priority,
            status=TaskStatus.PENDING,
            created_at=self.model.step_count
        )
        
        # Add to priority queue (negative priority for max-heap behavior)
        self.task_queue.put((-priority, self.task_counter, task))
        
        # Mark cell as having pending task
        if target_cell in self.knowledge_base:
            self.knowledge_base[target_cell].pending_tasks.append(task_id)
    
    def assign_pending_tasks(self):
        """Assign pending tasks to available workers."""
        # ENHANCED: Process more tasks per step for faster execution
        tasks_to_assign = min(20, self.task_queue.qsize())
        
        for _ in range(tasks_to_assign):
            if self.task_queue.empty():
                break
            
            _, _, task = self.task_queue.get()
            
            # Determine worker type needed for this task
            worker_type = self._get_worker_type_for_task(task.task_type)
            
            if worker_type and worker_type in self.worker_registry:
                self.assign_task(worker_type, task)
    
    def _get_worker_type_for_task(self, task_type: TaskType) -> str:
        """Map task type to worker agent type."""
        mapping = {
            TaskType.PLOUGH: "ploughing",
            TaskType.SOW: "sowing",
            TaskType.WATER: "watering",
            TaskType.HARVEST: "harvesting",
            TaskType.MONITOR: "drone"
        }
        return mapping.get(task_type, "")
    
    def assign_task(self, worker_type: str, task: Task):
        """
        Assign a task to a specific worker type.
        
        Args:
            worker_type: Type of worker to assign task to
            task: Task object to assign
        """
        worker = self.worker_registry.get(worker_type)
        if not worker:
            return
        
        task.status = TaskStatus.ASSIGNED
        task.assigned_to = worker.unique_id
        self.assigned_tasks[task.task_id] = task
        
        # Publish task assignment message
        message = Message(
            topic=TOPIC_TASK_ASSIGNED,
            sender_id=self.unique_id,
            timestamp=self.model.step_count,
            payload={
                'task': task,
                'worker_type': worker_type
            }
        )
        self.model.message_bus.publish(TOPIC_TASK_ASSIGNED, message)
    
    def handle_feedback(self, message: Message):
        """
        Process feedback messages from worker agents.
        
        Args:
            message: Message object containing feedback
        """
        topic = message.topic
        payload = message.payload
        
        if topic == TOPIC_TASK_COMPLETED:
            # Task completed successfully
            task_id = payload.get('task_id')
            if task_id in self.assigned_tasks:
                task = self.assigned_tasks[task_id]
                task.status = TaskStatus.COMPLETED
                task.completed_at = self.model.step_count
                
                # Remove from pending tasks in knowledge base
                if task.target_cell in self.knowledge_base:
                    kb = self.knowledge_base[task.target_cell]
                    if task_id in kb.pending_tasks:
                        kb.pending_tasks.remove(task_id)
                
                # Remove from assigned tasks
                del self.assigned_tasks[task_id]
        
        elif topic == TOPIC_ALERT_DISEASE:
            # Disease detected - create high priority watering task
            cell_pos = payload.get('cell_position')
            if cell_pos:
                self.create_task(TaskType.WATER, cell_pos, priority=95)
        
        elif topic == TOPIC_ALERT_OBSTACLE:
            # Obstacle encountered - could implement rerouting logic here
            pass
        
        elif topic == TOPIC_STATUS_UPDATE:
            # General status update from worker
            pass
