import os
import re
import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import mimetypes
import threading
import time

# ==================== PREMIUM SEARCH - FIND MY LOST FILE ====================

class PremiumSearchEngine:
    def __init__(self):
        self.search_db = os.path.join(os.path.expanduser("~"), ".desktop_ai_search.db")
        self.file_index = {}
        self.content_cache = {}
        self.access_history = []
        self._init_search_database()
        self._load_file_index()
        
    def _init_search_database(self):
        """Initialize search database"""
        try:
            conn = sqlite3.connect(self.search_db)
            cursor = conn.cursor()
            
            # File index table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE,
                    filename TEXT,
                    file_size INTEGER,
                    file_type TEXT,
                    content_preview TEXT,
                    last_modified TEXT,
                    last_accessed TEXT,
                    folder_path TEXT,
                    file_hash TEXT,
                    indexed_date TEXT
                )
            ''')
            
            # File access history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS access_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT,
                    access_type TEXT,
                    timestamp TEXT,
                    user_activity TEXT
                )
            ''')
            
            # Content search cache
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS content_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT,
                    content_text TEXT,
                    keywords TEXT,
                    last_updated TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error initializing search database: {e}")
    
    def _load_file_index(self):
        """Load existing file index"""
        try:
            conn = sqlite3.connect(self.search_db)
            cursor = conn.cursor()
            
            cursor.execute('SELECT file_path, filename, last_modified FROM file_index')
            results = cursor.fetchall()
            
            for file_path, filename, last_modified in results:
                self.file_index[file_path] = {
                    'filename': filename,
                    'last_modified': last_modified,
                    'indexed': True
                }
            
            conn.close()
        except Exception as e:
            print(f"Error loading file index: {e}")
    
    def find_lost_file(self, description, search_type='comprehensive'):
        """PREMIUM: Find lost file with natural language description"""
        try:
            if search_type == 'basic':
                return "🔒 Premium Feature: Upgrade for advanced file search with content analysis"
            
            # Parse the description
            search_terms = self._extract_search_terms(description)
            
            # Multi-layered search
            results = []
            
            # 1. Filename search
            filename_results = self._search_by_filename(search_terms)
            results.extend(filename_results)
            
            # 2. Content search (PREMIUM)
            content_results = self._search_by_content(search_terms)
            results.extend(content_results)
            
            # 3. Temporal search (PREMIUM)
            temporal_results = self._search_by_time(description)
            results.extend(temporal_results)
            
            # 4. Context search (PREMIUM)
            context_results = self._search_by_context(search_terms)
            results.extend(context_results)
            
            # Remove duplicates and rank results
            unique_results = self._deduplicate_and_rank(results)
            
            if not unique_results:
                return "❌ No files found matching your description. Try different keywords or check if the file exists."
            
            return self._format_search_results(unique_results, description)
        
        except Exception as e:
            return f"Error in premium search: {str(e)}"
    
    def find_files_by_date(self, date_description):
        """Find files worked on specific date"""
        try:
            # Parse date from description
            target_date = self._parse_date_description(date_description)
            
            if not target_date:
                return "Could not understand the date. Try: 'last Tuesday', 'yesterday', '2023-12-15'"
            
            conn = sqlite3.connect(self.search_db)
            cursor = conn.cursor()
            
            # Search access history for that date
            start_date = target_date.strftime('%Y-%m-%d 00:00:00')
            end_date = target_date.strftime('%Y-%m-%d 23:59:59')
            
            cursor.execute('''
                SELECT DISTINCT file_path, access_type, timestamp 
                FROM access_history 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
            ''', (start_date, end_date))
            
            results = cursor.fetchall()
            conn.close()
            
            if not results:
                return f"No files found for {target_date.strftime('%A, %B %d, %Y')}"
            
            # Format results
            result_text = f"📅 Files you worked on {target_date.strftime('%A, %B %d, %Y')}:\n\n"
            
            for file_path, access_type, timestamp in results[:20]:  # Limit to 20
                if os.path.exists(file_path):
                    filename = os.path.basename(file_path)
                    time_str = datetime.fromisoformat(timestamp).strftime('%H:%M')
                    result_text += f"• {filename}\n"
                    result_text += f"  📁 {os.path.dirname(file_path)}\n"
                    result_text += f"  🕐 {access_type} at {time_str}\n\n"
            
            return result_text
        
        except Exception as e:
            return f"Error searching by date: {str(e)}"
    
    def find_file_with_content(self, content_description):
        """Find file containing specific content"""
        try:
            search_terms = content_description.lower().split()
            
            conn = sqlite3.connect(self.search_db)
            cursor = conn.cursor()
            
            # Search in content cache
            results = []
            for term in search_terms:
                cursor.execute('''
                    SELECT file_path, content_text 
                    FROM content_cache 
                    WHERE content_text LIKE ? OR keywords LIKE ?
                ''', (f'%{term}%', f'%{term}%'))
                
                term_results = cursor.fetchall()
                results.extend(term_results)
            
            conn.close()
            
            if not results:
                return f"No files found containing '{content_description}'"
            
            # Remove duplicates and format
            unique_files = {}
            for file_path, content in results:
                if os.path.exists(file_path):
                    if file_path not in unique_files:
                        unique_files[file_path] = content
            
            if not unique_files:
                return "Files found in index but no longer exist on disk"
            
            result_text = f"📄 Files containing '{content_description}':\n\n"
            
            for file_path, content in list(unique_files.items())[:10]:  # Limit to 10
                filename = os.path.basename(file_path)
                # Show content snippet
                snippet = self._extract_content_snippet(content, search_terms)
                
                result_text += f"• {filename}\n"
                result_text += f"  📁 {os.path.dirname(file_path)}\n"
                result_text += f"  💬 ...{snippet}...\n\n"
            
            return result_text
        
        except Exception as e:
            return f"Error searching file content: {str(e)}"
    
    def _extract_search_terms(self, description):
        """Extract meaningful search terms from description"""
        try:
            # Remove common words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'was', 'were', 'is', 'are', 'where', 'that', 'file', 'document'}
            
            # Extract words
            words = re.findall(r'\b\w+\b', description.lower())
            
            # Filter meaningful terms
            search_terms = [word for word in words if len(word) > 2 and word not in stop_words]
            
            # Look for file types
            file_types = ['excel', 'word', 'pdf', 'powerpoint', 'image', 'photo', 'video', 'audio']
            for file_type in file_types:
                if file_type in description.lower():
                    search_terms.append(file_type)
            
            return search_terms
        
        except Exception as e:
            return description.lower().split()
    
    def _search_by_filename(self, search_terms):
        """Search by filename"""
        try:
            results = []
            
            conn = sqlite3.connect(self.search_db)
            cursor = conn.cursor()
            
            for term in search_terms:
                cursor.execute('SELECT * FROM file_index WHERE filename LIKE ?', (f'%{term}%',))
                term_results = cursor.fetchall()
                
                for result in term_results:
                    file_path = result[1]
                    if os.path.exists(file_path):
                        results.append({
                            'file_path': file_path,
                            'match_type': 'filename',
                            'match_term': term,
                            'score': 10,  # High score for filename matches
                            'details': result
                        })
            
            conn.close()
            return results
        
        except Exception as e:
            return []
    
    def _search_by_content(self, search_terms):
        """Search by file content (PREMIUM)"""
        try:
            results = []
            
            conn = sqlite3.connect(self.search_db)
            cursor = conn.cursor()
            
            for term in search_terms:
                cursor.execute('''
                    SELECT fc.file_path, fc.content_text, fi.filename, fi.last_modified
                    FROM content_cache fc
                    JOIN file_index fi ON fc.file_path = fi.file_path
                    WHERE fc.content_text LIKE ? OR fc.keywords LIKE ?
                ''', (f'%{term}%', f'%{term}%'))
                
                term_results = cursor.fetchall()
                
                for file_path, content, filename, last_modified in term_results:
                    if os.path.exists(file_path):
                        results.append({
                            'file_path': file_path,
                            'match_type': 'content',
                            'match_term': term,
                            'score': 8,  # Good score for content matches
                            'content_snippet': self._extract_content_snippet(content, [term])
                        })
            
            conn.close()
            return results
        
        except Exception as e:
            return []
    
    def _search_by_time(self, description):
        """Search by temporal references (PREMIUM)"""
        try:
            results = []
            
            # Parse time references
            time_patterns = {
                'last week': 7,
                'yesterday': 1,
                'last tuesday': None,  # Special handling
                'this morning': 0.5,
                'last month': 30
            }
            
            for pattern, days_ago in time_patterns.items():
                if pattern in description.lower():
                    if days_ago is not None:
                        target_date = datetime.now() - timedelta(days=days_ago)
                        results.extend(self._get_files_from_date_range(target_date, target_date + timedelta(days=1)))
            
            return results
        
        except Exception as e:
            return []
    
    def _search_by_context(self, search_terms):
        """Search by context (folder, recent activity)"""
        try:
            results = []
            
            # Search in recently accessed files
            conn = sqlite3.connect(self.search_db)
            cursor = conn.cursor()
            
            # Get recent files that might match
            cursor.execute('''
                SELECT DISTINCT ah.file_path, ah.timestamp, fi.filename
                FROM access_history ah
                JOIN file_index fi ON ah.file_path = fi.file_path
                WHERE ah.timestamp > ?
                ORDER BY ah.timestamp DESC
                LIMIT 50
            ''', ((datetime.now() - timedelta(days=7)).isoformat(),))
            
            recent_files = cursor.fetchall()
            
            # Check if any search terms match these recent files
            for file_path, timestamp, filename in recent_files:
                if os.path.exists(file_path):
                    for term in search_terms:
                        if term in filename.lower() or term in file_path.lower():
                            results.append({
                                'file_path': file_path,
                                'match_type': 'recent_context',
                                'match_term': term,
                                'score': 6,  # Medium score for context matches
                                'last_access': timestamp
                            })
            
            conn.close()
            return results
        
        except Exception as e:
            return []
    
    def _deduplicate_and_rank(self, results):
        """Remove duplicates and rank by relevance"""
        try:
            # Group by file path
            file_scores = {}
            
            for result in results:
                file_path = result['file_path']
                if file_path not in file_scores:
                    file_scores[file_path] = {
                        'total_score': 0,
                        'match_types': [],
                        'details': result
                    }
                
                file_scores[file_path]['total_score'] += result['score']
                file_scores[file_path]['match_types'].append(result['match_type'])
            
            # Sort by score
            ranked_results = sorted(
                file_scores.items(),
                key=lambda x: x[1]['total_score'],
                reverse=True
            )
            
            return ranked_results[:15]  # Return top 15 results
        
        except Exception as e:
            return []
    
    def _format_search_results(self, results, original_query):
        """Format search results for display"""
        try:
            if not results:
                return "No files found"
            
            result_text = f"🔍 Found {len(results)} files matching '{original_query}':\n\n"
            
            for i, (file_path, data) in enumerate(results, 1):
                filename = os.path.basename(file_path)
                folder = os.path.dirname(file_path)
                score = data['total_score']
                match_types = ', '.join(set(data['match_types']))
                
                # File info
                try:
                    stat = os.stat(file_path)
                    size_mb = stat.st_size / (1024 * 1024)
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                except:
                    size_mb = 0
                    modified = 'Unknown'
                
                result_text += f"{i}. **{filename}** (Score: {score})\n"
                result_text += f"   📁 {folder}\n"
                result_text += f"   📊 {size_mb:.1f} MB • Modified: {modified}\n"
                result_text += f"   🎯 Matched: {match_types}\n"
                
                # Add content snippet if available
                if 'content_snippet' in data['details']:
                    result_text += f"   💬 \"{data['details']['content_snippet']}\"\n"
                
                result_text += "\n"
            
            result_text += "💡 Tip: Use more specific keywords for better results"
            return result_text
        
        except Exception as e:
            return f"Error formatting results: {str(e)}"
    
    def _parse_date_description(self, description):
        """Parse natural language date descriptions"""
        try:
            today = datetime.now()
            description = description.lower()
            
            if 'yesterday' in description:
                return today - timedelta(days=1)
            elif 'last tuesday' in description:
                # Find last Tuesday
                days_back = (today.weekday() - 1) % 7
                if days_back == 0:  # Today is Tuesday
                    days_back = 7
                return today - timedelta(days=days_back)
            elif 'last week' in description:
                return today - timedelta(days=7)
            elif 'last month' in description:
                return today - timedelta(days=30)
            
            # Try to parse specific date formats
            date_patterns = [
                r'(\d{4}-\d{2}-\d{2})',
                r'(\d{2}/\d{2}/\d{4})',
                r'(\d{2}-\d{2}-\d{4})'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, description)
                if match:
                    date_str = match.group(1)
                    try:
                        if '-' in date_str and len(date_str.split('-')[0]) == 4:
                            return datetime.strptime(date_str, '%Y-%m-%d')
                        elif '/' in date_str:
                            return datetime.strptime(date_str, '%m/%d/%Y')
                        elif '-' in date_str:
                            return datetime.strptime(date_str, '%m-%d-%Y')
                    except:
                        continue
            
            return None
        
        except Exception as e:
            return None
    
    def _extract_content_snippet(self, content, search_terms):
        """Extract relevant snippet from content"""
        try:
            if not content or not search_terms:
                return "No preview available"
            
            content = content.lower()
            
            # Find the first occurrence of any search term
            best_pos = len(content)
            best_term = None
            
            for term in search_terms:
                pos = content.find(term.lower())
                if pos != -1 and pos < best_pos:
                    best_pos = pos
                    best_term = term
            
            if best_term is None:
                return content[:100]
            
            # Extract snippet around the term
            start = max(0, best_pos - 50)
            end = min(len(content), best_pos + 100)
            
            snippet = content[start:end].strip()
            
            # Clean up the snippet
            if len(snippet) > 100:
                snippet = snippet[:100] + "..."
            
            return snippet
        
        except Exception as e:
            return "Preview unavailable"
    
    def _get_files_from_date_range(self, start_date, end_date):
        """Get files accessed in date range"""
        try:
            results = []
            
            conn = sqlite3.connect(self.search_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT DISTINCT file_path, timestamp
                FROM access_history
                WHERE timestamp BETWEEN ? AND ?
            ''', (start_date.isoformat(), end_date.isoformat()))
            
            files = cursor.fetchall()
            
            for file_path, timestamp in files:
                if os.path.exists(file_path):
                    results.append({
                        'file_path': file_path,
                        'match_type': 'temporal',
                        'match_term': 'date_range',
                        'score': 7,
                        'access_time': timestamp
                    })
            
            conn.close()
            return results
        
        except Exception as e:
            return []
    
    def index_file_system(self, root_paths=None):
        """Index file system for premium search (background process)"""
        try:
            if root_paths is None:
                root_paths = [
                    os.path.expanduser("~"),
                    "C:\\" if os.name == 'nt' else "/"
                ]
            
            indexed_count = 0
            
            for root_path in root_paths:
                if os.path.exists(root_path):
                    for root, dirs, files in os.walk(root_path):
                        # Skip system directories
                        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['System32', 'Windows', 'Program Files']]
                        
                        for file in files:
                            if indexed_count >= 10000:  # Limit for performance
                                break
                            
                            file_path = os.path.join(root, file)
                            
                            try:
                                if self._should_index_file(file_path):
                                    self._index_single_file(file_path)
                                    indexed_count += 1
                            except Exception as e:
                                continue
            
            return f"✅ Indexed {indexed_count} files for premium search"
        
        except Exception as e:
            return f"Error indexing files: {str(e)}"
    
    def _should_index_file(self, file_path):
        """Check if file should be indexed"""
        try:
            # Skip very large files
            if os.path.getsize(file_path) > 100 * 1024 * 1024:  # 100MB
                return False
            
            # Skip system files
            if any(sys_dir in file_path for sys_dir in ['.git', '__pycache__', 'node_modules', '.vscode']):
                return False
            
            # Focus on common file types
            _, ext = os.path.splitext(file_path)
            indexable_extensions = ['.txt', '.docx', '.pdf', '.xlsx', '.pptx', '.py', '.js', '.html', '.css', '.json', '.xml', '.csv']
            
            return ext.lower() in indexable_extensions
        
        except Exception as e:
            return False
    
    def _index_single_file(self, file_path):
        """Index a single file"""
        try:
            conn = sqlite3.connect(self.search_db)
            cursor = conn.cursor()
            
            # Get file info
            stat = os.stat(file_path)
            filename = os.path.basename(file_path)
            file_size = stat.st_size
            file_type = mimetypes.guess_type(file_path)[0] or 'unknown'
            last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
            folder_path = os.path.dirname(file_path)
            
            # Generate file hash
            file_hash = self._generate_file_hash(file_path)
            
            # Extract content preview
            content_preview = self._extract_file_content(file_path)
            
            # Insert or update file index
            cursor.execute('''
                INSERT OR REPLACE INTO file_index 
                (file_path, filename, file_size, file_type, content_preview, last_modified, folder_path, file_hash, indexed_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (file_path, filename, file_size, file_type, content_preview[:500], last_modified, folder_path, file_hash, datetime.now().isoformat()))
            
            # Store full content for search
            if content_preview:
                keywords = ' '.join(self._extract_keywords(content_preview))
                cursor.execute('''
                    INSERT OR REPLACE INTO content_cache
                    (file_path, content_text, keywords, last_updated)
                    VALUES (?, ?, ?, ?)
                ''', (file_path, content_preview, keywords, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
        
        except Exception as e:
            pass  # Skip problematic files
    
    def _generate_file_hash(self, file_path):
        """Generate hash for file"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return "unknown"
    
    def _extract_file_content(self, file_path):
        """Extract searchable content from file"""
        try:
            _, ext = os.path.splitext(file_path)
            ext = ext.lower()
            
            if ext in ['.txt', '.py', '.js', '.html', '.css', '.json', '.xml', '.csv']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()[:5000]  # First 5000 chars
            
            # For other file types, return filename and path as searchable content
            return f"{os.path.basename(file_path)} {file_path}"
        
        except Exception as e:
            return ""
    
    def _extract_keywords(self, content):
        """Extract keywords from content"""
        try:
            # Simple keyword extraction
            words = re.findall(r'\b\w+\b', content.lower())
            
            # Filter out common words and short words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            keywords = [word for word in words if len(word) > 3 and word not in stop_words]
            
            # Return unique keywords
            return list(set(keywords))[:50]  # Limit to 50 keywords
        
        except Exception as e:
            return []
    
    def record_file_access(self, file_path, access_type='opened'):
        """Record file access for temporal search"""
        try:
            conn = sqlite3.connect(self.search_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO access_history (file_path, access_type, timestamp, user_activity)
                VALUES (?, ?, ?, ?)
            ''', (file_path, access_type, datetime.now().isoformat(), 'user_interaction'))
            
            conn.commit()
            conn.close()
        
        except Exception as e:
            pass  # Don't break functionality if logging fails

# ==================== GLOBAL INSTANCE ====================

premium_search = PremiumSearchEngine()

# ==================== CONVENIENCE FUNCTIONS ====================

def find_lost_file(description):
    """Premium: Find lost file with natural language"""
    return premium_search.find_lost_file(description, 'comprehensive')

def find_files_by_date(date_description):
    """Find files worked on specific date"""
    return premium_search.find_files_by_date(date_description)

def find_file_with_content(content_description):
    """Find file containing specific content"""
    return premium_search.find_file_with_content(content_description)

def index_files_for_search():
    """Index file system for premium search"""
    return premium_search.index_file_system()

def record_file_access(file_path, access_type='opened'):
    """Record file access for tracking"""
    return premium_search.record_file_access(file_path, access_type)
