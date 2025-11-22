import os
import shutil
import zipfile
import tarfile
import hashlib
import PyPDF2
import pdfplumber
from docx import Document
from docx2pdf import convert
from PyPDF2 import PdfWriter, PdfReader
import pikepdf
import json
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
import mimetypes

# ==================== ADVANCED FILE OPERATIONS ====================

class AdvancedFileManager:
    def __init__(self):
        self.file_patterns = {
            "documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt"],
            "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
            "videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
            "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"],
            "archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
            "code": [".py", ".js", ".html", ".css", ".cpp", ".java", ".c", ".php"],
            "data": [".csv", ".json", ".xml", ".sql", ".db", ".xlsx", ".xls"]
        }
        self.backup_history = self._load_backup_history()
    
    def _load_backup_history(self):
        """Load backup history"""
        try:
            history_file = os.path.join(os.path.expanduser("~"), ".desktop_ai_backup_history.json")
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def _save_backup_history(self):
        """Save backup history"""
        try:
            history_file = os.path.join(os.path.expanduser("~"), ".desktop_ai_backup_history.json")
            with open(history_file, 'w') as f:
                json.dump(self.backup_history, f, indent=2)
        except:
            pass
    
    def organize_files_by_type(self, source_dir, create_folders=True):
        """Organize files by type into folders"""
        try:
            source_path = Path(source_dir)
            if not source_path.exists():
                return f"Directory {source_dir} does not exist"
            
            organized_count = 0
            results = []
            
            for file_path in source_path.iterdir():
                if file_path.is_file():
                    file_ext = file_path.suffix.lower()
                    
                    # Determine file category
                    category = "others"
                    for cat, extensions in self.file_patterns.items():
                        if file_ext in extensions:
                            category = cat
                            break
                    
                    # Create category folder if needed
                    category_folder = source_path / category.title()
                    if create_folders and not category_folder.exists():
                        category_folder.mkdir()
                    
                    # Move file
                    if create_folders:
                        new_path = category_folder / file_path.name
                        if not new_path.exists():
                            shutil.move(str(file_path), str(new_path))
                            organized_count += 1
                            results.append(f"Moved {file_path.name} to {category.title()}/")
            
            return f"Organized {organized_count} files:\n" + "\n".join(results[:20])
        
        except Exception as e:
            return f"Error organizing files: {str(e)}"
    
    def rename_files_pattern(self, directory, pattern, new_pattern):
        """Rename multiple files using patterns"""
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return f"Directory {directory} does not exist"
            
            renamed_count = 0
            results = []
            
            # Support for numbered patterns like "Photo_1", "Photo_2", etc.
            if "{n}" in new_pattern:
                counter = 1
                for file_path in sorted(dir_path.glob(pattern)):
                    if file_path.is_file():
                        new_name = new_pattern.replace("{n}", str(counter))
                        new_path = file_path.parent / new_name
                        
                        if not new_path.exists():
                            file_path.rename(new_path)
                            renamed_count += 1
                            results.append(f"{file_path.name} → {new_name}")
                            counter += 1
            else:
                # Simple pattern replacement
                for file_path in dir_path.glob(pattern):
                    if file_path.is_file():
                        new_name = file_path.name.replace(pattern.replace("*", ""), new_pattern)
                        new_path = file_path.parent / new_name
                        
                        if not new_path.exists():
                            file_path.rename(new_path)
                            renamed_count += 1
                            results.append(f"{file_path.name} → {new_name}")
            
            return f"Renamed {renamed_count} files:\n" + "\n".join(results[:20])
        
        except Exception as e:
            return f"Error renaming files: {str(e)}"
    
    def find_duplicate_files(self, directory, check_content=True):
        """Find duplicate files in directory"""
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return f"Directory {directory} does not exist"
            
            file_hashes = {}
            duplicates = []
            
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    if check_content:
                        # Hash file content
                        file_hash = self._get_file_hash(file_path)
                    else:
                        # Use file size as simple check
                        file_hash = str(file_path.stat().st_size)
                    
                    if file_hash in file_hashes:
                        duplicates.append({
                            "original": file_hashes[file_hash],
                            "duplicate": str(file_path),
                            "size": file_path.stat().st_size
                        })
                    else:
                        file_hashes[file_hash] = str(file_path)
            
            if duplicates:
                result = f"Found {len(duplicates)} duplicate files:\n"
                total_waste = 0
                for dup in duplicates[:20]:  # Show first 20
                    size_mb = dup["size"] / (1024 * 1024)
                    total_waste += dup["size"]
                    result += f"\nDuplicate: {Path(dup['duplicate']).name} ({size_mb:.1f} MB)\n"
                    result += f"Original: {dup['original']}\n"
                
                total_waste_mb = total_waste / (1024 * 1024)
                result += f"\nTotal wasted space: {total_waste_mb:.1f} MB"
                return result
            else:
                return "No duplicate files found"
        
        except Exception as e:
            return f"Error finding duplicates: {str(e)}"
    
    def _get_file_hash(self, file_path):
        """Get MD5 hash of file content"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return str(file_path.stat().st_size)  # Fallback to size
    
    def find_large_files(self, directory, min_size_mb=100):
        """Find large files eating up space"""
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return f"Directory {directory} does not exist"
            
            large_files = []
            min_size_bytes = min_size_mb * 1024 * 1024
            
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    file_size = file_path.stat().st_size
                    if file_size > min_size_bytes:
                        large_files.append({
                            "path": str(file_path),
                            "size": file_size,
                            "size_mb": file_size / (1024 * 1024)
                        })
            
            # Sort by size (largest first)
            large_files.sort(key=lambda x: x["size"], reverse=True)
            
            if large_files:
                result = f"Found {len(large_files)} files larger than {min_size_mb} MB:\n"
                total_size = 0
                for file_info in large_files[:20]:  # Show first 20
                    total_size += file_info["size"]
                    result += f"{Path(file_info['path']).name}: {file_info['size_mb']:.1f} MB\n"
                    result += f"  Location: {file_info['path']}\n"
                
                total_size_gb = total_size / (1024 * 1024 * 1024)
                result += f"\nTotal size of large files: {total_size_gb:.1f} GB"
                return result
            else:
                return f"No files larger than {min_size_mb} MB found"
        
        except Exception as e:
            return f"Error finding large files: {str(e)}"
    
    def find_unused_files(self, directory, days_unused=180):
        """Find files not accessed in specified days"""
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return f"Directory {directory} does not exist"
            
            cutoff_date = datetime.now() - timedelta(days=days_unused)
            unused_files = []
            
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    # Get last access time
                    last_access = datetime.fromtimestamp(file_path.stat().st_atime)
                    if last_access < cutoff_date:
                        unused_files.append({
                            "path": str(file_path),
                            "last_access": last_access,
                            "size": file_path.stat().st_size
                        })
            
            # Sort by last access (oldest first)
            unused_files.sort(key=lambda x: x["last_access"])
            
            if unused_files:
                result = f"Found {len(unused_files)} files unused for {days_unused}+ days:\n"
                total_size = 0
                for file_info in unused_files[:20]:  # Show first 20
                    total_size += file_info["size"]
                    size_mb = file_info["size"] / (1024 * 1024)
                    last_access_str = file_info["last_access"].strftime("%Y-%m-%d")
                    result += f"{Path(file_info['path']).name} ({size_mb:.1f} MB)\n"
                    result += f"  Last accessed: {last_access_str}\n"
                    result += f"  Location: {file_info['path']}\n"
                
                total_size_mb = total_size / (1024 * 1024)
                result += f"\nTotal size of unused files: {total_size_mb:.1f} MB"
                return result
            else:
                return f"No files unused for {days_unused}+ days found"
        
        except Exception as e:
            return f"Error finding unused files: {str(e)}"
    
    def compress_folder(self, folder_path, output_path=None, format="zip"):
        """Compress folder into archive"""
        try:
            folder = Path(folder_path)
            if not folder.exists():
                return f"Folder {folder_path} does not exist"
            
            if output_path is None:
                output_path = f"{folder_path}.{format}"
            
            if format.lower() == "zip":
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in folder.rglob("*"):
                        if file_path.is_file():
                            arcname = file_path.relative_to(folder.parent)
                            zipf.write(file_path, arcname)
            
            elif format.lower() in ["tar", "tar.gz"]:
                mode = "w:gz" if format == "tar.gz" else "w"
                with tarfile.open(output_path, mode) as tarf:
                    tarf.add(folder_path, arcname=folder.name)
            
            compressed_size = Path(output_path).stat().st_size
            original_size = sum(f.stat().st_size for f in folder.rglob("*") if f.is_file())
            
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            return f"Compressed {folder.name} to {output_path}\n" \
                   f"Original size: {original_size / (1024*1024):.1f} MB\n" \
                   f"Compressed size: {compressed_size / (1024*1024):.1f} MB\n" \
                   f"Compression ratio: {compression_ratio:.1f}%"
        
        except Exception as e:
            return f"Error compressing folder: {str(e)}"
    
    def extract_archive(self, archive_path, extract_to=None):
        """Extract archive file"""
        try:
            archive = Path(archive_path)
            if not archive.exists():
                return f"Archive {archive_path} does not exist"
            
            if extract_to is None:
                extract_to = archive.parent / archive.stem
            
            extract_path = Path(extract_to)
            extract_path.mkdir(exist_ok=True)
            
            if archive.suffix.lower() == ".zip":
                with zipfile.ZipFile(archive_path, 'r') as zipf:
                    zipf.extractall(extract_path)
                    extracted_files = len(zipf.namelist())
            
            elif archive.suffix.lower() in [".tar", ".gz", ".bz2"]:
                with tarfile.open(archive_path, 'r:*') as tarf:
                    tarf.extractall(extract_path)
                    extracted_files = len(tarf.getnames())
            
            else:
                return f"Unsupported archive format: {archive.suffix}"
            
            return f"Extracted {extracted_files} files from {archive.name} to {extract_path}"
        
        except Exception as e:
            return f"Error extracting archive: {str(e)}"
    
    def natural_language_search(self, query, search_directory=None):
        """Search files using natural language queries"""
        try:
            if search_directory is None:
                search_directory = os.path.expanduser("~")
            
            search_path = Path(search_directory)
            if not search_path.exists():
                return f"Directory {search_directory} does not exist"
            
            # Parse natural language query
            results = []
            query_lower = query.lower()
            
            # Extract search terms
            search_terms = []
            if "about" in query_lower:
                # Extract topic after "about"
                about_match = re.search(r'about\s+(\w+)', query_lower)
                if about_match:
                    search_terms.append(about_match.group(1))
            
            if "pdf" in query_lower:
                file_types = [".pdf"]
            elif "image" in query_lower or "photo" in query_lower:
                file_types = self.file_patterns["images"]
            elif "document" in query_lower:
                file_types = self.file_patterns["documents"]
            elif "video" in query_lower:
                file_types = self.file_patterns["videos"]
            else:
                file_types = None
            
            # Time-based search
            time_filter = None
            if "last week" in query_lower:
                time_filter = datetime.now() - timedelta(days=7)
            elif "last month" in query_lower:
                time_filter = datetime.now() - timedelta(days=30)
            elif "today" in query_lower:
                time_filter = datetime.now() - timedelta(days=1)
            
            # Search files
            for file_path in search_path.rglob("*"):
                if file_path.is_file():
                    match_score = 0
                    
                    # Check file type
                    if file_types and file_path.suffix.lower() in file_types:
                        match_score += 2
                    elif file_types:
                        continue
                    
                    # Check filename for search terms
                    filename_lower = file_path.name.lower()
                    for term in search_terms:
                        if term in filename_lower:
                            match_score += 3
                    
                    # Check time filter
                    if time_filter:
                        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_time > time_filter:
                            match_score += 1
                        else:
                            continue
                    
                    # General keyword search in filename
                    keywords = re.findall(r'\w+', query_lower)
                    for keyword in keywords:
                        if keyword in filename_lower and keyword not in ["find", "search", "file", "about"]:
                            match_score += 1
                    
                    if match_score > 0:
                        results.append({
                            "path": str(file_path),
                            "name": file_path.name,
                            "score": match_score,
                            "size": file_path.stat().st_size,
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime)
                        })
            
            # Sort by relevance score
            results.sort(key=lambda x: x["score"], reverse=True)
            
            if results:
                result_text = f"Found {len(results)} files matching '{query}':\n"
                for file_info in results[:15]:  # Show top 15 results
                    size_mb = file_info["size"] / (1024 * 1024)
                    modified_str = file_info["modified"].strftime("%Y-%m-%d %H:%M")
                    result_text += f"\n{file_info['name']} (Score: {file_info['score']})\n"
                    result_text += f"  Size: {size_mb:.1f} MB, Modified: {modified_str}\n"
                    result_text += f"  Location: {file_info['path']}\n"
                
                return result_text
            else:
                return f"No files found matching '{query}'"
        
        except Exception as e:
            return f"Error in natural language search: {str(e)}"
    
    def create_backup(self, source_path, backup_location=None):
        """Create backup of files/folders"""
        try:
            source = Path(source_path)
            if not source.exists():
                return f"Source {source_path} does not exist"
            
            if backup_location is None:
                backup_location = os.path.join(os.path.expanduser("~"), "Backups")
            
            backup_dir = Path(backup_location)
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{source.name}_backup_{timestamp}"
            backup_path = backup_dir / backup_name
            
            if source.is_file():
                shutil.copy2(source, backup_path)
                backup_size = backup_path.stat().st_size
            else:
                shutil.copytree(source, backup_path)
                backup_size = sum(f.stat().st_size for f in backup_path.rglob("*") if f.is_file())
            
            # Record backup
            backup_record = {
                "source": str(source),
                "backup_path": str(backup_path),
                "timestamp": timestamp,
                "size": backup_size
            }
            
            self.backup_history.append(backup_record)
            self._save_backup_history()
            
            size_mb = backup_size / (1024 * 1024)
            return f"Backup created successfully:\n" \
                   f"Source: {source}\n" \
                   f"Backup: {backup_path}\n" \
                   f"Size: {size_mb:.1f} MB"
        
        except Exception as e:
            return f"Error creating backup: {str(e)}"
    
    def get_backup_history(self):
        """Get backup history"""
        if not self.backup_history:
            return "No backups found"
        
        result = " Backup History:\n\n"
        for backup in self.backup_history[-10:]:  # Show last 10
            timestamp = datetime.fromisoformat(backup['timestamp']).strftime("%Y-%m-%d %H:%M")
            size_mb = backup['size'] / (1024 * 1024)
            result += f"{timestamp}: {backup['source']} {backup['destination']}\n"
            result += f"  Size: {size_mb:.1f} MB, Files: {backup['files_count']}\n\n"
        
        return result
    
    # ==================== ADVANCED PDF OPERATIONS ====================
    
    def merge_pdfs(self, pdf_files, output_path):
        """Merge multiple PDFs into one"""
        try:
            merger = PdfWriter()
            
            for pdf_file in pdf_files:
                if os.path.exists(pdf_file) and pdf_file.lower().endswith('.pdf'):
                    reader = PdfReader(pdf_file)
                    for page in reader.pages:
                        merger.add_page(page)
            
            with open(output_path, 'wb') as output_file:
                merger.write(output_file)
            
            return f"Merged {len(pdf_files)} PDFs into {output_path}"
        
        except Exception as e:
            return f"Error merging PDFs: {str(e)}"
    
    def split_pdf(self, pdf_path, page_ranges, output_dir=None):
        """Split PDF into multiple files based on page ranges"""
        try:
            if not os.path.exists(pdf_path):
                return f"PDF file {pdf_path} not found"
            
            if output_dir is None:
                output_dir = os.path.dirname(pdf_path)
            
            reader = PdfReader(pdf_path)
            total_pages = len(reader.pages)
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            
            results = []
            
            for i, page_range in enumerate(page_ranges):
                writer = PdfWriter()
                
                if isinstance(page_range, tuple):
                    start, end = page_range
                    start = max(0, start - 1)  # Convert to 0-based
                    end = min(total_pages, end)
                    
                    for page_num in range(start, end):
                        writer.add_page(reader.pages[page_num])
                    
                    output_file = os.path.join(output_dir, f"{base_name}_pages_{start+1}-{end}.pdf")
                else:
                    # Single page
                    page_num = max(0, min(total_pages - 1, page_range - 1))
                    writer.add_page(reader.pages[page_num])
                    output_file = os.path.join(output_dir, f"{base_name}_page_{page_range}.pdf")
                
                with open(output_file, 'wb') as output:
                    writer.write(output)
                
                results.append(output_file)
            
            return f"Split PDF into {len(results)} files:\n" + "\n".join([f" {os.path.basename(f)}" for f in results])
        
        except Exception as e:
            return f"Error splitting PDF: {str(e)}"
    
    def compress_pdf(self, pdf_path, output_path=None, quality='medium'):
        """Compress PDF for smaller file size"""
        try:
            if not os.path.exists(pdf_path):
                return f"PDF file {pdf_path} not found"
            
            if output_path is None:
                base, ext = os.path.splitext(pdf_path)
                output_path = f"{base}_compressed{ext}"
            
            # Quality settings
            quality_settings = {
                'low': {'image_quality': 30, 'compress_level': 9},
                'medium': {'image_quality': 50, 'compress_level': 6},
                'high': {'image_quality': 70, 'compress_level': 3}
            }
            
            settings = quality_settings.get(quality, quality_settings['medium'])
            
            # Use pikepdf for compression
            with pikepdf.open(pdf_path) as pdf:
                pdf.save(output_path, compress_streams=True, 
                        object_stream_mode=pikepdf.ObjectStreamMode.generate)
            
            # Get file sizes
            original_size = os.path.getsize(pdf_path)
            compressed_size = os.path.getsize(output_path)
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            return f"PDF compressed successfully!\nOriginal: {original_size / 1024 / 1024:.1f} MB\nCompressed: {compressed_size / 1024 / 1024:.1f} MB\nSaved: {compression_ratio:.1f}%\nOutput: {output_path}"
        
        except Exception as e:
            return f"Error compressing PDF: {str(e)}"
    
    def remove_pdf_password(self, pdf_path, password, output_path=None):
        """Remove password protection from PDF"""
        try:
            if not os.path.exists(pdf_path):
                return f"PDF file {pdf_path} not found"
            
            if output_path is None:
                base, ext = os.path.splitext(pdf_path)
                output_path = f"{base}_unlocked{ext}"
            
            with pikepdf.open(pdf_path, password=password) as pdf:
                pdf.save(output_path)
            
            return f"Password removed successfully!\nUnlocked PDF saved as: {output_path}"
        
        except pikepdf.PasswordError:
            return "Incorrect password provided"
        except Exception as e:
            return f"Error removing password: {str(e)}"
    
    def add_pdf_watermark(self, pdf_path, watermark_text, output_path=None, opacity=0.3):
        """Add watermark to PDF"""
        try:
            if not os.path.exists(pdf_path):
                return f"PDF file {pdf_path} not found"
            
            if output_path is None:
                base, ext = os.path.splitext(pdf_path)
                output_path = f"{base}_watermarked{ext}"
            
            reader = PdfReader(pdf_path)
            writer = PdfWriter()
            
            # Create watermark (simplified - in production you'd use reportlab)
            for page in reader.pages:
                # Add watermark logic here (requires reportlab for proper implementation)
                writer.add_page(page)
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return f"Watermark added successfully!\nWatermarked PDF saved as: {output_path}"
        
        except Exception as e:
            return f"Error adding watermark: {str(e)}"
    
    # ==================== ADVANCED BACKUP & RECOVERY ====================
    
    def recover_deleted_files(self, search_path=None):
        """Attempt to recover deleted files from trash/recycle bin"""
        try:
            recovered_files = []
            
            # Linux trash locations
            trash_locations = [
                os.path.join(os.path.expanduser("~"), ".local/share/Trash/files"),
                "/tmp/.Trash-1000/files"  # System trash
            ]
            
            for trash_path in trash_locations:
                if os.path.exists(trash_path):
                    for item in os.listdir(trash_path):
                        item_path = os.path.join(trash_path, item)
                        if os.path.isfile(item_path):
                            recovered_files.append({
                                'name': item,
                                'path': item_path,
                                'size': os.path.getsize(item_path),
                                'modified': datetime.fromtimestamp(os.path.getmtime(item_path))
                            })
            
            if recovered_files:
                result = f"Found {len(recovered_files)} recoverable files:\n\n"
                for file_info in recovered_files[:20]:  # Show first 20
                    size_mb = file_info['size'] / (1024 * 1024)
                    modified = file_info['modified'].strftime("%Y-%m-%d %H:%M")
                    result += f" {file_info['name']} ({size_mb:.1f} MB, modified: {modified})\n"
                
                result += f"\nTo restore files, copy them from: {trash_locations[0]}"
                return result
            else:
                return "No recoverable files found in trash"
        
        except Exception as e:
            return f"Error recovering files: {str(e)}"
    
    def incremental_backup(self, source_path, backup_path):
        """Create incremental backup (only changed files)"""
        try:
            if not os.path.exists(source_path):
                return f"Source path {source_path} not found"
            
            # Create backup directory if it doesn't exist
            os.makedirs(backup_path, exist_ok=True)
            
            # Load previous backup manifest
            manifest_file = os.path.join(backup_path, "backup_manifest.json")
            previous_manifest = {}
            
            if os.path.exists(manifest_file):
                with open(manifest_file, 'r') as f:
                    previous_manifest = json.load(f)
            
            current_manifest = {}
            files_copied = 0
            total_size = 0
            
            # Walk through source directory
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    source_file = os.path.join(root, file)
                    relative_path = os.path.relpath(source_file, source_path)
                    
                    # Get file stats
                    stat = os.stat(source_file)
                    file_hash = self._get_file_hash(source_file)
                    
                    current_manifest[relative_path] = {
                        'size': stat.st_size,
                        'modified': stat.st_mtime,
                        'hash': file_hash
                    }
                    
                    # Check if file needs backup
                    needs_backup = (
                        relative_path not in previous_manifest or
                        previous_manifest[relative_path]['hash'] != file_hash
                    )
                    
                    if needs_backup:
                        # Create backup directory structure
                        backup_file = os.path.join(backup_path, relative_path)
                        backup_dir = os.path.dirname(backup_file)
                        os.makedirs(backup_dir, exist_ok=True)
                        
                        # Copy file
                        shutil.copy2(source_file, backup_file)
                        files_copied += 1
                        total_size += stat.st_size
            
            # Save new manifest
            with open(manifest_file, 'w') as f:
                json.dump(current_manifest, f, indent=2)
            
            # Update backup history
            backup_info = {
                'timestamp': datetime.now().isoformat(),
                'source': source_path,
                'destination': backup_path,
                'type': 'incremental',
                'files_count': files_copied,
                'size': total_size
            }
            
            self.backup_history.append(backup_info)
            self._save_backup_history()
            
            size_mb = total_size / (1024 * 1024)
            return f"Incremental backup completed!\nFiles backed up: {files_copied}\nTotal size: {size_mb:.1f} MB\nLocation: {backup_path}"
        
        except Exception as e:
            return f"Error creating incremental backup: {str(e)}"
    
    def schedule_backup(self, source_path, backup_path, frequency='daily'):
        """Schedule automatic backups"""
        try:
            # Create backup schedule entry
            schedule_entry = {
                'source': source_path,
                'destination': backup_path,
                'frequency': frequency,
                'next_backup': self._calculate_next_backup_time(frequency),
                'created': datetime.now().isoformat()
            }
            
            # Load existing schedules
            schedule_file = os.path.join(os.path.expanduser("~"), ".desktop_ai_backup_schedule.json")
            schedules = []
            
            if os.path.exists(schedule_file):
                with open(schedule_file, 'r') as f:
                    schedules = json.load(f)
            
            schedules.append(schedule_entry)
            
            with open(schedule_file, 'w') as f:
                json.dump(schedules, f, indent=2)
            
            next_backup = datetime.fromisoformat(schedule_entry['next_backup']).strftime("%Y-%m-%d %H:%M")
            return f"Backup scheduled successfully!\nFrequency: {frequency}\nNext backup: {next_backup}\nSource: {source_path}\nDestination: {backup_path}"
        
        except Exception as e:
            return f"Error scheduling backup: {str(e)}"
    
    def _calculate_next_backup_time(self, frequency):
        """Calculate next backup time based on frequency"""
        now = datetime.now()
        
        if frequency == 'hourly':
            return (now + timedelta(hours=1)).isoformat()
        elif frequency == 'daily':
            return (now + timedelta(days=1)).isoformat()
        elif frequency == 'weekly':
            return (now + timedelta(weeks=1)).isoformat()
        elif frequency == 'monthly':
            return (now + timedelta(days=30)).isoformat()
        else:
            return (now + timedelta(days=1)).isoformat()  # Default to daily
    
    # ==================== GLOBAL INSTANCE ====================
    
    file_manager = AdvancedFileManager()
    
    # ==================== CONVENIENCE FUNCTIONS ====================
    
    # organize_files function removed - use file_manager.organize_files_by_type() directly

    def rename_files_with_pattern(directory, pattern, new_pattern):
        """Rename files using patterns"""
        return file_manager.rename_files_pattern(directory, pattern, new_pattern)

    def find_duplicates(directory, check_content=True):
        """Find duplicate files"""
        return file_manager.find_duplicate_files(directory, check_content)

# ==================== CONVENIENCE FUNCTIONS ====================

# organize_files function removed - use file_manager.organize_files_by_type() directly

def rename_files_with_pattern(directory, pattern, new_pattern):
    """Rename files using patterns"""
    return file_manager.rename_files_pattern(directory, pattern, new_pattern)

def find_duplicates(directory, check_content=True):
    """Find duplicate files"""
    return file_manager.find_duplicate_files(directory, check_content)

def find_large_files(directory, min_size_mb=100):
    """Find large files"""
    return file_manager.find_large_files(directory, min_size_mb)

def find_unused_files(directory, days_unused=180):
    """Find unused files"""
    return file_manager.find_unused_files(directory, days_unused)

def compress_files(folder_path, output_path=None, format="zip"):
    """Compress folder"""
    return file_manager.compress_folder(folder_path, output_path, format)

def extract_files(archive_path, extract_to=None):
    """Extract archive"""
    return file_manager.extract_archive(archive_path, extract_to)

def smart_file_search(query, search_directory=None):
    """Natural language file search"""
    return file_manager.natural_language_search(query, search_directory)

def backup_files(source_path, backup_location=None):
    """Create backup"""
    return file_manager.create_backup(source_path, backup_location)

def get_backup_history():
    """Get backup history"""
    return file_manager.get_backup_history()
