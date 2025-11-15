import os
import subprocess
import platform
import json
import time
from datetime import datetime

# ==================== APPLICATION LAUNCHER ====================

class AppLauncher:
    def __init__(self):
        self.app_registry = self._build_app_registry()
        self.recent_apps = self._load_recent_apps()
        self.user_habits = self._load_user_habits()
    
    def _build_app_registry(self):
        """Build registry of common applications and their launch commands"""
        system = platform.system().lower()
        
        if system == "windows":
            return {
                # Development Tools
                "vscode": ["code"],
                "visual studio code": ["code"],
                "vs code": ["code"],
                "sublime": ["subl"],
                "notepad++": ["notepad++"],
                "atom": ["atom"],
                "pycharm": ["pycharm64.exe"],
                "intellij": ["idea64.exe"],
                
                # Browsers
                "chrome": ["chrome"],
                "firefox": ["firefox"],
                "edge": ["msedge"],
                "opera": ["opera"],
                "brave": ["brave"],
                
                # Office Applications
                "word": ["winword"],
                "excel": ["excel"],
                "powerpoint": ["powerpnt"],
                "outlook": ["outlook"],
                "onenote": ["onenote"],
                "teams": ["teams"],
                
                # Media & Communication
                "vlc": ["vlc"],
                "spotify": ["spotify"],
                "discord": ["discord"],
                "slack": ["slack"],
                "zoom": ["zoom"],
                "skype": ["skype"],
                "whatsapp": ["whatsapp"],
                
                # System Tools
                "calculator": ["calc"],
                "notepad": ["notepad"],
                "paint": ["mspaint"],
                "cmd": ["cmd"],
                "powershell": ["powershell"],
                "task manager": ["taskmgr"],
                "control panel": ["control"],
                "file explorer": ["explorer"],
                
                # Other Applications
                "photoshop": ["photoshop"],
                "gimp": ["gimp"],
                "blender": ["blender"],
                "obs": ["obs64"],
                "steam": ["steam"],
                "telegram": ["telegram"]
            }
        else:  # Linux/Unix
            return {
                # Development Tools
                "vscode": ["code"],
                "visual studio code": ["code"],
                "vs code": ["code"],
                "sublime": ["subl"],
                "vim": ["vim"],
                "emacs": ["emacs"],
                "gedit": ["gedit"],
                "nano": ["nano"],
                "pycharm": ["pycharm"],
                "intellij": ["idea"],
                
                # Browsers
                "chrome": ["google-chrome"],
                "chromium": ["chromium-browser"],
                "firefox": ["firefox"],
                "opera": ["opera"],
                "brave": ["brave-browser"],
                
                # Office Applications
                "libreoffice": ["libreoffice"],
                "writer": ["libreoffice", "--writer"],
                "calc": ["libreoffice", "--calc"],
                "impress": ["libreoffice", "--impress"],
                "office": ["libreoffice"],
                
                # Media & Communication
                "vlc": ["vlc"],
                "spotify": ["spotify"],
                "discord": ["discord"],
                "slack": ["slack"],
                "zoom": ["zoom"],
                "skype": ["skypeforlinux"],
                "telegram": ["telegram-desktop"],
                
                # System Tools
                "terminal": ["gnome-terminal"],
                "files": ["nautilus"],
                "file manager": ["nautilus"],
                "calculator": ["gnome-calculator"],
                "text editor": ["gedit"],
                "system monitor": ["gnome-system-monitor"],
                
                # Other Applications
                "gimp": ["gimp"],
                "blender": ["blender"],
                "obs": ["obs"],
                "steam": ["steam"],
                "camera": ["cheese"]
            }
    
    def _load_recent_apps(self):
        """Load recently used applications"""
        try:
            recent_file = os.path.join(os.path.expanduser("~"), ".desktop_ai_recent_apps.json")
            if os.path.exists(recent_file):
                with open(recent_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def _save_recent_apps(self):
        """Save recently used applications"""
        try:
            recent_file = os.path.join(os.path.expanduser("~"), ".desktop_ai_recent_apps.json")
            with open(recent_file, 'w') as f:
                json.dump(self.recent_apps, f)
        except:
            pass
    
    def _load_user_habits(self):
        """Load user habits and patterns"""
        try:
            habits_file = os.path.join(os.path.expanduser("~"), ".desktop_ai_habits.json")
            if os.path.exists(habits_file):
                with open(habits_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"morning_apps": [], "work_apps": [], "evening_apps": [], "patterns": {}}
    
    def _save_user_habits(self):
        """Save user habits and patterns"""
        try:
            habits_file = os.path.join(os.path.expanduser("~"), ".desktop_ai_habits.json")
            with open(habits_file, 'w') as f:
                json.dump(self.user_habits, f)
        except:
            pass
    
    def launch_app(self, app_name):
        """Launch an application by name"""
        try:
            app_name_lower = app_name.lower()
            
            # Check if app is in registry
            if app_name_lower in self.app_registry:
                cmd = self.app_registry[app_name_lower]
                
                # Try to launch the application
                if platform.system().lower() == "windows":
                    subprocess.Popen(cmd, shell=True)
                else:
                    subprocess.Popen(cmd)
                
                # Update recent apps
                self._update_recent_apps(app_name)
                self._learn_usage_pattern(app_name)
                
                return f"Successfully launched {app_name}"
            
            # Try to launch by direct command
            else:
                if platform.system().lower() == "windows":
                    subprocess.Popen(app_name, shell=True)
                else:
                    subprocess.Popen([app_name])
                
                self._update_recent_apps(app_name)
                return f"Attempted to launch {app_name}"
        
        except Exception as e:
            return f"Failed to launch {app_name}: {str(e)}"
    
    def _update_recent_apps(self, app_name):
        """Update recent apps list"""
        app_entry = {
            "name": app_name,
            "timestamp": datetime.now().isoformat(),
            "count": 1
        }
        
        # Check if app already in recent list
        for i, app in enumerate(self.recent_apps):
            if app["name"].lower() == app_name.lower():
                self.recent_apps[i]["count"] += 1
                self.recent_apps[i]["timestamp"] = datetime.now().isoformat()
                break
        else:
            self.recent_apps.append(app_entry)
        
        # Keep only last 20 apps
        self.recent_apps = sorted(self.recent_apps, key=lambda x: x["timestamp"], reverse=True)[:20]
        self._save_recent_apps()
    
    def _learn_usage_pattern(self, app_name):
        """Learn user usage patterns"""
        current_hour = datetime.now().hour
        
        # Categorize by time of day
        if 6 <= current_hour < 12:
            category = "morning_apps"
        elif 12 <= current_hour < 18:
            category = "work_apps"
        else:
            category = "evening_apps"
        
        if app_name not in self.user_habits[category]:
            self.user_habits[category].append(app_name)
        
        # Track patterns
        if app_name not in self.user_habits["patterns"]:
            self.user_habits["patterns"][app_name] = {"hours": [], "days": []}
        
        self.user_habits["patterns"][app_name]["hours"].append(current_hour)
        self.user_habits["patterns"][app_name]["days"].append(datetime.now().weekday())
        
        # Keep only last 50 entries per app
        for pattern_type in ["hours", "days"]:
            if len(self.user_habits["patterns"][app_name][pattern_type]) > 50:
                self.user_habits["patterns"][app_name][pattern_type] = \
                    self.user_habits["patterns"][app_name][pattern_type][-50:]
        
        self._save_user_habits()
    
    def get_recent_apps(self):
        """Get list of recently used applications"""
        if not self.recent_apps:
            return "No recent applications found"
        
        result = "Recently Used Applications:\n"
        for i, app in enumerate(self.recent_apps[:10], 1):
            timestamp = datetime.fromisoformat(app["timestamp"]).strftime("%m/%d %H:%M")
            result += f"{i}. {app['name']} (used {app['count']} times, last: {timestamp})\n"
        
        return result
    
    def open_recent_files(self, app_name=None):
        """Open recent files in specified application"""
        try:
            if platform.system().lower() == "windows":
                if app_name and app_name.lower() in ["word", "excel", "powerpoint"]:
                    # Open recent files in Office apps
                    subprocess.Popen([self.app_registry[app_name.lower()][0], "/r"])
                    return f"Opened recent files in {app_name}"
                else:
                    # Open Windows recent files
                    subprocess.Popen(["explorer", "shell:recent"])
                    return "Opened recent files"
            else:
                # Linux - open recent files in file manager
                subprocess.Popen(["nautilus", "recent:///"])
                return "Opened recent files"
        
        except Exception as e:
            return f"Error opening recent files: {str(e)}"
    
    def suggest_apps(self):
        """Suggest apps based on time and usage patterns"""
        current_hour = datetime.now().hour
        current_day = datetime.now().weekday()
        
        suggestions = []
        
        # Time-based suggestions
        if 6 <= current_hour < 12:
            suggestions.extend(self.user_habits.get("morning_apps", []))
        elif 12 <= current_hour < 18:
            suggestions.extend(self.user_habits.get("work_apps", []))
        else:
            suggestions.extend(self.user_habits.get("evening_apps", []))
        
        # Pattern-based suggestions
        for app, patterns in self.user_habits.get("patterns", {}).items():
            if current_hour in patterns.get("hours", []) or current_day in patterns.get("days", []):
                suggestions.append(app)
        
        # Remove duplicates and limit
        suggestions = list(set(suggestions))[:5]
        
        if suggestions:
            return "Suggested apps based on your habits:\n" + "\n".join([f"• {app}" for app in suggestions])
        else:
            return "No app suggestions available yet. Use apps to build your pattern!"
    
    def launch_morning_apps(self):
        """Launch usual morning applications"""
        morning_apps = self.user_habits.get("morning_apps", [])
        if not morning_apps:
            # Default morning apps
            morning_apps = ["chrome", "outlook", "teams"]
        
        launched = []
        for app in morning_apps[:5]:  # Limit to 5 apps
            try:
                result = self.launch_app(app)
                if "Successfully" in result:
                    launched.append(app)
                time.sleep(1)  # Small delay between launches
            except:
                continue
        
        if launched:
            return f"Launched morning apps: {', '.join(launched)}"
        else:
            return "No morning apps configured or available"
    
    def launch_work_apps(self):
        """Launch usual work applications"""
        work_apps = self.user_habits.get("work_apps", [])
        if not work_apps:
            # Default work apps
            work_apps = ["vscode", "chrome", "slack", "teams"]
        
        launched = []
        for app in work_apps[:5]:  # Limit to 5 apps
            try:
                result = self.launch_app(app)
                if "Successfully" in result:
                    launched.append(app)
                time.sleep(1)  # Small delay between launches
            except:
                continue
        
        if launched:
            return f"Launched work apps: {', '.join(launched)}"
        else:
            return "No work apps configured or available"
    
    def list_available_apps(self):
        """List all available applications in registry"""
        result = "Available Applications:\n\n"
        
        categories = {
            "Development": ["vscode", "sublime", "pycharm", "intellij", "atom"],
            "Browsers": ["chrome", "firefox", "edge", "opera", "brave"],
            "Office": ["word", "excel", "powerpoint", "outlook", "teams"],
            "Media": ["vlc", "spotify", "discord", "slack"],
            "System": ["calculator", "notepad", "file explorer", "terminal"]
        }
        
        for category, apps in categories.items():
            result += f"{category}:\n"
            for app in apps:
                if app in self.app_registry:
                    result += f"  • {app}\n"
            result += "\n"
        
        return result
    
    def open_camera(self):
        """Open camera application"""
        try:
            if platform.system().lower() == "windows":
                subprocess.Popen(["start", "microsoft.windows.camera:"], shell=True)
                return "Camera application opened"
            else:
                # Try different camera apps for Linux
                camera_apps = ["cheese", "guvcview", "kamoso", "camorama"]
                for app in camera_apps:
                    try:
                        subprocess.Popen([app])
                        return f"Camera opened with {app}"
                    except FileNotFoundError:
                        continue
                return "No camera application found. Install 'cheese' or 'guvcview'"
        
        except Exception as e:
            return f"Error opening camera: {str(e)}"

# ==================== GLOBAL INSTANCE ====================

app_launcher = AppLauncher()

# ==================== CONVENIENCE FUNCTIONS ====================

def launch_application(app_name):
    """Launch an application by name"""
    return app_launcher.launch_app(app_name)

def get_recent_applications():
    """Get recently used applications"""
    return app_launcher.get_recent_apps()

def open_recent_files(app_name=None):
    """Open recent files"""
    return app_launcher.open_recent_files(app_name)

def suggest_applications():
    """Suggest applications based on usage patterns"""
    return app_launcher.suggest_apps()

def launch_morning_routine():
    """Launch morning applications"""
    return app_launcher.launch_morning_apps()

def launch_work_routine():
    """Launch work applications"""
    return app_launcher.launch_work_apps()

def list_available_applications():
    """List all available applications"""
    return app_launcher.list_available_apps()

def open_camera():
    """Open camera application"""
    return app_launcher.open_camera()
