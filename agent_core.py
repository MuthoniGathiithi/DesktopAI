#!/usr/bin/env python3
"""
Linux Desktop AI Agent - Core Conversational Engine
Intelligent chatbot that understands context and executes system commands
"""

import json
import logging
import re
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentCore:
    """
    Main conversational agent core
    Handles natural language understanding and command execution
    """
    
    def __init__(self, ollama_host: str = "localhost", ollama_port: int = 11434):
        """Initialize the agent core"""
        self.ollama_url = f"http://{ollama_host}:{ollama_port}"
        self.model = "llama3.1:8b"
        self.conversation_history: List[Dict[str, str]] = []
        self.system_context = self._get_system_context()
        
        logger.info("Agent Core initialized")
    
    def _get_system_context(self) -> str:
        """Get current system context for the agent"""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return f"""Current System Status:
- CPU Usage: {cpu_percent}%
- RAM: {memory.percent}% ({memory.available // (1024**3)}GB free)
- Disk: {disk.percent}% ({disk.free // (1024**3)}GB free)
- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        except Exception as e:
            logger.error(f"Error getting system context: {e}")
            return "System status unavailable"
    
    def chat(self, user_message: str) -> str:
        """
        Process user message and generate response
        Handles both conversation and command execution
        """
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Determine if this is a command or conversation
        is_command = self._is_system_command(user_message)
        
        if is_command:
            # Execute system command
            response = self._handle_system_command(user_message)
        else:
            # Generate conversational response
            response = self._generate_conversation_response(user_message)
        
        # Add response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return response
    
    def _is_system_command(self, message: str) -> bool:
        """Determine if message is a system command request"""
        system_keywords = [
            "check", "clean", "organize", "install", "update", "remove",
            "monitor", "scan", "fix", "repair", "optimize", "backup",
            "restore", "delete", "move", "copy", "compress", "extract",
            "search", "find", "list", "show", "display", "report",
            "speed", "test", "diagnose", "troubleshoot", "debug"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in system_keywords)
    
    def _handle_system_command(self, message: str) -> str:
        """Handle system command execution"""
        # First try pattern-based command detection (fast)
        module, action = self._detect_command_pattern(message)
        
        if module:
            # Execute using detected pattern
            if module == "monitor":
                return self._execute_monitor_command(action)
            elif module == "cleanup":
                return self._execute_cleanup_command(action)
            elif module == "files":
                return self._execute_file_command(action, message)
            elif module == "network":
                return self._execute_network_command(action)
            elif module == "packages":
                return self._execute_package_command(action)
            elif module == "security":
                return self._execute_security_command(action)
            elif module == "dev":
                return self._execute_dev_command(action)
        
        # Fallback: use Llama for complex commands
        prompt = f"""Quick: what module for "{message}"? Answer: monitor|cleanup|files|network|packages|security|dev"""
        
        try:
            response = self._query_llama(prompt, timeout=15)
            module = response.strip().lower()
            
            if module == "monitor":
                return self._execute_monitor_command("status")
            elif module == "cleanup":
                return self._execute_cleanup_command("clean")
            elif module == "files":
                return self._execute_file_command("organize", message)
            elif module == "network":
                return self._execute_network_command("test")
            elif module == "packages":
                return self._execute_package_command("update")
            elif module == "security":
                return self._execute_security_command("scan")
            elif module == "dev":
                return self._execute_dev_command("status")
        except:
            pass
        
        return f"I can help with that, but let me understand better. Are you asking me to monitor, cleanup, organize files, check network, manage packages, run security checks, or work with developer tools?"
    
    def _detect_command_pattern(self, message: str) -> Tuple[Optional[str], str]:
        """Detect command using pattern matching (fast, no LLM)"""
        msg_lower = message.lower()
        
        # Monitor commands
        if any(word in msg_lower for word in ["check", "monitor", "status", "health", "cpu", "ram", "memory", "disk", "temp", "battery"]):
            if "cpu" in msg_lower:
                return ("monitor", "cpu")
            elif "memory" in msg_lower or "ram" in msg_lower:
                return ("monitor", "memory")
            elif "disk" in msg_lower or "storage" in msg_lower:
                return ("monitor", "disk")
            elif "temp" in msg_lower:
                return ("monitor", "temperature")
            else:
                return ("monitor", "health")
        
        # Cleanup commands
        if any(word in msg_lower for word in ["clean", "cleanup", "free", "space", "cache", "trash", "delete", "remove"]):
            if "cache" in msg_lower:
                return ("cleanup", "cache")
            elif "trash" in msg_lower:
                return ("cleanup", "trash")
            else:
                return ("cleanup", "disk")
        
        # File commands
        if any(word in msg_lower for word in ["organize", "sort", "find", "search", "duplicate", "rename", "move", "copy"]):
            if "organize" in msg_lower or "sort" in msg_lower:
                return ("files", "organize")
            elif "duplicate" in msg_lower:
                return ("files", "duplicate")
            elif "find" in msg_lower or "search" in msg_lower:
                return ("files", "search")
            else:
                return ("files", "manage")
        
        # Network commands
        if any(word in msg_lower for word in ["internet", "speed", "network", "wifi", "connection", "dns", "ping", "latency"]):
            if "speed" in msg_lower:
                return ("network", "speed")
            elif "dns" in msg_lower:
                return ("network", "dns")
            else:
                return ("network", "test")
        
        # Package commands
        if any(word in msg_lower for word in ["install", "update", "upgrade", "remove", "uninstall", "package", "software", "apt", "list"]):
            if "remove" in msg_lower or "uninstall" in msg_lower:
                return ("packages", "remove")
            elif "list" in msg_lower or "installed" in msg_lower:
                return ("packages", "list")
            elif "install" in msg_lower and "uninstall" not in msg_lower:
                return ("packages", "install")
            elif "update" in msg_lower or "upgrade" in msg_lower:
                return ("packages", "update")
            else:
                return ("packages", "update")
        
        # Security commands
        if any(word in msg_lower for word in ["security", "scan", "malware", "firewall", "safe", "threat", "virus"]):
            if "scan" in msg_lower:
                return ("security", "scan")
            elif "firewall" in msg_lower:
                return ("security", "firewall")
            else:
                return ("security", "check")
        
        # Developer commands
        if any(word in msg_lower for word in ["git", "docker", "code", "dev", "port", "server", "database", "repo"]):
            if "git" in msg_lower or "repo" in msg_lower:
                return ("dev", "git")
            elif "docker" in msg_lower:
                return ("dev", "docker")
            elif "port" in msg_lower:
                return ("dev", "port")
            else:
                return ("dev", "status")
        
        return (None, "")
    
    def _generate_conversation_response(self, message: str) -> str:
        """Generate natural conversational response"""
        message_lower = message.lower()
        
        # Quick responses for common greetings (no LLM needed)
        if message_lower in ["hi", "hello", "hey", "greetings"]:
            return "Hello! I'm your Linux desktop AI agent. I can help with system tasks, monitoring, cleanup, and much more. What can I do for you?"
        
        if message_lower in ["how are you?", "how are you", "how's it going?"]:
            return f"I'm running great! Your system looks healthy. {self._get_quick_status()}"
        
        if message_lower in ["what can you do?", "what can you do", "help", "capabilities"]:
            return """I can help with:
