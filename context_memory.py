import os
import json
import time
import psutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

# ==================== ADVANCED CONTEXT MEMORY & SESSION MANAGEMENT ====================

class ContextMemoryEngine:
    def __init__(self):
        self.db_path = os.path.join(os.path.expanduser("~"), ".desktop_ai_context.db")
        self.session_start = datetime.now()
        self.current_session_id = self._generate_session_id()
        self._init_database()
        self._start_activity_tracking()
    
    def _generate_session_id(self):
        """Generate unique session ID"""
        timestamp = str(int(time.time()))
        return hashlib.md5(timestamp.encode()).hexdigest()[:8]
    
    def _init_database(self):
        """Initialize SQLite database for context storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    start_time TEXT,
                    end_time TEXT,
                    duration INTEGER,
                    activity_count INTEGER
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    timestamp TEXT,
                    activity_type TEXT,
                    description TEXT,
                    file_path TEXT,
                    application TEXT,
                    context_data TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_access (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT,
                    file_name TEXT,
                    access_time TEXT,
                    access_type TEXT,
                    application TEXT,
                    project_context TEXT,
                    file_content_hash TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS app_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_name TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    duration INTEGER,
                    files_opened TEXT,
                    session_context TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            # Start new session
            self._start_new_session()
            
        except Exception as e:
            print(f"Error initializing context database: {e}")
    
    def _start_new_session(self):
        """Start a new session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sessions (id, start_time, activity_count)
                VALUES (?, ?, 0)
            ''', (self.current_session_id, self.session_start.isoformat()))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error starting session: {e}")
    
    def _start_activity_tracking(self):
        """Start background activity tracking"""
        # This would run in a separate thread in production
        self.track_activity("session_start", "Desktop AI session started", context_data={
            "session_id": self.current_session_id,
            "start_time": self.session_start.isoformat()
        })
    
    def track_activity(self, activity_type, description, file_path=None, application=None, context_data=None):
        """Track user activity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            context_json = json.dumps(context_data) if context_data else None
            
            cursor.execute('''
                INSERT INTO activities (session_id, timestamp, activity_type, description, 
                                     file_path, application, context_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.current_session_id,
                datetime.now().isoformat(),
                activity_type,
                description,
                file_path,
                application,
                context_json
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error tracking activity: {e}")
    
    def track_file_access(self, file_path, access_type, application=None, project_context=None):
        """Track file access for context building"""
        try:
            if not os.path.exists(file_path):
                return
            
            file_name = os.path.basename(file_path)
            
            # Generate content hash for change tracking
            content_hash = None
            try:
                with open(file_path, 'rb') as f:
                    content_hash = hashlib.md5(f.read()).hexdigest()
            except:
                pass
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO file_access (file_path, file_name, access_time, access_type,
                                       application, project_context, file_content_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                file_path,
                file_name,
                datetime.now().isoformat(),
                access_type,
                application,
                project_context,
                content_hash
            ))
            
            conn.commit()
            conn.close()
            
            # Also track as activity
            self.track_activity("file_access", f"{access_type} {file_name}", 
                              file_path=file_path, application=application,
                              context_data={"project": project_context})
            
        except Exception as e:
            print(f"Error tracking file access: {e}")
    
    def get_session_timeline(self, session_id=None, hours_back=None):
        """Get timeline of activities"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if session_id:
                cursor.execute('''
                    SELECT timestamp, activity_type, description, file_path, application
                    FROM activities
                    WHERE session_id = ?
                    ORDER BY timestamp DESC
                ''', (session_id,))
            elif hours_back:
                cutoff_time = (datetime.now() - timedelta(hours=hours_back)).isoformat()
                cursor.execute('''
                    SELECT timestamp, activity_type, description, file_path, application
                    FROM activities
                    WHERE timestamp > ?
                    ORDER BY timestamp DESC
                ''', (cutoff_time,))
            else:
                # Current session
                cursor.execute('''
                    SELECT timestamp, activity_type, description, file_path, application
                    FROM activities
                    WHERE session_id = ?
                    ORDER BY timestamp DESC
                ''', (self.current_session_id,))
            
            activities = cursor.fetchall()
            conn.close()
            
            if not activities:
                return "No activities found for the specified timeframe"
            
            result = "🕒 Activity Timeline:\n\n"
            for activity in activities[:50]:  # Show last 50
                timestamp, act_type, description, file_path, application = activity
                time_str = datetime.fromisoformat(timestamp).strftime("%H:%M:%S")
                
                result += f"{time_str} - {description}"
                if application:
                    result += f" ({application})"
                if file_path:
                    result += f"\n  📁 {os.path.basename(file_path)}"
                result += "\n\n"
            
            return result
            
        except Exception as e:
            return f"Error retrieving timeline: {e}"
    
    def what_was_i_doing(self, time_reference):
        """Answer 'what was I doing before lunch?' type questions"""
        try:
            # Parse time reference
            if "lunch" in time_reference.lower():
                # Assume lunch is around 12-13:00
                target_time = datetime.now().replace(hour=12, minute=0, second=0)
            elif "morning" in time_reference.lower():
                target_time = datetime.now().replace(hour=9, minute=0, second=0)
            elif "yesterday" in time_reference.lower():
                target_time = datetime.now() - timedelta(days=1)
            else:
                # Try to parse specific time
                target_time = datetime.now() - timedelta(hours=2)  # Default to 2 hours ago
            
            # Get activities around that time
            start_time = (target_time - timedelta(hours=1)).isoformat()
            end_time = (target_time + timedelta(hours=1)).isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, activity_type, description, file_path, application
                FROM activities
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
            ''', (start_time, end_time))
            
            activities = cursor.fetchall()
            conn.close()
            
            if not activities:
                return f"No activities found around {target_time.strftime('%Y-%m-%d %H:%M')}"
            
            result = f"🔍 What you were doing around {target_time.strftime('%H:%M')}:\n\n"
            
            # Group activities by type
            file_activities = []
            app_activities = []
            other_activities = []
            
            for activity in activities:
                timestamp, act_type, description, file_path, application = activity
                if file_path:
                    file_activities.append((timestamp, description, file_path, application))
                elif application:
                    app_activities.append((timestamp, description, application))
                else:
                    other_activities.append((timestamp, description))
            
            if file_activities:
                result += "📁 Files you were working with:\n"
                for timestamp, desc, file_path, app in file_activities[:10]:
                    time_str = datetime.fromisoformat(timestamp).strftime("%H:%M")
                    result += f"  {time_str} - {os.path.basename(file_path)}"
                    if app:
                        result += f" ({app})"
                    result += "\n"
                result += "\n"
            
            if app_activities:
                result += "🚀 Applications you were using:\n"
                for timestamp, desc, app in app_activities[:10]:
                    time_str = datetime.fromisoformat(timestamp).strftime("%H:%M")
                    result += f"  {time_str} - {desc} ({app})\n"
                result += "\n"
            
            return result
            
        except Exception as e:
            return f"Error retrieving activity history: {e}"
    
    def continue_where_left_off(self):
        """Restore last session state"""
        try:
            # Get last session's final activities
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get last 5 file activities
            cursor.execute('''
                SELECT DISTINCT file_path, application, MAX(timestamp) as last_access
                FROM activities
                WHERE file_path IS NOT NULL
                AND session_id != ?
                GROUP BY file_path
                ORDER BY last_access DESC
                LIMIT 5
            ''', (self.current_session_id,))
            
            recent_files = cursor.fetchall()
            
            # Get last 3 applications
            cursor.execute('''
                SELECT DISTINCT application, MAX(timestamp) as last_use
                FROM activities
                WHERE application IS NOT NULL
                AND session_id != ?
                GROUP BY application
                ORDER BY last_use DESC
                LIMIT 3
            ''', (self.current_session_id,))
            
            recent_apps = cursor.fetchall()
            conn.close()
            
            result = "🔄 Continuing where you left off...\n\n"
            
            if recent_files:
                result += "📁 Recent files to reopen:\n"
                for file_path, app, last_access in recent_files:
                    if os.path.exists(file_path):
                        time_str = datetime.fromisoformat(last_access).strftime("%Y-%m-%d %H:%M")
                        result += f"  • {os.path.basename(file_path)} (last accessed: {time_str})\n"
                        
                        # Try to open file (simplified - would need proper app launching)
                        self.track_activity("file_restore", f"Restored {os.path.basename(file_path)}", 
                                          file_path=file_path, application=app)
                result += "\n"
            
            if recent_apps:
                result += "🚀 Recent applications:\n"
                for app, last_use in recent_apps:
                    time_str = datetime.fromisoformat(last_use).strftime("%Y-%m-%d %H:%M")
                    result += f"  • {app} (last used: {time_str})\n"
                result += "\n"
            
            result += "Session restored! You can now continue your work."
            return result
            
        except Exception as e:
            return f"Error restoring session: {e}"
    
    def find_project_related_files(self, project_name):
        """Find all files related to a specific project"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Search in multiple ways
            search_patterns = [
                f"%{project_name}%",
                f"%{project_name.lower()}%",
                f"%{project_name.upper()}%"
            ]
            
            all_files = set()
            
            for pattern in search_patterns:
                # Search in file paths
                cursor.execute('''
                    SELECT DISTINCT file_path, file_name, MAX(access_time) as last_access
                    FROM file_access
                    WHERE file_path LIKE ? OR file_name LIKE ? OR project_context LIKE ?
                    GROUP BY file_path
                    ORDER BY last_access DESC
                ''', (pattern, pattern, pattern))
                
                files = cursor.fetchall()
                all_files.update(files)
                
                # Search in activity descriptions
                cursor.execute('''
                    SELECT DISTINCT file_path, description, MAX(timestamp) as last_activity
                    FROM activities
                    WHERE (description LIKE ? OR file_path LIKE ?) AND file_path IS NOT NULL
                    GROUP BY file_path
                    ORDER BY last_activity DESC
                ''', (pattern, pattern))
                
                activities = cursor.fetchall()
                for file_path, desc, timestamp in activities:
                    if file_path:
                        all_files.add((file_path, os.path.basename(file_path), timestamp))
            
            conn.close()
            
            if not all_files:
                return f"No files found related to project '{project_name}'"
            
            result = f"🔍 Files related to '{project_name}':\n\n"
            
            # Sort by last access time
            sorted_files = sorted(all_files, key=lambda x: x[2], reverse=True)
            
            for file_path, file_name, last_access in sorted_files[:20]:  # Show top 20
                if os.path.exists(file_path):
                    time_str = datetime.fromisoformat(last_access).strftime("%Y-%m-%d %H:%M")
                    file_size = os.path.getsize(file_path) / 1024  # KB
                    result += f"📄 {file_name}\n"
                    result += f"   Path: {file_path}\n"
                    result += f"   Last accessed: {time_str}\n"
                    result += f"   Size: {file_size:.1f} KB\n\n"
            
            return result
            
        except Exception as e:
            return f"Error finding project files: {e}"
    
    def search_entire_system(self, query, include_content=False):
        """Search for files across entire file system"""
        try:
            results = []
            search_paths = [
                os.path.expanduser("~"),  # Home directory
                "/usr/share",  # System files (Linux)
                "/opt",  # Optional software
            ]
            
            # Add Windows paths if on Windows
            if os.name == 'nt':
                search_paths.extend([
                    "C:\\Users",
                    "C:\\Program Files",
                    "C:\\Program Files (x86)"
                ])
            
            query_lower = query.lower()
            
            for search_path in search_paths:
                if not os.path.exists(search_path):
                    continue
                
                try:
                    for root, dirs, files in os.walk(search_path):
                        # Skip system directories that might cause issues
                        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
                        
                        for file in files:
                            if query_lower in file.lower():
                                file_path = os.path.join(root, file)
                                try:
                                    stat = os.stat(file_path)
                                    results.append({
                                        'path': file_path,
                                        'name': file,
                                        'size': stat.st_size,
                                        'modified': datetime.fromtimestamp(stat.st_mtime),
                                        'match_type': 'filename'
                                    })
                                except:
                                    continue
                        
                        # Limit results to prevent overwhelming output
                        if len(results) >= 100:
                            break
                    
                    if len(results) >= 100:
                        break
                        
                except PermissionError:
                    continue
                except Exception:
                    continue
            
            if not results:
                return f"No files found matching '{query}' in system search"
            
            # Sort by modification time (most recent first)
            results.sort(key=lambda x: x['modified'], reverse=True)
            
            result_text = f"🔍 System-wide search results for '{query}' ({len(results)} files found):\n\n"
            
            for file_info in results[:30]:  # Show top 30
                size_mb = file_info['size'] / (1024 * 1024)
                modified = file_info['modified'].strftime("%Y-%m-%d %H:%M")
                
                result_text += f"📄 {file_info['name']}\n"
                result_text += f"   Path: {file_info['path']}\n"
                result_text += f"   Size: {size_mb:.2f} MB\n"
                result_text += f"   Modified: {modified}\n\n"
            
            if len(results) > 30:
                result_text += f"... and {len(results) - 30} more files\n"
            
            # Track this search
            self.track_activity("system_search", f"Searched entire system for '{query}'", 
                              context_data={"query": query, "results_count": len(results)})
            
            return result_text
            
        except Exception as e:
            return f"Error searching system: {e}"
    
    def get_context_summary(self):
        """Get summary of current context and activities"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get session stats
            cursor.execute('''
                SELECT COUNT(*) FROM activities WHERE session_id = ?
            ''', (self.current_session_id,))
            activity_count = cursor.fetchone()[0]
            
            # Get recent files
            cursor.execute('''
                SELECT COUNT(DISTINCT file_path) FROM activities 
                WHERE session_id = ? AND file_path IS NOT NULL
            ''', (self.current_session_id,))
            files_count = cursor.fetchone()[0]
            
            # Get recent apps
            cursor.execute('''
                SELECT COUNT(DISTINCT application) FROM activities 
                WHERE session_id = ? AND application IS NOT NULL
            ''', (self.current_session_id,))
            apps_count = cursor.fetchone()[0]
            
            conn.close()
            
            session_duration = datetime.now() - self.session_start
            duration_str = str(session_duration).split('.')[0]  # Remove microseconds
            
            result = f"""📊 Current Session Context:

