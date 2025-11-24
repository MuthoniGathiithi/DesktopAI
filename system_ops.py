import os
import subprocess
import shutil
import psutil
import time
import socket
from datetime import datetime
import platform
import tkinter as tk
from tkinter import simpledialog, messagebox

# ==================== STORAGE OPERATIONS ====================

def check_storage():
    """Check disk storage usage"""
    try:
        storage_info = []
        
        # Get all disk partitions
        partitions = psutil.disk_partitions()
        
        for partition in partitions:
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                
                # Convert bytes to GB
                total_gb = partition_usage.total / (1024**3)
                used_gb = partition_usage.used / (1024**3)
                free_gb = partition_usage.free / (1024**3)
                usage_percent = (partition_usage.used / partition_usage.total) * 100
                
                storage_info.append(f"""
Drive: {partition.device}
Mount Point: {partition.mountpoint}
File System: {partition.fstype}
Total: {total_gb:.2f} GB
Used: {used_gb:.2f} GB ({usage_percent:.1f}%)
Free: {free_gb:.2f} GB
""")
            except PermissionError:
                storage_info.append(f"Drive: {partition.device} - Permission denied")
        
        return "Storage Information:\n" + "\n".join(storage_info)
    
    except Exception as e:
        return f"Error checking storage: {str(e)}"

# ==================== NETWORK OPERATIONS ====================

