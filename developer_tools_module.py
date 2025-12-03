#!/usr/bin/env python3
"""
Developer Tools Module for Desktop AI Agent
Handles development-related tasks
"""

import subprocess
import os
import logging
from typing import Dict, Any, List
from module_framework import BaseModule, ModuleResult, ResultStatus

logger = logging.getLogger(__name__)


class DeveloperToolsModule(BaseModule):
    """
    Developer tools module
    Git, Docker, databases, virtual environments, dev servers
    """
    
    def __init__(self):
        super().__init__(
            name="developer_tools",
            description="Developer tools and utilities",
            version="1.0.0"
        )
    
    def get_supported_actions(self) -> List[str]:
        """Get supported developer actions"""
        return [
            "git_status",
            "git_clone",
            "git_commit",
            "git_push",
            "docker_list",
            "docker_cleanup",
            "create_venv",
            "activate_venv",
            "check_port",
            "start_server",
            "database_backup",
            "find_port_conflicts"
        ]
    
    def execute(self, action: str, parameters: Dict[str, Any]) -> ModuleResult:
        """Execute developer action"""
        try:
            if action == "git_status":
                return self._git_status(parameters)
            elif action == "git_clone":
                return self._git_clone(parameters)
            elif action == "git_commit":
                return self._git_commit(parameters)
            elif action == "git_push":
                return self._git_push(parameters)
            elif action == "docker_list":
                return self._docker_list()
            elif action == "docker_cleanup":
                return self._docker_cleanup()
            elif action == "create_venv":
                return self._create_venv(parameters)
            elif action == "activate_venv":
                return self._activate_venv(parameters)
            elif action == "check_port":
                return self._check_port(parameters)
            elif action == "start_server":
                return self._start_server(parameters)
            elif action == "database_backup":
                return self._database_backup(parameters)
            elif action == "find_port_conflicts":
                return self._find_port_conflicts()
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message=f"Unknown action: {action}",
                    data={}
                )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message=f"Error executing {action}",
                data={},
                error=str(e)
            )
    
    def _git_status(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Get git repository status"""
        repo_path = parameters.get("path", os.getcwd())
        
        try:
            result = subprocess.run(
                ["git", "-C", repo_path, "status"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message="Git status retrieved",
                    data={"status": result.stdout}
                )
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message="Not a git repository",
                    data={},
                    error=result.stderr
                )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Git status error",
                data={},
                error=str(e)
            )
    
    def _git_clone(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Clone a git repository"""
        repo_url = parameters.get("url")
        dest_path = parameters.get("path", os.getcwd())
        
        if not repo_url:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="url parameter required",
                data={}
            )
        
        try:
            result = subprocess.run(
                ["git", "clone", repo_url, dest_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message=f"Cloned repository to {dest_path}",
                    data={"path": dest_path}
                )
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message="Failed to clone repository",
                    data={},
                    error=result.stderr
                )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Git clone error",
                data={},
                error=str(e)
            )
    
    def _git_commit(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Commit changes to git"""
        repo_path = parameters.get("path", os.getcwd())
        message = parameters.get("message", "Auto commit")
        
        try:
            # Add all changes
            subprocess.run(
                ["git", "-C", repo_path, "add", "-A"],
                capture_output=True,
                timeout=10
            )
            
            # Commit
            result = subprocess.run(
                ["git", "-C", repo_path, "commit", "-m", message],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message=f"Committed: {message}",
                    data={"message": message}
                )
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message="Failed to commit",
                    data={},
                    error=result.stderr
                )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Git commit error",
                data={},
                error=str(e)
            )
    
    def _git_push(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Push changes to remote"""
        repo_path = parameters.get("path", os.getcwd())
        branch = parameters.get("branch", "main")
        
        try:
            result = subprocess.run(
                ["git", "-C", repo_path, "push", "origin", branch],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message=f"Pushed to {branch}",
                    data={"branch": branch}
                )
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message="Failed to push",
                    data={},
                    error=result.stderr
                )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Git push error",
                data={},
                error=str(e)
            )
    
    def _docker_list(self) -> ModuleResult:
        """List Docker containers and images"""
        try:
            # List containers
            containers_result = subprocess.run(
                ["docker", "ps", "-a"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # List images
            images_result = subprocess.run(
                ["docker", "images"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            data = {
                "containers": containers_result.stdout,
                "images": images_result.stdout
            }
            
            return ModuleResult(
                status=ResultStatus.SUCCESS,
                message="Docker resources listed",
                data=data
            )
        except FileNotFoundError:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Docker not installed",
                data={},
                error="Install Docker from https://docs.docker.com/install/"
            )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Docker list error",
                data={},
                error=str(e)
            )
    
    def _docker_cleanup(self) -> ModuleResult:
        """Clean up Docker resources"""
        try:
            result = subprocess.run(
                ["docker", "system", "prune", "-f"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message="Docker cleanup complete",
                    data={"output": result.stdout}
                )
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message="Docker cleanup failed",
                    data={},
                    error=result.stderr
                )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Docker cleanup error",
                data={},
                error=str(e)
            )
    
    def _create_venv(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Create Python virtual environment"""
        venv_path = parameters.get("path", "venv")
        python_version = parameters.get("python", "python3")
        
        try:
            result = subprocess.run(
                [python_version, "-m", "venv", venv_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message=f"Virtual environment created at {venv_path}",
                    data={"path": venv_path}
                )
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message="Failed to create virtual environment",
                    data={},
                    error=result.stderr
                )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Virtual environment creation error",
                data={},
                error=str(e)
            )
    
    def _activate_venv(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Get activation command for virtual environment"""
        venv_path = parameters.get("path", "venv")
        
        activate_script = os.path.join(venv_path, "bin", "activate")
        
        if os.path.exists(activate_script):
            return ModuleResult(
                status=ResultStatus.SUCCESS,
                message=f"To activate: source {activate_script}",
                data={"activate_script": activate_script}
            )
        else:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message=f"Virtual environment not found at {venv_path}",
                data={}
            )
    
    def _check_port(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Check if a port is in use"""
        port = parameters.get("port")
        
        if not port:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="port parameter required",
                data={}
            )
        
        try:
            result = subprocess.run(
                ["lsof", "-i", f":{port}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message=f"Port {port} is in use",
                    data={"port": port, "in_use": True, "processes": result.stdout}
                )
            else:
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message=f"Port {port} is available",
                    data={"port": port, "in_use": False}
                )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Port check error",
                data={},
                error=str(e)
            )
    
    def _start_server(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Start a development server"""
        server_type = parameters.get("type", "http")
        port = parameters.get("port", 8000)
        path = parameters.get("path", os.getcwd())
        
        try:
            if server_type == "http":
                cmd = ["python3", "-m", "http.server", str(port), "--directory", path]
            elif server_type == "python":
                cmd = ["python3", "-m", "http.server", str(port)]
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message=f"Unknown server type: {server_type}",
                    data={}
                )
            
            # Start in background
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            return ModuleResult(
                status=ResultStatus.SUCCESS,
                message=f"Started {server_type} server on port {port}",
                data={"type": server_type, "port": port}
            )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Server start error",
                data={},
                error=str(e)
            )
    
    def _database_backup(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Backup database"""
        db_type = parameters.get("type", "mysql")
        db_name = parameters.get("database")
        output_path = parameters.get("output", f"{db_name}_backup.sql")
        
        if not db_name:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="database parameter required",
                data={}
            )
        
        try:
            if db_type == "mysql":
                cmd = ["mysqldump", "-u", "root", "-p", db_name]
            elif db_type == "postgresql":
                cmd = ["pg_dump", db_name]
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message=f"Unknown database type: {db_type}",
                    data={}
                )
            
            with open(output_path, "w") as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, timeout=300)
            
            if result.returncode == 0:
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message=f"Database backed up to {output_path}",
                    data={"output": output_path}
                )
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message="Database backup failed",
                    data={},
                    error=result.stderr.decode()
                )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Database backup error",
                data={},
                error=str(e)
            )
    
    def _find_port_conflicts(self) -> ModuleResult:
        """Find port conflicts"""
        try:
            result = subprocess.run(
                ["netstat", "-tuln"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            listening_ports = []
            for line in result.stdout.split("\n"):
                if "LISTEN" in line:
                    listening_ports.append(line.strip())
            
            return ModuleResult(
                status=ResultStatus.SUCCESS,
                message=f"Found {len(listening_ports)} listening ports",
                data={"ports": listening_ports}
            )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Port conflict check error",
                data={},
                error=str(e)
            )


if __name__ == "__main__":
    module = DeveloperToolsModule()
    print("Developer Tools Module Test")
    print(f"Supported actions: {module.get_supported_actions()}")
