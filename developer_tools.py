import os
import subprocess
import json
import re
import time
import requests
from datetime import datetime
from pathlib import Path
import ast
import sqlite3

# ==================== DEVELOPER TOOLS - HIGH-PAYING MARKET ====================

class DeveloperToolsEngine:
    def __init__(self):
        self.projects_db = os.path.join(os.path.expanduser("~"), ".desktop_ai_projects.db")
        self.active_environments = {}
        self._init_projects_db()
    
    def _init_projects_db(self):
        """Initialize projects database"""
        try:
            conn = sqlite3.connect(self.projects_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    path TEXT,
                    repo_url TEXT,
                    language TEXT,
                    framework TEXT,
                    created_date TEXT,
                    last_accessed TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_path TEXT,
                    file_path TEXT,
                    line_number INTEGER,
                    todo_text TEXT,
                    priority TEXT,
                    created_date TEXT,
                    status TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error initializing projects database: {e}")
    
    def clone_and_setup_project(self, repo_url, project_name=None):
        """Clone repo + setup venv + install dependencies + open VS Code"""
        try:
            if not project_name:
                project_name = repo_url.split('/')[-1].replace('.git', '')
            
            project_path = os.path.join(os.path.expanduser("~"), "Projects", project_name)
            
            steps = []
            
            # Step 1: Clone repository
            steps.append("🔄 Cloning repository...")
            clone_result = subprocess.run(
                ["git", "clone", repo_url, project_path],
                capture_output=True, text=True
            )
            
            if clone_result.returncode != 0:
                return f"❌ Failed to clone repository: {clone_result.stderr}"
            
            steps.append("✅ Repository cloned successfully")
            
            # Step 2: Detect project type and setup environment
            os.chdir(project_path)
            
            # Python project
            if os.path.exists("requirements.txt") or os.path.exists("setup.py") or os.path.exists("pyproject.toml"):
                steps.append("🐍 Python project detected")
                
                # Create virtual environment
                venv_result = subprocess.run(
                    ["python", "-m", "venv", "venv"],
                    capture_output=True, text=True
                )
                
                if venv_result.returncode == 0:
                    steps.append("✅ Virtual environment created")
                    
                    # Activate venv and install dependencies
                    if os.name == 'nt':  # Windows
                        pip_path = os.path.join(project_path, "venv", "Scripts", "pip")
                    else:  # Linux/Mac
                        pip_path = os.path.join(project_path, "venv", "bin", "pip")
                    
                    if os.path.exists("requirements.txt"):
                        install_result = subprocess.run(
                            [pip_path, "install", "-r", "requirements.txt"],
                            capture_output=True, text=True
                        )
                        
                        if install_result.returncode == 0:
                            steps.append("✅ Dependencies installed from requirements.txt")
                        else:
                            steps.append(f"⚠️ Some dependencies failed to install: {install_result.stderr[:100]}")
            
            # Node.js project
            elif os.path.exists("package.json"):
                steps.append("📦 Node.js project detected")
                
                npm_result = subprocess.run(
                    ["npm", "install"],
                    capture_output=True, text=True
                )
                
                if npm_result.returncode == 0:
                    steps.append("✅ NPM dependencies installed")
                else:
                    steps.append(f"⚠️ NPM install failed: {npm_result.stderr[:100]}")
            
            # Step 3: Open in VS Code
            steps.append("🚀 Opening in VS Code...")
            try:
                subprocess.Popen(["code", project_path])
                steps.append("✅ VS Code opened")
            except FileNotFoundError:
                steps.append("⚠️ VS Code not found in PATH")
            
            # Step 4: Save project to database
            self._save_project_to_db(project_name, project_path, repo_url)
            steps.append("📝 Project saved to database")
            
            return f"🎉 Project setup completed!\n\n" + "\n".join(steps) + f"\n\nProject location: {project_path}"
        
        except Exception as e:
            return f"❌ Error setting up project: {str(e)}"
    
    def _save_project_to_db(self, name, path, repo_url):
        """Save project information to database"""
        try:
            conn = sqlite3.connect(self.projects_db)
            cursor = conn.cursor()
            
            # Detect language and framework
            language = self._detect_language(path)
            framework = self._detect_framework(path)
            
            cursor.execute('''
                INSERT INTO projects (name, path, repo_url, language, framework, created_date, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, path, repo_url, language, framework, datetime.now().isoformat(), datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving project: {e}")
    
    def _detect_language(self, project_path):
        """Detect primary programming language"""
        try:
            extensions = {}
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    extensions[ext] = extensions.get(ext, 0) + 1
            
            # Map extensions to languages
            lang_map = {
                '.py': 'Python',
                '.js': 'JavaScript',
                '.ts': 'TypeScript',
                '.java': 'Java',
                '.cpp': 'C++',
                '.c': 'C',
                '.cs': 'C#',
                '.go': 'Go',
                '.rs': 'Rust',
                '.php': 'PHP',
                '.rb': 'Ruby'
            }
            
            if extensions:
                most_common_ext = max(extensions, key=extensions.get)
                return lang_map.get(most_common_ext, 'Unknown')
            
            return 'Unknown'
        except:
            return 'Unknown'
    
    def _detect_framework(self, project_path):
        """Detect framework/technology stack"""
        try:
            frameworks = []
            
            # Check for common framework files
            if os.path.exists(os.path.join(project_path, "package.json")):
                with open(os.path.join(project_path, "package.json"), 'r') as f:
                    package_data = json.load(f)
                    deps = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}
                    
                    if 'react' in deps:
                        frameworks.append('React')
                    if 'vue' in deps:
                        frameworks.append('Vue.js')
                    if 'angular' in deps:
                        frameworks.append('Angular')
                    if 'express' in deps:
                        frameworks.append('Express.js')
                    if 'next' in deps:
                        frameworks.append('Next.js')
            
            if os.path.exists(os.path.join(project_path, "requirements.txt")):
                with open(os.path.join(project_path, "requirements.txt"), 'r') as f:
                    reqs = f.read().lower()
                    if 'django' in reqs:
                        frameworks.append('Django')
                    if 'flask' in reqs:
                        frameworks.append('Flask')
                    if 'fastapi' in reqs:
                        frameworks.append('FastAPI')
            
            return ', '.join(frameworks) if frameworks else 'Unknown'
        except:
            return 'Unknown'
    
    def find_all_todos(self, project_path=None):
        """Find all TODO comments → Create task list"""
        try:
            if not project_path:
                project_path = os.getcwd()
            
            todos = []
            todo_patterns = [
                r'#\s*TODO:?\s*(.+)',
                r'//\s*TODO:?\s*(.+)',
                r'/\*\s*TODO:?\s*(.+)\s*\*/',
                r'<!--\s*TODO:?\s*(.+)\s*-->',
                r'#\s*FIXME:?\s*(.+)',
                r'//\s*FIXME:?\s*(.+)',
                r'#\s*HACK:?\s*(.+)',
                r'//\s*HACK:?\s*(.+)',
                r'#\s*NOTE:?\s*(.+)',
                r'//\s*NOTE:?\s*(.+)'
            ]
            
            # File extensions to search
            code_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.go', '.rs', '.php', '.rb', '.html', '.css', '.scss', '.vue', '.jsx', '.tsx']
            
            for root, dirs, files in os.walk(project_path):
                # Skip common directories
                dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.venv', 'venv', 'build', 'dist']]
                
                for file in files:
                    if any(file.lower().endswith(ext) for ext in code_extensions):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                lines = f.readlines()
                                
                                for line_num, line in enumerate(lines, 1):
                                    for pattern in todo_patterns:
                                        match = re.search(pattern, line, re.IGNORECASE)
                                        if match:
                                            todo_text = match.group(1).strip()
                                            priority = 'high' if 'FIXME' in line.upper() else 'medium' if 'TODO' in line.upper() else 'low'
                                            
                                            todos.append({
                                                'file': os.path.relpath(file_path, project_path),
                                                'line': line_num,
                                                'text': todo_text,
                                                'priority': priority,
                                                'type': 'FIXME' if 'FIXME' in line.upper() else 'TODO' if 'TODO' in line.upper() else 'NOTE'
                                            })
                        except Exception as e:
                            continue
            
            # Save to database
            self._save_todos_to_db(project_path, todos)
            
            if not todos:
                return "No TODO comments found in the project"
            
            # Format results
            result = f"📝 Found {len(todos)} TODO items in project:\n\n"
            
            # Group by priority
            high_priority = [t for t in todos if t['priority'] == 'high']
            medium_priority = [t for t in todos if t['priority'] == 'medium']
            low_priority = [t for t in todos if t['priority'] == 'low']
            
            if high_priority:
                result += "🔴 HIGH PRIORITY (FIXME):\n"
                for todo in high_priority[:10]:
                    result += f"  • {todo['file']}:{todo['line']} - {todo['text']}\n"
                result += "\n"
            
            if medium_priority:
                result += "🟡 MEDIUM PRIORITY (TODO):\n"
                for todo in medium_priority[:10]:
                    result += f"  • {todo['file']}:{todo['line']} - {todo['text']}\n"
                result += "\n"
            
            if low_priority:
                result += "🟢 LOW PRIORITY (NOTES):\n"
                for todo in low_priority[:5]:
                    result += f"  • {todo['file']}:{todo['line']} - {todo['text']}\n"
            
            if len(todos) > 25:
                result += f"\n... and {len(todos) - 25} more items"
            
            return result
        
        except Exception as e:
            return f"Error finding TODOs: {str(e)}"
    
    def _save_todos_to_db(self, project_path, todos):
        """Save TODOs to database"""
        try:
            conn = sqlite3.connect(self.projects_db)
            cursor = conn.cursor()
            
            # Clear existing TODOs for this project
            cursor.execute('DELETE FROM todos WHERE project_path = ?', (project_path,))
            
            # Insert new TODOs
            for todo in todos:
                cursor.execute('''
                    INSERT INTO todos (project_path, file_path, line_number, todo_text, priority, created_date, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (project_path, todo['file'], todo['line'], todo['text'], todo['priority'], datetime.now().isoformat(), 'open'))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving TODOs: {e}")
    
    def run_tests_and_explain_errors(self, project_path=None):
        """Run tests → Explain errors in plain English"""
        try:
            if not project_path:
                project_path = os.getcwd()
            
            os.chdir(project_path)
            
            # Detect test framework and run tests
            test_command = None
            
            if os.path.exists("pytest.ini") or any("pytest" in f for f in os.listdir() if f.endswith('.txt')):
                test_command = ["python", "-m", "pytest", "-v"]
            elif os.path.exists("manage.py"):  # Django
                test_command = ["python", "manage.py", "test"]
            elif os.path.exists("package.json"):
                test_command = ["npm", "test"]
            elif any(f.startswith("test_") and f.endswith(".py") for f in os.listdir()):
                test_command = ["python", "-m", "unittest", "discover"]
            else:
                return "No test framework detected in this project"
            
            # Run tests
            result = subprocess.run(test_command, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return "✅ All tests passed successfully!"
            
            # Parse and explain errors
            error_output = result.stdout + result.stderr
            explanations = self._explain_test_errors(error_output)
            
            return f"❌ Tests failed. Here's what went wrong:\n\n{explanations}"
        
        except subprocess.TimeoutExpired:
            return "⏰ Tests timed out after 60 seconds"
        except Exception as e:
            return f"Error running tests: {str(e)}"
    
    def _explain_test_errors(self, error_output):
        """Explain test errors in plain English"""
        try:
            explanations = []
            
            # Common error patterns and explanations
            error_patterns = {
                r'AssertionError': "❌ **Assertion Failed**: A test expected one thing but got another. Check your logic.",
                r'ImportError|ModuleNotFoundError': "📦 **Missing Module**: A required package or module isn't installed or can't be found.",
                r'AttributeError': "🔍 **Attribute Error**: Trying to use a method or property that doesn't exist on an object.",
                r'TypeError': "🔧 **Type Error**: Wrong data type used (e.g., trying to add a number to a string).",
                r'ValueError': "📊 **Value Error**: Correct type but invalid value (e.g., negative number where positive expected).",
                r'KeyError': "🗝️ **Key Error**: Trying to access a dictionary key that doesn't exist.",
                r'IndexError': "📋 **Index Error**: Trying to access a list item that doesn't exist (index out of range).",
                r'FileNotFoundError': "📁 **File Not Found**: Trying to open a file that doesn't exist.",
                r'PermissionError': "🔒 **Permission Denied**: Don't have rights to access a file or directory.",
                r'SyntaxError': "⚠️ **Syntax Error**: Code has invalid Python syntax (typos, missing colons, etc.).",
                r'IndentationError': "📏 **Indentation Error**: Incorrect spacing/tabs in Python code."
            }
            
            lines = error_output.split('\n')
            for line in lines:
                for pattern, explanation in error_patterns.items():
                    if re.search(pattern, line, re.IGNORECASE):
                        explanations.append(f"{explanation}\n  📍 Details: {line.strip()}")
                        break
            
            if not explanations:
                # Generic explanation
                explanations.append("🤔 **Unknown Error**: The test failed but I couldn't identify the specific issue. Check the full error output above.")
            
            return "\n\n".join(explanations[:5])  # Show top 5 errors
        
        except Exception as e:
            return f"Error explaining test failures: {str(e)}"
    
    def generate_smart_commit_message(self, project_path=None):
        """Generate smart commit message"""
        try:
            if not project_path:
                project_path = os.getcwd()
            
            os.chdir(project_path)
            
            # Get git diff
            diff_result = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True)
            
            if not diff_result.stdout:
                # No staged changes, check unstaged
                diff_result = subprocess.run(["git", "diff"], capture_output=True, text=True)
                if not diff_result.stdout:
                    return "No changes detected. Stage your changes first with 'git add'"
            
            # Analyze changes
            diff_content = diff_result.stdout
            changes = self._analyze_git_diff(diff_content)
            
            # Generate commit message
            commit_message = self._generate_commit_message(changes)
            
            return f"📝 Suggested commit message:\n\n{commit_message}\n\nUse: git commit -m \"{commit_message}\""
        
        except Exception as e:
            return f"Error generating commit message: {str(e)}"
    
    def _analyze_git_diff(self, diff_content):
        """Analyze git diff to understand changes"""
        try:
            changes = {
                'files_added': [],
                'files_modified': [],
                'files_deleted': [],
                'lines_added': 0,
                'lines_removed': 0,
                'functions_added': [],
                'functions_modified': [],
                'is_feature': False,
                'is_bugfix': False,
                'is_refactor': False
            }
            
            lines = diff_content.split('\n')
            current_file = None
            
            for line in lines:
                if line.startswith('+++'):
                    current_file = line[6:] if line[6:] != '/dev/null' else None
                    if current_file and current_file not in changes['files_modified']:
                        changes['files_modified'].append(current_file)
                elif line.startswith('---'):
                    if line[6:] != '/dev/null' and current_file is None:
                        changes['files_deleted'].append(line[6:])
                elif line.startswith('+') and not line.startswith('+++'):
                    changes['lines_added'] += 1
                    # Check for new functions
                    if re.search(r'def\s+\w+|function\s+\w+|class\s+\w+', line):
                        changes['functions_added'].append(line.strip())
                elif line.startswith('-') and not line.startswith('---'):
                    changes['lines_removed'] += 1
            
            # Determine change type
            if any('test' in f for f in changes['files_modified']):
                changes['is_feature'] = True
            if any('fix' in f.lower() or 'bug' in f.lower() for f in changes['files_modified']):
                changes['is_bugfix'] = True
            if changes['lines_added'] > changes['lines_removed'] * 2:
                changes['is_feature'] = True
            elif changes['lines_removed'] > changes['lines_added']:
                changes['is_refactor'] = True
            
            return changes
        
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_commit_message(self, changes):
        """Generate commit message based on changes"""
        try:
            if 'error' in changes:
                return "Update code"
            
            # Determine commit type
            if changes['is_feature']:
                prefix = "feat:"
            elif changes['is_bugfix']:
                prefix = "fix:"
            elif changes['is_refactor']:
                prefix = "refactor:"
            else:
                prefix = "update:"
            
            # Generate description
            if changes['functions_added']:
                description = f"add {len(changes['functions_added'])} new function(s)"
            elif len(changes['files_modified']) == 1:
                filename = os.path.basename(changes['files_modified'][0])
                description = f"update {filename}"
            elif len(changes['files_modified']) > 1:
                description = f"update {len(changes['files_modified'])} files"
            else:
                description = "update code"
            
            return f"{prefix} {description}"
        
        except Exception as e:
            return "update: code changes"
    
    def execute_terminal_command(self, command):
        """Terminal command execution via voice/text"""
        try:
            # Security check - don't allow dangerous commands
            dangerous_commands = ['rm -rf', 'del /f', 'format', 'fdisk', 'dd if=']
            if any(dangerous in command.lower() for dangerous in dangerous_commands):
                return "❌ Dangerous command blocked for security"
            
            # Execute command
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            
            output = result.stdout
            if result.stderr:
                output += f"\nErrors: {result.stderr}"
            
            if result.returncode == 0:
                return f"✅ Command executed successfully:\n\n{output}"
            else:
                return f"❌ Command failed (exit code {result.returncode}):\n\n{output}"
        
        except subprocess.TimeoutExpired:
            return "⏰ Command timed out after 30 seconds"
        except Exception as e:
            return f"Error executing command: {str(e)}"
    
    def deploy_to_production(self, project_path=None, platform="auto"):
        """Deploy to production"""
        try:
            if not project_path:
                project_path = os.getcwd()
            
            os.chdir(project_path)
            
            # Auto-detect deployment platform
            if platform == "auto":
                if os.path.exists("vercel.json"):
                    platform = "vercel"
                elif os.path.exists("netlify.toml"):
                    platform = "netlify"
                elif os.path.exists("Dockerfile"):
                    platform = "docker"
                elif os.path.exists("requirements.txt"):
                    platform = "heroku"
                else:
                    platform = "generic"
            
            deployment_steps = []
            
            # Run pre-deployment checks
            deployment_steps.append("🔍 Running pre-deployment checks...")
            
            # Check for tests
            if os.path.exists("test") or any("test" in f for f in os.listdir()):
                test_result = subprocess.run(["python", "-m", "pytest"], capture_output=True, text=True)
                if test_result.returncode == 0:
                    deployment_steps.append("✅ All tests passed")
                else:
                    return f"❌ Tests failed. Fix tests before deployment:\n{test_result.stderr[:200]}"
            
            # Platform-specific deployment
            if platform == "vercel":
                deploy_result = subprocess.run(["vercel", "--prod"], capture_output=True, text=True)
                if deploy_result.returncode == 0:
                    deployment_steps.append("✅ Deployed to Vercel")
                    # Extract URL from output
                    url_match = re.search(r'https://[^\s]+', deploy_result.stdout)
                    if url_match:
                        deployment_steps.append(f"🌐 Live at: {url_match.group()}")
                else:
                    return f"❌ Vercel deployment failed: {deploy_result.stderr}"
            
            elif platform == "heroku":
                # Check for Procfile
                if not os.path.exists("Procfile"):
                    with open("Procfile", "w") as f:
                        f.write("web: python app.py")
                    deployment_steps.append("📝 Created Procfile")
                
                # Deploy to Heroku
                deploy_result = subprocess.run(["git", "push", "heroku", "main"], capture_output=True, text=True)
                if deploy_result.returncode == 0:
                    deployment_steps.append("✅ Deployed to Heroku")
                else:
                    return f"❌ Heroku deployment failed: {deploy_result.stderr}"
            
            else:
                deployment_steps.append("⚠️ Generic deployment - manual steps required")
            
            return f"🚀 Deployment completed!\n\n" + "\n".join(deployment_steps)
        
        except Exception as e:
            return f"Error deploying: {str(e)}"
    
    def list_projects(self):
        """List all managed projects"""
        try:
            conn = sqlite3.connect(self.projects_db)
            cursor = conn.cursor()
            
            cursor.execute('SELECT name, path, language, framework, created_date FROM projects ORDER BY last_accessed DESC')
            projects = cursor.fetchall()
            conn.close()
            
            if not projects:
                return "No projects found. Use 'clone and setup' to add projects."
            
            result = "💻 Your Development Projects:\n\n"
            for name, path, language, framework, created in projects:
                created_date = datetime.fromisoformat(created).strftime("%Y-%m-%d")
                result += f"📁 **{name}**\n"
                result += f"   Path: {path}\n"
                result += f"   Language: {language}\n"
                result += f"   Framework: {framework}\n"
                result += f"   Created: {created_date}\n\n"
            
            return result
        
        except Exception as e:
            return f"Error listing projects: {str(e)}"

# ==================== GLOBAL INSTANCE ====================

dev_tools = DeveloperToolsEngine()

# ==================== CONVENIENCE FUNCTIONS ====================

def clone_and_setup(repo_url, project_name=None):
    """Clone repo + setup environment + open VS Code"""
    return dev_tools.clone_and_setup_project(repo_url, project_name)

def find_todos(project_path=None):
    """Find all TODO comments"""
    return dev_tools.find_all_todos(project_path)

def run_tests_explain_errors(project_path=None):
    """Run tests and explain errors"""
    return dev_tools.run_tests_and_explain_errors(project_path)

def generate_commit_message(project_path=None):
    """Generate smart commit message"""
    return dev_tools.generate_smart_commit_message(project_path)

def execute_command(command):
    """Execute terminal command"""
    return dev_tools.execute_terminal_command(command)

def deploy_project(project_path=None, platform="auto"):
    """Deploy to production"""
    return dev_tools.deploy_to_production(project_path, platform)

def list_dev_projects():
    """List development projects"""
    return dev_tools.list_projects()