def check_internet_speed():
    """Check internet connectivity and basic speed test"""
    try:
        # Test connectivity
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        
        # Basic speed test using ping
        if platform.system().lower() == "windows":
            ping_cmd = ["ping", "-n", "4", "8.8.8.8"]
        else:
            ping_cmd = ["ping", "-c", "4", "8.8.8.8"]
        
        result = subprocess.run(ping_cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return f"Internet Connection: ✓ Connected\n\nPing Test Results:\n{result.stdout}"
        else:
            return "Internet Connection: ✗ No connection or timeout"
    
    except Exception as e:
        return f"Internet Connection: ✗ Error checking connection: {str(e)}"

def get_wifi_info():
    """Get WiFi connection information"""
    try:
        if platform.system().lower() == "windows":
            # Windows WiFi info
            result = subprocess.run(["netsh", "wlan", "show", "profiles"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return f"WiFi Profiles:\n{result.stdout}"
            else:
                return "Could not retrieve WiFi information"
        else:
            # Linux WiFi info
            try:
                result = subprocess.run(["nmcli", "dev", "wifi", "list"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return f"Available WiFi Networks:\n{result.stdout}"
                else:
                    # Try iwlist as fallback
                    result = subprocess.run(["iwlist", "scan"], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        return f"WiFi Scan Results:\n{result.stdout[:1000]}..."
                    else:
                        return "Could not retrieve WiFi information. May need sudo privileges."
            except FileNotFoundError:
                return "WiFi tools not available. Install network-manager or wireless-tools."
    
    except Exception as e:
        return f"Error getting WiFi info: {str(e)}"

def connect_wifi(network_name, password=None):
    """Connect to WiFi network"""
    try:
        if platform.system().lower() == "windows":
            if password:
                cmd = ["netsh", "wlan", "connect", f"name={network_name}"]
            else:
                cmd = ["netsh", "wlan", "connect", f"name={network_name}"]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return f"Successfully connected to {network_name}"
            else:
                return f"Failed to connect to {network_name}: {result.stderr}"
        else:
            # Linux WiFi connection
            if password:
                cmd = ["nmcli", "dev", "wifi", "connect", network_name, "password", password]
            else:
                cmd = ["nmcli", "dev", "wifi", "connect", network_name]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return f"Successfully connected to {network_name}"
            else:
                return f"Failed to connect to {network_name}: {result.stderr}"
    
    except Exception as e:
        return f"Error connecting to WiFi: {str(e)}"

# ==================== AUDIO OPERATIONS ====================

def adjust_volume(level=None, action=None):
    """Adjust system volume"""
    try:
        if platform.system().lower() == "windows":
            # Windows volume control
            if action == "mute":
                subprocess.run(["nircmd", "mutesysvolume", "1"], check=False)
                return "Volume muted"
            elif action == "unmute":
                subprocess.run(["nircmd", "mutesysvolume", "0"], check=False)
                return "Volume unmuted"
            elif level is not None:
                # Set volume (0-100)
                volume_level = max(0, min(100, int(level)))
                subprocess.run(["nircmd", "setsysvolume", str(int(volume_level * 655.35))], check=False)
                return f"Volume set to {volume_level}%"
            else:
                return "Please specify volume level (0-100) or action (mute/unmute)"
        else:
            # Linux volume control using amixer
            if action == "mute":
                result = subprocess.run(["amixer", "set", "Master", "mute"], 
                                      capture_output=True, text=True)
                return "Volume muted" if result.returncode == 0 else "Failed to mute volume"
            elif action == "unmute":
                result = subprocess.run(["amixer", "set", "Master", "unmute"], 
                                      capture_output=True, text=True)
                return "Volume unmuted" if result.returncode == 0 else "Failed to unmute volume"
            elif level is not None:
                volume_level = max(0, min(100, int(level)))
                result = subprocess.run(["amixer", "set", "Master", f"{volume_level}%"], 
                                      capture_output=True, text=True)
                return f"Volume set to {volume_level}%" if result.returncode == 0 else "Failed to set volume"
            else:
                return "Please specify volume level (0-100) or action (mute/unmute)"
    
    except Exception as e:
        return f"Error adjusting volume: {str(e)}"

def get_volume():
    """Get current volume level"""
    try:
        if platform.system().lower() == "windows":
            return "Volume info not available on Windows without additional tools"
        else:
            result = subprocess.run(["amixer", "get", "Master"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return f"Current Volume Info:\n{result.stdout}"
            else:
                return "Could not get volume information"
    except Exception as e:
        return f"Error getting volume: {str(e)}"

# ==================== SCREENSHOT OPERATIONS ====================

def take_screenshot(filename=None):
    """Take a screenshot"""
    try:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        # Ensure filename has .png extension
        if not filename.endswith('.png'):
            filename += '.png'
        
        # Save to Desktop
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.exists(desktop_path):
            desktop_path = os.path.expanduser("~")
        
        full_path = os.path.join(desktop_path, filename)
        
        if platform.system().lower() == "windows":
            # Windows screenshot using PowerShell
            ps_script = f"""
            Add-Type -AssemblyName System.Windows.Forms
            Add-Type -AssemblyName System.Drawing
            $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
            $bitmap = New-Object System.Drawing.Bitmap $bounds.width, $bounds.height
            $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
            $graphics.CopyFromScreen($bounds.X, $bounds.Y, 0, 0, $bounds.size)
            $bitmap.Save('{full_path}')
            $graphics.Dispose()
            $bitmap.Dispose()
            """
            result = subprocess.run(["powershell", "-Command", ps_script], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return f"Screenshot saved as {full_path}"
            else:
                return f"Failed to take screenshot: {result.stderr}"
        else:
            # Linux screenshot using scrot or gnome-screenshot
            try:
                result = subprocess.run(["scrot", full_path], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return f"Screenshot saved as {full_path}"
            except FileNotFoundError:
                try:
                    result = subprocess.run(["gnome-screenshot", "-f", full_path], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        return f"Screenshot saved as {full_path}"
                except FileNotFoundError:
                    return "Screenshot tools not available. Install 'scrot' or 'gnome-screenshot'"
            
            return f"Failed to take screenshot: {result.stderr if 'result' in locals() else 'Unknown error'}"
    
    except Exception as e:
        return f"Error taking screenshot: {str(e)}"

# ==================== PROCESS MANAGEMENT ====================

def list_processes():
    """List running processes"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu': proc.info['cpu_percent'],
                    'memory': proc.info['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu'] or 0, reverse=True)
        
        result = "Top Running Processes (by CPU usage):\n"
        result += f"{'PID':<8} {'Name':<25} {'CPU%':<8} {'Memory%':<8}\n"
        result += "-" * 50 + "\n"
        
        for proc in processes[:20]:  # Show top 20
            result += f"{proc['pid']:<8} {proc['name'][:24]:<25} {proc['cpu'] or 0:<8.1f} {proc['memory'] or 0:<8.1f}\n"
        
        return result
    
    except Exception as e:
        return f"Error listing processes: {str(e)}"

def kill_process(process_name_or_pid):
    """Kill a process by name or PID"""
    try:
        if process_name_or_pid.isdigit():
            # Kill by PID
            pid = int(process_name_or_pid)
            proc = psutil.Process(pid)
            proc.terminate()
            return f"Process with PID {pid} ({proc.name()}) terminated"
        else:
            # Kill by name
            killed_count = 0
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == process_name_or_pid.lower():
                    proc.terminate()
                    killed_count += 1
            
            if killed_count > 0:
                return f"Terminated {killed_count} process(es) named '{process_name_or_pid}'"
            else:
                return f"No process found with name '{process_name_or_pid}'"
    
    except psutil.NoSuchProcess:
        return f"Process not found"
    except psutil.AccessDenied:
        return f"Access denied. May need administrator privileges"
    except Exception as e:
        return f"Error killing process: {str(e)}"

# ==================== GUI PASSWORD HELPER ====================

def get_gui_password(title="Authentication Required", prompt="Enter your password:"):
    """Get password using GUI dialog instead of command line"""
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        password = simpledialog.askstring(title, prompt, show='*')
        root.destroy()
        return password
    except Exception as e:
        return None

# ==================== SYSTEM POWER OPERATIONS ====================

def shutdown_system(delay_minutes=0):
    """Shutdown the computer with GUI password prompt"""
    try:
        if platform.system().lower() == "windows":
            # Windows doesn't need password for shutdown
            if delay_minutes > 0:
                delay_seconds = delay_minutes * 60
                subprocess.run(["shutdown", "/s", "/t", str(delay_seconds)])
                return f"System will shutdown in {delay_minutes} minutes"
            else:
                subprocess.run(["shutdown", "/s", "/t", "0"])
                return "Shutting down system now..."
        else:
            # Linux - get password via GUI
            password = get_gui_password("Shutdown Authentication", "Enter your password to shutdown:")
            if password is None:
                return "Shutdown cancelled - no password provided"
            
            if delay_minutes > 0:
                cmd = f"echo '{password}' | sudo -S shutdown -h +{delay_minutes}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    return f"System will shutdown in {delay_minutes} minutes"
                else:
                    return f"Failed to schedule shutdown: {result.stderr}"
            else:
                cmd = f"echo '{password}' | sudo -S shutdown -h now"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    return "Shutting down system now..."
                else:
                    return f"Failed to shutdown: {result.stderr}"
    
    except Exception as e:
        return f"Error shutting down system: {str(e)}"

def restart_system(delay_minutes=0):
    """Restart the computer with GUI password prompt"""
    try:
        if platform.system().lower() == "windows":
            # Windows doesn't need password for restart
            if delay_minutes > 0:
                delay_seconds = delay_minutes * 60
                subprocess.run(["shutdown", "/r", "/t", str(delay_seconds)])
                return f"System will restart in {delay_minutes} minutes"
            else:
                subprocess.run(["shutdown", "/r", "/t", "0"])
                return "Restarting system now..."
        else:
            # Linux - get password via GUI
            password = get_gui_password("Restart Authentication", "Enter your password to restart:")
            if password is None:
                return "Restart cancelled - no password provided"
            
            if delay_minutes > 0:
                cmd = f"echo '{password}' | sudo -S shutdown -r +{delay_minutes}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    return f"System will restart in {delay_minutes} minutes"
                else:
                    return f"Failed to schedule restart: {result.stderr}"
            else:
                cmd = f"echo '{password}' | sudo -S shutdown -r now"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    return "Restarting system now..."
                else:
                    return f"Failed to restart: {result.stderr}"
    
    except Exception as e:
        return f"Error restarting system: {str(e)}"

def cancel_shutdown():
    """Cancel scheduled shutdown/restart"""
    try:
        if platform.system().lower() == "windows":
            subprocess.run(["shutdown", "/a"])
            return "Shutdown/restart cancelled"
        else:
            subprocess.run(["sudo", "shutdown", "-c"])
            return "Shutdown/restart cancelled"
    
    except Exception as e:
        return f"Error cancelling shutdown: {str(e)}"

# ==================== BRIGHTNESS CONTROL ====================

def adjust_brightness(level=None, action=None):
    """Adjust screen brightness"""
    try:
        if platform.system().lower() == "windows":
            # Windows brightness control using WMI
            if action == "increase":
                result = subprocess.run([
                    "powershell", "-Command",
                    "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,100)"
                ], capture_output=True, text=True)
                return "Brightness increased to maximum"
            elif action == "decrease":
                result = subprocess.run([
                    "powershell", "-Command", 
                    "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,20)"
                ], capture_output=True, text=True)
                return "Brightness decreased to minimum"
            elif level is not None:
                brightness_level = max(1, min(100, int(level)))
                result = subprocess.run([
                    "powershell", "-Command",
                    f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{brightness_level})"
                ], capture_output=True, text=True)
                return f"Brightness set to {brightness_level}%"
            else:
                return "Please specify brightness level (1-100) or action (increase/decrease)"
        else:
            # Linux brightness control
            if action == "increase":
                result = subprocess.run(["xrandr", "--output", "$(xrandr | grep ' connected' | head -1 | cut -d' ' -f1)", "--brightness", "1.0"], 
                                      shell=True, capture_output=True, text=True)
                return "Brightness increased to maximum"
            elif action == "decrease":
                result = subprocess.run(["xrandr", "--output", "$(xrandr | grep ' connected' | head -1 | cut -d' ' -f1)", "--brightness", "0.3"], 
                                      shell=True, capture_output=True, text=True)
                return "Brightness decreased to minimum"
            elif level is not None:
                brightness_level = max(0.1, min(1.0, float(level) / 100))
                result = subprocess.run([
                    "bash", "-c", 
                    f"xrandr --output $(xrandr | grep ' connected' | head -1 | cut -d' ' -f1) --brightness {brightness_level}"
                ], capture_output=True, text=True)
                return f"Brightness set to {int(brightness_level * 100)}%"
            else:
                return "Please specify brightness level (1-100) or action (increase/decrease)"
    
    except Exception as e:
        return f"Error adjusting brightness: {str(e)}"

def get_brightness():
    """Get current brightness level"""
    try:
        if platform.system().lower() == "windows":
            result = subprocess.run([
                "powershell", "-Command",
                "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness"
            ], capture_output=True, text=True)
            if result.returncode == 0:
                return f"Current brightness: {result.stdout.strip()}%"
            else:
                return "Could not get brightness information"
        else:
            result = subprocess.run([
                "bash", "-c",
                "xrandr --verbose | grep -i brightness | head -1"
            ], capture_output=True, text=True)
            if result.returncode == 0:
                return f"Current brightness info: {result.stdout.strip()}"
            else:
                return "Could not get brightness information"
    except Exception as e:
        return f"Error getting brightness: {str(e)}"

# ==================== LOCK/LOGOUT OPERATIONS ====================

def lock_computer():
    """Lock the computer screen"""
    try:
        if platform.system().lower() == "windows":
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
            return "Computer locked"
        else:
            # Try different lock commands for Linux
            lock_commands = [
                ["gnome-screensaver-command", "--lock"],
                ["xdg-screensaver", "lock"],
                ["dm-tool", "lock"],
                ["loginctl", "lock-session"]
            ]
            
            for cmd in lock_commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        return "Computer locked"
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    continue
            
            return "Could not lock computer. Lock command not available."
    
    except Exception as e:
        return f"Error locking computer: {str(e)}"

def logout_user():
    """Log out the current user"""
    try:
        if platform.system().lower() == "windows":
            subprocess.run(["shutdown", "/l"])
            return "Logging out user..."
        else:
            # Linux logout
            logout_commands = [
                ["gnome-session-quit", "--logout", "--no-prompt"],
                ["loginctl", "terminate-user", os.getenv("USER")],
                ["pkill", "-KILL", "-u", os.getenv("USER")]
            ]
            
            for cmd in logout_commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        return "Logging out user..."
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    continue
            
            return "Could not log out user. Logout command not available."
    
    except Exception as e:
        return f"Error logging out user: {str(e)}"

# ==================== BATTERY OPERATIONS ====================

def get_battery_status():
    """Get battery status and health information"""
    try:
        if not hasattr(psutil, "sensors_battery") or psutil.sensors_battery() is None:
            return "Battery information not available (desktop computer or no battery detected)"
        
        battery = psutil.sensors_battery()
        
        status = "Charging" if battery.power_plugged else "Discharging"
        percent = battery.percent
        time_left = "Unknown"
        
        if battery.secsleft != psutil.POWER_TIME_UNLIMITED and battery.secsleft != psutil.POWER_TIME_UNKNOWN:
            hours = battery.secsleft // 3600
            minutes = (battery.secsleft % 3600) // 60
            time_left = f"{hours}h {minutes}m"
        
        # Get additional battery health info (Linux)
        health_info = ""
        if platform.system().lower() == "linux":
            try:
                # Try to get battery health from /sys/class/power_supply/
                battery_path = "/sys/class/power_supply/BAT0"
                if os.path.exists(battery_path):
                    try:
                        with open(f"{battery_path}/capacity", "r") as f:
                            capacity = f.read().strip()
                        with open(f"{battery_path}/status", "r") as f:
                            bat_status = f.read().strip()
                        with open(f"{battery_path}/health", "r") as f:
                            health = f.read().strip()
                        health_info = f"\nHealth: {health}\nCapacity: {capacity}%\nStatus: {bat_status}"
                    except:
                        pass
            except:
                pass
        
        return f"""
Battery Status:
Charge Level: {percent}%
Status: {status}
Time Remaining: {time_left}
Power Plugged: {'Yes' if battery.power_plugged else 'No'}{health_info}
"""
    
    except Exception as e:
        return f"Error getting battery status: {str(e)}"

def optimize_battery():
    """Optimize battery performance"""
    try:
        optimizations = []
        
        if platform.system().lower() == "windows":
            # Windows battery optimization
            result = subprocess.run([
                "powershell", "-Command",
                "powercfg /setactive 961cc777-2547-4f9d-b4a6-679b2da8b814"  # Power saver mode
            ], capture_output=True, text=True)
            if result.returncode == 0:
                optimizations.append("✓ Activated power saver mode")
            
            # Reduce screen brightness
            subprocess.run([
                "powershell", "-Command",
                "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,30)"
            ], capture_output=True, text=True)
            optimizations.append("✓ Reduced screen brightness to 30%")
            
        else:
            # Linux battery optimization
            try:
                # Enable power saving mode
                result = subprocess.run(["sudo", "cpupower", "frequency-set", "-g", "powersave"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    optimizations.append("✓ Set CPU governor to powersave")
            except FileNotFoundError:
                pass
            
            # Reduce brightness
            subprocess.run([
                "bash", "-c",
                "xrandr --output $(xrandr | grep ' connected' | head -1 | cut -d' ' -f1) --brightness 0.3"
            ], capture_output=True, text=True)
            optimizations.append("✓ Reduced screen brightness to 30%")
        
        if optimizations:
            return "Battery optimization completed:\n" + "\n".join(optimizations)
        else:
            return "No battery optimizations were applied"
    
    except Exception as e:
        return f"Error optimizing battery: {str(e)}"

def enable_power_saving():
    """Enable power saving mode"""
    try:
        if platform.system().lower() == "windows":
            result = subprocess.run([
                "powershell", "-Command",
                "powercfg /setactive 961cc777-2547-4f9d-b4a6-679b2da8b814"
            ], capture_output=True, text=True)
            return "Power saving mode enabled" if result.returncode == 0 else "Failed to enable power saving mode"
        else:
            # Linux power saving
            commands_run = []
            try:
                subprocess.run(["sudo", "cpupower", "frequency-set", "-g", "powersave"], check=True)
                commands_run.append("✓ CPU governor set to powersave")
            except:
                pass
            
            try:
                subprocess.run(["sudo", "echo", "auto", ">", "/sys/bus/usb/devices/*/power/control"], shell=True)
                commands_run.append("✓ USB autosuspend enabled")
            except:
                pass
            
            return "Power saving mode enabled:\n" + "\n".join(commands_run) if commands_run else "Power saving mode partially enabled"
    
    except Exception as e:
        return f"Error enabling power saving: {str(e)}"

# ==================== CPU MONITORING ====================

def monitor_cpu_usage(threshold=80):
    """Monitor CPU usage and alert on spikes"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
        
        result = f"CPU Usage: {cpu_percent}%\n"
        result += f"Per Core: {', '.join([f'Core {i}: {usage}%' for i, usage in enumerate(cpu_per_core)])}\n"
        
        if cpu_percent > threshold:
            result += f"\n⚠️ HIGH CPU USAGE ALERT! ({cpu_percent}% > {threshold}%)\n"
            
            # Get top CPU consuming processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    if proc.info['cpu_percent'] > 5:  # Only show processes using >5% CPU
                        processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            result += "Top CPU consuming processes:\n"
            for proc in processes[:5]:
                result += f"  {proc['name']}: {proc['cpu_percent']}%\n"
        
        return result
    
    except Exception as e:
        return f"Error monitoring CPU: {str(e)}"

def detect_frozen_apps():
    """Detect and optionally kill frozen applications"""
    try:
        frozen_apps = []
        
        for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent']):
            try:
                # Check if process is not responding (zombie or stopped)
                if proc.info['status'] in [psutil.STATUS_ZOMBIE, psutil.STATUS_STOPPED]:
                    frozen_apps.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'status': proc.info['status']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if frozen_apps:
            result = "Detected frozen applications:\n"
            for app in frozen_apps:
                result += f"  PID {app['pid']}: {app['name']} (Status: {app['status']})\n"
            result += "\nUse 'kill process <name>' to terminate frozen apps."
            return result
        else:
            return "No frozen applications detected"
    
    except Exception as e:
        return f"Error detecting frozen apps: {str(e)}"

# ==================== SYSTEM INFO ====================

def get_system_info():
    """Get comprehensive system information"""
    try:
        info = f"""
System Information:
OS: {platform.system()} {platform.release()}
Architecture: {platform.architecture()[0]}
Processor: {platform.processor()}
Machine: {platform.machine()}
Node: {platform.node()}

CPU Usage: {psutil.cpu_percent(interval=1)}%
Memory Usage: {psutil.virtual_memory().percent}%
Boot Time: {datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')}
"""
        return info
    
    except Exception as e:
        return f"Error getting system info: {str(e)}"
