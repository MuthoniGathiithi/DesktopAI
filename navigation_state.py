import os
import json

class FileSystemNavigator:
    def __init__(self):
        self.current_path = os.path.expanduser("~")  # Start at home
        self.path_history = []
        self.state_file = os.path.join(os.path.dirname(__file__), "nav_state.json")
        self.load_state()
    
    def get_main_folders(self):
        """Return main system locations"""
        home = os.path.expanduser("~")
        main_folders = {
            "home": home,
            "desktop": os.path.join(home, "Desktop"),
            "documents": os.path.join(home, "Documents"), 
            "downloads": os.path.join(home, "Downloads"),
            "pictures": os.path.join(home, "Pictures"),
            "music": os.path.join(home, "Music"),
            "videos": os.path.join(home, "Videos")
        }
        
        # Add root for Linux/Mac or drives for Windows
        if os.name != 'nt':
            main_folders["root"] = "/"
        else:
            # Add available drives on Windows
            import string
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    main_folders[f"drive_{letter}"] = drive
        
        return main_folders
    
    def navigate_to(self, path):
        """Navigate to a specific path"""
        if path in self.get_main_folders():
            # Navigate to main folder
            new_path = self.get_main_folders()[path]
        elif os.path.isabs(path):
            # Absolute path
            new_path = path
        else:
            # Relative path from current location
            new_path = os.path.join(self.current_path, path)
        
        if os.path.exists(new_path) and os.path.isdir(new_path):
            self.path_history.append(self.current_path)
            self.current_path = new_path
            self.save_state()
            return True, f"Navigated to {new_path}"
        else:
            return False, f"Path does not exist: {new_path}"
    
    def go_back(self):
        """Go back to previous directory"""
        if self.path_history:
            self.current_path = self.path_history.pop()
            self.save_state()
            return True, f"Went back to {self.current_path}"
        else:
            return False, "No previous directory to go back to"
    
    def get_current_path(self):
        """Get current directory path"""
        return self.current_path
    
    def get_current_path_name(self):
        """Get friendly name of current path"""
        main_folders = self.get_main_folders()
        for name, path in main_folders.items():
            if self.current_path == path:
                return name.title()
        return os.path.basename(self.current_path) or self.current_path
    
    def save_state(self):
        """Save navigation state to file"""
        try:
            state = {
                "current_path": self.current_path,
                "path_history": self.path_history
            }
            with open(self.state_file, 'w') as f:
                json.dump(state, f)
        except:
            pass  # Ignore save errors
    
    def load_state(self):
        """Load navigation state from file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.current_path = state.get("current_path", os.path.expanduser("~"))
                    self.path_history = state.get("path_history", [])
        except:
            pass  # Ignore load errors

# Global navigator instance
navigator = FileSystemNavigator()
