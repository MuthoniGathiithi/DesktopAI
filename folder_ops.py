import os
import shutil
import glob
from datetime import datetime
from navigation_state import navigator

# ==================== NAVIGATION FUNCTIONS ====================

def navigate_to(location):
    """Navigate to a specific location"""
    success, message = navigator.navigate_to(location)
    return message

def go_back():
    """Go back to previous directory"""
    success, message = navigator.go_back()
    return message

def get_current_location():
    """Get current location info"""
    current_path = navigator.get_current_path()
    current_name = navigator.get_current_path_name()
    return f"Currently in: {current_name} ({current_path})"

def list_main_folders():
    """List main system folders"""
    main_folders = navigator.get_main_folders()
    return list(main_folders.keys())

# ==================== FOLDER OPERATIONS ====================

def create_folder(folder_name, location=None):
    """Create a folder at specified location or current location"""
    if location:
        success, message = navigator.navigate_to(location)
        if not success:
            return message
    
    current_path = navigator.get_current_path()
    folder_path = os.path.join(current_path, folder_name)
    
    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            return f"Folder '{folder_name}' created in {navigator.get_current_path_name()}"
        else:
            return f"Folder '{folder_name}' already exists in {navigator.get_current_path_name()}"
    except Exception as e:
        return f"Error creating folder: {str(e)}"

def delete_folder(folder_name):
    """Delete a folder from current location"""
    current_path = navigator.get_current_path()
    folder_path = os.path.join(current_path, folder_name)
    
    try:
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            shutil.rmtree(folder_path)  # Delete folder and all contents
            return f"Folder '{folder_name}' deleted from {navigator.get_current_path_name()}"
        else:
            return f"Folder '{folder_name}' does not exist in {navigator.get_current_path_name()}"
    except Exception as e:
        return f"Error deleting folder: {str(e)}"

def list_folders():
    """List folders in current location"""
    current_path = navigator.get_current_path()
    
    try:
        items = os.listdir(current_path)
        folders = [f for f in items if os.path.isdir(os.path.join(current_path, f))]
        
        if not folders:
            return f"No folders found in {navigator.get_current_path_name()}"
        
        return folders
    except Exception as e:
        return f"Error listing folders: {str(e)}"

# ==================== FILE OPERATIONS ====================

def create_file(file_name, content="", location=None):
    """Create a file at specified location or current location"""
    if location:
        success, message = navigator.navigate_to(location)
        if not success:
            return message
    
    current_path = navigator.get_current_path()
    file_path = os.path.join(current_path, file_name)
    
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        return f"File '{file_name}' created in {navigator.get_current_path_name()}"
    except Exception as e:
        return f"Error creating file: {str(e)}"

def delete_file(file_name):
    """Delete a file from current location"""
    current_path = navigator.get_current_path()
    file_path = os.path.join(current_path, file_name)
    
    try:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            os.remove(file_path)
            return f"File '{file_name}' deleted from {navigator.get_current_path_name()}"
        else:
            return f"File '{file_name}' does not exist in {navigator.get_current_path_name()}"
    except Exception as e:
        return f"Error deleting file: {str(e)}"

def list_files():
    """List files in current location"""
    current_path = navigator.get_current_path()
    
    try:
        items = os.listdir(current_path)
        files = [f for f in items if os.path.isfile(os.path.join(current_path, f))]
        
        if not files:
            return f"No files found in {navigator.get_current_path_name()}"
        
        return files
    except Exception as e:
        return f"Error listing files: {str(e)}"

def list_all():
    """List both files and folders in current location"""
    current_path = navigator.get_current_path()
    
    try:
        items = os.listdir(current_path)
        folders = [f + "/" for f in items if os.path.isdir(os.path.join(current_path, f))]
        files = [f for f in items if os.path.isfile(os.path.join(current_path, f))]
        
        all_items = folders + files
        
        if not all_items:
            return f"No items found in {navigator.get_current_path_name()}"
        
        return all_items
    except Exception as e:
        return f"Error listing items: {str(e)}"

def move_file(file_name, destination):
    """Move a file to another location"""
    current_path = navigator.get_current_path()
    source_path = os.path.join(current_path, file_name)
    
    # Handle destination
    if destination in navigator.get_main_folders():
        dest_path = navigator.get_main_folders()[destination]
    elif os.path.isabs(destination):
        dest_path = destination
    else:
        dest_path = os.path.join(current_path, destination)
    
    final_dest = os.path.join(dest_path, file_name)
    
    try:
        if not os.path.exists(source_path):
            return f"File '{file_name}' does not exist in current location"
        
        if not os.path.exists(dest_path):
            return f"Destination '{destination}' does not exist"
        
        shutil.move(source_path, final_dest)
        return f"File '{file_name}' moved to {destination}"
    except Exception as e:
        return f"Error moving file: {str(e)}"

def rename_file(old_name, new_name):
    """Rename a file in current location"""
    current_path = navigator.get_current_path()
    old_path = os.path.join(current_path, old_name)
    new_path = os.path.join(current_path, new_name)
    
    try:
        if not os.path.exists(old_path):
            return f"File '{old_name}' does not exist in current location"
        
        if os.path.exists(new_path):
            return f"File '{new_name}' already exists in current location"
        
        os.rename(old_path, new_path)
        return f"File renamed from '{old_name}' to '{new_name}'"
    except Exception as e:
        return f"Error renaming file: {str(e)}"

def search_files(pattern, search_in_subfolders=False):
    """Search for files matching a pattern"""
    current_path = navigator.get_current_path()
    
    try:
        if search_in_subfolders:
            # Recursive search
            matches = []
            for root, dirs, files in os.walk(current_path):
                for file in files:
                    if pattern.lower() in file.lower():
                        rel_path = os.path.relpath(os.path.join(root, file), current_path)
                        matches.append(rel_path)
        else:
            # Search only in current directory
            files = [f for f in os.listdir(current_path) if os.path.isfile(os.path.join(current_path, f))]
            matches = [f for f in files if pattern.lower() in f.lower()]
        
        if not matches:
            search_scope = "current folder and subfolders" if search_in_subfolders else "current folder"
            return f"No files found matching '{pattern}' in {search_scope}"
        
        return matches
    except Exception as e:
        return f"Error searching files: {str(e)}"

