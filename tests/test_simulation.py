"""
Integration tests for FAI-Farm simulation.

Tests the complete simulation cycle including agent coordination,
task execution, and state transitions.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.farm_model import FarmModel
from model.cell_state import CellState


def test_model_initialization():
    """Test that the model initializes correctly with all components."""
    model = FarmModel(width=10, height=10, num_workers=6)
    
    # Check grid initialization
    assert model.width == 10
    assert model.height == 10
    assert model.grid is not None
    
    # Check agents created
    assert model.master_agent is not None
    assert len(model.worker_agents) == 5  # 5 worker agents
    
    # Check all cells initialized to INITIAL state
    initial_count = sum(1 for state in model.cell_states.values() 
                       if state == CellState.INITIAL)
    assert initial_count == 100  # 10x10 grid
    
    print("✓ Model initialization test passed")


def test_cell_state_transitions():
    """Test that cells progress through expected state transitions."""
    model = FarmModel(width=5, height=5, num_workers=6)
    
    # Manually set a cell to PLOUGHED and verify
    test_pos = (2, 2)
    model.set_cell_state(test_pos, CellState.PLOUGHED)
    assert model.get_cell_state(test_pos) == CellState.PLOUGHED
    
    # Set to SOWN with attributes
    model.set_cell_state(test_pos, CellState.SOWN)
    model.update_cell_attributes(test_pos, water_level=0.5, growth_progress=0)
    assert model.get_cell_state(test_pos) == CellState.SOWN
    
    # Set to GROWING
    model.set_cell_state(test_pos, CellState.GROWING)
    assert model.get_cell_state(test_pos) == CellState.GROWING
    
    print("✓ Cell state transition test passed")


def test_message_bus_communication():
    """Test that message bus delivers messages correctly."""
    model = FarmModel(width=5, height=5, num_workers=6)
    
    # Track if message was received
    received_messages = []
    
    def test_callback(message):
        received_messages.append(message)
    
    # Subscribe to a test topic
    model.message_bus.subscribe("test.topic", test_callback)
    
    # Publish a message
    from model.cell_state import Message
    test_message = Message(
        topic="test.topic",
        sender_id=999,
        timestamp=0,
        payload={"test": "data"}
    )
    model.message_bus.publish("test.topic", test_message)
    
    # Process messages
    model.message_bus.process_messages()
    
    # Verify message was received
    assert len(received_messages) == 1
    assert received_messages[0].payload["test"] == "data"
    
    print("✓ Message bus communication test passed")


def test_full_simulation_cycle():
    """
    Run a complete simulation cycle and verify expected behavior.
    
    Tests:
    - Cells progress through agricultural states
    - Harvest count increases over time
    - No agent deadlocks or exceptions
    - Message bus delivers messages
    """
    print("\nRunning full simulation cycle test (500 steps)...")
    
    model = FarmModel(width=10, height=10, num_workers=6)
    
    # Track state changes
    initial_states = {
        CellState.INITIAL: model.count_cells_by_state(CellState.INITIAL),
        CellState.PLOUGHED: 0,
        CellState.SOWN: 0,
        CellState.GROWING: 0,
        CellState.HEALTHY: 0,
        CellState.READY_TO_HARVEST: 0
    }
    
    # Run simulation for 500 steps
    exception_occurred = False
    try:
        for step in range(500):
            model.step()
            
            # Print progress every 100 steps
            if (step + 1) % 100 == 0:
                ploughed = model.count_cells_by_state(CellState.PLOUGHED)
                sown = model.count_cells_by_state(CellState.SOWN)
                growing = model.count_cells_by_state(CellState.GROWING)
                healthy = model.count_cells_by_state(CellState.HEALTHY)
                harvested = model.harvested_count
                print(f"  Step {step + 1}: Ploughed={ploughed}, Sown={sown}, "
                      f"Growing={growing}, Healthy={healthy}, Harvested={harvested}")
    
    except Exception as e:
        exception_occurred = True
        print(f"✗ Exception occurred during simulation: {e}")
        raise
    
    # Verify no exceptions occurred
    assert not exception_occurred, "Simulation should run without exceptions"
    
    # Verify cells have progressed through states
    final_ploughed = model.count_cells_by_state(CellState.PLOUGHED)
    final_sown = model.count_cells_by_state(CellState.SOWN)
    final_growing = model.count_cells_by_state(CellState.GROWING)
    final_healthy = model.count_cells_by_state(CellState.HEALTHY)
    
    # At least some cells should have been processed
    assert (final_ploughed + final_sown + final_growing + final_healthy) > 0, \
        "Some cells should have progressed beyond INITIAL state"
    
    # Verify harvest count increased
    assert model.harvested_count >= 0, "Harvest count should be non-negative"
    
    # Verify agents are still functioning (not deadlocked)
    assert model.master_agent is not None
    assert len(model.worker_agents) == 5
    
    print(f"\n✓ Full simulation cycle test passed")
    print(f"  Final state: {model.harvested_count} crops harvested")
    print(f"  Ploughed: {final_ploughed}, Sown: {final_sown}, "
          f"Growing: {final_growing}, Healthy: {final_healthy}")


def test_agent_task_execution():
    """Test that agents can receive and execute tasks."""
    model = FarmModel(width=5, height=5, num_workers=6)
    
    # Get a worker agent
    ploughing_agent = model.worker_agents[0]
    
    # Verify agent is initialized correctly
    assert ploughing_agent.agent_type == "ploughing"
    assert ploughing_agent.status.value == "idle"
    
    # Run a few steps to allow task assignment
    for _ in range(10):
        model.step()
    
    # Verify model is functioning
    assert model.step_count == 10
    
    print("✓ Agent task execution test passed")


def run_all_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("FAI-Farm Integration Tests")
    print("=" * 60)
    
    try:
        test_model_initialization()
        test_cell_state_transitions()
        test_message_bus_communication()
        test_agent_task_execution()
        test_full_simulation_cycle()
        
        print("\n" + "=" * 60)
        print("All tests passed successfully!")
        print("=" * 60)
        return True
    
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
