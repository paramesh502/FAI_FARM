#!/bin/bash

# FAI-Farm Setup and Run Script
# This script sets up the environment and provides options to run different components

echo "=========================================="
echo "FAI-Farm Multi-Agent System"
echo "=========================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"
echo ""

# Function to install dependencies
install_deps() {
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo "✓ Dependencies installed!"
    echo ""
}

# Function to run tests
run_tests() {
    echo "Running tests..."
    python tests/test_simulation.py
    echo ""
}

# Function to train ML model
train_ml() {
    echo "Training ML disease classifier..."
    python ml/disease_classifier.py
    echo ""
}

# Function to run Mesa visualization
run_mesa() {
    echo "Starting Mesa visualization..."
    echo "Opening at http://127.0.0.1:8521"
    python run.py
}

# Function to run Streamlit dashboard
run_dashboard() {
    echo "Starting Streamlit dashboard..."
    echo "Opening at http://localhost:8501"
    streamlit run dashboard/streamlit_app.py
}

# Main menu
echo "What would you like to do?"
echo ""
echo "1) Install dependencies"
echo "2) Run tests"
echo "3) Train ML model"
echo "4) Run Mesa visualization (original)"
echo "5) Run Streamlit dashboard (recommended)"
echo "6) Full setup (install + train + dashboard)"
echo "7) Exit"
echo ""
read -p "Enter choice [1-7]: " choice

case $choice in
    1)
        install_deps
        ;;
    2)
        run_tests
        ;;
    3)
        train_ml
        ;;
    4)
        run_mesa
        ;;
    5)
        run_dashboard
        ;;
    6)
        install_deps
        train_ml
        run_dashboard
        ;;
    7)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac
