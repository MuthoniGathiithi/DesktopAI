import os
import re
import json
from datetime import datetime
from pathlib import Path
import requests
from urllib.parse import urlparse

# ==================== CITATION GENERATOR ====================

class CitationGenerator:
    def __init__(self):
        self.citation_styles = {
            'apa': self._generate_apa_citation,
            'mla': self._generate_mla_citation,
            'chicago': self._generate_chicago_citation,
            'harvard': self._generate_harvard_citation,
            'ieee': self._generate_ieee_citation
        }
        self.citation_history = []
    
    def generate_citation(self, source_type, source_info, style='apa'):
        """Generate citation for various source types"""
        try:
            style = style.lower()
            if style not in self.citation_styles:
                return f"Unsupported citation style: {style}. Available: {', '.join(self.citation_styles.keys())}"
            
            citation_func = self.citation_styles[style]
            citation = citation_func(source_type, source_info)
            
            # Save to history
            self.citation_history.append({
                'citation': citation,
                'style': style,
                'source_type': source_type,
                'timestamp': datetime.now().isoformat()
            })
            
            return citation
        
        except Exception as e:
            return f"Error generating citation: {str(e)}"
    
    def generate_pdf_citation(self, pdf_path, style='apa'):
        """Generate citation for PDF file"""
        try:
            if not os.path.exists(pdf_path):
                return f"PDF file not found: {pdf_path}"
            
            # Extract metadata from PDF
            metadata = self._extract_pdf_metadata(pdf_path)
            
            # Generate citation based on extracted info
            citation = self.generate_citation('pdf', metadata, style)
            
            return f"📄 PDF Citation ({style.upper()}):\n\n{citation}\n\nSource: {pdf_path}"
        
        except Exception as e:
            return f"Error generating PDF citation: {str(e)}"
    
    def generate_website_citation(self, url, style='apa'):
        """Generate citation for website"""
        try:
            # Extract website metadata
            metadata = self._extract_website_metadata(url)
            
            citation = self.generate_citation('website', metadata, style)
            
            return f"🌐 Website Citation ({style.upper()}):\n\n{citation}\n\nSource: {url}"
        
        except Exception as e:
            return f"Error generating website citation: {str(e)}"
    
    def _extract_pdf_metadata(self, pdf_path):
        """Extract metadata from PDF file"""
        try:
            # Try to use PyPDF2 for metadata extraction
            try:
                import PyPDF2
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    metadata = reader.metadata
                    
                    return {
                        'title': metadata.get('/Title', os.path.basename(pdf_path)),
                        'author': metadata.get('/Author', 'Unknown Author'),
                        'year': self._extract_year_from_metadata(metadata),
                        'filename': os.path.basename(pdf_path),
                        'filepath': pdf_path
                    }
            except ImportError:
                pass
            
            # Fallback: extract info from filename
            filename = os.path.basename(pdf_path)
            
            # Try to extract year from filename
            year_match = re.search(r'(19|20)\d{2}', filename)
            year = year_match.group() if year_match else str(datetime.now().year)
            
            # Clean filename for title
            title = re.sub(r'\.(pdf|PDF)$', '', filename)
            title = re.sub(r'[_-]', ' ', title)
            
            return {
                'title': title,
                'author': 'Unknown Author',
                'year': year,
                'filename': filename,
                'filepath': pdf_path
            }
        
        except Exception as e:
            return {
                'title': os.path.basename(pdf_path),
                'author': 'Unknown Author',
                'year': str(datetime.now().year),
                'filename': os.path.basename(pdf_path),
                'filepath': pdf_path
            }
    
    def _extract_website_metadata(self, url):
        """Extract metadata from website"""
        try:
            # Parse URL
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            # Try to fetch page metadata
            try:
                response = requests.get(url, timeout=10)
                content = response.text
                
                # Extract title
                title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
                title = title_match.group(1).strip() if title_match else domain
                
                # Extract author from meta tags
                author_match = re.search(r'<meta[^>]*name=["\']author["\'][^>]*content=["\']([^"\']+)["\']', content, re.IGNORECASE)
                author = author_match.group(1) if author_match else domain
                
                # Extract publication date
                date_patterns = [
                    r'<meta[^>]*name=["\']date["\'][^>]*content=["\']([^"\']+)["\']',
                    r'<meta[^>]*property=["\']article:published_time["\'][^>]*content=["\']([^"\']+)["\']'
                ]
                
                pub_date = None
                for pattern in date_patterns:
                    date_match = re.search(pattern, content, re.IGNORECASE)
                    if date_match:
                        pub_date = date_match.group(1)
                        break
                
                year = self._extract_year_from_date(pub_date) if pub_date else str(datetime.now().year)
                
                return {
                    'title': title,
                    'author': author,
                    'year': year,
                    'url': url,
                    'domain': domain,
                    'access_date': datetime.now().strftime('%B %d, %Y')
                }
            
            except:
                # Fallback if can't fetch page
                return {
                    'title': domain,
                    'author': domain,
                    'year': str(datetime.now().year),
                    'url': url,
                    'domain': domain,
                    'access_date': datetime.now().strftime('%B %d, %Y')
                }
        
        except Exception as e:
            return {
                'title': 'Unknown Title',
                'author': 'Unknown Author',
                'year': str(datetime.now().year),
                'url': url,
                'domain': 'unknown',
                'access_date': datetime.now().strftime('%B %d, %Y')
            }
    
    def _extract_year_from_metadata(self, metadata):
        """Extract year from PDF metadata"""
        try:
            # Check creation date
            if '/CreationDate' in metadata:
                date_str = str(metadata['/CreationDate'])
                year_match = re.search(r'(19|20)\d{2}', date_str)
                if year_match:
                    return year_match.group()
            
            # Check modification date
            if '/ModDate' in metadata:
                date_str = str(metadata['/ModDate'])
                year_match = re.search(r'(19|20)\d{2}', date_str)
                if year_match:
                    return year_match.group()
            
            return str(datetime.now().year)
        except:
            return str(datetime.now().year)
    
    def _extract_year_from_date(self, date_str):
        """Extract year from date string"""
        try:
            year_match = re.search(r'(19|20)\d{2}', date_str)
            return year_match.group() if year_match else str(datetime.now().year)
        except:
            return str(datetime.now().year)
    
    def _generate_apa_citation(self, source_type, info):
        """Generate APA style citation"""
        try:
            if source_type == 'pdf':
                # APA format: Author, A. A. (Year). Title. Publisher.
                author = info.get('author', 'Unknown Author')
                year = info.get('year', datetime.now().year)
                title = info.get('title', 'Unknown Title')
                
                # Format author (last name, first initial)
                if author != 'Unknown Author' and ',' not in author:
                    name_parts = author.split()
                    if len(name_parts) >= 2:
                        author = f"{name_parts[-1]}, {name_parts[0][0]}."
                
                return f"{author} ({year}). {title}. [PDF file]."
            
            elif source_type == 'website':
                # APA format: Author, A. A. (Year, Month Date). Title. Website Name. URL
                author = info.get('author', info.get('domain', 'Unknown Author'))
                year = info.get('year', datetime.now().year)
                title = info.get('title', 'Unknown Title')
                domain = info.get('domain', 'Unknown Website')
                url = info.get('url', '')
                access_date = info.get('access_date', datetime.now().strftime('%B %d, %Y'))
                
                return f"{author} ({year}). {title}. {domain}. Retrieved {access_date}, from {url}"
            
            return "Unknown source type for APA citation"
        
        except Exception as e:
            return f"Error generating APA citation: {str(e)}"
    
    def _generate_mla_citation(self, source_type, info):
        """Generate MLA style citation"""
        try:
            if source_type == 'pdf':
                # MLA format: Author. "Title." Year. PDF file.
                author = info.get('author', 'Unknown Author')
                year = info.get('year', datetime.now().year)
                title = info.get('title', 'Unknown Title')
                
                return f'{author}. "{title}." {year}. PDF file.'
            
            elif source_type == 'website':
                # MLA format: Author. "Title." Website Name, Date, URL.
                author = info.get('author', info.get('domain', 'Unknown Author'))
                title = info.get('title', 'Unknown Title')
                domain = info.get('domain', 'Unknown Website')
                year = info.get('year', datetime.now().year)
                url = info.get('url', '')
                
                return f'{author}. "{title}." {domain}, {year}, {url}.'
            
            return "Unknown source type for MLA citation"
        
        except Exception as e:
            return f"Error generating MLA citation: {str(e)}"
    
    def _generate_chicago_citation(self, source_type, info):
        """Generate Chicago style citation"""
        try:
            if source_type == 'pdf':
                # Chicago format: Author. "Title." Year. PDF file.
                author = info.get('author', 'Unknown Author')
                year = info.get('year', datetime.now().year)
                title = info.get('title', 'Unknown Title')
                
                return f'{author}. "{title}." {year}. PDF file.'
            
            elif source_type == 'website':
                # Chicago format: Author. "Title." Website Name. Accessed Date. URL.
                author = info.get('author', info.get('domain', 'Unknown Author'))
                title = info.get('title', 'Unknown Title')
                domain = info.get('domain', 'Unknown Website')
                access_date = info.get('access_date', datetime.now().strftime('%B %d, %Y'))
                url = info.get('url', '')
                
                return f'{author}. "{title}." {domain}. Accessed {access_date}. {url}.'
            
            return "Unknown source type for Chicago citation"
        
        except Exception as e:
            return f"Error generating Chicago citation: {str(e)}"
    
    def _generate_harvard_citation(self, source_type, info):
        """Generate Harvard style citation"""
        try:
            if source_type == 'pdf':
                # Harvard format: Author, A. (Year) 'Title', PDF file.
                author = info.get('author', 'Unknown Author')
                year = info.get('year', datetime.now().year)
                title = info.get('title', 'Unknown Title')
                
                return f"{author} ({year}) '{title}', PDF file."
            
            elif source_type == 'website':
                # Harvard format: Author, A. (Year) 'Title', Website Name, accessed Date, <URL>.
                author = info.get('author', info.get('domain', 'Unknown Author'))
                year = info.get('year', datetime.now().year)
                title = info.get('title', 'Unknown Title')
                domain = info.get('domain', 'Unknown Website')
                access_date = info.get('access_date', datetime.now().strftime('%d %B %Y'))
                url = info.get('url', '')
                
                return f"{author} ({year}) '{title}', {domain}, accessed {access_date}, <{url}>."
            
            return "Unknown source type for Harvard citation"
        
        except Exception as e:
            return f"Error generating Harvard citation: {str(e)}"
    
    def _generate_ieee_citation(self, source_type, info):
        """Generate IEEE style citation"""
        try:
            if source_type == 'pdf':
                # IEEE format: A. Author, "Title," Year. [PDF file].
                author = info.get('author', 'Unknown Author')
                year = info.get('year', datetime.now().year)
                title = info.get('title', 'Unknown Title')
                
                # Format author for IEEE (A. B. Author)
                if author != 'Unknown Author':
                    name_parts = author.split()
                    if len(name_parts) >= 2:
                        author = f"{name_parts[0][0]}. {' '.join(name_parts[1:])}"
                
                return f'{author}, "{title}," {year}. [PDF file].'
            
            elif source_type == 'website':
                # IEEE format: A. Author, "Title," Website Name, Year. [Online]. Available: URL. [Accessed: Date].
                author = info.get('author', info.get('domain', 'Unknown Author'))
                title = info.get('title', 'Unknown Title')
                domain = info.get('domain', 'Unknown Website')
                year = info.get('year', datetime.now().year)
                url = info.get('url', '')
                access_date = info.get('access_date', datetime.now().strftime('%b. %d, %Y'))
                
                return f'{author}, "{title}," {domain}, {year}. [Online]. Available: {url}. [Accessed: {access_date}].'
            
            return "Unknown source type for IEEE citation"
        
        except Exception as e:
            return f"Error generating IEEE citation: {str(e)}"
    
    def get_citation_history(self):
        """Get citation history"""
        try:
            if not self.citation_history:
                return "No citations generated yet"
            
            result = "📚 Citation History:\n\n"
            for i, entry in enumerate(self.citation_history[-10:], 1):  # Show last 10
                timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M')
                result += f"{i}. {entry['style'].upper()} - {entry['source_type']}\n"
                result += f"   {entry['citation']}\n"
                result += f"   Generated: {timestamp}\n\n"
            
            return result
        
        except Exception as e:
            return f"Error getting citation history: {str(e)}"
    
    def generate_bibliography(self, citations, style='apa'):
        """Generate bibliography from multiple citations"""
        try:
            if not citations:
                return "No citations provided"
            
            result = f"📖 Bibliography ({style.upper()}):\n\n"
            
            for i, citation in enumerate(citations, 1):
                result += f"{citation}\n\n"
            
            return result
        
        except Exception as e:
            return f"Error generating bibliography: {str(e)}"

# ==================== GLOBAL INSTANCE ====================

citation_generator = CitationGenerator()

# ==================== CONVENIENCE FUNCTIONS ====================

def generate_pdf_citation(pdf_path, style='apa'):
    """Generate citation for PDF file"""
    return citation_generator.generate_pdf_citation(pdf_path, style)

def generate_website_citation(url, style='apa'):
    """Generate citation for website"""
    return citation_generator.generate_website_citation(url, style)

def get_citation_history():
    """Get citation history"""
    return citation_generator.get_citation_history()

def generate_bibliography(citations, style='apa'):
    """Generate bibliography"""
    return citation_generator.generate_bibliography(citations, style)
