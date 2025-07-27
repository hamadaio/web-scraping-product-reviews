#!/bin/bash

# Navigate to the dashboard directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "dashboard_env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv dashboard_env
    echo "Installing dependencies..."
    dashboard_env/bin/pip install pandas numpy textblob
fi

# Run the dashboard app
echo "🚀 Starting Review Analytics Dashboard..."
echo "📁 Current directory: $(pwd)"
echo "🐍 Using Python: $(dashboard_env/bin/python --version)"

dashboard_env/bin/python dashboard_app.py
