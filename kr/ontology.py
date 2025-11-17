"""
Farm Ontology for FAI-Farm.

Defines the conceptual model of the farm domain including crops, plots,
resources, and their relationships.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple
from enum import Enum


class CropType(Enum):
    """Types of crops that can be grown."""
    WHEAT = "wheat"
    CORN = "corn"
    RICE = "rice"
    SOYBEAN = "soybean"
    TOMATO = "tomato"


class SoilType(Enum):
    """Types of soil."""
    CLAY = "clay"
    SANDY = "sandy"
    LOAM = "loam"
    SILT = "silt"


class GrowthStage(Enum):
    """Crop growth stages."""
    SEED = "seed"
    GERMINATION = "germination"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUITING = "fruiting"
    MATURATION = "maturation"
    HARVEST_READY = "harvest_ready"


class DiseaseType(Enum):
    """Types of crop diseases."""
    LEAF_SPOT = "leaf_spot"
    POWDERY_MILDEW = "powdery_mildew"
    ROOT_ROT = "root_rot"
    BLIGHT = "blight"
    RUST = "rust"


@dataclass
class Crop:
    """
    Represents a crop with its properties and requirements.
    """
    type: CropType
    name: str
    growth_duration: int  # days to maturity
    water_requirement: float  # liters per day
    optimal_temperature: Tuple[float, float]  # (min, max) in Celsius
    suitable_soil_types: List[SoilType]
    growth_stage: GrowthStage = GrowthStage.SEED
    health_status: float = 1.0  # 0.0 to 1.0
    diseases: Set[DiseaseType] = field(default_factory=set)
    
    def is_suitable_for_soil(self, soil_type: SoilType) -> bool:
        """Check if crop can grow in given soil type."""
        return soil_type in self.suitable_soil_types
    
    def advance_growth_stage(self):
        """Advance to next growth stage."""
        stages = list(GrowthStage)
        current_index = stages.index(self.growth_stage)
        if current_index < len(stages) - 1:
            self.growth_stage = stages[current_index + 1]
    
    def is_harvest_ready(self) -> bool:
        """Check if crop is ready for harvest."""
        return self.growth_stage == GrowthStage.HARVEST_READY


@dataclass
class Plot:
    """
    Represents a farm plot with its properties.
    """
    id: str
    position: Tuple[int, int]
    area: float  # square meters
    soil_type: SoilType
    soil_moisture: float  # 0.0 to 1.0
    soil_nutrients: Dict[str, float]  # N, P, K levels
    current_crop: Optional[Crop] = None
    is_ploughed: bool = False
    last_watered: int = 0
    
    def can_plant(self, crop: Crop) -> bool:
        """Check if a crop can be planted in this plot."""
        return (
            self.is_ploughed and
            self.current_crop is None and
            crop.is_suitable_for_soil(self.soil_type)
        )
    
    def plant_crop(self, crop: Crop) -> bool:
        """Plant a crop in this plot."""
        if self.can_plant(crop):
            self.current_crop = crop
            return True
        return False
    
    def harvest_crop(self) -> Optional[Crop]:
        """Harvest the current crop."""
        if self.current_crop and self.current_crop.is_harvest_ready():
            crop = self.current_crop
            self.current_crop = None
            self.is_ploughed = False
            return crop
        return None


@dataclass
class Resource:
    """
    Represents a farm resource.
    """
    name: str
    type: str  # water, fuel, fertilizer, etc.
    quantity: float
    unit: str
    cost_per_unit: float
    
    def consume(self, amount: float) -> bool:
        """Consume resource."""
        if self.quantity >= amount:
            self.quantity -= amount
            return True
        return False
    
    def replenish(self, amount: float):
        """Add resource."""
        self.quantity += amount


@dataclass
class Equipment:
    """
    Represents farm equipment.
    """
    name: str
    type: str  # tractor, plough, sprayer, etc.
    fuel_consumption: float  # per hour
    maintenance_cost: float
    is_available: bool = True
    current_location: Optional[Tuple[int, int]] = None


class FarmOntology:
    """
    Complete farm ontology managing all domain concepts and relationships.
    """
    
    def __init__(self):
        """Initialize the farm ontology."""
        self.crops: Dict[str, Crop] = {}
        self.plots: Dict[str, Plot] = {}
        self.resources: Dict[str, Resource] = {}
        self.equipment: Dict[str, Equipment] = {}
        
        # Define crop knowledge base
        self._initialize_crop_knowledge()
    
    def _initialize_crop_knowledge(self):
        """Initialize crop knowledge base with standard crops."""
        # Wheat
        wheat = Crop(
            type=CropType.WHEAT,
            name="Winter Wheat",
            growth_duration=120,
            water_requirement=25.0,
            optimal_temperature=(15.0, 25.0),
            suitable_soil_types=[SoilType.LOAM, SoilType.CLAY]
        )
        self.crops["wheat"] = wheat
        
        # Corn
        corn = Crop(
            type=CropType.CORN,
            name="Sweet Corn",
            growth_duration=90,
            water_requirement=30.0,
            optimal_temperature=(20.0, 30.0),
            suitable_soil_types=[SoilType.LOAM, SoilType.SANDY]
        )
        self.crops["corn"] = corn
        
        # Rice
        rice = Crop(
            type=CropType.RICE,
            name="Paddy Rice",
            growth_duration=150,
            water_requirement=50.0,
            optimal_temperature=(25.0, 35.0),
            suitable_soil_types=[SoilType.CLAY, SoilType.SILT]
        )
        self.crops["rice"] = rice
    
    def add_plot(self, plot: Plot):
        """Add a plot to the ontology."""
        self.plots[plot.id] = plot
    
    def add_resource(self, resource: Resource):
        """Add a resource to the ontology."""
        self.resources[resource.name] = resource
    
    def add_equipment(self, equipment: Equipment):
        """Add equipment to the ontology."""
        self.equipment[equipment.name] = equipment
    
    def get_suitable_crops_for_plot(self, plot_id: str) -> List[Crop]:
        """Get list of crops suitable for a given plot."""
        if plot_id not in self.plots:
            return []
        
        plot = self.plots[plot_id]
        suitable = []
        
        for crop in self.crops.values():
            if crop.is_suitable_for_soil(plot.soil_type):
                suitable.append(crop)
        
        return suitable
    
    def get_plots_with_crop(self, crop_type: CropType) -> List[Plot]:
        """Get all plots growing a specific crop type."""
        return [
            plot for plot in self.plots.values()
            if plot.current_crop and plot.current_crop.type == crop_type
        ]
    
    def get_plots_needing_water(self, threshold: float = 0.3) -> List[Plot]:
        """Get plots with low soil moisture."""
        return [
            plot for plot in self.plots.values()
            if plot.soil_moisture < threshold and plot.current_crop is not None
        ]
    
    def get_plots_ready_for_harvest(self) -> List[Plot]:
        """Get plots with crops ready for harvest."""
        return [
            plot for plot in self.plots.values()
            if plot.current_crop and plot.current_crop.is_harvest_ready()
        ]
    
    def calculate_water_demand(self) -> float:
        """Calculate total water demand for all crops."""
        total = 0.0
        for plot in self.plots.values():
            if plot.current_crop:
                total += plot.current_crop.water_requirement * plot.area
        return total
    
    def export_ontology(self, filename: str):
        """Export ontology to a file."""
        with open(filename, 'w') as f:
            f.write("# FAI-Farm Ontology\n\n")
            
            f.write("## Crops\n")
            for crop in self.crops.values():
                f.write(f"- {crop.name} ({crop.type.value})\n")
                f.write(f"  Duration: {crop.growth_duration} days\n")
                f.write(f"  Water: {crop.water_requirement} L/day\n")
            
            f.write("\n## Plots\n")
            for plot in self.plots.values():
                f.write(f"- {plot.id} at {plot.position}\n")
                f.write(f"  Soil: {plot.soil_type.value}\n")
                if plot.current_crop:
                    f.write(f"  Crop: {plot.current_crop.name}\n")
            
            f.write("\n## Resources\n")
            for resource in self.resources.values():
                f.write(f"- {resource.name}: {resource.quantity} {resource.unit}\n")
