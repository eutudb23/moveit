# Move

A cross-platform mouse movement tool that prevents screen lock and sleep by moving the mouse in small circular patterns. Works on macOS, Windows, and Linux.

## Features

- **Cross-platform**: Works on macOS, Windows, and Linux
- **Single-file execution**: No setup required - just run the Python file
- **Auto-install dependencies**: Automatically installs required packages
- **Smart idle detection**: Only moves when machine has been idle for specified time
- **Screen lock detection**: Never moves when screen is locked
- **Configurable intervals**: Set time between movements in minutes and seconds
- **Settings persistence**: Remembers your preferred settings
- **Small movements**: Uses small circular patterns (25px radius by default)
- **Visual indicator**: Shows a small circle in the center of screen when active
- **Terminal-based**: Run from command line with various options
- **Safe operation**: Includes fail-safe mechanism (move mouse to corner to stop)

## Quick Start (Zero Setup!)

**Just run it!** The tool will automatically install dependencies if needed.

**Ultra-simple version:**
```bash
python3 simple.py 2 30    # 2 minutes 30 seconds (30s idle threshold)
python3 simple.py 1 0 60  # 1 minute interval, 60s idle threshold
python3 simple.py 0 30 45 # 30 seconds interval, 45s idle threshold
```

**Full-featured version:**
```bash
python3 move.py -m 2 -s 30
python3 move.py --load
```

*Note: If you get an "externally-managed-environment" error on macOS, try: `pip3 install --user pyautogui` first, then run the tool. For other options, see the Installation section below.*

## Installation

**Option 1: Zero Setup (Recommended)**
- Just download and run! Dependencies install automatically.

**Option 2: Manual Setup**

### Installing Python and pip

**macOS (with Homebrew):**
```bash
# Install Python (includes pip)
brew install python

# Verify installation
python3 --version
pip3 --version

# For externally-managed environment error, use one of these options:

# Option 1: Use virtual environment (recommended)
python3 -m venv ~/moveit-env
source ~/moveit-env/bin/activate
pip install pyautogui

# Option 2: Use --user flag
pip3 install --user pyautogui

# Option 3: Use --break-system-packages (not recommended)
pip3 install --break-system-packages pyautogui
```

**macOS (without Homebrew):**
```bash
# Download Python from python.org or use built-in Python
# Python 3.6+ includes pip by default
python3 --version
pip3 --version

# For externally-managed environment error, use virtual environment:
python3 -m venv ~/moveit-env
source ~/moveit-env/bin/activate
pip install pyautogui
```

**Windows:**
```bash
# Download Python from python.org (includes pip)
# Or use Windows Store: "Python 3.11" or newer

# Verify installation
python --version
pip --version
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# CentOS/RHEL/Fedora
sudo yum install python3 python3-pip
# or
sudo dnf install python3 python3-pip

# Verify installation
python3 --version
pip3 --version
```

### Installing Dependencies
```bash
pip install -r requirements.txt
# or
pip3 install -r requirements.txt  # on macOS if needed
```

## Usage

### Ultra-Simple Version (`simple.py`)

```bash
# Basic usage - minutes, seconds, and idle threshold
python simple.py 2 30    # 2 minutes 30 seconds (30s idle threshold)
python simple.py 1 0 60  # 1 minute interval, 60s idle threshold
python simple.py 0 30 45 # 30 seconds interval, 45s idle threshold
```

### Full-Featured Version (`move.py`)

```bash
# Use default settings (1 minute interval)
python move.py

# Use saved settings
python move.py --load

# Set custom interval (2 minutes 30 seconds)
python move.py -m 2 -s 30

# Set custom interval and save it
python move.py -m 0 -s 45 --save
```

### Launcher Scripts

```bash
# macOS/Linux
./run.sh 2 30

# Windows
run.bat 2 30
```

### Command Line Options

- `-m, --minutes`: Interval in minutes
- `-s, --seconds`: Interval in seconds  
- `--save`: Save current settings for future use
- `--load`: Load and use saved settings (overrides -m and -s)
- `--radius`: Circle radius in pixels (default: 25)
- `--steps`: Number of steps to complete circle (default: 20)
- `--idle`: Idle threshold in seconds before moving (default: 30)
- `-h, --help`: Show help message

### Examples

```bash
# 30 seconds interval, save settings
python move.py -m 0 -s 30 --save

# 5 minutes interval with larger circle and 60s idle threshold
python move.py -m 5 -s 0 --radius 15 --idle 60

# Use saved settings
python move.py --load

# Quick 15-second interval with 45s idle threshold
python move.py -s 15 --idle 45
```

## How It Works

The tool intelligently moves your mouse in a small circular pattern only when:
1. **Machine is idle** for the specified threshold (default: 30 seconds)
2. **Screen is not locked**
3. **Enough time has passed** since the last movement

**Timing Logic:**
- **Idle threshold**: How long machine must be idle before moving (e.g., 30 seconds)
- **Interval**: Time between movements when idle (e.g., 4 minutes 90 seconds)
- **Total cycle**: The interval time includes the idle detection period

The default pattern:
- **Radius**: 25 pixels
- **Steps**: 20 steps to complete a full circle
- **Duration**: Each circle takes about 1 second to complete
- **Return**: Mouse returns to original position after each circle
- **Visual Indicator**: Shows a small circle in screen center when active
- **Idle Detection**: Only moves when machine has been idle for 30+ seconds
- **Lock Detection**: Never moves when screen is locked

## Settings

Settings are automatically saved to `~/.move_settings.json` when you use the `--save` flag. The settings include:
- Interval minutes and seconds
- Circle radius
- Number of circle steps
- Idle threshold (seconds of inactivity before moving)

## Stopping the Tool

- Press `Ctrl+C` in the terminal
- Move your mouse to any corner of the screen (fail-safe mechanism)

## Requirements

- Python 3.6+
- macOS, Windows, or Linux
- **Dependencies install automatically** (no manual setup needed)

## Notes

- The tool uses small, subtle movements to avoid interfering with normal computer use
- **Smart operation**: Only moves when machine is idle and screen is unlocked
- **Visual feedback**: A small circle appears in the center of your screen when the tool is active
- Settings are saved in your home directory for persistence across sessions
- The fail-safe mechanism stops the tool if you move the mouse to a screen corner
- Perfect for preventing screen lock during presentations or long-running processes
- Idle detection works on macOS, Windows, and Linux (with xprintidle)
