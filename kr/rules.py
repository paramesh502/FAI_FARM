"""
Rule-based reasoning engine for FAI-Farm.

Implements forward-chaining inference for disease diagnosis and
agricultural decision-making.
"""

from typing import List, Dict, Callable, Any, Set
from dataclasses import dataclass
from enum import Enum
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kr.ontology import DiseaseType, Plot, Crop


class RuleCondition(Enum):
    """Types of conditions in rules."""
    GREATER_THAN = ">"
    LESS_THAN = "<"
    EQUALS = "=="
    AND = "AND"
    OR = "OR"


@dataclass
class Rule:
    """
    Represents a production rule in the form IF conditions THEN actions.
    """
    id: str
    name: str
    conditions: List[Callable[[Dict], bool]]
    actions: List[Callable[[Dict], None]]
    priority: int = 50
    description: str = ""
    
    def evaluate(self, facts: Dict) -> bool:
        """
        Evaluate if all conditions are satisfied.
        
        Args:
            facts: Current facts/state
        
        Returns:
            True if all conditions satisfied
        """
        return all(condition(facts) for condition in self.conditions)
    
    def execute(self, facts: Dict):
        """
        Execute all actions.
        
        Args:
            facts: Current facts/state to modify
        """
        for action in self.actions:
            action(facts)


