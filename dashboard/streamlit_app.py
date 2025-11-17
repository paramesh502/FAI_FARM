"""
Streamlit Dashboard for FAI-Farm Multi-Agent System

Provides an interactive web dashboard for monitoring and controlling
the farm simulation with real-time metrics and visualizations.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.farm_model import FarmModel
from model.cell_state import CellState


# Page configuration
st.set_page_config(
    page_title="FAI-Farm Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional color scheme
COLORS = {
    'primary': '#2E7D32',
    'secondary': '#1B5E20',
    'accent': '#4CAF50',
    'warning': '#F57C00',
    'danger': '#C62828',
    'neutral': '#757575',
    'background': '#FAFAFA',
    'card': '#FFFFFF'
}

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: 600;
        color: #1B5E20;
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 1rem;
        border-bottom: 3px solid #2E7D32;
        letter-spacing: 1px;
    }
    .subtitle {
        font-size: 1rem;
        color: #757575;
        text-align: center;
        margin-top: -1rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #E0E0E0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2E7D32;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #E0E0E0;
    }
    .status-good {
        color: #2E7D32;
        font-weight: 600;
    }
    .status-warning {
        color: #F57C00;
        font-weight: 600;
    }
    .status-critical {
        color: #C62828;
        font-weight: 600;
    }
    .info-box {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #4CAF50;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.3s;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'model' not in st.session_state:
        st.session_state.model = None
    if 'running' not in st.session_state:
        st.session_state.running = False
    if 'step_count' not in st.session_state:
        st.session_state.step_count = 0
    if 'metrics_history' not in st.session_state:
        st.session_state.metrics_history = []


def create_model(width, height):
    """Create a new farm model."""
    return FarmModel(width=width, height=height, num_workers=6)


def get_current_metrics(model):
    """Extract current metrics from the model."""
    return {
        'step': model.step_count,
        'ploughed': model.count_cells_by_state(CellState.PLOUGHED),
        'sown': model.count_cells_by_state(CellState.SOWN),
        'growing': model.count_cells_by_state(CellState.GROWING),
        'healthy': model.count_cells_by_state(CellState.HEALTHY),
        'diseased': model.count_cells_by_state(CellState.DISEASED),
        'ready': model.count_cells_by_state(CellState.READY_TO_HARVEST),
        'harvested': model.harvested_count
    }


def create_farm_grid_plot(model):
    """Create a heatmap visualization of the farm grid."""
    # Create state matrix
    state_matrix = []
    for y in range(model.height):
        row = []
        for x in range(model.width):
            state = model.get_cell_state((x, y))
            row.append(state.value)
        state_matrix.append(row)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=state_matrix,
        colorscale=[
            [0, '#E8E8E8'],  # INITIAL
            [0.14, '#8B4513'],  # PLOUGHED
            [0.28, '#D2B48C'],  # SOWN
            [0.42, '#90EE90'],  # GROWING
            [0.57, '#FFD700'],  # NEED_WATER
            [0.71, '#228B22'],  # HEALTHY
            [0.85, '#DC143C'],  # DISEASED
            [1, '#FFA500']   # READY_TO_HARVEST
        ],
        showscale=False,
        hovertemplate='X: %{x}<br>Y: %{y}<br>State: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Farm Grid State",
        xaxis_title="X Coordinate",
        yaxis_title="Y Coordinate",
        height=500,
        yaxis=dict(autorange='reversed')
    )
    
    return fig


def create_metrics_chart(metrics_history):
    """Create time-series chart of key metrics."""
    if not metrics_history:
        return None
    
    df = pd.DataFrame(metrics_history)
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Cell States Over Time', 'Crop Health', 
                       'Harvest Progress', 'Disease Incidents')
    )
    
    # Cell states
    fig.add_trace(
        go.Scatter(x=df['step'], y=df['ploughed'], name='Ploughed', 
                  line=dict(color='#8B4513')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df['step'], y=df['sown'], name='Sown',
                  line=dict(color='#D2B48C')),
        row=1, col=1
    )
    
    # Crop health
    fig.add_trace(
        go.Scatter(x=df['step'], y=df['growing'], name='Growing',
                  line=dict(color='#90EE90')),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=df['step'], y=df['healthy'], name='Healthy',
                  line=dict(color='#228B22')),
        row=1, col=2
    )
    
    # Harvest progress
    fig.add_trace(
        go.Scatter(x=df['step'], y=df['harvested'], name='Harvested',
                  line=dict(color='#FFA500'), fill='tozeroy'),
        row=2, col=1
    )
    
    # Disease incidents
    fig.add_trace(
        go.Scatter(x=df['step'], y=df['diseased'], name='Diseased',
                  line=dict(color='#DC143C'), fill='tozeroy'),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=True)
    fig.update_xaxes(title_text="Simulation Step")
    fig.update_yaxes(title_text="Count")
    
    return fig


def create_agent_status_table(model):
    """Create a table showing agent statuses."""
    agent_data = []
    
    # Master agent
    agent_data.append({
        'Agent': 'Master Agent',
        'Type': 'Coordinator',
        'Position': f"{model.master_agent.pos}",
        'Status': 'Active',
        'Tasks Assigned': len(model.master_agent.assigned_tasks)
    })
    
    # Worker agents
    for agent in model.worker_agents:
        agent_data.append({
            'Agent': f'{agent.agent_type.title()} Agent',
            'Type': agent.agent_type,
            'Position': f"{agent.pos}",
            'Status': agent.status.value,
            'Current Task': agent.current_task.task_id if agent.current_task else 'None'
        })
    
    return pd.DataFrame(agent_data)


def main():
    """Main Streamlit application."""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">FAI-FARM MULTI-AGENT SYSTEM</div>', 
                unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Advanced Agricultural Simulation & Monitoring Platform</div>', 
                unsafe_allow_html=True)
    
    # Sidebar controls
    with st.sidebar:
        st.header("SIMULATION CONTROLS")
        
        # Model configuration
        st.subheader("Configuration")
        grid_width = st.slider("Grid Width", 10, 50, 20)
        grid_height = st.slider("Grid Height", 10, 50, 20)
        
        # Initialize/Reset button
        if st.button("Initialize / Reset Simulation", use_container_width=True, type="primary"):
            st.session_state.model = create_model(grid_width, grid_height)
            st.session_state.step_count = 0
            st.session_state.metrics_history = []
            st.session_state.running = False
            st.success("Simulation initialized successfully")
        
        st.markdown("---")
        
        # Simulation controls
        st.subheader("Execution Controls")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Start", use_container_width=True):
                if st.session_state.model:
                    st.session_state.running = True
                else:
                    st.error("Please initialize simulation first")
        
        with col2:
            if st.button("Pause", use_container_width=True):
                st.session_state.running = False
        
        if st.button("Step Forward", use_container_width=True):
            if st.session_state.model:
                st.session_state.model.step()
                st.session_state.step_count += 1
                metrics = get_current_metrics(st.session_state.model)
                st.session_state.metrics_history.append(metrics)
                st.rerun()
        
        steps_to_run = st.number_input("Steps to Execute", 1, 1000, 10)
        if st.button(f"Run {steps_to_run} Steps", use_container_width=True):
            if st.session_state.model:
                progress_bar = st.progress(0)
                for i in range(steps_to_run):
                    st.session_state.model.step()
                    st.session_state.step_count += 1
                    metrics = get_current_metrics(st.session_state.model)
                    st.session_state.metrics_history.append(metrics)
                    progress_bar.progress((i + 1) / steps_to_run)
                st.success(f"Completed {steps_to_run} steps")
                st.rerun()
        
        st.markdown("---")
        
        # Information
        st.subheader("System Information")
        if st.session_state.model:
            st.metric("Current Step", st.session_state.step_count)
            st.metric("Grid Size", f"{grid_width} × {grid_height}")
            st.metric("Total Cells", grid_width * grid_height)
        
        st.markdown("---")
        st.caption("FAI-Farm Multi-Agent System v2.0")
    
    # Main content
    if st.session_state.model is None:
        st.info("Initialize the simulation using the sidebar controls to begin")
        
        # Show feature overview
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="section-header">Multi-Agent System</div>', unsafe_allow_html=True)
            st.write("Master Agent coordination")
            st.write("5 specialized worker agents")
            st.write("Autonomous task execution")
            st.write("Message-based communication")
        
        with col2:
            st.markdown('<div class="section-header">AI Features</div>', unsafe_allow_html=True)
            st.write("PDDL planning engine")
            st.write("CSP-based scheduling")
            st.write("Rule-based reasoning")
            st.write("Machine learning classifier")
        
        with col3:
            st.markdown('<div class="section-header">Real-Time Monitoring</div>', unsafe_allow_html=True)
            st.write("Live grid visualization")
            st.write("Performance metrics tracking")
            st.write("Agent status monitoring")
            st.write("Data export capabilities")
    
    else:
        # Get weather and yield data first
        weather = st.session_state.model.weather
        yield_pred = st.session_state.model.calculate_yield_prediction()
        
        # Weather and Yield Prediction Section
        st.markdown('<div class="section-header">Weather & Yield Forecast</div>', unsafe_allow_html=True)
        
        # Weather Calculation Explanation
        with st.expander("📊 Weather Simulation Methodology", expanded=False):
            st.markdown("### How Weather Data is Generated")
            st.markdown("""
            **Weather is simulated internally** (not from external API) with realistic variations:
            """)
            
            st.code("""
