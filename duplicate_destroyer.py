import os
import hashlib
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import shutil

# ==================== DUPLICATE DESTROYER - RECLAIM STORAGE ====================

class DuplicateDestroyer:
    def __init__(self):
        self.scan_results = {}
        self.duplicate_groups = {}
        self.space_savings = 0
        
    def scan_for_duplicates(self, scan_paths=None, quick_scan=False):
        """Scan entire computer for duplicates in 2 minutes"""
        try:
            if scan_paths is None:
                scan_paths = [
                    os.path.expanduser("~"),
                    "C:\\" if os.name == 'nt' else "/"
                ]
            
            print("🔍 Starting duplicate scan...")
            
            file_hashes = defaultdict(list)
            total_files = 0
            total_size = 0
            duplicate_size = 0
            
            for scan_path in scan_paths:
                if os.path.exists(scan_path):
                    for root, dirs, files in os.walk(scan_path):
                        # Skip system directories for speed
                        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['System32', 'Windows', 'Program Files', 'node_modules']]
                        
                        for file in files:
                            if total_files >= 50000 and quick_scan:  # Limit for quick scan
                                break
                                
                            file_path = os.path.join(root, file)
                            
                            try:
                                file_size = os.path.getsize(file_path)
                                
                                # Skip very small files (< 1KB) and very large files (> 1GB) for speed
                                if file_size < 1024 or file_size > 1024*1024*1024:
                                    continue
                                
                                # Generate file hash
                                file_hash = self._generate_file_hash(file_path, quick_scan)
                                
                                if file_hash:
                                    file_hashes[file_hash].append({
                                        'path': file_path,
                                        'size': file_size,
                                        'name': file,
                                        'modified': os.path.getmtime(file_path)
                                    })
                                    
                                    total_files += 1
                                    total_size += file_size
                            
                            except Exception as e:
                                continue
            
            # Find duplicates
            duplicates = {}
            for file_hash, files in file_hashes.items():
                if len(files) > 1:
                    duplicates[file_hash] = files
                    # Calculate space that could be saved
                    file_size = files[0]['size']
                    duplicate_size += file_size * (len(files) - 1)
            
            self.duplicate_groups = duplicates
            self.space_savings = duplicate_size
            
            # Generate results
            duplicate_count = sum(len(files) - 1 for files in duplicates.values())
            space_saved_gb = duplicate_size / (1024**3)
            
            result = f"🔍 Duplicate Scan Complete!\n\n"
            result += f"📊 **RESULTS:**\n"
            result += f"• Scanned: {total_files:,} files\n"
            result += f"• Found: {len(duplicates)} duplicate groups\n"
            result += f"• Duplicate files: {duplicate_count:,}\n"
            result += f"• **Space wasted: {space_saved_gb:.1f} GB**\n\n"
            
            if space_saved_gb > 5:
                result += f"💰 **You could save ₹{int(space_saved_gb * 1000)} by not buying extra storage!**\n\n"
            
            # Show top duplicate groups
            if duplicates:
                result += "🔥 **TOP SPACE WASTERS:**\n"
                sorted_groups = sorted(duplicates.items(), key=lambda x: x[1][0]['size'] * (len(x[1]) - 1), reverse=True)
                
                for i, (hash_key, files) in enumerate(sorted_groups[:5], 1):
                    file_size_mb = files[0]['size'] / (1024**2)
                    wasted_mb = file_size_mb * (len(files) - 1)
                    result += f"{i}. **{files[0]['name']}** - {len(files)} copies wasting {wasted_mb:.1f} MB\n"
                
                result += f"\n💡 Use 'delete duplicates' to reclaim this space!"
            
            return result
        
        except Exception as e:
            return f"Error scanning for duplicates: {str(e)}"
    
    def _generate_file_hash(self, file_path, quick_scan=False):
        """Generate hash for file comparison"""
        try:
            hash_md5 = hashlib.md5()
            
            with open(file_path, "rb") as f:
                if quick_scan:
                    # Quick scan: hash first 64KB + file size
                    chunk = f.read(65536)  # 64KB
                    hash_md5.update(chunk)
                    hash_md5.update(str(os.path.getsize(file_path)).encode())
                else:
                    # Full scan: hash entire file
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)
            
            return hash_md5.hexdigest()
        
        except Exception as e:
            return None
    
    def show_duplicate_groups(self, limit=10):
        """Show duplicate groups with smart grouping"""
        try:
            if not self.duplicate_groups:
                return "No duplicates found. Run 'scan for duplicates' first."
            
            result = f"📁 **DUPLICATE GROUPS** (Top {limit}):\n\n"
            
            sorted_groups = sorted(
                self.duplicate_groups.items(), 
                key=lambda x: x[1][0]['size'] * (len(x[1]) - 1), 
                reverse=True
            )
            
            for i, (hash_key, files) in enumerate(sorted_groups[:limit], 1):
                file_size_mb = files[0]['size'] / (1024**2)
                wasted_space = file_size_mb * (len(files) - 1)
                
                result += f"**Group {i}: {files[0]['name']}**\n"
                result += f"💾 Size: {file_size_mb:.1f} MB each\n"
                result += f"📊 Copies: {len(files)} files\n"
                result += f"💸 Wasted: {wasted_space:.1f} MB\n\n"
                
                # Show file locations
                result += "📍 **Locations:**\n"
                for j, file_info in enumerate(files, 1):
                    modified_date = datetime.fromtimestamp(file_info['modified']).strftime('%Y-%m-%d')
                    result += f"  {j}. {file_info['path']} (Modified: {modified_date})\n"
                
                result += "\n" + "="*50 + "\n\n"
            
            total_wasted_gb = self.space_savings / (1024**3)
            result += f"🎯 **TOTAL RECOVERABLE SPACE: {total_wasted_gb:.1f} GB**\n"
            result += f"💰 **EQUIVALENT TO: ₹{int(total_wasted_gb * 1000)} in storage costs**"
            
            return result
        
        except Exception as e:
            return f"Error showing duplicate groups: {str(e)}"
    
    def smart_delete_duplicates(self, keep_strategy='newest'):
        """Smart duplicate deletion with user-friendly strategy"""
        try:
            if not self.duplicate_groups:
                return "No duplicates found. Run 'scan for duplicates' first."
            
            deleted_files = []
            space_freed = 0
            errors = []
            
            for hash_key, files in self.duplicate_groups.items():
                try:
                    # Determine which file to keep based on strategy
                    if keep_strategy == 'newest':
                        # Keep the most recently modified file
                        files_sorted = sorted(files, key=lambda x: x['modified'], reverse=True)
                    elif keep_strategy == 'oldest':
                        # Keep the oldest file
                        files_sorted = sorted(files, key=lambda x: x['modified'])
                    elif keep_strategy == 'shortest_path':
                        # Keep file with shortest path (likely in main folders)
                        files_sorted = sorted(files, key=lambda x: len(x['path']))
                    else:
                        # Default: keep first found
                        files_sorted = files
                    
                    keep_file = files_sorted[0]
                    delete_files = files_sorted[1:]
                    
                    # Delete duplicate files
                    for file_info in delete_files:
                        try:
                            if os.path.exists(file_info['path']):
                                os.remove(file_info['path'])
                                deleted_files.append(file_info['path'])
                                space_freed += file_info['size']
                        except Exception as e:
                            errors.append(f"Could not delete {file_info['path']}: {str(e)}")
                
                except Exception as e:
                    errors.append(f"Error processing duplicate group: {str(e)}")
            
            space_freed_gb = space_freed / (1024**3)
            
            result = f"🗑️ **DUPLICATE CLEANUP COMPLETE!**\n\n"
            result += f"✅ **Files deleted:** {len(deleted_files)}\n"
            result += f"💾 **Space freed:** {space_freed_gb:.2f} GB\n"
            result += f"💰 **Money saved:** ₹{int(space_freed_gb * 1000)} (no need for extra storage!)\n"
            result += f"📋 **Strategy used:** Keep {keep_strategy} file from each group\n\n"
            
            if errors:
                result += f"⚠️ **Errors ({len(errors)}):**\n"
                for error in errors[:5]:  # Show first 5 errors
                    result += f"• {error}\n"
                if len(errors) > 5:
                    result += f"• ... and {len(errors) - 5} more errors\n"
            
            # Clear the duplicate groups since they're processed
            self.duplicate_groups = {}
            
            return result
        
        except Exception as e:
            return f"Error deleting duplicates: {str(e)}"
    
    def find_duplicate_downloads(self):
        """Find duplicate files in Downloads folder"""
        try:
            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
            
            if not os.path.exists(downloads_path):
                return "Downloads folder not found"
            
            # Scan only Downloads folder
            result = self.scan_for_duplicates([downloads_path], quick_scan=True)
            
            if self.duplicate_groups:
                downloads_result = f"📥 **DUPLICATE DOWNLOADS FOUND!**\n\n"
                
                total_wasted = 0
                for files in self.duplicate_groups.values():
                    file_size = files[0]['size']
                    total_wasted += file_size * (len(files) - 1)
                
                wasted_gb = total_wasted / (1024**3)
                downloads_result += f"💾 **Wasted space in Downloads: {wasted_gb:.1f} GB**\n\n"
                
                # Show specific duplicate downloads
                downloads_result += "🔥 **DUPLICATE DOWNLOADS:**\n"
                for i, (hash_key, files) in enumerate(self.duplicate_groups.items(), 1):
                    if i > 10:  # Limit to top 10
                        break
                    
                    file_size_mb = files[0]['size'] / (1024**2)
                    downloads_result += f"{i}. **{files[0]['name']}** - {len(files)} copies ({file_size_mb:.1f} MB each)\n"
                
                downloads_result += f"\n💡 Clean up Downloads to free {wasted_gb:.1f} GB!"
                return downloads_result
            else:
                return "✅ No duplicate downloads found!"
        
        except Exception as e:
            return f"Error scanning Downloads: {str(e)}"
    
    def find_duplicate_photos(self):
        """Find duplicate photos (same image in multiple folders)"""
        try:
            photo_paths = [
                os.path.join(os.path.expanduser("~"), "Pictures"),
                os.path.join(os.path.expanduser("~"), "Desktop"),
                os.path.join(os.path.expanduser("~"), "Downloads")
            ]
            
            # Filter to only photo extensions
            photo_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic'}
            
            photo_hashes = defaultdict(list)
            total_photos = 0
            
            for photo_path in photo_paths:
                if os.path.exists(photo_path):
                    for root, dirs, files in os.walk(photo_path):
                        for file in files:
                            file_ext = os.path.splitext(file)[1].lower()
                            if file_ext in photo_extensions:
                                file_path = os.path.join(root, file)
                                
                                try:
                                    file_size = os.path.getsize(file_path)
                                    if file_size > 10240:  # Skip very small images (< 10KB)
                                        file_hash = self._generate_file_hash(file_path, quick_scan=True)
                                        
                                        if file_hash:
                                            photo_hashes[file_hash].append({
                                                'path': file_path,
                                                'size': file_size,
                                                'name': file
                                            })
                                            total_photos += 1
                                
                                except Exception as e:
                                    continue
            
            # Find duplicate photos
            duplicate_photos = {h: files for h, files in photo_hashes.items() if len(files) > 1}
            
            if not duplicate_photos:
                return f"✅ No duplicate photos found among {total_photos} photos!"
            
            total_wasted = sum(
                files[0]['size'] * (len(files) - 1) 
                for files in duplicate_photos.values()
            )
            wasted_gb = total_wasted / (1024**3)
            
            result = f"📸 **DUPLICATE PHOTOS FOUND!**\n\n"
            result += f"📊 Total photos scanned: {total_photos}\n"
            result += f"🔄 Duplicate groups: {len(duplicate_photos)}\n"
            result += f"💾 **Wasted space: {wasted_gb:.1f} GB**\n\n"
            
            result += "🔥 **TOP DUPLICATE PHOTOS:**\n"
            sorted_photos = sorted(duplicate_photos.items(), key=lambda x: x[1][0]['size'] * (len(x[1]) - 1), reverse=True)
            
            for i, (hash_key, files) in enumerate(sorted_photos[:8], 1):
                file_size_mb = files[0]['size'] / (1024**2)
                result += f"{i}. **{files[0]['name']}** - {len(files)} copies ({file_size_mb:.1f} MB each)\n"
                
                # Show where the duplicates are
                folders = list(set(os.path.dirname(f['path']) for f in files))
                result += f"   📁 Found in: {len(folders)} different folders\n"
            
            result += f"\n💡 Delete photo duplicates to free {wasted_gb:.1f} GB!"
            
            # Store results for potential deletion
            self.duplicate_groups = duplicate_photos
            
            return result
        
        except Exception as e:
            return f"Error scanning for duplicate photos: {str(e)}"
    
    def get_storage_analysis(self):
        """Get comprehensive storage analysis"""
        try:
            # Analyze different types of files
            user_home = os.path.expanduser("~")
            
            analysis = {
                'total_size': 0,
                'file_types': defaultdict(lambda: {'count': 0, 'size': 0}),
                'large_files': [],
                'old_files': [],
                'temp_files': []
            }
            
            # Scan user directories
            scan_dirs = [
                os.path.join(user_home, "Documents"),
                os.path.join(user_home, "Downloads"),
                os.path.join(user_home, "Pictures"),
                os.path.join(user_home, "Videos"),
                os.path.join(user_home, "Desktop")
            ]
            
            for scan_dir in scan_dirs:
                if os.path.exists(scan_dir):
                    for root, dirs, files in os.walk(scan_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            
                            try:
                                file_size = os.path.getsize(file_path)
                                file_ext = os.path.splitext(file)[1].lower()
                                
                                analysis['total_size'] += file_size
                                analysis['file_types'][file_ext]['count'] += 1
                                analysis['file_types'][file_ext]['size'] += file_size
                                
                                # Track large files (> 100MB)
                                if file_size > 100 * 1024 * 1024:
                                    analysis['large_files'].append({
                                        'path': file_path,
                                        'size': file_size,
                                        'name': file
                                    })
                                
                                # Track temp files
                                if any(temp in file.lower() for temp in ['temp', 'tmp', 'cache', '~']):
                                    analysis['temp_files'].append({
                                        'path': file_path,
                                        'size': file_size,
                                        'name': file
                                    })
                            
                            except Exception as e:
                                continue
            
            # Generate report
            total_gb = analysis['total_size'] / (1024**3)
            
            result = f"💾 **STORAGE ANALYSIS REPORT**\n\n"
            result += f"📊 **Total analyzed:** {total_gb:.1f} GB\n\n"
            
            # Top file types by size
            result += "📁 **SPACE USAGE BY FILE TYPE:**\n"
            sorted_types = sorted(
                analysis['file_types'].items(), 
                key=lambda x: x[1]['size'], 
                reverse=True
            )
            
            for i, (ext, data) in enumerate(sorted_types[:10], 1):
                size_gb = data['size'] / (1024**3)
                ext_name = ext if ext else 'No extension'
                result += f"{i}. **{ext_name}**: {size_gb:.1f} GB ({data['count']} files)\n"
            
            # Large files
            if analysis['large_files']:
                result += f"\n🐘 **LARGE FILES (>100MB):**\n"
                large_files_sorted = sorted(analysis['large_files'], key=lambda x: x['size'], reverse=True)
                
                for i, file_info in enumerate(large_files_sorted[:5], 1):
                    size_gb = file_info['size'] / (1024**3)
                    result += f"{i}. **{file_info['name']}**: {size_gb:.1f} GB\n"
            
            # Temp files
            if analysis['temp_files']:
                temp_size = sum(f['size'] for f in analysis['temp_files'])
                temp_gb = temp_size / (1024**3)
                result += f"\n🗑️ **TEMP FILES:** {temp_gb:.1f} GB ({len(analysis['temp_files'])} files)\n"
                result += f"💡 Clean temp files to free {temp_gb:.1f} GB!\n"
            
            return result
        
        except Exception as e:
            return f"Error analyzing storage: {str(e)}"

# ==================== GLOBAL INSTANCE ====================

duplicate_destroyer = DuplicateDestroyer()

# ==================== CONVENIENCE FUNCTIONS ====================

def scan_duplicates(quick_scan=True):
    """Scan for duplicate files"""
    return duplicate_destroyer.scan_for_duplicates(quick_scan=quick_scan)

def show_duplicates(limit=10):
    """Show duplicate groups"""
    return duplicate_destroyer.show_duplicate_groups(limit)

def delete_duplicates(strategy='newest'):
    """Delete duplicate files"""
    return duplicate_destroyer.smart_delete_duplicates(strategy)

def find_duplicate_downloads():
    """Find duplicates in Downloads"""
    return duplicate_destroyer.find_duplicate_downloads()

def find_duplicate_photos():
    """Find duplicate photos"""
    return duplicate_destroyer.find_duplicate_photos()

def analyze_storage():
    """Get storage analysis"""
    return duplicate_destroyer.get_storage_analysis()
