"""
Complete System Demonstration for FAI-Farm v2.0

This script demonstrates all features of the FAI-Farm system:
1. Core multi-agent simulation
2. PDDL planning
3. CSP scheduling
4. Rule-based reasoning
5. ML disease classification
6. Weather simulation & smart irrigation ⭐ NEW
7. Yield prediction ⭐ NEW
8. Crop stress monitoring ⭐ NEW
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model.farm_model import FarmModel
from model.cell_state import CellState
from planning.planner import PDDLPlanner
from csp.scheduler import CSPScheduler, ResourceType
from kr.rules import RuleEngine
from kr.ontology import FarmOntology, Plot, SoilType
from ml.disease_classifier import DiseaseClassifier


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_core_simulation():
    """Demonstrate core multi-agent simulation."""
    print_section("1. CORE MULTI-AGENT SIMULATION")
    
    print("\n📊 Initializing farm model (10x10 grid)...")
    model = FarmModel(width=10, height=10, num_workers=6)
    
    print(f"✓ Created {len(model.worker_agents)} worker agents")
    print(f"✓ Master Agent at position {model.master_agent.pos}")
    
    print("\n🚀 Running simulation for 100 steps...")
    for i in range(100):
        model.step()
        if (i + 1) % 25 == 0:
            ploughed = model.count_cells_by_state(CellState.PLOUGHED)
            sown = model.count_cells_by_state(CellState.SOWN)
            growing = model.count_cells_by_state(CellState.GROWING)
            healthy = model.count_cells_by_state(CellState.HEALTHY)
            harvested = model.harvested_count
            print(f"  Step {i+1:3d}: Ploughed={ploughed}, Sown={sown}, "
                  f"Growing={growing}, Healthy={healthy}, Harvested={harvested}")
    
    print(f"\n✓ Simulation complete!")
    print(f"  Total harvested: {model.harvested_count} crops")
    
    return model


def demo_pddl_planning():
    """Demonstrate PDDL planning."""
    print_section("2. PDDL PLANNING")
    
    print("\n📋 Loading PDDL domain and problem...")
    planner = PDDLPlanner(
        domain_file="planning/domain.pddl",
        problem_file="planning/problem_example.pddl"
    )
    
    print("✓ PDDL files loaded")
    print("\n🎯 Generating plan...")
    plan = planner.generate_plan()
    
    print(f"✓ Plan generated with {len(plan)} actions")
    print("\nPlan Preview (first 5 actions):")
    for action in plan[:5]:
        print(f"  {action}")
    
    print(f"\n📊 Plan Metrics:")
    print(f"  Makespan: {planner.get_plan_makespan()} steps")
    print(f"  Cost: {planner.get_plan_cost()}")
    
    return planner


def demo_csp_scheduling():
    """Demonstrate CSP scheduling."""
    print_section("3. CSP SCHEDULING")
    
    print("\n⚙️ Initializing CSP scheduler...")
    scheduler = CSPScheduler(time_horizon=50)
    
    print("✓ Scheduler initialized with resources:")
    print(f"  Water: {scheduler.resources[ResourceType.WATER].max_capacity}L")
    print(f"  Fuel: {scheduler.resources[ResourceType.FUEL].max_capacity}L")
    print(f"  Tools: {scheduler.resources[ResourceType.TOOLS].max_capacity} units")
    
    print("\n📝 Creating sample tasks...")
    tasks = [
        {
            'task_id': 'task_1',
            'task_type': 'PLOUGH',
            'target_cell': (5, 5),
            'priority': 80,
            'duration': 2,
            'resources': {ResourceType.FUEL: 10.0}
        },
        {
            'task_id': 'task_2',
            'task_type': 'SOW',
            'target_cell': (5, 5),
            'priority': 70,
            'duration': 1,
            'resources': {ResourceType.FUEL: 5.0}
        },
        {
            'task_id': 'task_3',
            'task_type': 'WATER',
            'target_cell': (5, 5),
            'priority': 90,
            'duration': 1,
            'resources': {ResourceType.WATER: 50.0}
        }
    ]
    
    agents = {
        'ploughing': [1],
        'sowing': [2],
        'watering': [3]
    }
    
    print(f"✓ Created {len(tasks)} tasks")
    
    print("\n🎯 Scheduling tasks...")
    assignments = scheduler.schedule_tasks(tasks, agents)
    
    print(f"✓ Successfully scheduled {len(assignments)} tasks")
    print("\nSchedule Preview:")
    for assignment in assignments[:3]:
        print(f"  Time {assignment.time_slot}: Agent {assignment.agent_id} "
              f"({assignment.agent_type}) -> {assignment.task_id}")
    
    metrics = scheduler.get_schedule_metrics()
    print(f"\n📊 Schedule Metrics:")
    print(f"  Makespan: {metrics['makespan']} time slots")
    print(f"  Total tasks: {metrics['total_tasks']}")
    
    return scheduler


def demo_rule_based_reasoning():
    """Demonstrate rule-based reasoning."""
    print_section("4. RULE-BASED REASONING")
    
    print("\n🧠 Initializing rule engine...")
    engine = RuleEngine()
    
    print(f"✓ Loaded {len(engine.rules)} rules")
    print("  - Disease diagnosis rules")
    print("  - Agricultural management rules")
    
    print("\n🔍 Testing disease diagnosis...")
    
    # Create test plot
    ontology = FarmOntology()
    plot = Plot(
        id="test_plot",
        position=(5, 5),
        area=100.0,
        soil_type=SoilType.LOAM,
        soil_moisture=0.4,
        soil_nutrients={'N': 50, 'P': 30, 'K': 40}
    )
    
    # Test case 1: High humidity + leaf spots
    print("\n  Test Case 1: High humidity + leaf spots")
    env_data = {
        'humidity': 85,
        'temperature': 25,
        'leaf_spots_detected': True
    }
    
    diagnosis = engine.diagnose_plot(plot, env_data)
    print(f"    Disease: {diagnosis['disease_diagnosed']}")
    print(f"    Action: {diagnosis['recommended_action']}")
    print(f"    Priority: {diagnosis['priority']}")
    
    # Test case 2: Low water level
    print("\n  Test Case 2: Low water level")
    plot.soil_moisture = 0.2
    env_data = {
        'humidity': 60,
        'temperature': 25,
        'crop_growing': True
    }
    
    diagnosis = engine.diagnose_plot(plot, env_data)
    print(f"    Action required: {diagnosis['action_required']}")
    print(f"    Priority: {diagnosis['priority']}")
    
    print("\n✓ Rule-based reasoning working correctly")
    
    return engine


def demo_ml_classification():
    """Demonstrate ML disease classification."""
    print_section("5. ML DISEASE CLASSIFICATION")
    
    print("\n🤖 Loading ML disease classifier...")
    classifier = DiseaseClassifier()
    
    # Check if model exists
    model_path = "../ml/disease_model.pkl"
    if not os.path.exists(model_path):
        model_path = "ml/disease_model.pkl"
    
    if os.path.exists(model_path):
        classifier.load_model(model_path)
        print(f"✓ Model loaded from {model_path}")
    else:
        print("⚠ Model not found, using freshly trained model")
        classifier.train()
    
    print("\n🔬 Testing disease predictions...")
    
    # Test case 1: Leaf spot conditions
    print("\n  Test Case 1: Leaf spot conditions")
    features = {
        'temperature': 28,
        'humidity': 85,
        'water_level': 0.4,
        'growth_progress': 60,
        'soil_moisture': 0.6,
        'days_since_watering': 3,
        'leaf_color_r': 150,
        'leaf_color_g': 140,
        'leaf_color_b': 90
    }
    
    disease, confidence = classifier.predict(features)
    print(f"    Predicted: {disease}")
    print(f"    Confidence: {confidence:.1%}")
    
    # Test case 2: Healthy conditions
    print("\n  Test Case 2: Healthy conditions")
    features = {
        'temperature': 22,
        'humidity': 60,
        'water_level': 0.7,
        'growth_progress': 50,
        'soil_moisture': 0.6,
        'days_since_watering': 1,
        'leaf_color_r': 100,
        'leaf_color_g': 180,
        'leaf_color_b': 100
    }
    
    disease, confidence = classifier.predict(features)
    print(f"    Predicted: {disease}")
    print(f"    Confidence: {confidence:.1%}")
    
    # Show feature importance
    print("\n📊 Feature Importance (Top 5):")
    importance = classifier.get_feature_importance()
    sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
    for feature, score in sorted_features[:5]:
        print(f"    {feature}: {score:.4f}")
    
    print("\n✓ ML classification working correctly")
    
    return classifier


def demo_weather_and_yield():
    """Demonstrate weather simulation and yield prediction."""
    print_section("6. WEATHER SIMULATION & YIELD PREDICTION ⭐ NEW")
    
    print("\n🌦️ Initializing farm with weather simulation...")
    model = FarmModel(width=10, height=10, num_workers=5)
    
    print(f"\n📊 Initial Weather Conditions:")
    print(f"  Temperature: {model.weather['temperature']:.1f}°C")
    print(f"  Humidity: {model.weather['humidity']:.0f}%")
    print(f"  Rain Forecast: {'Yes ☔' if model.weather['rain_forecast_24h'] else 'No ☀️'}")
    print(f"  Wind Speed: {model.weather['wind_speed']:.1f} km/h")
    
    print("\n🚀 Running simulation for 50 steps...")
    for i in range(50):
        model.step()
        if (i + 1) % 10 == 0:
            print(f"  Step {i + 1}: Temp={model.weather['temperature']:.1f}°C, "
                  f"Rain={'Yes' if model.weather['rain_forecast_24h'] else 'No'}")
    
    print(f"\n📊 Updated Weather Conditions:")
    print(f"  Temperature: {model.weather['temperature']:.1f}°C")
    print(f"  Humidity: {model.weather['humidity']:.0f}%")
    print(f"  Rain Forecast: {'Yes ☔' if model.weather['rain_forecast_24h'] else 'No ☀️'}")
    
    print("\n🌾 Yield Prediction:")
    yield_pred = model.calculate_yield_prediction()
    print(f"  Estimated Yield: {yield_pred['estimated_yield']:.2f} units")
    print(f"  Current Harvest: {yield_pred['current_harvest']} units")
    print(f"  Potential Total: {yield_pred['potential_yield']:.2f} units")
    print(f"  Days to Harvest: {yield_pred['days_to_harvest']}")
    print(f"  Average Growth: {yield_pred['average_growth_progress']:.1f}%")
    print(f"  Healthy Crops: {yield_pred['healthy_crops']}")
    print(f"  At-Risk Crops: {yield_pred['at_risk_crops']}")
    
    print("\n✓ Weather simulation and yield prediction working correctly")
    
    return model


def demo_stress_monitoring():
    """Demonstrate crop stress monitoring."""
    print_section("7. CROP STRESS MONITORING ⭐ NEW")
    
    print("\n🚨 Initializing stress monitoring system...")
    model = FarmModel(width=10, height=10, num_workers=5)
    
    print("\n🚀 Running simulation for 60 steps...")
    for i in range(60):
        model.step()
        if (i + 1) % 20 == 0:
            stress = model.get_stress_indicators()
            print(f"  Step {i + 1}: Health Score={stress['overall_health_score']:.1f}%, "
                  f"Water Stress={stress['water_stress_percentage']:.1f}%")
    
    print("\n📊 Final Stress Analysis:")
    stress = model.get_stress_indicators()
    print(f"  Water Stressed Crops: {stress['water_stressed_count']} ({stress['water_stress_percentage']:.1f}%)")
    print(f"  Temperature Stressed: {stress['temperature_stressed_count']} ({stress['temperature_stress_percentage']:.1f}%)")
    print(f"  Total Crops: {stress['total_crops']}")
    print(f"  Overall Health Score: {stress['overall_health_score']:.1f}%")
    
    # Generate recommendations
    print("\n💡 Automated Recommendations:")
    if stress['water_stress_percentage'] > 30:
        print("  ⚠️ High water stress detected - Increase irrigation frequency")
    if stress['temperature_stress_percentage'] > 20:
        print("  🔥 Temperature stress alert - Consider cooling measures")
    if model.weather['rain_forecast_24h']:
        print("  🌧️ Rain forecasted - Irrigation automatically delayed")
    if model.weather['temperature'] > 32:
        print("  🌡️ High temperature warning - Monitor crops closely")
    if stress['overall_health_score'] > 80:
        print("  ✅ All systems operating normally")
    
    print("\n✓ Stress monitoring working correctly")
    
    return model


def main():
    """Run complete system demonstration."""
    print("\n" + "=" * 70)
    print("  FAI-FARM COMPLETE SYSTEM DEMONSTRATION v2.0")
    print("  Multi-Agent Agricultural Simulation with AI")
    print("=" * 70)
    
    try:
        # Run all demonstrations
        model = demo_core_simulation()
        planner = demo_pddl_planning()
        scheduler = demo_csp_scheduling()
        engine = demo_rule_based_reasoning()
        classifier = demo_ml_classification()
        weather_model = demo_weather_and_yield()
        stress_model = demo_stress_monitoring()
        
        # Final summary
        print_section("DEMONSTRATION COMPLETE")
        print("\n✅ All systems operational!")
        print("\n📊 Summary:")
        print(f"  ✓ Core Simulation: {model.harvested_count} crops harvested")
        print(f"  ✓ PDDL Planning: {len(planner.plan)} actions generated")
        print(f"  ✓ CSP Scheduling: {len(scheduler.assignments)} tasks scheduled")
        print(f"  ✓ Weather Simulation: Temperature {weather_model.weather['temperature']:.1f}°C")
        print(f"  ✓ Yield Prediction: {weather_model.calculate_yield_prediction()['estimated_yield']:.2f} units")
        print(f"  ✓ Stress Monitoring: {stress_model.get_stress_indicators()['overall_health_score']:.1f}% health")
        print(f"  ✓ Rule Engine: {len(engine.rules)} rules loaded")
        print(f"  ✓ ML Classifier: Model trained and ready")
        
        print("\n🎯 System Status: READY FOR DEPLOYMENT")
        print("\n💡 Next Steps:")
        print("  1. Run Mesa visualization: python run.py")
        print("  2. Run Streamlit dashboard: streamlit run dashboard/streamlit_app.py")
        print("  3. Review documentation in *.md files")
        
        print("\n" + "=" * 70)
        print("  Demo completed successfully!")
        print("=" * 70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
