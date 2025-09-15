#!/usr/bin/env python3
"""
One-liner Move Tool
Usage: python simple.py [minutes] [seconds]
Example: python simple.py 2 30  (2 minutes 30 seconds)
"""

import sys, time, math, subprocess, json, platform
from pathlib import Path

# Auto-install pyautogui
try:
    import pyautogui
except ImportError:
    print("Installing pyautogui...")
    try:
        # Try normal install first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyautogui"])
        import pyautogui
    except subprocess.CalledProcessError:
        print("Trying with --break-system-packages flag...")
        try:
            # Try with --break-system-packages flag for externally-managed environments
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", "pyautogui"])
            import pyautogui
        except subprocess.CalledProcessError:
            print("Error: Could not install pyautogui automatically.")
            print("Please run: pip3 install --break-system-packages pyautogui")
            sys.exit(1)

def get_idle_time():
    """Get system idle time in seconds"""
    try:
        if platform.system() == "Darwin":  # macOS
            result = subprocess.run(['ioreg', '-c', 'IOHIDSystem'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'HIDIdleTime' in line:
                        idle_ns = int(line.split('=')[1].strip().rstrip(';'))
                        return idle_ns / 1000000000
        elif platform.system() == "Windows":
            import ctypes
            from ctypes import wintypes
            kernel32 = ctypes.windll.kernel32
            last_input = wintypes.DWORD()
            kernel32.GetLastInputInfo(ctypes.byref(last_input))
            return (kernel32.GetTickCount() - last_input.value) / 1000.0
        elif platform.system() == "Linux":
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

def jiggle():
    start_x, start_y = pyautogui.position()
    for i in range(20):
        angle = (2 * math.pi * i) / 20
        x = start_x + int(25 * math.cos(angle))
        y = start_y + int(25 * math.sin(angle))
        pyautogui.moveTo(x, y, duration=0.1)
        time.sleep(0.05)
    pyautogui.moveTo(start_x, start_y, duration=0.1)

def main():
    # Parse simple arguments
    minutes = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    seconds = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    idle_threshold = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    interval = minutes * 60 + seconds
    
    if interval <= 0:
        print("Usage: python simple.py [minutes] [seconds] [idle_threshold]")
        print("Example: python simple.py 2 30 60  (2m 30s interval, 60s idle threshold)")
        sys.exit(1)
    
    print(f"Move started - {minutes}m {seconds}s interval, {idle_threshold}s idle threshold")
    print(f"Total cycle: {minutes}m {seconds}s (including idle detection)")
    print("Press Ctrl+C to stop")
    
    last_move_time = 0
    
    try:
        while True:
            current_time = time.time()
            
            # Check if screen is locked
            if is_screen_locked():
                print("Screen is locked - skipping movement")
                time.sleep(10)
                continue
            
            # Check if machine has been idle long enough
            idle_time = get_idle_time()
            if idle_time < idle_threshold:
                print(f"Machine active (idle {idle_time:.1f}s) - skipping movement")
                time.sleep(10)
                continue
            
            # Check if enough time has passed since last movement
            if current_time - last_move_time >= interval:
                print(f"Machine idle {idle_time:.1f}s - moving mouse")
                # Show visual indicator only when actually moving
                show_activity_indicator()
                jiggle()
                last_move_time = current_time
            else:
                time.sleep(10)
                
    except KeyboardInterrupt:
        print("\nStopped")

if __name__ == "__main__":
    main()
