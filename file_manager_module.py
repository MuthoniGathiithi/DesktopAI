#!/usr/bin/env python3
"""
File Manager Module for Desktop AI Agent
Handles file operations, organization, and management
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import logging

from module_framework import BaseModule, ModuleResult, ResultStatus

logger = logging.getLogger(__name__)


class FileManagerModule(BaseModule):
    """
    File management module
    Organizes, renames, compresses, and manages files
    """
    
    def __init__(self):
        super().__init__(
            name="file_manager",
            description="File management and organization",
            version="1.0.0"
        )
    
    def get_supported_actions(self) -> List[str]:
        """Get supported file management actions"""
        return [
            "organize_downloads",
            "batch_rename",
            "find_duplicates",
            "compress_files",
            "sort_photos",
            "move_by_extension",
            "create_folder_structure",
            "find_large_files",
            "cleanup_empty_folders",
            "search_files"
        ]
    
    def execute(self, action: str, parameters: Dict[str, Any]) -> ModuleResult:
        """Execute file management action"""
        try:
            if action == "organize_downloads":
                return self._organize_downloads(parameters)
            elif action == "batch_rename":
                return self._batch_rename(parameters)
            elif action == "find_duplicates":
                return self._find_duplicates(parameters)
            elif action == "compress_files":
                return self._compress_files(parameters)
            elif action == "sort_photos":
                return self._sort_photos(parameters)
            elif action == "move_by_extension":
                return self._move_by_extension(parameters)
            elif action == "create_folder_structure":
                return self._create_folder_structure(parameters)
            elif action == "find_large_files":
                return self._find_large_files(parameters)
            elif action == "cleanup_empty_folders":
                return self._cleanup_empty_folders(parameters)
            elif action == "search_files":
                return self._search_files(parameters)
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message=f"Unknown action: {action}",
                    data={}
                )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message=f"Error executing {action}",
                data={},
                error=str(e)
            )
    
    def _organize_downloads(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Organize downloads folder by file type"""
        downloads_dir = parameters.get("path", os.path.expanduser("~/Downloads"))
        
        if not os.path.exists(downloads_dir):
            return ModuleResult(
                status=ResultStatus.FAILED,
                message=f"Downloads folder not found: {downloads_dir}",
                data={}
            )
        
        # File type categories
        categories = {
            "Documents": [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt"],
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
            "Videos": [".mp4", ".mkv", ".avi", ".mov", ".flv"],
            "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
            "Code": [".py", ".js", ".java", ".cpp", ".c", ".html", ".css"],
            "Executables": [".exe", ".sh", ".deb", ".rpm"]
        }
        
        organized = {}
        
        for filename in os.listdir(downloads_dir):
            filepath = os.path.join(downloads_dir, filename)
            
            if os.path.isfile(filepath):
                ext = os.path.splitext(filename)[1].lower()
                
                # Find category
                category = "Other"
                for cat, extensions in categories.items():
                    if ext in extensions:
                        category = cat
                        break
                
                # Create category folder if needed
                category_path = os.path.join(downloads_dir, category)
                if not os.path.exists(category_path):
                    os.makedirs(category_path)
                
                # Move file
                try:
                    dest = os.path.join(category_path, filename)
                    shutil.move(filepath, dest)
                    organized[category] = organized.get(category, 0) + 1
                except Exception as e:
                    logger.warning(f"Failed to move {filename}: {e}")
        
        return ModuleResult(
            status=ResultStatus.SUCCESS,
            message=f"Organized {sum(organized.values())} files",
            data={"organized": organized}
        )
    
    def _batch_rename(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Batch rename files"""
        directory = parameters.get("path", os.getcwd())
        pattern = parameters.get("pattern", "file_")
        start_num = parameters.get("start", 1)
        
        if not os.path.exists(directory):
            return ModuleResult(
                status=ResultStatus.FAILED,
                message=f"Directory not found: {directory}",
                data={}
            )
        
        renamed = []
        counter = start_num
        
        for filename in sorted(os.listdir(directory)):
            filepath = os.path.join(directory, filename)
            
            if os.path.isfile(filepath):
                ext = os.path.splitext(filename)[1]
                new_name = f"{pattern}{counter}{ext}"
                new_path = os.path.join(directory, new_name)
                
                try:
                    os.rename(filepath, new_path)
                    renamed.append({"old": filename, "new": new_name})
                    counter += 1
                except Exception as e:
                    logger.warning(f"Failed to rename {filename}: {e}")
        
        return ModuleResult(
            status=ResultStatus.SUCCESS,
            message=f"Renamed {len(renamed)} files",
            data={"renamed": renamed}
        )
    
    def _find_duplicates(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Find duplicate files"""
        directory = parameters.get("path", os.getcwd())
        
        if not os.path.exists(directory):
            return ModuleResult(
                status=ResultStatus.FAILED,
                message=f"Directory not found: {directory}",
                data={}
            )
        
        # Hash files to find duplicates
        import hashlib
        file_hashes = {}
        duplicates = {}
        
        for root, dirs, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                
                try:
                    with open(filepath, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    
                    if file_hash in file_hashes:
                        if file_hash not in duplicates:
                            duplicates[file_hash] = [file_hashes[file_hash]]
                        duplicates[file_hash].append(filepath)
                    else:
                        file_hashes[file_hash] = filepath
                except Exception as e:
                    logger.warning(f"Failed to hash {filepath}: {e}")
        
        return ModuleResult(
            status=ResultStatus.SUCCESS,
            message=f"Found {len(duplicates)} duplicate groups",
            data={"duplicates": duplicates}
        )
    
    def _compress_files(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Compress files"""
        directory = parameters.get("path", os.getcwd())
        output = parameters.get("output", "archive.tar.gz")
        
        if not os.path.exists(directory):
            return ModuleResult(
                status=ResultStatus.FAILED,
                message=f"Directory not found: {directory}",
                data={}
            )
        
        try:
            shutil.make_archive(
                output.replace(".tar.gz", ""),
                "gztar",
                directory
            )
            
            size = os.path.getsize(output)
            return ModuleResult(
                status=ResultStatus.SUCCESS,
                message=f"Created archive: {output} ({size} bytes)",
                data={"archive": output, "size": size}
            )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Failed to compress files",
                data={},
                error=str(e)
            )
    
    def _sort_photos(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Sort photos by date"""
        directory = parameters.get("path", os.path.expanduser("~/Pictures"))
        
        if not os.path.exists(directory):
            return ModuleResult(
                status=ResultStatus.FAILED,
                message=f"Directory not found: {directory}",
                data={}
            )
        
        sorted_count = 0
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            
            if os.path.isfile(filepath):
                # Check if it's an image
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                    try:
                        # Get file modification time
                        mtime = os.path.getmtime(filepath)
                        date = datetime.fromtimestamp(mtime)
                        
                        # Create folder structure: Year/Month
                        year_folder = os.path.join(directory, str(date.year))
                        month_folder = os.path.join(year_folder, f"{date.month:02d}")
                        
                        os.makedirs(month_folder, exist_ok=True)
                        
                        # Move file
                        dest = os.path.join(month_folder, filename)
                        shutil.move(filepath, dest)
                        sorted_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to sort {filename}: {e}")
        
        return ModuleResult(
            status=ResultStatus.SUCCESS,
            message=f"Sorted {sorted_count} photos",
            data={"sorted": sorted_count}
        )
    
    def _move_by_extension(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Move files by extension"""
        directory = parameters.get("path", os.getcwd())
        
        if not os.path.exists(directory):
            return ModuleResult(
                status=ResultStatus.FAILED,
                message=f"Directory not found: {directory}",
                data={}
            )
        
        moved = {}
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            
            if os.path.isfile(filepath):
                ext = os.path.splitext(filename)[1].lower()
                if ext:
                    ext = ext[1:]  # Remove dot
                    ext_folder = os.path.join(directory, ext)
                    
                    os.makedirs(ext_folder, exist_ok=True)
                    
                    try:
                        dest = os.path.join(ext_folder, filename)
                        shutil.move(filepath, dest)
                        moved[ext] = moved.get(ext, 0) + 1
                    except Exception as e:
                        logger.warning(f"Failed to move {filename}: {e}")
        
        return ModuleResult(
            status=ResultStatus.SUCCESS,
            message=f"Moved {sum(moved.values())} files",
            data={"moved": moved}
        )
    
    def _create_folder_structure(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Create folder structure"""
        base_path = parameters.get("path", os.getcwd())
        structure = parameters.get("structure", {})
        
        if not structure:
            structure = {
                "Documents": ["Work", "Personal", "Projects"],
                "Media": ["Photos", "Videos", "Music"],
                "Archive": ["2024", "2025"]
            }
        
        created = []
        
        def create_structure(base, struct):
            for folder, subfolders in struct.items():
                folder_path = os.path.join(base, folder)
                os.makedirs(folder_path, exist_ok=True)
                created.append(folder_path)
                
                if isinstance(subfolders, list):
                    for subfolder in subfolders:
                        subfolder_path = os.path.join(folder_path, subfolder)
                        os.makedirs(subfolder_path, exist_ok=True)
                        created.append(subfolder_path)
        
        create_structure(base_path, structure)
        
        return ModuleResult(
            status=ResultStatus.SUCCESS,
            message=f"Created {len(created)} folders",
            data={"created": created}
        )
    
    def _find_large_files(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Find large files"""
        directory = parameters.get("path", os.getcwd())
        min_size = parameters.get("min_size", 100 * 1024 * 1024)  # 100MB default
        limit = parameters.get("limit", 20)
        
        if not os.path.exists(directory):
            return ModuleResult(
                status=ResultStatus.FAILED,
                message=f"Directory not found: {directory}",
                data={}
            )
        
        large_files = []
        
        for root, dirs, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    size = os.path.getsize(filepath)
                    if size >= min_size:
                        large_files.append({
                            "path": filepath,
                            "size": size,
                            "size_mb": size / (1024 * 1024)
                        })
                except Exception:
                    pass
        
        # Sort by size and limit
        large_files.sort(key=lambda x: x["size"], reverse=True)
        large_files = large_files[:limit]
        
        return ModuleResult(
            status=ResultStatus.SUCCESS,
            message=f"Found {len(large_files)} large files",
            data={"files": large_files}
        )
    
    def _cleanup_empty_folders(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Clean up empty folders"""
        directory = parameters.get("path", os.getcwd())
        
        if not os.path.exists(directory):
            return ModuleResult(
                status=ResultStatus.FAILED,
                message=f"Directory not found: {directory}",
                data={}
            )
        
        removed = []
        
        for root, dirs, files in os.walk(directory, topdown=False):
            for dirname in dirs:
                dirpath = os.path.join(root, dirname)
                try:
                    if not os.listdir(dirpath):
                        os.rmdir(dirpath)
                        removed.append(dirpath)
                except Exception as e:
                    logger.warning(f"Failed to remove {dirpath}: {e}")
        
        return ModuleResult(
            status=ResultStatus.SUCCESS,
            message=f"Removed {len(removed)} empty folders",
            data={"removed": removed}
        )
    
    def _search_files(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Search for files"""
        directory = parameters.get("path", os.getcwd())
        pattern = parameters.get("pattern", "*")
        file_type = parameters.get("type", None)
        
        if not os.path.exists(directory):
            return ModuleResult(
                status=ResultStatus.FAILED,
                message=f"Directory not found: {directory}",
                data={}
            )
        
        results = []
        
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if pattern.lower() in filename.lower():
                    if file_type is None or filename.endswith(file_type):
                        filepath = os.path.join(root, filename)
                        results.append({
                            "path": filepath,
                            "name": filename,
                            "size": os.path.getsize(filepath)
                        })
        
        return ModuleResult(
            status=ResultStatus.SUCCESS,
            message=f"Found {len(results)} files",
            data={"files": results}
        )


if __name__ == "__main__":
    module = FileManagerModule()
    print("File Manager Module Test")
    print(f"Supported actions: {module.get_supported_actions()}")
