#!/bin/bash
# Move tool launcher that handles virtual environment automatically

# Check if virtual environment exists
if [ ! -d "$HOME/moveit-env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv ~/moveit-env
    source ~/moveit-env/bin/activate
    pip install pyautogui
else
    source ~/moveit-env/bin/activate
fi

# Run the tool with all arguments
python3 "$(dirname "$0")/simple.py" "$@"
