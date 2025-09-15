#!/usr/bin/env python3
"""
Mouse Jiggler - A cross-platform mouse movement tool
Moves the mouse in small circular patterns to prevent screen lock/sleep
Single-file executable version with automatic dependency installation
"""

import argparse
import json
import os
import sys
import time
import math
import subprocess
import platform
from pathlib import Path

def install_pyautogui():
    """Install pyautogui if not available"""
    try:
        import pyautogui
        return pyautogui
    except ImportError:
        print("Installing pyautogui...")
        try:
            # Try normal install first
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyautogui"])
            import pyautogui
            print("pyautogui installed successfully!")
            return pyautogui
        except subprocess.CalledProcessError:
            print("Trying with --break-system-packages flag...")
            try:
                # Try with --break-system-packages flag for externally-managed environments
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", "pyautogui"])
                import pyautogui
                print("pyautogui installed successfully!")
                return pyautogui
            except subprocess.CalledProcessError:
                print("Error: Could not install pyautogui automatically.")
                print("Please run: pip3 install --break-system-packages pyautogui")
                print("Or use a virtual environment: python3 -m venv ~/moveit-env && source ~/moveit-env/bin/activate && pip install pyautogui")
                sys.exit(1)

# Install and import pyautogui
pyautogui = install_pyautogui()