🕒 Session Duration: {duration_str}
📈 Total Activities: {activity_count}
📁 Files Accessed: {files_count}
🚀 Applications Used: {apps_count}

Session ID: {self.current_session_id}
Started: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}

Use these commands to explore your context:
• "What was I doing before lunch?" - Get activity timeline
• "Continue where I left off" - Restore last session
• "Find files related to ProjectX" - Search by project context
• "Search entire system for filename" - System-wide file search"""
            
            return result
            
        except Exception as e:
            return f"Error getting context summary: {e}"

# ==================== GLOBAL INSTANCE ====================

context_engine = ContextMemoryEngine()

# ==================== CONVENIENCE FUNCTIONS ====================

def track_user_activity(activity_type, description, file_path=None, application=None, context_data=None):
    """Track user activity"""
    context_engine.track_activity(activity_type, description, file_path, application, context_data)

def track_file_access(file_path, access_type, application=None, project_context=None):
    """Track file access"""
    context_engine.track_file_access(file_path, access_type, application, project_context)

def get_session_timeline(hours_back=None):
    """Get activity timeline"""
    return context_engine.get_session_timeline(hours_back=hours_back)

def what_was_i_doing(time_reference):
    """Answer what was I doing questions"""
    return context_engine.what_was_i_doing(time_reference)

def continue_where_left_off():
    """Continue from last session"""
    return context_engine.continue_where_left_off()

def find_project_files(project_name):
    """Find project related files"""
    return context_engine.find_project_related_files(project_name)

def search_entire_system(query):
    """Search entire file system"""
    return context_engine.search_entire_system(query)

def get_context_summary():
    """Get context summary"""
    return context_engine.get_context_summary()