class RuleEngine:
    """
    Forward-chaining rule engine for agricultural reasoning.
    """
    
    def __init__(self):
        """Initialize the rule engine."""
        self.rules: List[Rule] = []
        self.facts: Dict[str, Any] = {}
        self.fired_rules: Set[str] = set()
        
        # Initialize disease diagnosis rules
        self._initialize_disease_rules()
        
        # Initialize agricultural management rules
        self._initialize_management_rules()
    
    def add_rule(self, rule: Rule):
        """Add a rule to the engine."""
        self.rules.append(rule)
        # Sort by priority (higher first)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    def add_fact(self, key: str, value: Any):
        """Add or update a fact."""
        self.facts[key] = value
    
    def get_fact(self, key: str, default=None):
        """Get a fact value."""
        return self.facts.get(key, default)
    
    def forward_chain(self, max_iterations: int = 100) -> List[str]:
        """
        Execute forward chaining inference.
        
        Args:
            max_iterations: Maximum inference cycles
        
        Returns:
            List of fired rule IDs
        """
        fired_this_cycle = []
        
        for _ in range(max_iterations):
            fired_any = False
            
            for rule in self.rules:
                # Skip already fired rules
                if rule.id in self.fired_rules:
                    continue
                
                # Check if conditions are met
                if rule.evaluate(self.facts):
                    # Execute actions
                    rule.execute(self.facts)
                    
                    # Mark as fired
                    self.fired_rules.add(rule.id)
                    fired_this_cycle.append(rule.id)
                    fired_any = True
            
            # Stop if no rules fired this cycle
            if not fired_any:
                break
        
        return fired_this_cycle
    
    def reset(self):
        """Reset the engine state."""
        self.facts = {}
        self.fired_rules = set()
    
    def _initialize_disease_rules(self):
        """Initialize disease diagnosis rules."""
        
        # Rule: Leaf Spot Detection
        leaf_spot_rule = Rule(
            id="disease_leaf_spot",
            name="Leaf Spot Disease Detection",
            description="IF humidity > 80% AND leaf_spots detected THEN diagnose leaf_spot disease",
            conditions=[
                lambda f: f.get('humidity', 0) > 80,
                lambda f: f.get('leaf_spots_detected', False)
            ],
            actions=[
                lambda f: f.update({'disease_diagnosed': DiseaseType.LEAF_SPOT}),
                lambda f: f.update({'treatment_required': True}),
                lambda f: f.update({'recommended_action': 'apply_fungicide'})
            ],
            priority=90
        )
        self.add_rule(leaf_spot_rule)
        
        # Rule: Powdery Mildew Detection
        mildew_rule = Rule(
            id="disease_powdery_mildew",
            name="Powdery Mildew Detection",
            description="IF temperature in range AND white_powder detected THEN diagnose powdery_mildew",
            conditions=[
                lambda f: 15 <= f.get('temperature', 0) <= 25,
                lambda f: f.get('white_powder_detected', False)
            ],
            actions=[
                lambda f: f.update({'disease_diagnosed': DiseaseType.POWDERY_MILDEW}),
                lambda f: f.update({'treatment_required': True}),
                lambda f: f.update({'recommended_action': 'apply_sulfur'})
            ],
            priority=90
        )
        self.add_rule(mildew_rule)
        
        # Rule: Root Rot Detection
        root_rot_rule = Rule(
            id="disease_root_rot",
            name="Root Rot Detection",
            description="IF water_level > 0.9 AND wilting detected THEN diagnose root_rot",
            conditions=[
                lambda f: f.get('water_level', 0) > 0.9,
                lambda f: f.get('wilting_detected', False)
            ],
            actions=[
                lambda f: f.update({'disease_diagnosed': DiseaseType.ROOT_ROT}),
                lambda f: f.update({'treatment_required': True}),
                lambda f: f.update({'recommended_action': 'reduce_watering'})
            ],
            priority=95
        )
        self.add_rule(root_rot_rule)
        
        # Rule: High Disease Risk
        high_risk_rule = Rule(
            id="disease_high_risk",
            name="High Disease Risk Alert",
            description="IF disease_probability > 0.7 THEN alert high_risk",
            conditions=[
                lambda f: f.get('disease_probability', 0) > 0.7
            ],
            actions=[
                lambda f: f.update({'disease_risk': 'high'}),
                lambda f: f.update({'alert_master_agent': True})
            ],
            priority=85
        )
        self.add_rule(high_risk_rule)
    
    def _initialize_management_rules(self):
        """Initialize agricultural management rules."""
        
        # Rule: Water Stress
        water_stress_rule = Rule(
            id="mgmt_water_stress",
            name="Water Stress Management",
            description="IF water_level < 0.3 AND crop_growing THEN schedule_watering",
            conditions=[
                lambda f: f.get('water_level', 1.0) < 0.3,
                lambda f: f.get('crop_growing', False)
            ],
            actions=[
                lambda f: f.update({'action_required': 'water'}),
                lambda f: f.update({'priority': 90})
            ],
            priority=80
        )
        self.add_rule(water_stress_rule)
        
        # Rule: Harvest Readiness
        harvest_rule = Rule(
            id="mgmt_harvest_ready",
            name="Harvest Readiness",
            description="IF growth_progress >= 100 THEN schedule_harvest",
            conditions=[
                lambda f: f.get('growth_progress', 0) >= 100
            ],
            actions=[
                lambda f: f.update({'action_required': 'harvest'}),
                lambda f: f.update({'priority': 80})
            ],
            priority=75
        )
        self.add_rule(harvest_rule)
        
        # Rule: Optimal Planting Conditions
        planting_rule = Rule(
            id="mgmt_optimal_planting",
            name="Optimal Planting Conditions",
            description="IF soil_ploughed AND temperature_optimal THEN recommend_planting",
            conditions=[
                lambda f: f.get('soil_ploughed', False),
                lambda f: 15 <= f.get('temperature', 0) <= 30
            ],
            actions=[
                lambda f: f.update({'action_required': 'sow'}),
                lambda f: f.update({'priority': 70})
            ],
            priority=70
        )
        self.add_rule(planting_rule)
        
        # Rule: Nutrient Deficiency
        nutrient_rule = Rule(
            id="mgmt_nutrient_deficiency",
            name="Nutrient Deficiency",
            description="IF nitrogen < 20 OR phosphorus < 15 THEN apply_fertilizer",
            conditions=[
                lambda f: f.get('nitrogen', 100) < 20 or f.get('phosphorus', 100) < 15
            ],
            actions=[
                lambda f: f.update({'action_required': 'fertilize'}),
                lambda f: f.update({'priority': 60})
            ],
            priority=65
        )
        self.add_rule(nutrient_rule)
    
    def diagnose_plot(self, plot: Plot, environmental_data: Dict) -> Dict:
        """
        Diagnose a plot's condition and recommend actions.
        
        Args:
            plot: Plot to diagnose
            environmental_data: Environmental conditions
        
        Returns:
            Diagnosis and recommendations
        """
        # Reset for new diagnosis
        self.reset()
        
        # Add plot facts
        self.add_fact('water_level', plot.soil_moisture)
        self.add_fact('soil_ploughed', plot.is_ploughed)
        
        if plot.current_crop:
            self.add_fact('crop_growing', True)
            self.add_fact('growth_progress', 
                         plot.current_crop.health_status * 100)
        
        # Add environmental facts
        for key, value in environmental_data.items():
            self.add_fact(key, value)
        
        # Run inference
        fired_rules = self.forward_chain()
        
        # Extract recommendations
        return {
            'fired_rules': fired_rules,
            'action_required': self.get_fact('action_required'),
            'priority': self.get_fact('priority', 50),
            'disease_diagnosed': self.get_fact('disease_diagnosed'),
            'treatment_required': self.get_fact('treatment_required', False),
            'recommended_action': self.get_fact('recommended_action'),
            'disease_risk': self.get_fact('disease_risk', 'low')
        }
    
    def export_rules(self, filename: str):
        """Export all rules to a file."""
        with open(filename, 'w') as f:
            f.write("# FAI-Farm Rule Base\n\n")
            
            for rule in self.rules:
                f.write(f"## Rule: {rule.name}\n")
                f.write(f"ID: {rule.id}\n")
                f.write(f"Priority: {rule.priority}\n")
                f.write(f"Description: {rule.description}\n")
                f.write("\n")
