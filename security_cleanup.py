import os
import subprocess
import shutil
import tempfile
import platform
import psutil
import json
from datetime import datetime
from pathlib import Path

# ==================== SECURITY & CLEANUP OPERATIONS ====================

class SecurityCleanup:
    def __init__(self):
        self.cleanup_history = self._load_cleanup_history()
        self.suspicious_patterns = [
            "*.tmp", "*.temp", "*.log", "cache*", "temp*", 
            "*.bak", "*.old", "~*", ".DS_Store", "Thumbs.db"
        ]
        self.browser_cache_paths = self._get_browser_cache_paths()
    
    def _load_cleanup_history(self):
        """Load cleanup history"""
        try:
            history_file = os.path.join(os.path.expanduser("~"), ".desktop_ai_cleanup_history.json")
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def _save_cleanup_history(self, cleanup_info):
        """Save cleanup history"""
        try:
            self.cleanup_history.append(cleanup_info)
            # Keep only last 50 entries
            self.cleanup_history = self.cleanup_history[-50:]
            
            history_file = os.path.join(os.path.expanduser("~"), ".desktop_ai_cleanup_history.json")
            with open(history_file, 'w') as f:
                json.dump(self.cleanup_history, f, indent=2)
        except:
            pass
    
    def _get_browser_cache_paths(self):
        """Get browser cache paths for different operating systems"""
        home = os.path.expanduser("~")
        system = platform.system().lower()
        
        if system == "windows":
            return {
                "chrome": os.path.join(home, "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Cache"),
                "firefox": os.path.join(home, "AppData", "Local", "Mozilla", "Firefox", "Profiles"),
                "edge": os.path.join(home, "AppData", "Local", "Microsoft", "Edge", "User Data", "Default", "Cache"),
                "temp": os.path.join(os.environ.get("TEMP", ""), "*"),
                "recent": os.path.join(home, "AppData", "Roaming", "Microsoft", "Windows", "Recent")
            }
        else:  # Linux
            return {
                "chrome": os.path.join(home, ".cache", "google-chrome"),
                "firefox": os.path.join(home, ".cache", "mozilla"),
                "temp": "/tmp/*",
                "cache": os.path.join(home, ".cache"),
                "thumbnails": os.path.join(home, ".cache", "thumbnails")
            }
    
    def scan_for_threats(self, quick_scan=True):
        """Basic security scan for suspicious files and processes"""
        try:
            threats = []
            
            # Check for suspicious processes
            suspicious_processes = self._check_suspicious_processes()
            if suspicious_processes:
                threats.extend(suspicious_processes)
            
            # Check for suspicious files (if not quick scan)
            if not quick_scan:
                suspicious_files = self._check_suspicious_files()
                if suspicious_files:
                    threats.extend(suspicious_files)
            
            # Check system integrity
            system_issues = self._check_system_integrity()
            if system_issues:
                threats.extend(system_issues)
            
            if threats:
                result = f"⚠️ Security Scan Results - {len(threats)} issues found:\n\n"
                for threat in threats[:20]:  # Show first 20
                    result += f"• {threat['type']}: {threat['description']}\n"
                    if 'location' in threat:
                        result += f"  Location: {threat['location']}\n"
                    result += f"  Risk Level: {threat['risk']}\n\n"
                
                return result
            else:
                return "✅ Security scan completed - No threats detected"
        
        except Exception as e:
            return f"Error during security scan: {str(e)}"
    
    def _check_suspicious_processes(self):
        """Check for suspicious running processes"""
        suspicious = []
        suspicious_names = [
            "cryptolocker", "wannacry", "trojan", "malware", "virus",
            "keylogger", "rootkit", "backdoor", "spyware"
        ]
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_name = proc.info['name'].lower()
                    
                    # Check for suspicious names
                    for sus_name in suspicious_names:
                        if sus_name in proc_name:
                            suspicious.append({
                                'type': 'Suspicious Process',
                                'description': f"Process '{proc.info['name']}' (PID: {proc.info['pid']})",
                                'risk': 'HIGH'
                            })
                    
                    # Check for high resource usage
                    if proc.info['cpu_percent'] and proc.info['cpu_percent'] > 90:
                        suspicious.append({
                            'type': 'High CPU Usage',
                            'description': f"Process '{proc.info['name']}' using {proc.info['cpu_percent']}% CPU",
                            'risk': 'MEDIUM'
                        })
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except:
            pass
        
        return suspicious
    
    def _check_suspicious_files(self):
        """Check for suspicious files"""
        suspicious = []
        suspicious_extensions = ['.exe', '.scr', '.bat', '.cmd', '.pif', '.com']
        
        try:
            # Check Downloads folder for suspicious files
            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
            if os.path.exists(downloads_path):
                for root, dirs, files in os.walk(downloads_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_ext = os.path.splitext(file)[1].lower()
                        
                        if file_ext in suspicious_extensions:
                            suspicious.append({
                                'type': 'Suspicious File',
                                'description': f"Executable file in Downloads: {file}",
                                'location': file_path,
                                'risk': 'MEDIUM'
                            })
        except:
            pass
        
        return suspicious
    
    def _check_system_integrity(self):
        """Basic system integrity checks"""
        issues = []
        
        try:
            # Check available disk space
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    free_percent = (usage.free / usage.total) * 100
                    
                    if free_percent < 10:
                        issues.append({
                            'type': 'Low Disk Space',
                            'description': f"Drive {partition.device} has only {free_percent:.1f}% free space",
                            'risk': 'MEDIUM'
                        })
                except:
                    continue
            
            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                issues.append({
                    'type': 'High Memory Usage',
                    'description': f"Memory usage is at {memory.percent}%",
                    'risk': 'MEDIUM'
                })
        
        except:
            pass
        
        return issues
    
    def clean_system_junk(self, deep_clean=False):
        """Clean system junk files"""
        try:
            cleaned_files = 0
            freed_space = 0
            cleanup_results = []
            
            # Clean temporary files
            temp_result = self._clean_temp_files()
            if temp_result:
                cleanup_results.append(temp_result)
                cleaned_files += temp_result.get('files', 0)
                freed_space += temp_result.get('space', 0)
            
            # Clean browser cache
            if deep_clean:
                browser_result = self._clean_browser_cache()
                if browser_result:
                    cleanup_results.append(browser_result)
                    cleaned_files += browser_result.get('files', 0)
                    freed_space += browser_result.get('space', 0)
            
            # Clean system cache
            cache_result = self._clean_system_cache()
            if cache_result:
                cleanup_results.append(cache_result)
                cleaned_files += cache_result.get('files', 0)
                freed_space += cache_result.get('space', 0)
            
            # Empty trash/recycle bin
            trash_result = self._empty_trash()
            if trash_result:
                cleanup_results.append(trash_result)
                cleaned_files += trash_result.get('files', 0)
                freed_space += trash_result.get('space', 0)
            
            # Save cleanup history
            cleanup_info = {
                'timestamp': datetime.now().isoformat(),
                'files_cleaned': cleaned_files,
                'space_freed': freed_space,
                'deep_clean': deep_clean
            }
            self._save_cleanup_history(cleanup_info)
            
            freed_mb = freed_space / (1024 * 1024)
            result = f"🧹 System cleanup completed!\n\n"
            result += f"Files cleaned: {cleaned_files}\n"
            result += f"Space freed: {freed_mb:.1f} MB\n\n"
            result += "Cleanup details:\n"
            for cleanup in cleanup_results:
                result += f"• {cleanup['description']}\n"
            
            return result
        
        except Exception as e:
            return f"Error during system cleanup: {str(e)}"
    
    def _clean_temp_files(self):
        """Clean temporary files"""
        try:
            files_deleted = 0
            space_freed = 0
            
            # Get temp directory
            temp_dir = tempfile.gettempdir()
            
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)
                        
                        # Only delete files older than 1 day
                        if os.path.getmtime(file_path) < (datetime.now().timestamp() - 86400):
                            os.remove(file_path)
                            files_deleted += 1
                            space_freed += file_size
                    except:
                        continue
            
            return {
                'description': f"Temporary files ({files_deleted} files)",
                'files': files_deleted,
                'space': space_freed
            }
        except:
            return None
    
    def _clean_browser_cache(self):
        """Clean browser cache files"""
        try:
            files_deleted = 0
            space_freed = 0
            
            for browser, cache_path in self.browser_cache_paths.items():
                if browser in ['chrome', 'firefox', 'edge'] and os.path.exists(cache_path):
                    try:
                        for root, dirs, files in os.walk(cache_path):
                            for file in files:
                                try:
                                    file_path = os.path.join(root, file)
                                    file_size = os.path.getsize(file_path)
                                    os.remove(file_path)
                                    files_deleted += 1
                                    space_freed += file_size
                                except:
                                    continue
                    except:
                        continue
            
            return {
                'description': f"Browser cache ({files_deleted} files)",
                'files': files_deleted,
                'space': space_freed
            }
        except:
            return None
    
    def _clean_system_cache(self):
        """Clean system cache"""
        try:
            files_deleted = 0
            space_freed = 0
            
            if platform.system().lower() == "linux":
                cache_dirs = [
                    os.path.join(os.path.expanduser("~"), ".cache"),
                    "/var/cache",
                    "/tmp"
                ]
                
                for cache_dir in cache_dirs:
                    if os.path.exists(cache_dir) and os.access(cache_dir, os.W_OK):
                        try:
                            for root, dirs, files in os.walk(cache_dir):
                                for file in files:
                                    try:
                                        file_path = os.path.join(root, file)
                                        if os.path.getmtime(file_path) < (datetime.now().timestamp() - 86400):
                                            file_size = os.path.getsize(file_path)
                                            os.remove(file_path)
                                            files_deleted += 1
                                            space_freed += file_size
                                    except:
                                        continue
                        except:
                            continue
            
            return {
                'description': f"System cache ({files_deleted} files)",
                'files': files_deleted,
                'space': space_freed
            }
        except:
            return None
    
    def _empty_trash(self):
        """Empty trash/recycle bin"""
        try:
            files_deleted = 0
            space_freed = 0
            
            if platform.system().lower() == "linux":
                trash_path = os.path.join(os.path.expanduser("~"), ".local/share/Trash/files")
                if os.path.exists(trash_path):
                    for item in os.listdir(trash_path):
                        try:
                            item_path = os.path.join(trash_path, item)
                            if os.path.isfile(item_path):
                                file_size = os.path.getsize(item_path)
                                os.remove(item_path)
                                files_deleted += 1
                                space_freed += file_size
                            elif os.path.isdir(item_path):
                                dir_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                                             for dirpath, dirnames, filenames in os.walk(item_path)
                                             for filename in filenames)
                                shutil.rmtree(item_path)
                                files_deleted += 1
                                space_freed += dir_size
                        except:
                            continue
            
            return {
                'description': f"Trash/Recycle bin ({files_deleted} items)",
                'files': files_deleted,
                'space': space_freed
            }
        except:
            return None
    
    def remove_bloatware(self):
        """Detect and suggest removal of bloatware"""
        try:
            bloatware_patterns = [
                "mcafee", "norton", "avg", "avast", "toolbar", "ask.com",
                "conduit", "babylon", "delta-search", "sweetpacks", "mystart"
            ]
            
            detected_bloatware = []
            
            # Check installed programs (Windows)
            if platform.system().lower() == "windows":
                try:
                    result = subprocess.run([
                        "powershell", "-Command",
                        "Get-WmiObject -Class Win32_Product | Select-Object Name"
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        installed_programs = result.stdout.lower()
                        for pattern in bloatware_patterns:
                            if pattern in installed_programs:
                                detected_bloatware.append(pattern)
                except:
                    pass
            
            # Check running processes for bloatware
            for proc in psutil.process_iter(['name']):
                try:
                    proc_name = proc.info['name'].lower()
                    for pattern in bloatware_patterns:
                        if pattern in proc_name:
                            detected_bloatware.append(proc_name)
                except:
                    continue
            
            if detected_bloatware:
                result = "🚫 Potential bloatware detected:\n\n"
                for bloat in set(detected_bloatware):
                    result += f"• {bloat}\n"
                result += "\nRecommendation: Review and uninstall unnecessary software through your system's control panel."
                return result
            else:
                return "✅ No obvious bloatware detected"
        
        except Exception as e:
            return f"Error checking for bloatware: {str(e)}"
    
    def optimize_startup(self):
        """Analyze and suggest startup optimization"""
        try:
            if platform.system().lower() == "windows":
                # Windows startup programs
                result = subprocess.run([
                    "powershell", "-Command",
                    "Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    return f"Windows Startup Programs:\n{result.stdout}\n\nRecommendation: Disable unnecessary startup programs in Task Manager > Startup tab"
                else:
                    return "Could not retrieve startup programs information"
            else:
                # Linux startup applications
                autostart_dirs = [
                    os.path.join(os.path.expanduser("~"), ".config/autostart"),
                    "/etc/xdg/autostart"
                ]
                
                startup_apps = []
                for autostart_dir in autostart_dirs:
                    if os.path.exists(autostart_dir):
                        for file in os.listdir(autostart_dir):
                            if file.endswith('.desktop'):
                                startup_apps.append(file)
                
                if startup_apps:
                    result = "Linux Startup Applications:\n"
                    for app in startup_apps:
                        result += f"• {app}\n"
                    result += "\nRecommendation: Review autostart applications in ~/.config/autostart/"
                    return result
                else:
                    return "No custom startup applications found"
        
        except Exception as e:
            return f"Error analyzing startup: {str(e)}"
    
    def get_cleanup_history(self):
        """Get cleanup history"""
        if not self.cleanup_history:
            return "No cleanup history found"
        
        result = "🧹 Cleanup History:\n\n"
        total_space = 0
        total_files = 0
        
        for cleanup in self.cleanup_history[-10:]:  # Show last 10
            timestamp = datetime.fromisoformat(cleanup['timestamp']).strftime("%Y-%m-%d %H:%M")
            space_mb = cleanup['space_freed'] / (1024 * 1024)
            total_space += cleanup['space_freed']
            total_files += cleanup['files_cleaned']
            
            result += f"{timestamp}: Cleaned {cleanup['files_cleaned']} files ({space_mb:.1f} MB)\n"
            if cleanup['deep_clean']:
                result += "  (Deep clean)\n"
        
        total_space_mb = total_space / (1024 * 1024)
        result += f"\nTotal: {total_files} files, {total_space_mb:.1f} MB freed"
        
        return result

# ==================== GLOBAL INSTANCE ====================

security_cleanup = SecurityCleanup()

# ==================== CONVENIENCE FUNCTIONS ====================

def scan_security_threats(quick_scan=True):
    """Scan for security threats"""
    return security_cleanup.scan_for_threats(quick_scan)

def clean_computer(deep_clean=False):
    """Clean system junk"""
    return security_cleanup.clean_system_junk(deep_clean)

def check_bloatware():
    """Check for bloatware"""
    return security_cleanup.remove_bloatware()

def optimize_computer_startup():
    """Optimize startup"""
    return security_cleanup.optimize_startup()

def get_cleanup_history():
    """Get cleanup history"""
    return security_cleanup.get_cleanup_history()
