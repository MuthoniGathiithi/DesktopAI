import os
import shutil
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

# ==================== SAFETY NET - MISTAKE PREVENTION AI ====================

class SafetyNetEngine:
    def __init__(self):
        self.action_history = []
        self.undo_stack = []
        self.safety_rules = self._load_safety_rules()
        self.max_undo_actions = 50
    
    def _load_safety_rules(self):
        """Load safety rules and thresholds"""
        return {
            'large_file_delete_threshold': 100,  # Warn if deleting 100+ files
            'recent_file_threshold': 24,  # Hours - warn if files modified recently
            'large_folder_size_mb': 1000,  # Warn for folders > 1GB
            'backup_check_extensions': ['.docx', '.xlsx', '.pptx', '.pdf', '.py', '.js', '.html'],
            'critical_folders': ['Documents', 'Desktop', 'Pictures', 'Videos', 'Downloads'],
            'system_folders': ['System32', 'Windows', 'Program Files', '/usr', '/etc', '/var']
        }
    
    def check_delete_safety(self, paths):
        """Check if delete operation is safe"""
        warnings = []
        file_count = 0
        total_size = 0
        recent_files = []
        important_files = []
        
        try:
            for path in paths if isinstance(paths, list) else [paths]:
                if not os.path.exists(path):
                    continue
                
                if os.path.isfile(path):
                    file_count += 1
                    size = os.path.getsize(path)
                    total_size += size
                    
                    # Check if file was modified recently
                    mod_time = datetime.fromtimestamp(os.path.getmtime(path))
                    if (datetime.now() - mod_time).total_seconds() < self.safety_rules['recent_file_threshold'] * 3600:
                        recent_files.append((path, mod_time))
                    
                    # Check if it's an important file type
                    ext = os.path.splitext(path)[1].lower()
                    if ext in self.safety_rules['backup_check_extensions']:
                        important_files.append(path)
                
                elif os.path.isdir(path):
                    # Count files in directory
                    for root, dirs, files in os.walk(path):
                        file_count += len(files)
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                size = os.path.getsize(file_path)
                                total_size += size
                                
                                # Check recent modifications
                                mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                                if (datetime.now() - mod_time).total_seconds() < self.safety_rules['recent_file_threshold'] * 3600:
                                    recent_files.append((file_path, mod_time))
                                
                                # Check important files
                                ext = os.path.splitext(file_path)[1].lower()
                                if ext in self.safety_rules['backup_check_extensions']:
                                    important_files.append(file_path)
                            except:
                                continue
            
            # Generate warnings
            if file_count >= self.safety_rules['large_file_delete_threshold']:
                warnings.append(f"⚠️ You're about to delete {file_count} files!")
            
            if recent_files:
                warnings.append(f"⚠️ {len(recent_files)} files were modified in the last {self.safety_rules['recent_file_threshold']} hours:")
                for file_path, mod_time in recent_files[:10]:  # Show first 10
                    time_str = mod_time.strftime("%Y-%m-%d %H:%M")
                    warnings.append(f"   • {os.path.basename(file_path)} (modified: {time_str})")
                if len(recent_files) > 10:
                    warnings.append(f"   ... and {len(recent_files) - 10} more recent files")
            
            if important_files:
                warnings.append(f"⚠️ {len(important_files)} important files (documents, code, etc.) will be deleted:")
                for file_path in important_files[:10]:
                    warnings.append(f"   • {os.path.basename(file_path)}")
                if len(important_files) > 10:
                    warnings.append(f"   ... and {len(important_files) - 10} more important files")
            
            total_size_mb = total_size / (1024 * 1024)
            if total_size_mb > 100:
                warnings.append(f"⚠️ Total size to delete: {total_size_mb:.1f} MB")
            
            # Check for critical folders
            for path in paths if isinstance(paths, list) else [paths]:
                path_name = os.path.basename(path)
                if any(critical in path_name for critical in self.safety_rules['critical_folders']):
                    warnings.append(f"⚠️ You're deleting from a critical folder: {path_name}")
            
            return {
                'safe': len(warnings) == 0,
                'warnings': warnings,
                'file_count': file_count,
                'total_size_mb': total_size_mb,
                'recent_files_count': len(recent_files),
                'important_files_count': len(important_files)
            }
        
        except Exception as e:
            return {
                'safe': False,
                'warnings': [f"Error checking delete safety: {str(e)}"],
                'file_count': 0,
                'total_size_mb': 0,
                'recent_files_count': 0,
                'important_files_count': 0
            }
    
    def check_email_safety(self, email_content, attachments=None):
        """Check email before sending"""
        warnings = []
        
        try:
            # Check for attachment mentions without attachments
            attachment_keywords = ['attach', 'attachment', 'attached', 'file', 'document', 'pdf', 'image']
            has_attachment_mention = any(keyword in email_content.lower() for keyword in attachment_keywords)
            
            if has_attachment_mention and not attachments:
                warnings.append("⚠️ You mentioned an attachment but didn't attach anything!")
            
            # Check for common mistakes
            if 'dear [name]' in email_content.lower() or '[name]' in email_content:
                warnings.append("⚠️ Email contains placeholder text like '[name]'")
            
            if email_content.strip().count('\n') < 2:
                warnings.append("⚠️ Email seems very short - are you sure it's complete?")
            
            # Check for sensitive information patterns
            sensitive_patterns = [
                r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card
                r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
                r'\bpassword\s*[:=]\s*\w+\b'  # Password
            ]
            
            import re
            for pattern in sensitive_patterns:
                if re.search(pattern, email_content, re.IGNORECASE):
                    warnings.append("⚠️ Email may contain sensitive information (credit card, SSN, password)")
                    break
            
            return {
                'safe': len(warnings) == 0,
                'warnings': warnings
            }
        
        except Exception as e:
            return {
                'safe': False,
                'warnings': [f"Error checking email safety: {str(e)}"]
            }
    
    def check_drive_format_safety(self, drive_path):
        """Check before formatting drive"""
        warnings = []
        
        try:
            if not os.path.exists(drive_path):
                return {'safe': False, 'warnings': ['Drive path does not exist']}
            
            # Check drive contents
            total_size = 0
            file_count = 0
            photo_count = 0
            document_count = 0
            
            photo_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.raw']
            doc_extensions = ['.pdf', '.docx', '.xlsx', '.pptx', '.txt']
            
            for root, dirs, files in os.walk(drive_path):
                file_count += len(files)
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        size = os.path.getsize(file_path)
                        total_size += size
                        
                        ext = os.path.splitext(file)[1].lower()
                        if ext in photo_extensions:
                            photo_count += 1
                        elif ext in doc_extensions:
                            document_count += 1
                    except:
                        continue
            
            total_size_gb = total_size / (1024 * 1024 * 1024)
            
            if total_size_gb > 0.1:  # More than 100MB
                warnings.append(f"⚠️ Drive contains {total_size_gb:.1f} GB of data")
            
            if photo_count > 0:
                warnings.append(f"⚠️ Drive contains {photo_count} photos with no backup detected")
            
            if document_count > 0:
                warnings.append(f"⚠️ Drive contains {document_count} documents")
            
            if file_count > 100:
                warnings.append(f"⚠️ Drive contains {file_count} files")
            
            return {
                'safe': len(warnings) == 0,
                'warnings': warnings,
                'total_size_gb': total_size_gb,
                'file_count': file_count,
                'photo_count': photo_count,
                'document_count': document_count
            }
        
        except Exception as e:
            return {
                'safe': False,
                'warnings': [f"Error checking drive safety: {str(e)}"]
            }
    
    def check_copy_operation_safety(self, source, destination):
        """Check for duplicate files before copying"""
        warnings = []
        
        try:
            if not os.path.exists(source):
                return {'safe': False, 'warnings': ['Source path does not exist']}
            
            if not os.path.exists(destination):
                return {'safe': True, 'warnings': []}
            
            # Check for duplicates
            duplicate_count = 0
            same_files = []
            total_duplicate_size = 0
            
            if os.path.isfile(source):
                dest_file = os.path.join(destination, os.path.basename(source))
                if os.path.exists(dest_file):
                    # Compare file sizes and modification times
                    src_size = os.path.getsize(source)
                    dest_size = os.path.getsize(dest_file)
                    
                    if src_size == dest_size:
                        duplicate_count = 1
                        same_files.append(os.path.basename(source))
                        total_duplicate_size = src_size
            
            elif os.path.isdir(source):
                for root, dirs, files in os.walk(source):
                    for file in files:
                        src_file = os.path.join(root, file)
                        rel_path = os.path.relpath(src_file, source)
                        dest_file = os.path.join(destination, rel_path)
                        
                        if os.path.exists(dest_file):
                            try:
                                src_size = os.path.getsize(src_file)
                                dest_size = os.path.getsize(dest_file)
                                
                                if src_size == dest_size:
                                    duplicate_count += 1
                                    same_files.append(file)
                                    total_duplicate_size += src_size
                            except:
                                continue
            
            if duplicate_count > 0:
                duplicate_size_mb = total_duplicate_size / (1024 * 1024)
                warnings.append(f"⚠️ Destination has {duplicate_count} files with same size ({duplicate_size_mb:.1f} MB)")
                warnings.append("Should I skip duplicates to save space and time?")
                
                if duplicate_count <= 10:
                    warnings.append("Duplicate files:")
                    for file in same_files:
                        warnings.append(f"   • {file}")
                else:
                    warnings.append(f"First 10 duplicate files:")
                    for file in same_files[:10]:
                        warnings.append(f"   • {file}")
                    warnings.append(f"   ... and {duplicate_count - 10} more")
            
            return {
                'safe': True,  # Not unsafe, just inefficient
                'warnings': warnings,
                'duplicate_count': duplicate_count,
                'duplicate_size_mb': total_duplicate_size / (1024 * 1024)
            }
        
        except Exception as e:
            return {
                'safe': False,
                'warnings': [f"Error checking copy safety: {str(e)}"]
            }
    
    def check_document_close_safety(self, document_paths=None):
        """Check for unsaved changes before closing"""
        warnings = []
        
        try:
            # This would integrate with actual applications in production
            # For now, simulate checking for unsaved changes
            
            if document_paths:
                unsaved_count = 0
                unsaved_docs = []
                
                for doc_path in document_paths:
                    # Simulate unsaved change detection
                    # In reality, this would check file modification times,
                    # application APIs, or temporary files
                    if os.path.exists(doc_path):
                        # Check if file was modified recently (within last hour)
                        mod_time = datetime.fromtimestamp(os.path.getmtime(doc_path))
                        if (datetime.now() - mod_time).total_seconds() < 3600:
                            unsaved_count += 1
                            unsaved_docs.append(os.path.basename(doc_path))
                
                if unsaved_count > 0:
                    warnings.append(f"⚠️ You have unsaved changes in {unsaved_count} document(s):")
                    for doc in unsaved_docs:
                        warnings.append(f"   • {doc}")
                    warnings.append("Save your work before closing!")
            
            return {
                'safe': len(warnings) == 0,
                'warnings': warnings
            }
        
        except Exception as e:
            return {
                'safe': False,
                'warnings': [f"Error checking document safety: {str(e)}"]
            }
    
    def record_action_for_undo(self, action_type, description, undo_data):
        """Record action for potential undo"""
        try:
            action_record = {
                'id': len(self.undo_stack),
                'timestamp': datetime.now().isoformat(),
                'action_type': action_type,
                'description': description,
                'undo_data': undo_data
            }
            
            self.undo_stack.append(action_record)
            
            # Keep only last N actions
            if len(self.undo_stack) > self.max_undo_actions:
                self.undo_stack.pop(0)
            
            return action_record['id']
        
        except Exception as e:
            print(f"Error recording action: {e}")
            return None
    
    def undo_last_action(self):
        """Undo the last action"""
        try:
            if not self.undo_stack:
                return "No actions to undo"
            
            last_action = self.undo_stack.pop()
            action_type = last_action['action_type']
            undo_data = last_action['undo_data']
            
            if action_type == 'file_delete':
                # Restore from backup location
                if 'backup_path' in undo_data and os.path.exists(undo_data['backup_path']):
                    shutil.move(undo_data['backup_path'], undo_data['original_path'])
                    return f"✅ Restored deleted file: {undo_data['original_path']}"
                else:
                    return "❌ Cannot restore file - backup not found"
            
            elif action_type == 'file_move':
                # Move back to original location
                if os.path.exists(undo_data['new_path']):
                    shutil.move(undo_data['new_path'], undo_data['original_path'])
                    return f"✅ Moved file back to: {undo_data['original_path']}"
                else:
                    return "❌ Cannot undo move - file not found"
            
            elif action_type == 'file_rename':
                # Rename back to original name
                if os.path.exists(undo_data['new_path']):
                    os.rename(undo_data['new_path'], undo_data['original_path'])
                    return f"✅ Renamed back to: {undo_data['original_path']}"
                else:
                    return "❌ Cannot undo rename - file not found"
            
            else:
                return f"❌ Cannot undo action type: {action_type}"
        
        except Exception as e:
            return f"Error undoing action: {str(e)}"
    
    def undo_actions_from_time(self, hours_back):
        """Undo all actions from the last N hours"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            actions_to_undo = []
            
            for action in reversed(self.undo_stack):
                action_time = datetime.fromisoformat(action['timestamp'])
                if action_time >= cutoff_time:
                    actions_to_undo.append(action)
                else:
                    break
            
            if not actions_to_undo:
                return f"No actions found in the last {hours_back} hours"
            
            results = []
            for action in actions_to_undo:
                # Remove from stack
                if action in self.undo_stack:
                    self.undo_stack.remove(action)
                
                # Perform undo
                self.undo_stack.append(action)  # Temporarily add back
                result = self.undo_last_action()
                results.append(f"• {action['description']}: {result}")
            
            return f"🔄 Undoing {len(actions_to_undo)} actions from last {hours_back} hours:\n\n" + "\n".join(results)
        
        except Exception as e:
            return f"Error undoing actions: {str(e)}"
    
    def get_undo_timeline(self):
        """Get timeline of undoable actions"""
        try:
            if not self.undo_stack:
                return "No undoable actions in history"
            
            result = "🕒 Undo Timeline (most recent first):\n\n"
            
            for action in reversed(self.undo_stack[-20:]):  # Show last 20
                timestamp = datetime.fromisoformat(action['timestamp'])
                time_str = timestamp.strftime("%H:%M:%S")
                result += f"{time_str} - {action['description']}\n"
            
            result += f"\nTotal undoable actions: {len(self.undo_stack)}"
            result += "\nUse 'undo last action' or 'undo everything from last hour'"
            
            return result
        
        except Exception as e:
            return f"Error getting undo timeline: {e}"

# ==================== GLOBAL INSTANCE ====================

safety_net = SafetyNetEngine()

# ==================== CONVENIENCE FUNCTIONS ====================

def check_delete_safety(paths):
    """Check if delete operation is safe"""
    return safety_net.check_delete_safety(paths)

def check_email_safety(email_content, attachments=None):
    """Check email before sending"""
    return safety_net.check_email_safety(email_content, attachments)

def check_drive_format_safety(drive_path):
    """Check before formatting drive"""
    return safety_net.check_drive_format_safety(drive_path)

def check_copy_safety(source, destination):
    """Check copy operation for duplicates"""
    return safety_net.check_copy_operation_safety(source, destination)

def check_document_close_safety(document_paths=None):
    """Check for unsaved changes"""
    return safety_net.check_document_close_safety(document_paths)

def record_action_for_undo(action_type, description, undo_data):
    """Record action for undo"""
    return safety_net.record_action_for_undo(action_type, description, undo_data)

def undo_last_action():
    """Undo last action"""
    return safety_net.undo_last_action()

def undo_actions_from_time(hours_back):
    """Undo actions from time period"""
    return safety_net.undo_actions_from_time(hours_back)

def get_undo_timeline():
    """Get undo timeline"""
    return safety_net.get_undo_timeline()