Initial Values (at start):
  Temperature: 25.0°C
  Humidity: 60.0%
  Rain Forecast: False (No rain)
  Wind Speed: 10.0 km/h

Update Frequency: Every 5 simulation steps

Temperature Update:
  New = Current + random(-2, +2)°C
  Range: 20-35°C
  
Humidity Update:
  New = Current + random(-5, +5)%
  Range: 40-90%
  
Rain Forecast:
  Probability: 10% chance per update
  Random check each update
  
Wind Speed Update:
  New = Current + random(-3, +3) km/h
  Range: 5-40 km/h
            """)
            
            st.markdown(f"""
            **Current Weather State:**
            - Temperature: {weather['temperature']:.1f}°C (Range: 20-35°C)
            - Humidity: {weather['humidity']:.0f}% (Range: 40-90%)
            - Rain Forecast: {'Yes' if weather['rain_forecast_24h'] else 'No'} (10% probability)
            - Wind Speed: {weather['wind_speed']:.1f} km/h (Range: 5-40 km/h)
            - Last Update: Step {(st.session_state.model.step_count // 5) * 5}
            - Next Update: Step {((st.session_state.model.step_count // 5) + 1) * 5}
            """)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Temperature", f"{weather['temperature']:.1f}°C")
        with col2:
            st.metric("Humidity", f"{weather['humidity']:.0f}%")
        with col3:
            st.metric("Rain Forecast", "Yes" if weather['rain_forecast_24h'] else "No")
        with col4:
            st.metric("Estimated Yield", f"{yield_pred['estimated_yield']:.1f} units")
        with col5:
            st.metric("Days to Harvest", yield_pred['days_to_harvest'])
        
        st.markdown("---")
        
        # Key metrics
        st.markdown('<div class="section-header">Key Performance Indicators</div>', unsafe_allow_html=True)
        
        metrics = get_current_metrics(st.session_state.model)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Ploughed Cells", metrics['ploughed'])
        with col2:
            st.metric("Sown Cells", metrics['sown'])
        with col3:
            st.metric("Healthy Crops", metrics['healthy'], 
                     delta=None if not st.session_state.metrics_history 
                     else metrics['healthy'] - st.session_state.metrics_history[-1]['healthy'])
        with col4:
            st.metric("Diseased Crops", metrics['diseased'],
                     delta=None if not st.session_state.metrics_history
                     else metrics['diseased'] - st.session_state.metrics_history[-1]['diseased'],
                     delta_color="inverse")
        with col5:
            st.metric("Harvested Crops", metrics['harvested'],
                     delta=None if not st.session_state.metrics_history
                     else metrics['harvested'] - st.session_state.metrics_history[-1]['harvested'])
        
        st.markdown("---")
        
        # Main visualizations
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Farm Grid", "Performance Metrics", "Agent Status", "Stress Monitoring", "Advanced Features"])
        
        with tab1:
            st.markdown('<div class="section-header">Farm Grid Visualization</div>', unsafe_allow_html=True)
            grid_plot = create_farm_grid_plot(st.session_state.model)
            st.plotly_chart(grid_plot, use_container_width=True)
            
            # Legend
            st.markdown("**Cell State Legend:**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown("Initial (Gray)")
                st.markdown("Ploughed (Brown)")
            with col2:
                st.markdown("Sown (Tan)")
                st.markdown("Growing (Light Green)")
            with col3:
                st.markdown("Need Water (Yellow)")
                st.markdown("Healthy (Dark Green)")
            with col4:
                st.markdown("Diseased (Red)")
                st.markdown("Ready to Harvest (Orange)")
        
        with tab2:
            st.markdown('<div class="section-header">Performance Metrics Over Time</div>', unsafe_allow_html=True)
            if st.session_state.metrics_history:
                metrics_chart = create_metrics_chart(st.session_state.metrics_history)
                st.plotly_chart(metrics_chart, use_container_width=True)
                
                # Summary statistics
                st.markdown('<div class="section-header">Summary Statistics</div>', unsafe_allow_html=True)
                df = pd.DataFrame(st.session_state.metrics_history)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Steps Executed", len(df))
                    st.metric("Peak Healthy Crops", df['healthy'].max())
                with col2:
                    st.metric("Total Crops Harvested", df['harvested'].iloc[-1])
                    st.metric("Total Disease Incidents", df['diseased'].sum())
                with col3:
                    avg_growing = df['growing'].mean()
                    st.metric("Average Growing Crops", f"{avg_growing:.1f}")
                    harvest_rate = df['harvested'].iloc[-1] / len(df) if len(df) > 0 else 0
                    st.metric("Harvest Rate (per step)", f"{harvest_rate:.2f}")
            else:
                st.info("Execute simulation steps to view performance metrics")
        
        with tab3:
            st.markdown('<div class="section-header">Agent Status Overview</div>', unsafe_allow_html=True)
            agent_table = create_agent_status_table(st.session_state.model)
            st.dataframe(agent_table, use_container_width=True, hide_index=True)
            
            # Agent details
            st.markdown('<div class="section-header">Detailed Agent Information</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Master Agent Status**")
                st.write(f"Current Position: {st.session_state.model.master_agent.pos}")
                st.write(f"Active Tasks: {len(st.session_state.model.master_agent.assigned_tasks)}")
                st.write(f"Task Queue Size: {st.session_state.model.master_agent.task_queue.qsize()}")
            
            with col2:
                st.markdown("**Worker Agent Summary**")
                idle_count = sum(1 for a in st.session_state.model.worker_agents 
                               if a.status.value == 'idle')
                working_count = sum(1 for a in st.session_state.model.worker_agents 
                                  if a.status.value == 'working')
                st.write(f"Idle Agents: {idle_count}")
                st.write(f"Working Agents: {working_count}")
                st.write(f"Total Agents: {len(st.session_state.model.worker_agents)}")
        
        with tab4:
            st.markdown('<div class="section-header">Crop Stress Monitoring</div>', unsafe_allow_html=True)
            
            stress = st.session_state.model.get_stress_indicators()
            weather = st.session_state.model.weather
            
            # Calculation Methodology Section
            with st.expander("📊 Calculation Methodology - How Numbers Are Computed", expanded=False):
                st.markdown("### Stress Detection Criteria")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("**Water Stress Detection:**")
                    st.code("""
Condition: water_level < 0.3 (30%)

For each crop cell:
  IF water_level < 0.3:
    Count as water-stressed
    
Percentage = (water_stressed / total_crops) × 100
                    """)
                
                with col_b:
                    st.markdown("**Temperature Stress Detection:**")
                    st.code("""
Condition: temperature > 32°C AND water_level < 0.5

For each crop cell:
  IF temperature > 32 AND water_level < 0.5:
    Count as temperature-stressed
    
Percentage = (temp_stressed / total_crops) × 100
                    """)
                
                st.markdown("**Overall Health Score:**")
                st.code("""
Formula: ((total_crops - stressed_crops) / total_crops) × 100

Where:
  stressed_crops = water_stressed + temperature_stressed
  
Interpretation:
  80-100% = Excellent
  60-79%  = Fair
  40-59%  = Poor
  <40%    = Critical
                """)
                
                st.markdown("**Current Calculation Example:**")
                st.code(f"""
Total Crops: {stress['total_crops']}
Water Stressed: {stress['water_stressed_count']} crops (water < 0.3)
Temperature Stressed: {stress['temperature_stressed_count']} crops (temp > 32°C + water < 0.5)

Water Stress % = ({stress['water_stressed_count']} / {stress['total_crops']}) × 100 = {stress['water_stress_percentage']}%
Temp Stress %  = ({stress['temperature_stressed_count']} / {stress['total_crops']}) × 100 = {stress['temperature_stress_percentage']}%

Total Stressed = {stress['water_stressed_count']} + {stress['temperature_stressed_count']} = {stress['water_stressed_count'] + stress['temperature_stressed_count']}
Health Score = (({stress['total_crops']} - {stress['water_stressed_count'] + stress['temperature_stressed_count']}) / {stress['total_crops']}) × 100 = {stress['overall_health_score']}%
                """)
            
            # Stress overview
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Water Stressed Crops", 
                         f"{stress['water_stressed_count']} ({stress['water_stress_percentage']}%)",
                         delta=None,
                         delta_color="inverse")
            with col2:
                st.metric("Temperature Stressed", 
                         f"{stress['temperature_stressed_count']} ({stress['temperature_stress_percentage']}%)",
                         delta=None,
                         delta_color="inverse")
            with col3:
                health_score = stress['overall_health_score']
                health_status = "Excellent" if health_score > 80 else "Fair" if health_score > 60 else "Poor"
                st.metric("Overall Health Score", f"{health_score:.1f}%", 
                         delta=None)
                st.markdown(f"**Status:** {health_status}")
            
            st.markdown("---")
            
            # Stress gauge chart
            st.markdown("**Stress Level Distribution**")
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=['Water Stress', 'Temperature Stress', 'Healthy'],
                y=[stress['water_stress_percentage'], 
                   stress['temperature_stress_percentage'],
                   stress['overall_health_score']],
                marker_color=['#2196F3', '#FF9800', '#4CAF50'],
                text=[f"{stress['water_stress_percentage']:.1f}%",
                      f"{stress['temperature_stress_percentage']:.1f}%",
                      f"{stress['overall_health_score']:.1f}%"],
                textposition='auto'
            ))
            
            fig.update_layout(
                title="Crop Health Distribution",
                yaxis_title="Percentage (%)",
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Recommendations
            st.markdown('<div class="section-header">Automated Recommendations</div>', unsafe_allow_html=True)
            
            recommendations = []
            
            if stress['water_stress_percentage'] > 30:
                recommendations.append("**High water stress detected** - Increase irrigation frequency")
            
            if stress['temperature_stress_percentage'] > 20:
                recommendations.append("**Temperature stress alert** - Consider shade nets or cooling measures")
            
            if weather['rain_forecast_24h']:
                recommendations.append("**Rain forecasted** - Irrigation automatically delayed to conserve water")
            
            if weather['temperature'] > 32:
                recommendations.append("**High temperature warning** - Monitor crops closely for heat stress")
            
            if yield_pred['at_risk_crops'] > 5:
                recommendations.append(f"**Disease alert** - {yield_pred['at_risk_crops']} crops at risk, apply treatment")
            
            if not recommendations:
                st.success("All systems operating normally. No immediate actions required.")
            else:
                for rec in recommendations:
                    st.warning(rec)
            
            # Yield prediction details
            st.markdown('<div class="section-header">Yield Prediction Details</div>', unsafe_allow_html=True)
            
            # Yield Calculation Methodology
            with st.expander("📊 Yield Calculation Methodology", expanded=False):
                st.markdown("### How Yield is Estimated")
                
                # Get actual counts for explanation
                growing = st.session_state.model.count_cells_by_state(CellState.GROWING)
                healthy = st.session_state.model.count_cells_by_state(CellState.HEALTHY)
                diseased = st.session_state.model.count_cells_by_state(CellState.DISEASED)
                ready = st.session_state.model.count_cells_by_state(CellState.READY_TO_HARVEST)
                
                st.markdown("**Yield Factors by Crop State:**")
                st.code("""
Healthy Crops:  1.0 yield per cell (100%)
Growing Crops:  0.7 yield per cell (70%)
Diseased Crops: 0.3 yield per cell (30%)
Ready Crops:    1.0 yield per cell (100%)
                """)
                
                st.markdown("**Current Calculation:**")
                st.code(f"""
Crop Counts:
  Healthy:  {healthy} crops
  Growing:  {growing} crops
  Diseased: {diseased} crops
  Ready:    {ready} crops

Yield Calculation:
  Healthy:  {healthy} × 1.0 = {healthy * 1.0:.2f} units
  Growing:  {growing} × 0.7 = {growing * 0.7:.2f} units
  Diseased: {diseased} × 0.3 = {diseased * 0.3:.2f} units
  Ready:    {ready} × 1.0 = {ready * 1.0:.2f} units
  
Total Estimated Yield = {yield_pred['estimated_yield']:.2f} units
                """)
                
                st.markdown("**Harvest Date Prediction:**")
                st.code(f"""
Average Growth Progress: {yield_pred['average_growth_progress']:.1f}%
Remaining Growth: {100 - yield_pred['average_growth_progress']:.1f}%

Growth Rate: 2% per simulation step
Days to Harvest = Remaining Growth / Growth Rate
                = {100 - yield_pred['average_growth_progress']:.1f} / 2
                = {yield_pred['days_to_harvest']} steps

Expected Harvest Step: {yield_pred['estimated_harvest_step']}
                """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Current Status**")
                st.write(f"Healthy Crops: {yield_pred['healthy_crops']}")
                st.write(f"At-Risk Crops: {yield_pred['at_risk_crops']}")
                st.write(f"Already Harvested: {yield_pred['current_harvest']}")
                st.write(f"Average Growth: {yield_pred['average_growth_progress']}%")
            
            with col2:
                st.markdown("**Forecast**")
                st.write(f"Estimated Yield: {yield_pred['estimated_yield']:.2f} units")
                st.write(f"Potential Total: {yield_pred['potential_yield']:.2f} units")
                st.write(f"Days to Harvest: {yield_pred['days_to_harvest']}")
                st.write(f"Expected Step: {yield_pred['estimated_harvest_step']}")
        
        with tab5:
            st.markdown('<div class="section-header">Advanced AI Features</div>', unsafe_allow_html=True)
            
            # CSP Scheduler info
            with st.expander("CSP Scheduler - Constraint Satisfaction"):
                st.write("Constraint-based task scheduling with resource allocation and optimization")
                st.code("""
Resource Management:
- Water: 1000L capacity
- Fuel: 500L capacity
- Tools: 5 units available

Constraint Types:
- Agent availability (prevents double-booking)
- Resource capacity limits
- Task time windows
- Task precedence relationships
- Priority-based allocation
                """)
            
            # PDDL Planner info
            with st.expander("PDDL Planner - Automated Planning"):
                st.write("High-level action planning and sequencing for farm operations")
                st.code("""
Available Actions:
1. move(agent, from_location, to_location)
2. plough(agent, plot)
3. sow(agent, plot, crop_type)
4. water(agent, plot)
5. scan(drone, plot)
6. harvest(agent, plot)

Planning Domain:
- Preconditions and effects defined
- Goal-oriented task generation
- Optimal action sequencing
                """)
            
            # Rule Engine info
            with st.expander("Rule Engine - Knowledge-Based Reasoning"):
                st.write("Forward-chaining inference engine for disease diagnosis and decision making")
                st.code("""
Sample Production Rules:

Disease Detection:
- IF humidity > 80% AND leaf_spots_present 
  THEN diagnose_leaf_spot_disease
  
Resource Management:
- IF water_level < 0.3 AND crop_growing 
  THEN schedule_watering_task
  
Harvest Readiness:
- IF growth_percentage >= 100% 
  THEN mark_ready_for_harvest
  
Health Monitoring:
- IF temperature > 35 AND humidity < 40
  THEN increase_irrigation_frequency
                """)
            
            # Export data
            st.markdown('<div class="section-header">Data Export</div>', unsafe_allow_html=True)
            if st.session_state.metrics_history:
                df = pd.DataFrame(st.session_state.metrics_history)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download Metrics as CSV",
                    data=csv,
                    file_name="fai_farm_metrics.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                st.caption(f"Export contains {len(df)} simulation steps with {len(df.columns)} metrics per step")
            else:
                st.info("No data available for export. Run the simulation first.")


if __name__ == "__main__":
    main()
