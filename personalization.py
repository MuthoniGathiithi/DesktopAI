import os
import json
import time
from datetime import datetime, timedelta
from collections import defaultdict, Counter

# ==================== PERSONALIZATION & HABITS ====================

class PersonalizationEngine:
    def __init__(self):
        self.user_data_file = os.path.join(os.path.expanduser("~"), ".desktop_ai_personalization.json")
        self.user_data = self._load_user_data()
        self.session_start = datetime.now()
        
    def _load_user_data(self):
        """Load user personalization data"""
        try:
            if os.path.exists(self.user_data_file):
                with open(self.user_data_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        
        return {
            "command_history": [],
            "app_usage": {},
            "file_patterns": {},
            "time_patterns": {},
            "shortcuts": {},
            "preferences": {
                "default_browser": None,
                "default_editor": None,
                "auto_organize": False,
                "backup_frequency": "weekly"
            },
            "workflows": {},
            "favorite_locations": [],
            "custom_commands": {}
        }
    
    def _save_user_data(self):
        """Save user personalization data"""
        try:
            with open(self.user_data_file, 'w') as f:
                json.dump(self.user_data, f, indent=2)
        except Exception as e:
            print(f"Error saving user data: {e}")
    
    def learn_command(self, command, success=True):
        """Learn from user commands"""
        try:
            timestamp = datetime.now().isoformat()
            hour = datetime.now().hour
            weekday = datetime.now().weekday()
            
            # Record command
            command_entry = {
                "command": command.lower(),
                "timestamp": timestamp,
                "hour": hour,
                "weekday": weekday,
                "success": success
            }
            
            self.user_data["command_history"].append(command_entry)
            
            # Keep only last 1000 commands
            if len(self.user_data["command_history"]) > 1000:
                self.user_data["command_history"] = self.user_data["command_history"][-1000:]
            
            # Update time patterns
            if hour not in self.user_data["time_patterns"]:
                self.user_data["time_patterns"][hour] = []
            self.user_data["time_patterns"][hour].append(command.lower())
            
            # Keep only last 50 commands per hour
            if len(self.user_data["time_patterns"][hour]) > 50:
                self.user_data["time_patterns"][hour] = self.user_data["time_patterns"][hour][-50:]
            
            self._save_user_data()
        except Exception as e:
            print(f"Error learning command: {e}")
    
    def learn_app_usage(self, app_name, duration_seconds=None):
        """Learn app usage patterns"""
        try:
            timestamp = datetime.now().isoformat()
            hour = datetime.now().hour
            
            if app_name not in self.user_data["app_usage"]:
                self.user_data["app_usage"][app_name] = {
                    "count": 0,
                    "total_duration": 0,
                    "last_used": timestamp,
                    "favorite_hours": [],
                    "usage_history": []
                }
            
            app_data = self.user_data["app_usage"][app_name]
            app_data["count"] += 1
            app_data["last_used"] = timestamp
            app_data["favorite_hours"].append(hour)
            
            if duration_seconds:
                app_data["total_duration"] += duration_seconds
            
            # Keep only last 100 hours
            if len(app_data["favorite_hours"]) > 100:
                app_data["favorite_hours"] = app_data["favorite_hours"][-100:]
            
            self._save_user_data()
        except Exception as e:
            print(f"Error learning app usage: {e}")
    
    def learn_file_pattern(self, file_path, action):
        """Learn file handling patterns"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            if not file_ext:
                return
            
            if file_ext not in self.user_data["file_patterns"]:
                self.user_data["file_patterns"][file_ext] = {
                    "actions": [],
                    "locations": [],
                    "apps": []
                }
            
            self.user_data["file_patterns"][file_ext]["actions"].append(action)
            self.user_data["file_patterns"][file_ext]["locations"].append(os.path.dirname(file_path))
            
            # Keep only last 50 entries
            for key in ["actions", "locations", "apps"]:
                if len(self.user_data["file_patterns"][file_ext][key]) > 50:
                    self.user_data["file_patterns"][file_ext][key] = \
                        self.user_data["file_patterns"][file_ext][key][-50:]
            
            self._save_user_data()
        except Exception as e:
            print(f"Error learning file pattern: {e}")
    
    def create_shortcut(self, shortcut_name, command):
        """Create custom shortcut"""
        try:
            self.user_data["shortcuts"][shortcut_name.lower()] = {
                "command": command,
                "created": datetime.now().isoformat(),
                "usage_count": 0
            }
            self._save_user_data()
            return f"Shortcut '{shortcut_name}' created for command '{command}'"
        except Exception as e:
            return f"Error creating shortcut: {e}"
    
    def use_shortcut(self, shortcut_name):
        """Use a custom shortcut"""
        try:
            shortcut_name = shortcut_name.lower()
            if shortcut_name in self.user_data["shortcuts"]:
                shortcut = self.user_data["shortcuts"][shortcut_name]
                shortcut["usage_count"] += 1
                shortcut["last_used"] = datetime.now().isoformat()
                self._save_user_data()
                return shortcut["command"]
            else:
                return None
        except Exception as e:
            return None
    
    def get_shortcuts(self):
        """Get all custom shortcuts"""
        if not self.user_data["shortcuts"]:
            return "No custom shortcuts created yet"
        
        result = "Custom Shortcuts:\n\n"
        for name, shortcut in self.user_data["shortcuts"].items():
            result += f"'{name}' → {shortcut['command']}\n"
            result += f"  Used {shortcut['usage_count']} times\n"
            if 'last_used' in shortcut:
                last_used = datetime.fromisoformat(shortcut['last_used']).strftime("%Y-%m-%d")
                result += f"  Last used: {last_used}\n"
            result += "\n"
        
        return result
    
    def suggest_commands(self):
        """Suggest commands based on current time and patterns"""
        try:
            current_hour = datetime.now().hour
            suggestions = []
            
            # Time-based suggestions
            if str(current_hour) in self.user_data["time_patterns"]:
                hour_commands = self.user_data["time_patterns"][str(current_hour)]
                command_counts = Counter(hour_commands)
                suggestions.extend([cmd for cmd, count in command_counts.most_common(3)])
            
            # Recent command patterns
            if self.user_data["command_history"]:
                recent_commands = [cmd["command"] for cmd in self.user_data["command_history"][-20:]]
                recent_counts = Counter(recent_commands)
                suggestions.extend([cmd for cmd, count in recent_counts.most_common(2)])
            
            # Remove duplicates and limit
            suggestions = list(dict.fromkeys(suggestions))[:5]
            
            if suggestions:
                return "Suggested commands for this time:\n" + "\n".join([f"• {cmd}" for cmd in suggestions])
            else:
                return "No command suggestions available yet. Keep using the system to build patterns!"
        except Exception as e:
            return f"Error getting suggestions: {e}"
    
    def suggest_apps(self):
        """Suggest apps based on usage patterns"""
        try:
            current_hour = datetime.now().hour
            suggestions = []
            
            for app, data in self.user_data["app_usage"].items():
                if data["favorite_hours"]:
                    hour_counts = Counter(data["favorite_hours"])
                    if current_hour in hour_counts and hour_counts[current_hour] >= 2:
                        suggestions.append((app, hour_counts[current_hour]))
            
            # Sort by frequency for this hour
            suggestions.sort(key=lambda x: x[1], reverse=True)
            
            if suggestions:
                result = "Suggested apps for this time:\n"
                for app, count in suggestions[:5]:
                    result += f"• {app} (used {count} times at this hour)\n"
                return result
            else:
                return "No app suggestions available yet. Launch apps to build patterns!"
        except Exception as e:
            return f"Error getting app suggestions: {e}"
    
    def create_workflow(self, workflow_name, commands):
        """Create a custom workflow"""
        try:
            self.user_data["workflows"][workflow_name.lower()] = {
                "commands": commands,
                "created": datetime.now().isoformat(),
                "usage_count": 0
            }
            self._save_user_data()
            return f"Workflow '{workflow_name}' created with {len(commands)} commands"
        except Exception as e:
            return f"Error creating workflow: {e}"
    
    def run_workflow(self, workflow_name):
        """Get commands for a workflow"""
        try:
            workflow_name = workflow_name.lower()
            if workflow_name in self.user_data["workflows"]:
                workflow = self.user_data["workflows"][workflow_name]
                workflow["usage_count"] += 1
                workflow["last_used"] = datetime.now().isoformat()
                self._save_user_data()
                return workflow["commands"]
            else:
                return None
        except Exception as e:
            return None
    
    def get_workflows(self):
        """Get all workflows"""
        if not self.user_data["workflows"]:
            return "No workflows created yet"
        
        result = "Custom Workflows:\n\n"
        for name, workflow in self.user_data["workflows"].items():
            result += f"'{name}' ({len(workflow['commands'])} commands)\n"
            result += f"  Used {workflow['usage_count']} times\n"
            result += f"  Commands: {', '.join(workflow['commands'][:3])}{'...' if len(workflow['commands']) > 3 else ''}\n\n"
        
        return result
    
    def add_favorite_location(self, path, name=None):
        """Add a favorite location"""
        try:
            if not os.path.exists(path):
                return f"Path {path} does not exist"
            
            location = {
                "path": path,
                "name": name or os.path.basename(path),
                "added": datetime.now().isoformat(),
                "visit_count": 0
            }
            
            # Check if already exists
            for loc in self.user_data["favorite_locations"]:
                if loc["path"] == path:
                    return f"Location {path} is already in favorites"
            
            self.user_data["favorite_locations"].append(location)
            self._save_user_data()
            return f"Added '{location['name']}' to favorite locations"
        except Exception as e:
            return f"Error adding favorite location: {e}"
    
    def visit_location(self, path):
        """Record visit to a location"""
        try:
            for location in self.user_data["favorite_locations"]:
                if location["path"] == path:
                    location["visit_count"] += 1
                    location["last_visited"] = datetime.now().isoformat()
                    self._save_user_data()
                    break
        except Exception as e:
            pass
    
    def get_favorite_locations(self):
        """Get favorite locations"""
        if not self.user_data["favorite_locations"]:
            return "No favorite locations added yet"
        
        result = "Favorite Locations:\n\n"
        # Sort by visit count
        sorted_locations = sorted(self.user_data["favorite_locations"], 
                                key=lambda x: x["visit_count"], reverse=True)
        
        for location in sorted_locations:
            result += f"📁 {location['name']}\n"
            result += f"   Path: {location['path']}\n"
            result += f"   Visits: {location['visit_count']}\n"
            if 'last_visited' in location:
                last_visit = datetime.fromisoformat(location['last_visited']).strftime("%Y-%m-%d")
                result += f"   Last visited: {last_visit}\n"
            result += "\n"
        
        return result
    
    def set_preference(self, key, value):
        """Set user preference"""
        try:
            if key in self.user_data["preferences"]:
                old_value = self.user_data["preferences"][key]
                self.user_data["preferences"][key] = value
                self._save_user_data()
                return f"Preference '{key}' changed from '{old_value}' to '{value}'"
            else:
                return f"Unknown preference: {key}"
        except Exception as e:
            return f"Error setting preference: {e}"
    
    def get_preferences(self):
        """Get user preferences"""
        result = "User Preferences:\n\n"
        for key, value in self.user_data["preferences"].items():
            result += f"{key.replace('_', ' ').title()}: {value}\n"
        
        return result
    
    def get_usage_stats(self):
        """Get usage statistics"""
        try:
            total_commands = len(self.user_data["command_history"])
            total_apps = len(self.user_data["app_usage"])
            total_shortcuts = len(self.user_data["shortcuts"])
            total_workflows = len(self.user_data["workflows"])
            
            # Most used commands
            if self.user_data["command_history"]:
                recent_commands = [cmd["command"] for cmd in self.user_data["command_history"][-100:]]
                top_commands = Counter(recent_commands).most_common(5)
            else:
                top_commands = []
            
            # Most used apps
            if self.user_data["app_usage"]:
                top_apps = sorted(self.user_data["app_usage"].items(), 
                                key=lambda x: x[1]["count"], reverse=True)[:5]
            else:
                top_apps = []
            
            result = f"""📊 Usage Statistics:

Total commands executed: {total_commands}
Apps tracked: {total_apps}
Custom shortcuts: {total_shortcuts}
Workflows created: {total_workflows}

Most used commands:"""
            
            for cmd, count in top_commands:
                result += f"\n  • {cmd} ({count} times)"
            
            result += "\n\nMost used apps:"
            for app, data in top_apps:
                result += f"\n  • {app} ({data['count']} times)"
            
            return result
        except Exception as e:
            return f"Error getting usage stats: {e}"
    
    def export_data(self, export_path=None):
        """Export user data"""
        try:
            if export_path is None:
                export_path = os.path.join(os.path.expanduser("~"), "desktop_ai_backup.json")
            
            with open(export_path, 'w') as f:
                json.dump(self.user_data, f, indent=2)
            
            return f"User data exported to {export_path}"
        except Exception as e:
            return f"Error exporting data: {e}"
    
    def import_data(self, import_path):
        """Import user data"""
        try:
            if not os.path.exists(import_path):
                return f"File {import_path} does not exist"
            
            with open(import_path, 'r') as f:
                imported_data = json.load(f)
            
            # Merge with existing data
            for key in imported_data:
                if key in self.user_data:
                    if isinstance(self.user_data[key], dict):
                        self.user_data[key].update(imported_data[key])
                    elif isinstance(self.user_data[key], list):
                        self.user_data[key].extend(imported_data[key])
                    else:
                        self.user_data[key] = imported_data[key]
            
            self._save_user_data()
            return f"User data imported from {import_path}"
        except Exception as e:
            return f"Error importing data: {e}"

# ==================== GLOBAL INSTANCE ====================

personalization = PersonalizationEngine()

# ==================== CONVENIENCE FUNCTIONS ====================

def learn_user_command(command, success=True):
    """Learn from user command"""
    personalization.learn_command(command, success)

def learn_user_app_usage(app_name, duration_seconds=None):
    """Learn app usage"""
    personalization.learn_app_usage(app_name, duration_seconds)

def create_user_shortcut(shortcut_name, command):
    """Create custom shortcut"""
    return personalization.create_shortcut(shortcut_name, command)

def use_user_shortcut(shortcut_name):
    """Use custom shortcut"""
    return personalization.use_shortcut(shortcut_name)

def get_user_shortcuts():
    """Get all shortcuts"""
    return personalization.get_shortcuts()

def suggest_user_commands():
    """Suggest commands"""
    return personalization.suggest_commands()

def suggest_user_apps():
    """Suggest apps"""
    return personalization.suggest_apps()

def create_user_workflow(workflow_name, commands):
    """Create workflow"""
    return personalization.create_workflow(workflow_name, commands)

def run_user_workflow(workflow_name):
    """Run workflow"""
    return personalization.run_workflow(workflow_name)

def get_user_workflows():
    """Get workflows"""
    return personalization.get_workflows()

def add_user_favorite_location(path, name=None):
    """Add favorite location"""
    return personalization.add_favorite_location(path, name)

def get_user_favorite_locations():
    """Get favorite locations"""
    return personalization.get_favorite_locations()

def set_user_preference(key, value):
    """Set preference"""
    return personalization.set_preference(key, value)

def get_user_preferences():
    """Get preferences"""
    return personalization.get_preferences()

def get_user_usage_stats():
    """Get usage statistics"""
    return personalization.get_usage_stats()

def export_user_data(export_path=None):
    """Export user data"""
    return personalization.export_data(export_path)

def import_user_data(import_path):
    """Import user data"""
    return personalization.import_data(import_path)
