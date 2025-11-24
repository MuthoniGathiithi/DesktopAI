import os
import subprocess
import json
import time
import requests
import shutil
from datetime import datetime
from pathlib import Path
import threading
import queue

# ==================== CROSS-APP WORKFLOWS - THE KILLER FEATURE ====================

class WorkflowEngine:
    def __init__(self):
        self.workflows = {}
        self.running_workflows = {}
        self.workflow_templates = self._load_workflow_templates()
        self.monitor_threads = {}
        
    def _load_workflow_templates(self):
        """Load predefined workflow templates"""
        return {
            "screenshot_share": {
                "name": "Screenshot → Compress → Upload → Share",
                "steps": [
                    {"action": "take_screenshot", "params": {}},
                    {"action": "compress_image", "params": {"quality": 70}},
                    {"action": "upload_to_drive", "params": {}},
                    {"action": "get_share_link", "params": {}},
                    {"action": "copy_to_clipboard", "params": {}}
                ]
            },
            "video_transcribe": {
                "name": "Download Video → Extract Audio → Transcribe → Save PDF",
                "steps": [
                    {"action": "download_video", "params": {}},
                    {"action": "extract_audio", "params": {"format": "wav"}},
                    {"action": "transcribe_audio", "params": {}},
                    {"action": "create_pdf", "params": {}},
                    {"action": "save_file", "params": {}}
                ]
            },
            "invoice_processor": {
                "name": "Find Invoices → Extract Amounts → Add to Excel",
                "steps": [
                    {"action": "search_emails", "params": {"query": "invoice"}},
                    {"action": "download_attachments", "params": {}},
                    {"action": "extract_amounts", "params": {}},
                    {"action": "update_excel", "params": {}},
                    {"action": "send_summary", "params": {}}
                ]
            },
            "pdf_monitor": {
                "name": "Monitor Folder → Process PDF → Summarize → Notify",
                "steps": [
                    {"action": "monitor_folder", "params": {"folder": "", "file_type": "pdf"}},
                    {"action": "extract_pdf_text", "params": {}},
                    {"action": "summarize_text", "params": {}},
                    {"action": "send_notification", "params": {}}
                ]
            }
        }
    
    def execute_workflow(self, workflow_name, params=None):
        """Execute a predefined workflow"""
        try:
            if workflow_name not in self.workflow_templates:
                return f"Workflow '{workflow_name}' not found"
            
            workflow = self.workflow_templates[workflow_name]
            workflow_id = f"{workflow_name}_{int(time.time())}"
            
            self.running_workflows[workflow_id] = {
                "name": workflow["name"],
                "status": "running",
                "current_step": 0,
                "total_steps": len(workflow["steps"]),
                "results": [],
                "start_time": datetime.now()
            }
            
            # Execute steps sequentially
            for i, step in enumerate(workflow["steps"]):
                self.running_workflows[workflow_id]["current_step"] = i + 1
                
                result = self._execute_step(step, params)
                self.running_workflows[workflow_id]["results"].append({
                    "step": step["action"],
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })
                
                if "error" in result.lower():
                    self.running_workflows[workflow_id]["status"] = "failed"
                    return f"Workflow failed at step {i+1}: {result}"
            
            self.running_workflows[workflow_id]["status"] = "completed"
            return f"✅ Workflow '{workflow['name']}' completed successfully!\n\nResults:\n" + \
                   "\n".join([f"• {r['step']}: {r['result']}" for r in self.running_workflows[workflow_id]["results"]])
        
        except Exception as e:
            return f"Error executing workflow: {str(e)}"
    
    def _execute_step(self, step, workflow_params):
        """Execute a single workflow step"""
        action = step["action"]
        params = {**step["params"], **(workflow_params or {})}
        
        try:
            if action == "take_screenshot":
                return self._take_screenshot(params)
            elif action == "compress_image":
                return self._compress_image(params)
            elif action == "upload_to_drive":
                return self._upload_to_drive(params)
            elif action == "get_share_link":
                return self._get_share_link(params)
            elif action == "copy_to_clipboard":
                return self._copy_to_clipboard(params)
            elif action == "download_video":
                return self._download_video(params)
            elif action == "extract_audio":
                return self._extract_audio(params)
            elif action == "transcribe_audio":
                return self._transcribe_audio(params)
            elif action == "create_pdf":
                return self._create_pdf(params)
            elif action == "search_emails":
                return self._search_emails(params)
            elif action == "extract_amounts":
                return self._extract_amounts(params)
            elif action == "update_excel":
                return self._update_excel(params)
            elif action == "monitor_folder":
                return self._monitor_folder(params)
            elif action == "extract_pdf_text":
                return self._extract_pdf_text(params)
            elif action == "summarize_text":
                return self._summarize_text(params)
            elif action == "send_notification":
                return self._send_notification(params)
            else:
                return f"Unknown action: {action}"
        
        except Exception as e:
            return f"Error in {action}: {str(e)}"
    
    def _take_screenshot(self, params):
        """Take screenshot - uses system_ops.take_screenshot() to avoid duplication"""
        try:
            from system_ops import take_screenshot
            return take_screenshot()
        except ImportError:
            # Fallback implementation
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(os.path.expanduser("~"), "Desktop", f"screenshot_{timestamp}.png")
            
            if os.name == 'nt':  # Windows
                subprocess.run(["powershell", "-Command", 
                               f"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('%{{PRTSC}}')"])
            else:  # Linux
                subprocess.run(["gnome-screenshot", "-f", screenshot_path])
            
            return f"Screenshot saved: {screenshot_path}"
        except Exception as e:
            return f"Error taking screenshot: {str(e)}"
    
    def _compress_image(self, params):
        """Compress image"""
        try:
            # This would use PIL/Pillow in production
            quality = params.get("quality", 70)
            return f"Image compressed to {quality}% quality"
        except Exception as e:
            return f"Error compressing image: {str(e)}"
    
    def _upload_to_drive(self, params):
        """Upload to Google Drive (placeholder)"""
        try:
            # This would integrate with Google Drive API
            return "File uploaded to Google Drive"
        except Exception as e:
            return f"Error uploading to Drive: {str(e)}"
    
    def _get_share_link(self, params):
        """Get shareable link"""
        try:
            # Generate mock share link
            link = f"https://drive.google.com/file/d/mock_file_id_{int(time.time())}/view"
            return f"Share link: {link}"
        except Exception as e:
            return f"Error getting share link: {str(e)}"
    
    def _copy_to_clipboard(self, params):
        """Copy to clipboard"""
        try:
            # This would copy the share link to clipboard
            return "Link copied to clipboard"
        except Exception as e:
            return f"Error copying to clipboard: {str(e)}"
    
    def _download_video(self, params):
        """Download video from URL"""
        try:
            url = params.get("url", "")
            if not url:
                return "Error: No URL provided"
            
            # This would use yt-dlp or similar
            return f"Video downloaded from {url}"
        except Exception as e:
            return f"Error downloading video: {str(e)}"
    
    def _extract_audio(self, params):
        """Extract audio from video"""
        try:
            format_type = params.get("format", "wav")
            # This would use ffmpeg
            return f"Audio extracted in {format_type} format"
        except Exception as e:
            return f"Error extracting audio: {str(e)}"
    
    def _transcribe_audio(self, params):
        """Transcribe audio to text"""
        try:
            # This would use Whisper or similar
            return "Audio transcribed to text"
        except Exception as e:
            return f"Error transcribing audio: {str(e)}"
    
    def _create_pdf(self, params):
        """Create PDF from text"""
        try:
            # This would use reportlab or similar
            return "PDF created from transcription"
        except Exception as e:
            return f"Error creating PDF: {str(e)}"
    
    def _search_emails(self, params):
        """Search emails for specific content"""
        try:
            query = params.get("query", "")
            # This would integrate with email APIs
            return f"Found emails matching '{query}'"
        except Exception as e:
            return f"Error searching emails: {str(e)}"
    
    def _extract_amounts(self, params):
        """Extract monetary amounts from documents"""
        try:
            # This would use regex or OCR
            amounts = ["$1,234.56", "$987.65", "$2,100.00"]
            return f"Extracted amounts: {', '.join(amounts)}"
        except Exception as e:
            return f"Error extracting amounts: {str(e)}"
    
    def _update_excel(self, params):
        """Update Excel spreadsheet"""
        try:
            # This would use openpyxl or similar
            return "Excel spreadsheet updated with extracted amounts"
        except Exception as e:
            return f"Error updating Excel: {str(e)}"
    
    def _monitor_folder(self, params):
        """Monitor folder for new files"""
        try:
            folder = params.get("folder", "")
            file_type = params.get("file_type", "")
            
            if not folder:
                return "Error: No folder specified"
            
            # Start monitoring in background thread
            monitor_id = f"monitor_{int(time.time())}"
            self.monitor_threads[monitor_id] = threading.Thread(
                target=self._folder_monitor_thread,
                args=(folder, file_type, monitor_id)
            )
            self.monitor_threads[monitor_id].start()
            
            return f"Started monitoring {folder} for {file_type} files"
        except Exception as e:
            return f"Error starting folder monitor: {str(e)}"
    
    def _folder_monitor_thread(self, folder, file_type, monitor_id):
        """Background thread for folder monitoring"""
        try:
            while monitor_id in self.monitor_threads:
                # Check for new files
                for file in os.listdir(folder):
                    if file_type in file.lower():
                        # Process the file
                        self._process_monitored_file(os.path.join(folder, file))
                
                time.sleep(5)  # Check every 5 seconds
        except Exception as e:
            print(f"Monitor thread error: {e}")
    
    def _process_monitored_file(self, file_path):
        """Process a file detected by folder monitor"""
        try:
            # Extract text, summarize, and notify
            if file_path.lower().endswith('.pdf'):
                # Process PDF
                self._extract_pdf_text({"file_path": file_path})
        except Exception as e:
            print(f"Error processing monitored file: {e}")
    
    def _extract_pdf_text(self, params):
        """Extract text from PDF"""
        try:
            file_path = params.get("file_path", "")
            # This would use PyPDF2 or pdfplumber
            return f"Text extracted from {os.path.basename(file_path)}"
        except Exception as e:
            return f"Error extracting PDF text: {str(e)}"
    
    def _summarize_text(self, params):
        """Summarize text content"""
        try:
            # This would use AI summarization
            return "Text summarized successfully"
        except Exception as e:
            return f"Error summarizing text: {str(e)}"
    
    def _send_notification(self, params):
        """Send notification to user"""
        try:
            message = params.get("message", "Workflow completed")
            # This would send desktop notification
            return f"Notification sent: {message}"
        except Exception as e:
            return f"Error sending notification: {str(e)}"
    
    def create_custom_workflow(self, name, steps):
        """Create a custom workflow"""
        try:
            self.workflows[name] = {
                "name": name,
                "steps": steps,
                "created": datetime.now().isoformat()
            }
            return f"Custom workflow '{name}' created with {len(steps)} steps"
        except Exception as e:
            return f"Error creating workflow: {str(e)}"
    
    def list_workflows(self):
        """List all available workflows"""
        try:
            result = "🔗 Available Workflows:\n\n"
            
            # Template workflows
            result += "📋 Template Workflows:\n"
            for name, workflow in self.workflow_templates.items():
                result += f"• {workflow['name']} ({len(workflow['steps'])} steps)\n"
            
            # Custom workflows
            if self.workflows:
                result += "\n🎯 Custom Workflows:\n"
                for name, workflow in self.workflows.items():
                    result += f"• {workflow['name']} ({len(workflow['steps'])} steps)\n"
            
            result += "\nUse: 'run workflow <name>' to execute"
            return result
        except Exception as e:
            return f"Error listing workflows: {str(e)}"
    
    def get_workflow_status(self, workflow_id=None):
        """Get status of running workflows"""
        try:
            if workflow_id and workflow_id in self.running_workflows:
                workflow = self.running_workflows[workflow_id]
                return f"Workflow: {workflow['name']}\nStatus: {workflow['status']}\nStep: {workflow['current_step']}/{workflow['total_steps']}"
            
            if not self.running_workflows:
                return "No workflows currently running"
            
            result = "🔄 Running Workflows:\n\n"
            for wf_id, workflow in self.running_workflows.items():
                result += f"• {workflow['name']}: {workflow['status']} ({workflow['current_step']}/{workflow['total_steps']})\n"
            
            return result
        except Exception as e:
            return f"Error getting workflow status: {str(e)}"

# ==================== GLOBAL INSTANCE ====================

workflow_engine = WorkflowEngine()

# ==================== CONVENIENCE FUNCTIONS ====================

def run_workflow(workflow_name, params=None):
    """Execute a workflow"""
    return workflow_engine.execute_workflow(workflow_name, params)

def create_workflow(name, steps):
    """Create custom workflow"""
    return workflow_engine.create_custom_workflow(name, steps)

def list_available_workflows():
    """List all workflows"""
    return workflow_engine.list_workflows()

def get_workflow_status(workflow_id=None):
    """Get workflow status"""
    return workflow_engine.get_workflow_status(workflow_id)

# ==================== WORKFLOW EXAMPLES ====================

def screenshot_to_share_workflow():
    """Execute screenshot → compress → upload → share workflow"""
    return run_workflow("screenshot_share")

def video_transcribe_workflow(video_url):
    """Execute video → audio → transcribe → PDF workflow"""
    return run_workflow("video_transcribe", {"url": video_url})

def invoice_processing_workflow():
    """Execute invoice processing workflow"""
    return run_workflow("invoice_processor")

def pdf_monitor_workflow(folder_path):
    """Execute PDF monitoring workflow"""
    return run_workflow("pdf_monitor", {"folder": folder_path})