• System monitoring (health, CPU, RAM, disk, temperature)
• Cleanup (free up space, clear caches)
• File management (organize, find duplicates)
• Network tools (speed test, DNS, connectivity)
• Package management (install, update, remove)
• Security (scan, firewall, updates)
• Developer tools (Git, Docker, ports)

Just ask me naturally! 😊"""
        
        if message_lower in ["thanks", "thank you", "thanks!", "thank you!"]:
            return "You're welcome! Let me know if you need anything else. 😊"
        
        # For other messages, use a quick LLM prompt
        prompt = f"""You are a friendly Linux AI agent. Keep response to 1-2 sentences max.
User said: "{message}"

If it's a greeting or casual chat, respond warmly.
If it's about system tasks, offer to help.
Be concise and friendly."""
        
        return self._query_llama(prompt)
    
    def _get_quick_status(self) -> str:
        """Get quick system status without full context"""
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory()
            return f"CPU: {cpu}%, RAM: {mem.percent}%"
        except:
            return "System status good."
    
    def _query_llama(self, prompt: str, timeout: int = 120) -> str:
        """Query Llama model via Ollama API"""
        try:
            url = f"{self.ollama_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(url, json=payload, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "").strip()
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return "I'm having trouble thinking right now. Please try again."
        
        except requests.Timeout:
            logger.error(f"Ollama query timeout (>{timeout}s)")
            return "I'm thinking... that took too long. Can you rephrase?"
        except Exception as e:
            logger.error(f"Error querying Llama: {e}")
            return "I encountered an error. Please try again."
    
    def _execute_monitor_command(self, action: str) -> str:
        """Execute system monitoring command"""
        try:
            import psutil
            
            if "health" in action or "status" in action:
                cpu_temp = self._get_cpu_temp()
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                return f"""🖥️ **System Health Report**
├─ CPU: {cpu_percent}% (Temp: {cpu_temp}°C)
├─ RAM: {memory.percent}% ({memory.available // (1024**3)}GB free)
├─ Disk: {disk.percent}% ({disk.free // (1024**3)}GB free)
└─ Status: {'✅ Healthy' if cpu_percent < 80 and memory.percent < 80 else '⚠️ Monitor'}"""
            
            elif "cpu" in action:
                cpu_percent = psutil.cpu_percent(interval=1)
                return f"CPU Usage: {cpu_percent}% - {'Good' if cpu_percent < 50 else 'Moderate' if cpu_percent < 80 else 'High'}"
            
            elif "memory" in action or "ram" in action:
                memory = psutil.virtual_memory()
                return f"RAM Usage: {memory.percent}% ({memory.available // (1024**3)}GB available)"
            
            elif "disk" in action or "storage" in action:
                disk = psutil.disk_usage('/')
                return f"Disk Usage: {disk.percent}% ({disk.free // (1024**3)}GB free)"
            
            else:
                return "Checking system health..."
        
        except Exception as e:
            logger.error(f"Monitor command error: {e}")
            return f"I couldn't check that. Error: {str(e)}"
    
    def _execute_cleanup_command(self, action: str) -> str:
        """Execute system cleanup command"""
        try:
            import subprocess
            import shutil
            
            if "disk" in action or "space" in action or "clean" in action:
                # Get initial disk space
                import psutil
                disk_before = psutil.disk_usage('/').free
                
                # Clean common cache locations
                cache_dirs = [
                    "~/.cache",
                    "~/.local/share/Trash",
                    "/tmp"
                ]
                
                cleaned_size = 0
                for cache_dir in cache_dirs:
                    try:
                        expanded_dir = cache_dir.replace("~", "/root")  # Adjust for actual user
                        if shutil.os.path.exists(expanded_dir):
                            for item in shutil.os.listdir(expanded_dir):
                                item_path = shutil.os.path.join(expanded_dir, item)
                                if shutil.os.path.isfile(item_path):
                                    cleaned_size += shutil.os.path.getsize(item_path)
                                    shutil.os.remove(item_path)
                    except Exception as e:
                        logger.debug(f"Could not clean {cache_dir}: {e}")
                
                disk_after = psutil.disk_usage('/').free
                freed = (disk_after - disk_before) / (1024**3)
                
                return f"""🧹 **Cleanup Complete**
├─ Cleaned cache and temp files
├─ Space freed: {freed:.2f}GB
└─ Disk now: {psutil.disk_usage('/').percent}% full"""
            
            else:
                return "Running cleanup..."
        
        except Exception as e:
            logger.error(f"Cleanup command error: {e}")
            return f"Cleanup encountered an issue: {str(e)}"
    
    def _execute_file_command(self, action: str, message: str) -> str:
        """Execute file management command"""
        try:
            import os
            import shutil
            import hashlib
            from pathlib import Path
            from datetime import datetime
            
            # Try to import exifread, but make it optional
            try:
                import exifread
                has_exifread = True
            except ImportError:
                has_exifread = False
            
            if "organize" in action or "sort" in action:
                # Organize files by type
                if "download" in message.lower():
                    folder = os.path.expanduser("~/Downloads")
                elif "documents" in message.lower() or "docs" in message.lower():
                    folder = os.path.expanduser("~/Documents")
                elif "pictures" in message.lower() or "photos" in message.lower():
                    folder = os.path.expanduser("~/Pictures")
                else:
                    return "📁 Please specify a folder to organize (e.g., 'organize downloads' or 'sort pictures')"
                
                if not os.path.exists(folder):
                    return f"❌ Folder not found: {folder}"
                
                # Define file type categories
                categories = {
                    'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
                    'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'],
                    'archives': ['.zip', '.tar', '.gz', '.7z', '.rar'],
                    'audio': ['.mp3', '.wav', '.ogg', '.m4a', '.flac'],
                    'videos': ['.mp4', '.avi', '.mov', '.wmv', '.mkv', '.flv'],
                    'code': ['.py', '.js', '.html', '.css', '.c', '.cpp', '.java', '.php', '.sh'],
                }
                
                # Create category folders
                for category in categories.keys():
                    os.makedirs(os.path.join(folder, category), exist_ok=True)
                
                # Move files to appropriate folders
                moved_count = 0
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    if os.path.isfile(file_path):
                        ext = os.path.splitext(filename)[1].lower()
                        for category, extensions in categories.items():
                            if ext in extensions:
                                try:
                                    dest = os.path.join(folder, category, filename)
                                    # Handle duplicate filenames
                                    counter = 1
                                    while os.path.exists(dest):
                                        name, ext = os.path.splitext(filename)
                                        dest = os.path.join(folder, category, f"{name}_{counter}{ext}")
                                        counter += 1
                                    shutil.move(file_path, dest)
                                    moved_count += 1
                                except Exception as e:
                                    logger.error(f"Error moving {filename}: {e}")
                
                return f"✅ Organized {moved_count} files in {os.path.basename(folder)} into categories!"
            
            elif "rename" in action:
                # Batch rename files with pattern
                if " to " not in message.lower():
                    return "🔄 Please specify the renaming pattern. Example: 'rename files from *.jpg to photo_*.jpg'"
                
                try:
                    # Extract pattern from message
                    import re
                    match = re.search(r'rename\s+files?\s+from\s+([^\s]+)\s+to\s+([^\s]+)', message, re.IGNORECASE)
                    if not match:
                        return "❌ Invalid rename format. Use: 'rename files from OLD_PATTERN to NEW_PATTERN'"
                    
                    old_pattern = match.group(1)
                    new_pattern = match.group(2)
                    directory = os.getcwd()  # Current directory
                    
                    # Handle patterns like '*.txt' or 'file_*.jpg'
                    import fnmatch
                    files = [f for f in os.listdir(directory) if fnmatch.fnmatch(f, old_pattern)]
                    
                    renamed = 0
                    for i, filename in enumerate(sorted(files), 1):
                        name, ext = os.path.splitext(filename)
                        new_name = new_pattern.replace('*', str(i).zfill(3))  # Replace * with 001, 002, etc.
                        if not new_name.endswith(ext):
                            new_name += ext
                        
                        try:
                            os.rename(
                                os.path.join(directory, filename),
                                os.path.join(directory, new_name)
                            )
                            renamed += 1
                        except Exception as e:
                            logger.error(f"Error renaming {filename}: {e}")
                    
                    return f"✅ Renamed {renamed} files using pattern: {new_pattern}"
                
                except Exception as e:
                    return f"❌ Error during batch rename: {str(e)}"
            
            elif "duplicate" in action:
                # Find duplicate files by content hash
                if not os.path.exists(message):
                    return "❌ Please specify a valid folder to scan for duplicates"
                
                hashes = {}
                duplicates = []
                
                for root, _, files in os.walk(message):
                    for filename in files:
                        filepath = os.path.join(root, filename)
                        try:
                            # Calculate file hash
                            with open(filepath, 'rb') as f:
                                file_hash = hashlib.md5(f.read()).hexdigest()
                            
                            if file_hash in hashes:
                                duplicates.append((filepath, hashes[file_hash]))
                            else:
                                hashes[file_hash] = filepath
                        except Exception as e:
                            logger.error(f"Error processing {filepath}: {e}")
                
                if not duplicates:
                    return "✅ No duplicate files found!"
                
                # Create a report
                report = ["🔍 Found duplicate files:", ""]
                for dup, original in duplicates:
                    report.append(f"• {dup} (duplicate of {original})")
                
                return "\n".join(report[:10]) + ("\n... and more" if len(report) > 10 else "")
            
            elif "compress" in action or "zip" in action:
                # Compress old files
                try:
                    import zipfile
                    from datetime import datetime, timedelta
                    
                    days_old = 30  # Default: files older than 30 days
                    if any(word in message for word in ['week', 'month', 'year']):
                        if 'week' in message:
                            days_old = 7
                        elif 'month' in message:
                            days_old = 30
                        elif 'year' in message:
                            days_old = 365
                    
                    # Find old files
                    now = datetime.now()
                    old_files = []
                    for root, _, files in os.walk(os.getcwd()):
                        for file in files:
                            filepath = os.path.join(root, file)
                            file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                            if now - file_mtime > timedelta(days=days_old):
                                old_files.append(filepath)
                    
                    if not old_files:
                        return f"ℹ️ No files older than {days_old} days found to compress."
                    
                    # Create archive
                    timestamp = now.strftime("%Y%m%d_%H%M%S")
                    archive_name = f"old_files_{timestamp}.zip"
                    with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for file in old_files:
                            zipf.write(file, os.path.basename(file))
                    
                    return f"✅ Compressed {len(old_files)} files older than {days_old} days into {archive_name}"
                
                except Exception as e:
                    return f"❌ Error compressing files: {str(e)}"
            
            elif "photo" in action or "picture" in action:
                # Sort photos by date/EXIF
                if not os.path.exists(message):
                    return "❌ Please specify a folder containing photos to sort"
                
                if not has_exifread:
                    return "⚠️ exifread not installed. Install with: pip install exifread\nWill use file modification time instead."
                
                supported_formats = ['.jpg', '.jpeg', '.png', '.tiff', '.nef', '.cr2']
                photo_count = 0
                
                for filename in os.listdir(message):
                    if any(filename.lower().endswith(ext) for ext in supported_formats):
                        filepath = os.path.join(message, filename)
                        try:
                            # Try to get EXIF data if available
                            date_folder = None
                            if has_exifread:
                                try:
                                    with open(filepath, 'rb') as f:
                                        tags = exifread.process_file(f, stop_tag='DateTimeOriginal')
                                        
                                        if 'EXIF DateTimeOriginal' in tags:
                                            date_taken = str(tags['EXIF DateTimeOriginal'])
                                            date_obj = datetime.strptime(date_taken, '%Y:%m:%d %H:%M:%S')
                                            date_folder = date_obj.strftime('%Y-%m')
                                except:
                                    pass
                            
                            # Fallback to file modification time
                            if not date_folder:
                                mtime = os.path.getmtime(filepath)
                                date_obj = datetime.fromtimestamp(mtime)
                                date_folder = date_obj.strftime('%Y-%m')
                            
                            # Create date-based folder structure
                            dest_folder = os.path.join(message, 'Sorted', date_folder)
                            os.makedirs(dest_folder, exist_ok=True)
                            
                            # Move file
                            shutil.move(
                                filepath,
                                os.path.join(dest_folder, filename)
                            )
                            photo_count += 1
                                
                        except Exception as e:
                            logger.error(f"Error processing {filename}: {e}")
                
                if photo_count > 0:
                    return f"✅ Sorted {photo_count} photos into date-based folders in 'Sorted' directory"
                else:
                    return "❌ No photos found or an error occurred while sorting"
            
            elif "structure" in action or "create folder" in action:
                # Create smart folder structure
                if not message.strip():
                    return "❌ Please specify the type of folder structure to create (e.g., 'project', 'website', 'python')"
                
                structures = {
                    'project': ['docs', 'src', 'tests', 'data', 'notebooks', 'config'],
                    'website': ['css', 'js', 'images', 'assets', 'pages', 'templates'],
                    'python': ['project_name', 'project_name/tests', 'docs', 'scripts'],
                    'react': ['public', 'src/components', 'src/assets', 'src/hooks', 'src/utils'],
                    'data': ['raw', 'processed', 'output', 'notebooks', 'reports']
                }
                
                structure_name = message.lower().strip()
                if structure_name not in structures:
                    return f"❌ Unknown structure type. Available: {', '.join(structures.keys())}"
                
                # Create directories
                base_dir = structure_name + "_project" if structure_name in ['python', 'react'] else structure_name
                os.makedirs(base_dir, exist_ok=True)
                
                for folder in structures[structure_name]:
                    os.makedirs(os.path.join(base_dir, folder), exist_ok=True)
                    
                    # Add README files
                    if structure_name == 'python':
                        with open(os.path.join(base_dir, 'README.md'), 'w') as f:
                            f.write(f"# {base_dir}\n\nProject description here.")
                        with open(os.path.join(base_dir, 'requirements.txt'), 'w') as f:
                            f.write("# Project dependencies")
                    elif structure_name == 'website':
                        with open(os.path.join(base_dir, 'index.html'), 'w') as f:
                            f.write("<!DOCTYPE html>\n<html>\n<head>\n    <title>New Website</title>\n</head>\n<body>\n    <h1>Welcome to your new website!</h1>\n</body>\n</html>")
                
                return f"✅ Created {structure_name} folder structure in '{base_dir}/'"
            
            elif "find" in action or "search" in action:
                # Enhanced file search
                import fnmatch
                
                # Extract search pattern from message
                search_terms = message.lower().split()
                extensions = ['.txt', '.md', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.py', '.js', '.html', '.css']
                
                # Look for file extensions in the search terms
                search_ext = None
                for term in search_terms:
                    if term.startswith('*.') and len(term) > 2:
                        search_ext = term[1:].lower()
                        search_terms.remove(term)
                        break
                
                # Search in current directory by default
                search_dir = os.getcwd()
                if ' in ' in message.lower():
                    dir_part = message.lower().split(' in ')[-1].strip()
                    if os.path.isdir(dir_part):
                        search_dir = dir_part
                
                # Perform search
                matches = []
                for root, _, files in os.walk(search_dir):
                    for file in files:
                        filepath = os.path.join(root, file)
                        rel_path = os.path.relpath(filepath, search_dir)
                        
                        # Check extension filter
                        if search_ext and not file.lower().endswith(search_ext):
                            continue
                            
                        # Check if all search terms are in the filename
                        if all(term in file.lower() for term in search_terms):
                            # Get file info
                            try:
                                size = os.path.getsize(filepath)
                                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                                matches.append((rel_path, size, mtime))
                            except:
                                pass
                
                # Format results
                if not matches:
                    return "🔍 No matching files found."
                
                results = [f"🔍 Found {len(matches)} matching files:", ""]
                for i, (path, size, mtime) in enumerate(sorted(matches)[:10], 1):
                    size_kb = f"{size/1024:.1f}KB" if size < 1024*1024 else f"{size/(1024*1024):.1f}MB"
                    results.append(f"{i}. {path} ({size_kb}, modified {mtime.strftime('%Y-%m-%d')})")
                
                if len(matches) > 10:
                    results.append(f"... and {len(matches) - 10} more")
                
                return "\n".join(results)
            
            else:
                return """I can help with various file operations. Here's what I can do:
• Organize files by type (e.g., 'organize downloads')
• Batch rename files (e.g., 'rename files from *.jpg to photo_*.jpg')
• Find duplicate files (e.g., 'find duplicates in ~/Pictures')
• Compress old files (e.g., 'compress files older than 30 days')
• Sort photos by date (e.g., 'sort photos in ~/Pictures')
• Create folder structures (e.g., 'create project structure')
• Search for files (e.g., 'find budget.xlsx in ~/Documents')"""
        
        except Exception as e:
            logger.error(f"File command error: {e}")
            return f"❌ Error processing file operation: {str(e)}"
    
    def _execute_network_command(self, action: str) -> str:
        """Execute network command"""
        try:
            import subprocess
            import socket
            import re
            import time
            import json
            from urllib.request import urlopen
            from urllib.error import URLError
            
            # Try to import optional modules
            try:
                import speedtest
                has_speedtest = True
            except ImportError:
                has_speedtest = False
            
            try:
                import dns.resolver
                has_dns_resolver = True
            except ImportError:
                has_dns_resolver = False
            
            def check_internet_connectivity() -> str:
                """Check if internet connection is available"""
                test_urls = [
                    'https://www.google.com',
                    'https://www.cloudflare.com',
                    'https://www.github.com'
                ]
                
                results = []
                for url in test_urls:
                    try:
                        start_time = time.time()
                        with urlopen(url, timeout=5) as response:
                            if response.status == 200:
                                latency = int((time.time() - start_time) * 1000)  # ms
                                results.append(f"• {url}: ✅ Connected ({latency}ms)")
                    except Exception as e:
                        results.append(f"• {url}: ❌ {str(e)}")
                
                return "🌐 Internet Connectivity Test\n" + "\n".join(results)
            
            def run_speed_test() -> str:
                """Run internet speed test"""
                if not has_speedtest:
                    return "⚠️ speedtest-cli not installed. Install with: pip install speedtest-cli"
                
                try:
                    st = speedtest.Speedtest()
                    st.get_best_server()
                    
                    download_speed = st.download() / 1_000_000  # Convert to Mbps
                    upload_speed = st.upload() / 1_000_000  # Convert to Mbps
                    ping = st.results.ping
                    
                    return f"🚀 Internet Speed Test\n" \
                           f"• Download: {download_speed:.2f} Mbps\n" \
                           f"• Upload: {upload_speed:.2f} Mbps\n" \
                           f"• Ping: {ping:.2f} ms"
                except Exception as e:
                    return f"❌ Speed test failed: {str(e)}"
            
            def check_dns_resolution() -> str:
                """Check DNS resolution and response times"""
                test_domains = ['google.com', 'github.com', 'wikipedia.org']
                results = []
                
                # Always test system DNS
                dns_results = []
                for domain in test_domains:
                    try:
                        start_time = time.time()
                        ip = socket.gethostbyname(domain)
                        latency = int((time.time() - start_time) * 1000)  # ms
                        dns_results.append(f"{domain} → {ip} ({latency}ms)")
                    except Exception as e:
                        dns_results.append(f"{domain} ❌ {str(e)}")
                
                results.append(f"System DNS:\n  " + "\n  ".join(dns_results))
                
                # Test other DNS servers if dnspython is available
                if has_dns_resolver:
                    dns_servers = {
                        'Google': '8.8.8.8',
                        'Cloudflare': '1.1.1.1',
                        'OpenDNS': '208.67.222.222',
                    }
                    
                    for name, dns_ip in dns_servers.items():
                        dns_results = []
                        for domain in test_domains:
                            try:
                                start_time = time.time()
                                resolver = dns.resolver.Resolver()
                                resolver.nameservers = [dns_ip]
                                answers = resolver.resolve(domain, 'A')
                                ip = answers[0].address
                                latency = int((time.time() - start_time) * 1000)  # ms
                                dns_results.append(f"{domain} → {ip} ({latency}ms)")
                            except Exception as e:
                                dns_results.append(f"{domain} ❌ {str(e)}")
                        
                        results.append(f"{name} DNS ({dns_ip}):\n  " + "\n  ".join(dns_results))
                
                return "🔍 DNS Resolution Test\n" + "\n".join([f"• {r}" for r in results])
            
            def get_wifi_signal() -> str:
                """Get WiFi signal strength and info"""
                try:
                    # Linux-specific implementation using iwconfig
                    result = subprocess.run(['iwconfig'], capture_output=True, text=True)
                    if result.returncode != 0:
                        return "❌ Could not get WiFi information. Are you connected to WiFi?"
                    
                    # Parse iwconfig output
                    interface_match = re.search(r'^(\w+)\s+.*?ESSID:"([^"]+)"', result.stdout, re.MULTILINE | re.DOTALL)
                    signal_match = re.search(r'Signal level=(-?\d+) dBm', result.stdout)
                    
                    if not interface_match or not signal_match:
                        return "❌ Could not parse WiFi information."
                    
                    interface, ssid = interface_match.groups()
                    signal_level = int(signal_match.group(1))
                    
                    # Convert dBm to quality percentage (very rough approximation)
                    quality = min(100, max(0, (signal_level + 100) * 2))
                    
                    # Get IP address
                    ip_result = subprocess.run(
                        ['ip', '-4', 'addr', 'show', interface],
                        capture_output=True, text=True
                    )
                    ip_match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', ip_result.stdout)
                    ip_address = ip_match.group(1) if ip_match else 'Unknown'
                    
                    return f"📶 WiFi Information\n" \
                           f"• Interface: {interface}\n" \
                           f"• SSID: {ssid}\n" \
                           f"• Signal: {signal_level} dBm ({quality:.0f}%)\n" \
                           f"• IP Address: {ip_address}"
                
                except Exception as e:
                    return f"❌ Error getting WiFi info: {str(e)}"
            
            def run_network_diagnostics() -> str:
                """Run comprehensive network diagnostics"""
                results = ["🔧 Network Diagnostics"]
                
                # 1. Check network interfaces
                try:
                    ip_result = subprocess.run(
                        ['ip', 'addr', 'show'],
                        capture_output=True, text=True
                    )
                    interfaces = re.findall(r'^\d+: (\w+):', ip_result.stdout, re.MULTILINE)
                    results.append("\n📡 Network Interfaces:" + "".join(f"\n  • {iface}" for iface in interfaces))
                except Exception as e:
                    results.append(f"\n❌ Could not list network interfaces: {str(e)}")
                
                # 2. Check routing table
                try:
                    route_result = subprocess.run(
                        ['ip', 'route'],
                        capture_output=True, text=True
                    )
                    results.append("\n🛣️  Routing Table:")
                    for line in route_result.stdout.splitlines():
                        results.append(f"  • {line}")
                except Exception as e:
                    results.append(f"\n❌ Could not get routing table: {str(e)}")
                
                # 3. Check open ports
                try:
                    ss_result = subprocess.run(
                        ['ss', '-tuln'],
                        capture_output=True, text=True
                    )
                    results.append("\n🔌 Open Ports:")
                    for line in ss_result.stdout.splitlines():
                        if 'LISTEN' in line:
                            results.append(f"  • {line.strip()}")
                except Exception as e:
                    results.append(f"\n❌ Could not check open ports: {str(e)}")
                
                return "\n".join(results)
            
            # Main command router
            if "speed" in action or "internet" in action:
                return run_speed_test()
            
            elif "dns" in action:
                if "change" in action or "set" in action:
                    # Parse DNS server from message
                    dns_servers = {
                        'google': '8.8.8.8,8.8.4.4',
                        'cloudflare': '1.1.1.1,1.0.0.1',
                        'opendns': '208.67.222.222,208.67.220.220',
                    }
                    
                    for name, servers in dns_servers.items():
                        if name in action.lower():
                            try:
                                # This requires root privileges
                                subprocess.run(
                                    ['sudo', 'resolvectl', 'dns', 'eth0', *servers.split(',')],
                                    check=True
                                )
                                return f"✅ Changed DNS to {name.capitalize()} ({servers})"
                            except subprocess.CalledProcessError as e:
                                return f"❌ Failed to change DNS: {str(e)}\nNote: This operation requires root privileges."
                    
                    return "Please specify a valid DNS provider (Google, Cloudflare, or OpenDNS)"
                else:
                    return check_dns_resolution()
            
            elif "wifi" in action or "connection" in action:
                if "signal" in action or "strength" in action:
                    return get_wifi_signal()
                elif "scan" in action:
                    try:
                        result = subprocess.run(
                            ['nmcli', 'device', 'wifi', 'list'],
                            capture_output=True, text=True
                        )
                        if result.returncode != 0:
                            return "❌ Could not scan for WiFi networks. Is WiFi enabled?"
                        
                        networks = result.stdout.splitlines()
                        return "📡 Available WiFi Networks:\n" + "\n".join(f"  • {n.strip()}" for n in networks[1:6])
                    except Exception as e:
                        return f"❌ Error scanning WiFi: {str(e)}"
                else:
                    return check_internet_connectivity()
            
            elif "diagnose" in action or "troubleshoot" in action:
                return run_network_diagnostics()
            
            elif "ping" in action:
                # Extract host from message
                host_match = re.search(r'ping\s+(?:to\s+)?(\S+)', action, re.IGNORECASE)
                host = host_match.group(1) if host_match else 'google.com'
                
                try:
                    result = subprocess.run(
                        ['ping', '-c', '4', host],
                        capture_output=True, text=True
                    )
                    return f"🏓 PING {host}\n{result.stdout}"
                except Exception as e:
                    return f"❌ Ping failed: {str(e)}"
            
            elif "traceroute" in action or "trace" in action:
                # Extract host from message
                host_match = re.search(r'(?:traceroute|trace|to)\s+(\S+)', action, re.IGNORECASE)
                host = host_match.group(1) if host_match else 'google.com'
                
                try:
                    result = subprocess.run(
                        ['traceroute', '-m', '15', host],
                        capture_output=True, text=True
                    )
                    return f"🛣️  TRACEROUTE to {host}\n{result.stdout}"
                except Exception as e:
                    return f"❌ Traceroute failed: {str(e)}"
            
            else:
                return """I can help with various network tasks. Here's what I can do:
• Check internet connectivity
• Run speed tests
• Check/change DNS settings
• Show WiFi signal strength
• Scan for WiFi networks
• Run network diagnostics
• Ping hosts
• Run traceroute

Try: 'check internet speed', 'show wifi signal', or 'run network diagnostics'"""
        
        except ImportError as e:
            return f"❌ Missing required package: {str(e)}\nPlease install it with: pip install {e.name or 'speedtest-cli'}"
        except Exception as e:
            logger.error(f"Network command error: {e}")
            return f"❌ Network operation failed: {str(e)}"
    
    def _execute_package_command(self, action: str) -> str:
        """Execute package management command"""
        try:
            import subprocess
            import re
            
            def run_apt_command(command: list, needs_sudo: bool = True) -> str:
                """Helper to run apt commands with proper error handling"""
                try:
                    cmd = ['sudo'] + command if needs_sudo else command
                    result = subprocess.run(
                        cmd, 
                        capture_output=True, 
                        text=True,
                        timeout=300
                    )
                    return result.stdout if result.returncode == 0 else result.stderr
                except subprocess.TimeoutExpired:
                    return "❌ Command timed out"
                except Exception as e:
                    return f"❌ Error: {str(e)}"
            
            def list_installed_packages() -> str:
                """List top 20 largest installed packages"""
                try:
                    cmd = "dpkg-query -Wf '${Package}\t${Installed-Size}\n' | sort -k2 -rn | head -20"
                    result = subprocess.run(
                        cmd, shell=True, capture_output=True, text=True
                    )
                    
                    if result.returncode != 0:
                        return "❌ Failed to list installed packages"
                    
                    output = ["📦 Top 20 Largest Installed Packages:\n"]
                    for i, line in enumerate(result.stdout.splitlines(), 1):
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            pkg = parts[0]
                            size_kb = int(parts[1]) if parts[1].isdigit() else 0
                            size_mb = size_kb / 1024
                            output.append(f"{i}. {pkg} ({size_mb:.1f} MB)")
                    
                    return "\n".join(output)
                except Exception as e:
                    return f"❌ Error listing packages: {str(e)}"
            
            def check_security_updates() -> str:
                """Check for security updates"""
                try:
                    result = subprocess.run(
                        ['apt', 'list', '--upgradable'],
                        capture_output=True, text=True
                    )
                    
                    if result.returncode != 0 or not result.stdout.strip():
                        return "✅ Your system is up to date with security patches!"
                    
                    updates = result.stdout.strip().split('\n')
                    output = [f"🔒 {len(updates)} Security Updates Available:\n"]
                    for update in updates[:10]:
                        pkg = update.split('/')[0]
                        output.append(f"• {pkg}")
                    
                    if len(updates) > 10:
                        output.append(f"... and {len(updates) - 10} more")
                    
                    return "\n".join(output)
                except Exception as e:
                    return f"❌ Error checking updates: {str(e)}"
            
            # Main command router
            if "update" in action or "upgrade" in action:
                if "security" in action:
                    return check_security_updates()
                
                result = run_apt_command(['apt', 'update'])
                if result.startswith('❌'):
                    return result
                
                upgrade_result = run_apt_command(['apt', 'upgrade', '-y'])
                if upgrade_result.startswith('❌'):
                    return upgrade_result
                
                run_apt_command(['apt', 'autoremove', '-y'])
                return "✅ System packages updated successfully!"
            
            elif "install" in action:
                pkg_match = re.search(r'install\s+([a-zA-Z0-9_.-]+)', action, re.IGNORECASE)
                if not pkg_match:
                    return "❌ Please specify a package to install (e.g., 'install htop')"
                
                pkg_name = pkg_match.group(1)
                result = run_apt_command(['apt', 'install', '-y', pkg_name])
                if result.startswith('❌'):
                    return result
                return f"✅ Successfully installed {pkg_name}"
            
            elif "remove" in action or "uninstall" in action:
                pkg_match = re.search(r'(?:remove|uninstall)\s+([a-zA-Z0-9_.-]+)', action, re.IGNORECASE)
                if not pkg_match:
                    return "❌ Please specify a package to remove"
                
                pkg_name = pkg_match.group(1)
                result = run_apt_command(['apt', 'remove', '-y', pkg_name])
                if result.startswith('❌'):
                    return result
                
                run_apt_command(['apt', 'autoremove', '-y'])
                return f"✅ Successfully removed {pkg_name}"
            
            elif "list" in action or "installed" in action:
                return list_installed_packages()
            
            elif "search" in action:
                search_term = action.replace("search", "").strip()
                if not search_term:
                    return "❌ Please specify a search term"
                
                result = run_apt_command(['apt-cache', 'search', search_term], False)
                if not result or result.startswith('❌'):
                    return f"❌ No packages found matching '{search_term}'"
                
                packages = result.splitlines()
                return f"🔍 Found {len(packages)} packages:\n" + "\n".join(f"• {p.split(' - ')[0]}" for p in packages[:10])
            
            elif "fix" in action or "broken" in action:
                result = run_apt_command(['dpkg', '--configure', '-a'])
                result2 = run_apt_command(['apt', 'install', '-f', '-y'])
                return "🛠️ Attempted to fix broken packages"
            
            else:
                return """📦 Package Management Help:
• update/upgrade - Update all system packages
• update security - Check for security updates
• install <package> - Install a package
• remove <package> - Remove a package
• search <term> - Search for packages
• list installed - List installed packages
• fix broken - Fix broken packages"""
        
        except Exception as e:
            logger.error(f"Package command error: {e}")
            return f"❌ Package operation failed: {str(e)}"
    
    def _execute_security_command(self, action: str) -> str:
        """Execute security command"""
        try:
            import subprocess
            
            if "scan" in action or "malware" in action:
                # Check if ClamAV is installed
                result = subprocess.run(['which', 'clamscan'], capture_output=True)
                if result.returncode != 0:
                    return "❌ ClamAV not installed. Install with: sudo apt install clamav"
                
                # Run a quick scan on home directory
                try:
                    scan_result = subprocess.run(
                        ['clamscan', '-r', '--quiet', os.path.expanduser('~')],
                        capture_output=True, text=True, timeout=300
                    )
                    if scan_result.returncode == 0:
                        return "✅ Security scan complete - No threats detected!"
                    else:
                        return f"⚠️ Security scan found issues:\n{scan_result.stdout}"
                except subprocess.TimeoutExpired:
                    return "⏱️ Scan timed out - your system is large"
            
            elif "firewall" in action or "ufw" in action:
                # Check firewall status
                result = subprocess.run(['sudo', 'ufw', 'status'], capture_output=True, text=True)
                if result.returncode == 0:
                    return f"🔒 Firewall Status:\n{result.stdout}"
                else:
                    return "❌ Could not check firewall status. UFW may not be installed."
            
            elif "update" in action or "patch" in action:
                # Check for security updates
                result = subprocess.run(
                    ['apt', 'list', '--upgradable'],
                    capture_output=True, text=True
                )
                if result.returncode == 0 and result.stdout.strip():
                    updates = result.stdout.strip().split('\n')
                    return f"🔐 {len(updates)} security updates available. Run 'update packages' to install."
                else:
                    return "✅ Your system is up to date with security patches!"
            
            elif "permission" in action or "chmod" in action:
                # Check file permissions in home directory
                result = subprocess.run(
                    ['find', os.path.expanduser('~'), '-type', 'f', '-perm', '/077', '-ls'],
                    capture_output=True, text=True, timeout=30
                )
                if result.stdout.strip():
                    return f"⚠️ Found files with unusual permissions:\n{result.stdout[:500]}"
                else:
                    return "✅ File permissions look good!"
            
            elif "ssh" in action or "key" in action:
                # Check SSH key security
                ssh_dir = os.path.expanduser('~/.ssh')
                if os.path.exists(ssh_dir):
                    result = subprocess.run(
                        ['ls', '-la', ssh_dir],
                        capture_output=True, text=True
                    )
                    return f"🔐 SSH Keys:\n{result.stdout}"
                else:
                    return "ℹ️ No SSH directory found"
            
            else:
                return """🛡️ Security Help:
• scan - Scan for malware (requires ClamAV)
• firewall - Check firewall status
• update - Check for security updates
• permission - Check file permissions
• ssh - Check SSH keys
• login - Check failed login attempts"""
        
        except Exception as e:
            logger.error(f"Security command error: {e}")
            return f"❌ Security operation failed: {str(e)}"
    
    def _execute_dev_command(self, action: str) -> str:
        """Execute developer tools command"""
        try:
            import subprocess
            import os
            
            if "git" in action or "repo" in action:
                # Manage Git repositories
                if "pull" in action or "update" in action:
                    # Pull all repos in ~/projects
                    projects_dir = os.path.expanduser('~/projects')
                    if not os.path.exists(projects_dir):
                        return "❌ ~/projects directory not found"
                    
                    repos_updated = 0
                    for repo in os.listdir(projects_dir):
                        repo_path = os.path.join(projects_dir, repo)
                        if os.path.isdir(repo_path) and os.path.exists(os.path.join(repo_path, '.git')):
                            try:
                                subprocess.run(
                                    ['git', 'pull'],
                                    cwd=repo_path,
                                    capture_output=True,
                                    timeout=30
                                )
                                repos_updated += 1
                            except:
                                pass
                    
                    return f"✅ Updated {repos_updated} Git repositories"
                
                elif "status" in action:
                    # Show git status in current directory
                    result = subprocess.run(
                        ['git', 'status'],
                        capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        return f"📊 Git Status:\n{result.stdout}"
                    else:
                        return "❌ Not a git repository"
                
                else:
                    return "🔧 Git Commands:\n• pull all repos\n• status - Show git status"
            
            elif "docker" in action:
                # Docker management
                if "clean" in action or "cleanup" in action:
                    try:
                        # Remove unused containers
                        subprocess.run(['docker', 'container', 'prune', '-f'], capture_output=True, timeout=30)
                        # Remove unused images
                        subprocess.run(['docker', 'image', 'prune', '-f'], capture_output=True, timeout=30)
                        return "✅ Docker cleanup complete - removed unused containers and images"
                    except Exception as e:
                        return f"❌ Docker cleanup failed: {str(e)}"
                
                elif "list" in action or "ps" in action:
                    result = subprocess.run(
                        ['docker', 'ps', '-a'],
                        capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        return f"🐳 Docker Containers:\n{result.stdout}"
                    else:
                        return "❌ Docker not running or not installed"
                
                else:
                    return "🐳 Docker Commands:\n• clean - Cleanup unused containers/images\n• list - List containers"
            
            elif "port" in action:
                # Check port usage
                if "check" in action or "list" in action:
                    result = subprocess.run(
                        ['ss', '-tuln'],
                        capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        lines = result.stdout.splitlines()
                        return f"🔌 Open Ports:\n" + "\n".join(lines[1:11])  # Show first 10
                    else:
                        return "❌ Could not check ports"
                
                else:
                    return "🔌 Port Commands:\n• check - List open ports\n• list - Show all listening ports"
            
            elif "venv" in action or "virtual" in action:
                # Virtual environment management
                venv_path = os.path.expanduser('~/venv')
                if "create" in action:
                    try:
                        subprocess.run(
                            ['python3', '-m', 'venv', venv_path],
                            capture_output=True, timeout=60
                        )
                        return f"✅ Virtual environment created at {venv_path}"
                    except Exception as e:
                        return f"❌ Failed to create venv: {str(e)}"
                
                elif "activate" in action:
                    return f"To activate: source {venv_path}/bin/activate"
                
                else:
                    return "🐍 Venv Commands:\n• create - Create virtual environment\n• activate - Show activation command"
            
            else:
                return """🔧 Developer Tools Help:
• git pull all repos - Update all git repositories
• docker clean - Cleanup Docker
• check ports - List open ports
• create venv - Create virtual environment"""
        
        except Exception as e:
            logger.error(f"Dev command error: {e}")
            return f"❌ Developer tool operation failed: {str(e)}"
    
    def _get_cpu_temp(self) -> str:
        """Get CPU temperature"""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp_millidegrees = int(f.read().strip())
                return str(temp_millidegrees // 1000)
        except:
            return "N/A"


def main():
    """Main entry point"""
    agent = AgentCore()
    
    print("\n" + "="*60)
    print("🤖 Linux Desktop AI Agent")
    print("="*60)
    print("Type 'quit' to exit, 'help' for commands\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "quit":
                print("Agent: Goodbye! Have a great day! 👋")
                break
            
            if user_input.lower() == "help":
                print("""Agent: I can help with:
  • System monitoring (check health, CPU, RAM, disk)
  • Cleanup (free up space, clear caches)
  • File management (organize, find, deduplicate)
  • Network tools (speed test, DNS, connectivity)
  • Package management (install, update, remove)
  • Security (scan, firewall, updates)
  • Developer tools (Git, Docker, ports)
  
Just ask me naturally! 😊""")
                continue
            
            response = agent.chat(user_input)
            print(f"Agent: {response}\n")
        
        except KeyboardInterrupt:
            print("\nAgent: Goodbye! 👋")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"Agent: I encountered an error: {str(e)}\n")


if __name__ == "__main__":
    main()
