"""
Pathfinding utilities for agent navigation.

This module implements A* pathfinding algorithm for grid-based navigation,
allowing agents to find optimal paths while avoiding obstacles.
"""

import heapq
from typing import List, Tuple, Set, Optional


def get_neighbors(pos: Tuple[int, int], width: int, height: int) -> List[Tuple[int, int]]:
    """
    Get valid neighboring cells for a grid position.
    
    Returns the 4-connected neighbors (up, down, left, right) that are
    within the grid boundaries.
    
    Args:
        pos: Current position as (x, y) tuple
        width: Grid width
        height: Grid height
    
    Returns:
        List of valid neighbor positions
    """
    x, y = pos
    neighbors = []
    
    # Check all 4 directions (up, down, left, right)
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < width and 0 <= ny < height:
            neighbors.append((nx, ny))
    
    return neighbors


def heuristic(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    """
    Calculate Manhattan distance heuristic between two positions.
    
    Args:
        pos1: First position (x, y)
        pos2: Second position (x, y)
    
    Returns:
        Manhattan distance between positions
    """
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def calculate_path(
    start: Tuple[int, int],
    goal: Tuple[int, int],
    width: int,
    height: int,
    obstacles: Optional[Set[Tuple[int, int]]] = None
) -> List[Tuple[int, int]]:
    """
    Calculate optimal path from start to goal using A* algorithm.
    
    Finds the shortest path on a grid while avoiding obstacles. Uses
    Manhattan distance as the heuristic function.
    
    Args:
        start: Starting position (x, y)
        goal: Goal position (x, y)
        width: Grid width
        height: Grid height
        obstacles: Set of positions that cannot be traversed
    
    Returns:
        List of positions from start to goal (inclusive), or empty list if no path exists
    """
    if obstacles is None:
        obstacles = set()
    
    # If start or goal is an obstacle, no path exists
    if start in obstacles or goal in obstacles:
        return []
    
    # If already at goal, return single-element path
    if start == goal:
        return [start]
    
    # Priority queue: (f_score, counter, position, path)
    # counter ensures stable sorting when f_scores are equal
    counter = 0
    open_set = [(0, counter, start, [start])]
    closed_set = set()
    
    # Track best g_score for each position
    g_scores = {start: 0}
    
    while open_set:
        f_score, _, current, path = heapq.heappop(open_set)
        
        # Skip if already processed
        if current in closed_set:
            continue
        
        # Check if we reached the goal
        if current == goal:
            return path
        
        closed_set.add(current)
        current_g = g_scores[current]
        
        # Explore neighbors
        for neighbor in get_neighbors(current, width, height):
            # Skip obstacles and already processed nodes
            if neighbor in obstacles or neighbor in closed_set:
                continue
            
            # Calculate tentative g_score (cost from start to neighbor)
            tentative_g = current_g + 1
            
            # If this path to neighbor is better than any previous one
            if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                g_scores[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor, goal)
                counter += 1
                new_path = path + [neighbor]
                heapq.heappush(open_set, (f_score, counter, neighbor, new_path))
    
    # No path found
    return []


def is_path_clear(
    start: Tuple[int, int],
    goal: Tuple[int, int],
    width: int,
    height: int,
    obstacles: Optional[Set[Tuple[int, int]]] = None
) -> bool:
    """
    Check if a clear path exists between start and goal.
    
    Args:
        start: Starting position (x, y)
        goal: Goal position (x, y)
        width: Grid width
        height: Grid height
        obstacles: Set of positions that cannot be traversed
    
    Returns:
        True if a path exists, False otherwise
    """
    path = calculate_path(start, goal, width, height, obstacles)
    return len(path) > 0
