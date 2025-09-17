#!/bin/bash

# Change to script directory
cd "$(dirname "$0")"

# Pull latest changes
git pull

# Function to install dependencies with pip fallback
install_dependencies() {
    if [ -f "Pipfile" ] && command -v pipenv &> /dev/null; then
        echo "Using pipenv for dependency management..."
        if pipenv install --quiet 2>/dev/null; then
            echo "✅ Pipenv setup successful"
            return 0
        else
            echo "⚠️  Pipenv failed, falling back to pip..."
        fi
    fi
    
    # Fallback to pip + venv
    echo "Setting up virtual environment with venv..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    elif [ -f "Pipfile" ]; then
        pip install praw
    fi
    
    echo "✅ Virtual environment setup successful"
    return 1  # Return 1 to indicate we're using venv, not pipenv
}

# Check if pipenv is installed, install if not
if ! command -v pipenv &> /dev/null; then
    echo "pipenv not found, installing..."
    pip3 install --user pipenv 2>/dev/null || echo "Failed to install pipenv, will use venv instead"
    # Add pipenv to PATH if it's not already there
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install dependencies
install_dependencies
pipenv_success=$?

# Run the bot
echo "Starting XEQTbot..."
if [ $pipenv_success -eq 0 ]; then
    # Use pipenv
    pipenv run python main.py "$@"
else
    # Use venv
    source venv/bin/activate
    python main.py "$@"
fi