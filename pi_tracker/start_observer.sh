#!/bin/bash

# Exit on error
set -e

echo "Setting up Art Observer..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found. Please install Python 3."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing required packages..."
pip install opencv-python-headless numpy requests

# Check for configuration file
if [ ! -f "config.json" ]; then
    echo "Creating default config.json..."
    cat > config.json << EOF
{
    "camera_id": "camera_1",
    "artwork_id": "artwork_1",
    "lambda_url": "https://your-lambda-url.amazonaws.com/prod/check-server",
    "video_source": 0
}
EOF
    echo "Please update config.json with your settings"
    exit 1
fi

# Start the observer
echo "Starting Art Observer..."
python3 run_observer.py