def get_idle_time():
    """Get system idle time in seconds"""
    try:
        if platform.system() == "Darwin":  # macOS
            result = subprocess.run(['ioreg', '-c', 'IOHIDSystem'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'HIDIdleTime' in line:
                        # Extract the value and convert from nanoseconds to seconds
                        idle_ns = int(line.split('=')[1].strip().rstrip(';'))
                        return idle_ns / 1000000000  # Convert nanoseconds to seconds
        elif platform.system() == "Windows":
            import ctypes
            from ctypes import wintypes
            kernel32 = ctypes.windll.kernel32
            last_input = wintypes.DWORD()
            kernel32.GetLastInputInfo(ctypes.byref(last_input))
            return (kernel32.GetTickCount() - last_input.value) / 1000.0
        elif platform.system() == "Linux":
            # Try to get idle time from X11
            try:
                result = subprocess.run(['xprintidle'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return int(result.stdout.strip()) / 1000.0
            except FileNotFoundError:
                pass
    except Exception:
        pass
    return 0

def is_screen_locked():
    """Check if screen is locked"""
    try:
        if platform.system() == "Darwin":  # macOS
            result = subprocess.run(['python3', '-c', 
                'import Quartz; print(Quartz.CGSessionCopyCurrentDictionary() is None)'], 
                capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip() == 'True'
        elif platform.system() == "Windows":
            import ctypes
            from ctypes import wintypes
            user32 = ctypes.windll.user32
            return user32.GetForegroundWindow() == 0
        elif platform.system() == "Linux":
            # Check if screen saver is active
            try:
                result = subprocess.run(['gnome-screensaver-command', '-q'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return 'is active' in result.stdout.lower()
            except FileNotFoundError:
                pass
    except Exception:
        pass
    return False

def show_activity_indicator():
    """Show a small visual indicator that the tool is active"""
    try:
        # Get screen dimensions
        screen_width, screen_height = pyautogui.size()
        center_x, center_y = screen_width // 2, screen_height // 2
        
        # Create a small circle indicator
        indicator_radius = 8
        for i in range(10):  # Show for 1 second (10 * 0.1s)
            angle = (2 * math.pi * i) / 10
            x = center_x + int(indicator_radius * math.cos(angle))
            y = center_y + int(indicator_radius * math.sin(angle))
            
            # Draw a small circle by moving mouse in a tiny circle
            pyautogui.moveTo(x, y, duration=0.05)
            time.sleep(0.05)
        
        # Return to center
        pyautogui.moveTo(center_x, center_y, duration=0.1)
        
    except Exception:
        # If visual indicator fails, just continue silently
        pass

class Move:
    def __init__(self):
        self.settings_file = Path.home() / '.move_settings.json'
        self.running = False
        self.circle_radius = 25  # pixels
        self.circle_steps = 20   # number of steps to complete a circle
        self.idle_threshold = 30  # seconds of idle time before moving
        
    def load_settings(self):
        """Load settings from file or return defaults"""
        default_settings = {
            'interval_minutes': 1,
            'interval_seconds': 0,
            'circle_radius': 25,
            'circle_steps': 20,
            'idle_threshold': 30
        }
        
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    # Merge with defaults to handle missing keys
                    for key, value in default_settings.items():
                        if key not in settings:
                            settings[key] = value
                    return settings
            except (json.JSONDecodeError, IOError):
                print(f"Warning: Could not load settings from {self.settings_file}")
                return default_settings
        return default_settings
    
    def save_settings(self, settings):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save settings: {e}")
    
    def get_interval_seconds(self, minutes, seconds):
        """Convert minutes and seconds to total seconds"""
        return minutes * 60 + seconds
    
    def move_mouse_circle(self):
        """Move mouse in a small circular pattern"""
        try:
            # Get current mouse position
            start_x, start_y = pyautogui.position()
            
            # Calculate circle points
            for i in range(self.circle_steps):
                if not self.running:
                    break
                    
                angle = (2 * math.pi * i) / self.circle_steps
                x = start_x + int(self.circle_radius * math.cos(angle))
                y = start_y + int(self.circle_radius * math.sin(angle))
                
                # Move mouse to calculated position
                pyautogui.moveTo(x, y, duration=0.1)
                time.sleep(0.05)  # Small delay between movements
            
            # Return to original position
            pyautogui.moveTo(start_x, start_y, duration=0.1)
            
        except pyautogui.FailSafeException:
            print("\nMove stopped due to fail-safe (mouse moved to corner)")
            self.running = False
        except Exception as e:
            print(f"Error during mouse movement: {e}")
            self.running = False
    
    def run(self, interval_minutes, interval_seconds, save_settings_flag):
        """Main execution loop"""
        interval = self.get_interval_seconds(interval_minutes, interval_seconds)
        
        # Save settings if requested
        if save_settings_flag:
            settings = {
                'interval_minutes': interval_minutes,
                'interval_seconds': interval_seconds,
                'circle_radius': self.circle_radius,
                'circle_steps': self.circle_steps,
                'idle_threshold': self.idle_threshold
            }
            self.save_settings(settings)
            print(f"Settings saved: {interval_minutes}m {interval_seconds}s interval")
        
        print(f"Move started with {interval_minutes}m {interval_seconds}s interval")
        print(f"Idle threshold: {self.idle_threshold} seconds")
        print(f"Total cycle: {interval_minutes}m {interval_seconds}s (including idle detection)")
        print("Press Ctrl+C to stop")
        
        self.running = True
        last_move_time = 0
        
        try:
            while self.running:
                current_time = time.time()
                
                # Check if screen is locked
                if is_screen_locked():
                    print("Screen is locked - skipping movement")
                    time.sleep(10)  # Check again in 10 seconds
                    continue
                
                # Check if machine has been idle long enough
                idle_time = get_idle_time()
                if idle_time < self.idle_threshold:
                    print(f"Machine active (idle {idle_time:.1f}s) - skipping movement")
                    time.sleep(10)  # Check again in 10 seconds
                    continue
                
                # Check if enough time has passed since last movement
                # The interval should be the total time including idle detection
                if current_time - last_move_time >= interval:
                    print(f"Machine idle {idle_time:.1f}s - moving mouse")
                    # Show visual indicator only when actually moving
                    show_activity_indicator()
                    self.move_mouse_circle()
                    last_move_time = current_time
                else:
                    # Wait a bit before checking again
                    time.sleep(10)
                    
        except KeyboardInterrupt:
            print("\nMove stopped by user")
            self.running = False

def main():
    parser = argparse.ArgumentParser(
        description="Move - Prevent screen lock with small mouse movements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python move.py                    # Use saved settings or default (1m 0s)
  python move.py -m 2 -s 30        # 2 minutes 30 seconds interval
  python move.py -m 0 -s 45 -s     # 45 seconds interval and save settings
  python move.py --load            # Load and use saved settings
        """
    )
    
    parser.add_argument('-m', '--minutes', type=int, default=None,
                       help='Interval in minutes (default: from saved settings or 1)')
    parser.add_argument('-s', '--seconds', type=int, default=None,
                       help='Interval in seconds (default: from saved settings or 0)')
    parser.add_argument('--save', action='store_true',
                       help='Save current settings for future use')
    parser.add_argument('--load', action='store_true',
                       help='Load and use saved settings (overrides -m and -s)')
    parser.add_argument('--radius', type=int, default=None,
                       help='Circle radius in pixels (default: 10)')
    parser.add_argument('--steps', type=int, default=None,
                       help='Number of steps to complete circle (default: 20)')
    parser.add_argument('--idle', type=int, default=None,
                       help='Idle threshold in seconds before moving (default: 30)')
    
    args = parser.parse_args()
    
    jiggler = Move()
    
    # Load saved settings
    settings = jiggler.load_settings()
    
    # Determine interval
    if args.load or (args.minutes is None and args.seconds is None):
        # Use saved settings
        interval_minutes = settings['interval_minutes']
        interval_seconds = settings['interval_seconds']
        print(f"Using saved settings: {interval_minutes}m {interval_seconds}s interval")
    else:
        # Use command line arguments or defaults
        interval_minutes = args.minutes if args.minutes is not None else 0
        interval_seconds = args.seconds if args.seconds is not None else 0
        
        # If no interval specified, use saved settings
        if interval_minutes == 0 and interval_seconds == 0:
            interval_minutes = settings['interval_minutes']
            interval_seconds = settings['interval_seconds']
            print(f"Using saved settings: {interval_minutes}m {interval_seconds}s interval")
    
    # Validate interval
    if interval_minutes < 0 or interval_seconds < 0:
        print("Error: Interval cannot be negative")
        sys.exit(1)
    
    if interval_minutes == 0 and interval_seconds == 0:
        print("Error: Interval must be greater than 0")
        sys.exit(1)
    
    # Apply custom radius, steps, and idle threshold if provided
    if args.radius is not None:
        jiggler.circle_radius = args.radius
    else:
        jiggler.circle_radius = settings['circle_radius']
    
    if args.steps is not None:
        jiggler.circle_steps = args.steps
    else:
        jiggler.circle_steps = settings['circle_steps']
    
    if args.idle is not None:
        jiggler.idle_threshold = args.idle
    else:
        jiggler.idle_threshold = settings['idle_threshold']
    
    # Disable pyautogui fail-safe for smoother operation
    pyautogui.FAILSAFE = True
    
    # Start the tool
    jiggler.run(interval_minutes, interval_seconds, args.save)

if __name__ == "__main__":
    main()
