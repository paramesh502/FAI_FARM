# FAI-Farm Multi-Agent System

A comprehensive agricultural simulation system demonstrating autonomous multi-agent coordination with advanced AI techniques including PDDL planning, CSP scheduling, rule-based reasoning, machine learning, and real-time monitoring.

## Features

### Core System
- Multi-Agent Architecture: 1 Master Agent + 5 specialized Worker Agents
- Autonomous Decision Making: Agents coordinate independently
- Real-Time Monitoring: Professional web-based dashboard

### AI Techniques (5)
1. PDDL Planning - High-level task planning and sequencing
2. CSP Scheduling - Constraint-based resource allocation
3. Rule-Based Reasoning - Forward-chaining inference engine
4. Machine Learning - Disease classification (93% accuracy)
5. A* Pathfinding - Optimal agent navigation

### Advanced Features
- Weather Simulation - Real-time weather tracking with smart irrigation
- Yield Prediction - Crop yield estimation and harvest forecasting
- Stress Monitoring - Water and temperature stress detection
- Automated Recommendations - Data-driven decision support

## Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### macOS/Linux Setup

```bash
# Clone repository
git clone https://github.com/paramesh502/FAI_FARM.git
cd FAI_FARM

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Windows Setup

```bash
# Clone repository
git clone https://github.com/paramesh502/FAI_FARM.git
cd FAI_FARM

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the System

### Dashboard (Recommended)

**macOS/Linux:**
```bash
streamlit run dashboard/streamlit_app.py
```

**Windows:**
```bash
streamlit run dashboard\streamlit_app.py
```

Access at: http://localhost:8501

### Mesa Visualization

**macOS/Linux:**
```bash
python run.py
```

**Windows:**
```bash
python run.py
```

Access at: http://127.0.0.1:8521

### Demo Script

**macOS/Linux:**
```bash
python demo_complete_system.py
```

**Windows:**
```bash
python demo_complete_system.py
```

## Quick Start Guide

1. Launch dashboard: `streamlit run dashboard/streamlit_app.py`
2. Click "Initialize / Reset Simulation" in sidebar
3. Click "Run 100 Steps" to see the farm in action
4. Explore tabs:
   - Farm Grid: Heatmap visualization
   - Performance Metrics: Time-series charts
   - Agent Status: Real-time monitoring
   - Stress Monitoring: Health analysis with recommendations
   - Advanced Features: AI details and data export

## Project Structure

```
FAI_FARM/
├── agents/              # Multi-agent implementations
├── model/               # Core simulation model
├── dashboard/           # Streamlit dashboard
├── planning/            # PDDL planning engine
├── csp/                 # CSP scheduler
├── kr/                  # Knowledge representation
├── ml/                  # Machine learning
├── utils/               # Utilities
├── tests/               # Test suite
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## Key Features

### Weather Simulation
- Temperature: 20-35°C with realistic variations
- Humidity: 40-90% dynamic range
- Rain forecast: 24-hour prediction
- Updates every 5 simulation steps
- Smart irrigation delays watering when rain forecasted

### Yield Prediction
- Real-time estimation based on crop health
- Harvest date prediction
- Growth progress tracking
- At-risk crop identification

### Stress Monitoring
- Water stress detection (water < 30%)
- Temperature stress (temp > 32°C + water < 50%)
- Overall health score (0-100%)
- Automated recommendations

## Troubleshooting

### Module not found
Ensure virtual environment is activated:
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Port already in use
Use different port:
```bash
streamlit run dashboard/streamlit_app.py --server.port 8502
```

## System Requirements

- Python 3.9+
- 4GB RAM minimum
- 500MB disk space

## Dependencies

- mesa==2.1.5
- streamlit>=1.28.0
- plotly>=5.17.0
- scikit-learn>=1.3.0
- pandas>=2.0.0
- numpy>=1.24.0

## Repository

https://github.com/paramesh502/FAI_FARM

## License

Available for academic and educational purposes.
