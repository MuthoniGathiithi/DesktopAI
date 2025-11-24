import os
import json
import shutil
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import subprocess

# ==================== DISASTER RECOVERY - UNDO DISASTER ====================

class DisasterRecoverySystem:
    def __init__(self):
        self.recovery_db = os.path.join(os.path.expanduser("~"), ".desktop_ai_recovery.db")
        self.recovery_vault = os.path.join(os.path.expanduser("~"), ".desktop_ai_vault")
        self.action_timeline = []
        self.monitoring_active = False
        self._init_recovery_system()
        
    def _init_recovery_system(self):
        """Initialize disaster recovery system"""
        try:
            # Create recovery vault
            os.makedirs(self.recovery_vault, exist_ok=True)
            
            # Initialize database
            conn = sqlite3.connect(self.recovery_db)
            cursor = conn.cursor()
            
            # Action timeline table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS action_timeline (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    action_type TEXT,
                    description TEXT,
                    affected_paths TEXT,
                    backup_location TEXT,
                    reversible INTEGER,
                    recovery_data TEXT,
                    user_initiated INTEGER
                )
            ''')
            
            # File snapshots table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT,
                    snapshot_path TEXT,
                    file_hash TEXT,
                    snapshot_time TEXT,
                    file_size INTEGER,
                    action_id INTEGER
                )
            ''')
            
            # System state table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    state_type TEXT,
                    state_data TEXT,
                    description TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            # Start monitoring
            self._start_system_monitoring()
            
        except Exception as e:
            print(f"Error initializing disaster recovery: {e}")
    
    def _start_system_monitoring(self):
        """Start background monitoring for disaster prevention"""
        try:
            if not self.monitoring_active:
                self.monitoring_active = True
                monitor_thread = threading.Thread(target=self._monitor_system_changes, daemon=True)
                monitor_thread.start()
        except Exception as e:
            print(f"Error starting monitoring: {e}")
    
    def _monitor_system_changes(self):
        """Background monitoring of system changes"""
        try:
            while self.monitoring_active:
                # Monitor critical directories for changes
                critical_dirs = [
                    os.path.join(os.path.expanduser("~"), "Documents"),
                    os.path.join(os.path.expanduser("~"), "Desktop"),
                    os.path.join(os.path.expanduser("~"), "Pictures")
                ]
                
                for directory in critical_dirs:
                    if os.path.exists(directory):
                        self._check_directory_changes(directory)
                
                time.sleep(30)  # Check every 30 seconds
        except Exception as e:
            print(f"Monitoring error: {e}")
    
    def _check_directory_changes(self, directory):
        """Check for changes in critical directories"""
        try:
            # This is a simplified version - in production, you'd use file system watchers
            pass
        except Exception as e:
            pass
    
    def record_action(self, action_type, description, affected_paths, user_initiated=True):
        """Record an action for potential recovery"""
        try:
            # Create backups before destructive actions
            backup_location = None
            recovery_data = {}
            
            if action_type in ['delete', 'move', 'overwrite', 'format']:
                backup_location = self._create_safety_backup(affected_paths)
                recovery_data = {
                    'original_paths': affected_paths,
                    'backup_location': backup_location,
                    'action_time': datetime.now().isoformat()
                }
            
            # Record in database
            conn = sqlite3.connect(self.recovery_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO action_timeline 
                (timestamp, action_type, description, affected_paths, backup_location, reversible, recovery_data, user_initiated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                action_type,
                description,
                json.dumps(affected_paths) if isinstance(affected_paths, list) else affected_paths,
                backup_location,
                1 if action_type in ['delete', 'move', 'overwrite'] else 0,
                json.dumps(recovery_data),
                1 if user_initiated else 0
            ))
            
            action_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return action_id
        
        except Exception as e:
            print(f"Error recording action: {e}")
            return None
    
    def _create_safety_backup(self, paths):
        """Create safety backup before destructive operations"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(self.recovery_vault, f"backup_{timestamp}")
            os.makedirs(backup_dir, exist_ok=True)
            
            if isinstance(paths, str):
                paths = [paths]
            
            backed_up_paths = []
            
            for path in paths:
                if os.path.exists(path):
                    try:
                        if os.path.isfile(path):
                            # Backup single file
                            filename = os.path.basename(path)
                            backup_path = os.path.join(backup_dir, filename)
                            shutil.copy2(path, backup_path)
                            backed_up_paths.append(backup_path)
                        
                        elif os.path.isdir(path):
                            # Backup directory
                            dirname = os.path.basename(path)
                            backup_path = os.path.join(backup_dir, dirname)
                            shutil.copytree(path, backup_path)
                            backed_up_paths.append(backup_path)
                    
                    except Exception as e:
                        print(f"Error backing up {path}: {e}")
                        continue
            
            return backup_dir if backed_up_paths else None
        
        except Exception as e:
            print(f"Error creating safety backup: {e}")
            return None
    
    def undo_last_action(self):
        """Undo the last reversible action"""
        try:
            conn = sqlite3.connect(self.recovery_db)
            cursor = conn.cursor()
            
            # Get the last reversible action
            cursor.execute('''
                SELECT * FROM action_timeline 
                WHERE reversible = 1 AND user_initiated = 1
                ORDER BY timestamp DESC 
                LIMIT 1
            ''')
            
            last_action = cursor.fetchone()
            
            if not last_action:
                return "❌ No reversible actions found"
            
            action_id, timestamp, action_type, description, affected_paths, backup_location, reversible, recovery_data, user_initiated = last_action
            
            # Attempt recovery
            recovery_result = self._perform_recovery(action_id, action_type, backup_location, recovery_data)
            
            conn.close()
            
            return f"🔄 Undo Result:\n{recovery_result}"
        
        except Exception as e:
            return f"Error during undo: {str(e)}"
    
    def undo_actions_from_time(self, minutes_ago):
        """Undo all actions from specified time period"""
        try:
            cutoff_time = datetime.now() - timedelta(minutes=minutes_ago)
            
            conn = sqlite3.connect(self.recovery_db)
            cursor = conn.cursor()
            
            # Get all reversible actions since cutoff time
            cursor.execute('''
                SELECT * FROM action_timeline 
                WHERE reversible = 1 AND timestamp > ? AND user_initiated = 1
                ORDER BY timestamp DESC
            ''', (cutoff_time.isoformat(),))
            
            actions = cursor.fetchall()
            
            if not actions:
                return f"❌ No reversible actions found in the last {minutes_ago} minutes"
            
            recovery_results = []
            recovered_count = 0
            
            for action in actions:
                action_id, timestamp, action_type, description, affected_paths, backup_location, reversible, recovery_data, user_initiated = action
                
                try:
                    result = self._perform_recovery(action_id, action_type, backup_location, recovery_data)
                    recovery_results.append(f"✅ {description}: {result}")
                    recovered_count += 1
                except Exception as e:
                    recovery_results.append(f"❌ {description}: Failed - {str(e)}")
            
            conn.close()
            
            result_text = f"🔄 Recovered {recovered_count}/{len(actions)} actions from last {minutes_ago} minutes:\n\n"
            result_text += "\n".join(recovery_results)
            
            return result_text
        
        except Exception as e:
            return f"Error during bulk undo: {str(e)}"
    
    def _perform_recovery(self, action_id, action_type, backup_location, recovery_data_str):
        """Perform the actual recovery operation"""
        try:
            if not backup_location or not os.path.exists(backup_location):
                return "❌ Backup not found - cannot recover"
            
            recovery_data = json.loads(recovery_data_str) if recovery_data_str else {}
            original_paths = recovery_data.get('original_paths', [])
            
            if isinstance(original_paths, str):
                original_paths = [original_paths]
            
            recovered_items = []
            
            # Restore from backup
            for backup_item in os.listdir(backup_location):
                backup_item_path = os.path.join(backup_location, backup_item)
                
                # Try to determine original location
                original_path = None
                for orig_path in original_paths:
                    if os.path.basename(orig_path) == backup_item:
                        original_path = orig_path
                        break
                
                if not original_path:
                    # Restore to Desktop if original location unknown
                    original_path = os.path.join(os.path.expanduser("~"), "Desktop", backup_item)
                
                try:
                    if os.path.isfile(backup_item_path):
                        # Restore file
                        os.makedirs(os.path.dirname(original_path), exist_ok=True)
                        shutil.copy2(backup_item_path, original_path)
                        recovered_items.append(original_path)
                    
                    elif os.path.isdir(backup_item_path):
                        # Restore directory
                        if os.path.exists(original_path):
                            shutil.rmtree(original_path)
                        shutil.copytree(backup_item_path, original_path)
                        recovered_items.append(original_path)
                
                except Exception as e:
                    print(f"Error restoring {backup_item}: {e}")
                    continue
            
            if recovered_items:
                return f"Restored {len(recovered_items)} items: {', '.join([os.path.basename(p) for p in recovered_items])}"
            else:
                return "❌ No items could be restored"
        
        except Exception as e:
            return f"Recovery failed: {str(e)}"
    
    def show_action_timeline(self, hours=24):
        """Show timeline of all actions for specified hours"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            conn = sqlite3.connect(self.recovery_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, action_type, description, reversible, user_initiated
                FROM action_timeline 
                WHERE timestamp > ?
                ORDER BY timestamp DESC
            ''', (cutoff_time.isoformat(),))
            
            actions = cursor.fetchall()
            conn.close()
            
            if not actions:
                return f"No actions recorded in the last {hours} hours"
            
            result_text = f"📅 Action Timeline (Last {hours} hours):\n\n"
            
            for timestamp, action_type, description, reversible, user_initiated in actions:
                time_str = datetime.fromisoformat(timestamp).strftime('%H:%M:%S')
                reversible_icon = "🔄" if reversible else "❌"
                user_icon = "👤" if user_initiated else "🤖"
                
                result_text += f"{time_str} {reversible_icon} {user_icon} {action_type.upper()}: {description}\n"
            
            result_text += f"\n🔄 = Reversible | ❌ = Not reversible | 👤 = User action | 🤖 = System action"
            
            return result_text
        
        except Exception as e:
            return f"Error showing timeline: {str(e)}"
    
    def find_deleted_files(self, days_ago=7):
        """Find files that were deleted in the specified period"""
        try:
            cutoff_time = datetime.now() - timedelta(days=days_ago)
            
            conn = sqlite3.connect(self.recovery_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, description, affected_paths, backup_location
                FROM action_timeline 
                WHERE action_type = 'delete' AND timestamp > ?
                ORDER BY timestamp DESC
            ''', (cutoff_time.isoformat(),))
            
            deleted_actions = cursor.fetchall()
            conn.close()
            
            if not deleted_actions:
                return f"No deleted files found in the last {days_ago} days"
            
            result_text = f"🗑️ Files deleted in the last {days_ago} days:\n\n"
            
            for timestamp, description, affected_paths, backup_location in deleted_actions:
                time_str = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M')
                recovery_status = "✅ Recoverable" if backup_location and os.path.exists(backup_location) else "❌ Not recoverable"
                
                result_text += f"📅 {time_str}\n"
                result_text += f"📄 {description}\n"
                result_text += f"🔄 {recovery_status}\n\n"
            
            result_text += "💡 Use 'undo last action' or 'undo from time' to recover files"
            
            return result_text
        
        except Exception as e:
            return f"Error finding deleted files: {str(e)}"
    
    def create_system_checkpoint(self, description="Manual checkpoint"):
        """Create a system checkpoint for major recovery"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            checkpoint_dir = os.path.join(self.recovery_vault, f"checkpoint_{timestamp}")
            os.makedirs(checkpoint_dir, exist_ok=True)
            
            # Backup critical user directories
            critical_dirs = [
                os.path.join(os.path.expanduser("~"), "Documents"),
                os.path.join(os.path.expanduser("~"), "Desktop"),
                os.path.join(os.path.expanduser("~"), "Pictures")
            ]
            
            backed_up_size = 0
            backed_up_files = 0
            
            for directory in critical_dirs:
                if os.path.exists(directory):
                    try:
                        dir_name = os.path.basename(directory)
                        backup_path = os.path.join(checkpoint_dir, dir_name)
                        
                        # Only backup files modified in last 7 days to save space
                        cutoff_time = time.time() - (7 * 24 * 60 * 60)
                        
                        for root, dirs, files in os.walk(directory):
                            for file in files:
                                file_path = os.path.join(root, file)
                                try:
                                    if os.path.getmtime(file_path) > cutoff_time:
                                        rel_path = os.path.relpath(file_path, directory)
                                        backup_file_path = os.path.join(backup_path, rel_path)
                                        os.makedirs(os.path.dirname(backup_file_path), exist_ok=True)
                                        shutil.copy2(file_path, backup_file_path)
                                        backed_up_size += os.path.getsize(file_path)
                                        backed_up_files += 1
                                except Exception as e:
                                    continue
                    
                    except Exception as e:
                        print(f"Error backing up {directory}: {e}")
                        continue
            
            # Record checkpoint in database
            conn = sqlite3.connect(self.recovery_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_states (timestamp, state_type, state_data, description)
                VALUES (?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                'checkpoint',
                json.dumps({
                    'checkpoint_path': checkpoint_dir,
                    'files_count': backed_up_files,
                    'total_size': backed_up_size
                }),
                description
            ))
            
            conn.commit()
            conn.close()
            
            size_mb = backed_up_size / (1024 * 1024)
            
            return f"✅ System checkpoint created!\n\nBacked up: {backed_up_files} files ({size_mb:.1f} MB)\nLocation: {checkpoint_dir}\nDescription: {description}"
        
        except Exception as e:
            return f"Error creating checkpoint: {str(e)}"
    
    def get_recovery_statistics(self):
        """Get disaster recovery statistics"""
        try:
            conn = sqlite3.connect(self.recovery_db)
            cursor = conn.cursor()
            
            # Count total actions
            cursor.execute('SELECT COUNT(*) FROM action_timeline')
            total_actions = cursor.fetchone()[0]
            
            # Count reversible actions
            cursor.execute('SELECT COUNT(*) FROM action_timeline WHERE reversible = 1')
            reversible_actions = cursor.fetchone()[0]
            
            # Count recent actions (last 24 hours)
            cutoff_time = (datetime.now() - timedelta(hours=24)).isoformat()
            cursor.execute('SELECT COUNT(*) FROM action_timeline WHERE timestamp > ?', (cutoff_time,))
            recent_actions = cursor.fetchone()[0]
            
            # Count checkpoints
            cursor.execute('SELECT COUNT(*) FROM system_states WHERE state_type = "checkpoint"')
            checkpoints = cursor.fetchone()[0]
            
            # Calculate vault size
            vault_size = 0
            if os.path.exists(self.recovery_vault):
                for root, dirs, files in os.walk(self.recovery_vault):
                    for file in files:
                        try:
                            vault_size += os.path.getsize(os.path.join(root, file))
                        except:
                            continue
            
            vault_size_mb = vault_size / (1024 * 1024)
            
            conn.close()
            
            result_text = f"📊 Disaster Recovery Statistics:\n\n"
            result_text += f"🔄 Total Actions Tracked: {total_actions}\n"
            result_text += f"✅ Reversible Actions: {reversible_actions}\n"
            result_text += f"📅 Actions (Last 24h): {recent_actions}\n"
            result_text += f"💾 System Checkpoints: {checkpoints}\n"
            result_text += f"🗄️ Recovery Vault Size: {vault_size_mb:.1f} MB\n\n"
            result_text += f"💡 Your data is protected with {reversible_actions} recoverable actions!"
            
            return result_text
        
        except Exception as e:
            return f"Error getting statistics: {str(e)}"

# ==================== GLOBAL INSTANCE ====================

disaster_recovery = DisasterRecoverySystem()

# ==================== CONVENIENCE FUNCTIONS ====================

def record_action(action_type, description, affected_paths, user_initiated=True):
    """Record action for disaster recovery"""
    return disaster_recovery.record_action(action_type, description, affected_paths, user_initiated)

def undo_last_disaster():
    """Undo the last action"""
    return disaster_recovery.undo_last_action()

def undo_actions_from_minutes(minutes):
    """Undo actions from specified minutes ago"""
    return disaster_recovery.undo_actions_from_time(minutes)

def show_disaster_timeline(hours=24):
    """Show action timeline"""
    return disaster_recovery.show_action_timeline(hours)

def find_my_deleted_files(days=7):
    """Find deleted files"""
    return disaster_recovery.find_deleted_files(days)

def create_recovery_checkpoint(description="Manual checkpoint"):
    """Create system checkpoint"""
    return disaster_recovery.create_system_checkpoint(description)

def get_disaster_recovery_stats():
    """Get recovery statistics"""
    return disaster_recovery.get_recovery_statistics()
