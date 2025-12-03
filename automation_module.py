#!/usr/bin/env python3
"""
Automation Module for Linux Desktop AI Agent
Handles scheduled tasks and automation workflows
"""

import subprocess
import logging
import json
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime, timedelta
from pathlib import Path
import time
import threading

from module_framework import BaseModule, ModuleResult, ResultStatus

logger = logging.getLogger(__name__)


class ScheduledTask:
    """Represents a scheduled task"""
    
    def __init__(self, name: str, action: Callable, interval: int, 
                 enabled: bool = True, description: str = ""):
        """
        Initialize scheduled task
        
        Args:
            name: Task name
            action: Callable to execute
            interval: Interval in seconds
            enabled: Whether task is enabled
            description: Task description
        """
        self.name = name
        self.action = action
        self.interval = interval
        self.enabled = enabled
        self.description = description
        self.last_run = None
        self.next_run = datetime.now() + timedelta(seconds=interval)
        self.run_count = 0
        self.error_count = 0
    
    def should_run(self) -> bool:
        """Check if task should run"""
        if not self.enabled:
            return False
        return datetime.now() >= self.next_run
    
    def execute(self) -> bool:
        """Execute task"""
        try:
            self.action()
            self.last_run = datetime.now()
            self.next_run = datetime.now() + timedelta(seconds=self.interval)
            self.run_count += 1
            logger.info(f"Task '{self.name}' executed successfully")
            return True
        except Exception as e:
            self.error_count += 1
            logger.error(f"Task '{self.name}' failed: {e}")
            return False


class AutomationModule(BaseModule):
    """
    Automation module
    Handles scheduled tasks and automation workflows
    """
    
    def __init__(self):
        super().__init__(
            name="automation",
            description="Task automation and scheduling",
            version="1.0.0"
        )
        self.tasks: Dict[str, ScheduledTask] = {}
        self.scheduler_thread = None
        self.running = False
    
    def get_supported_actions(self) -> List[str]:
        """Get supported automation actions"""
        return [
            "schedule_task",
            "list_tasks",
            "enable_task",
            "disable_task",
            "run_task",
            "remove_task",
            "start_scheduler",
            "stop_scheduler",
            "get_task_info"
        ]
    
    def execute(self, action: str, parameters: Dict[str, Any]) -> ModuleResult:
        """Execute automation action"""
        try:
            if action == "schedule_task":
                return self._schedule_task(parameters)
            elif action == "list_tasks":
                return self._list_tasks()
            elif action == "enable_task":
                return self._enable_task(parameters)
            elif action == "disable_task":
                return self._disable_task(parameters)
            elif action == "run_task":
                return self._run_task(parameters)
            elif action == "remove_task":
                return self._remove_task(parameters)
            elif action == "start_scheduler":
                return self._start_scheduler()
            elif action == "stop_scheduler":
                return self._stop_scheduler()
            elif action == "get_task_info":
                return self._get_task_info(parameters)
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
    
    def _schedule_task(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Schedule a new task"""
        task_name = parameters.get("name")
        interval = parameters.get("interval", 3600)  # Default 1 hour
        description = parameters.get("description", "")
        
        if not task_name:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="name parameter required",
                data={}
            )
        
        if task_name in self.tasks:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message=f"Task '{task_name}' already exists",
                data={}
            )
        
        # Create a dummy task (actual implementation would use provided action)
        task = ScheduledTask(
            name=task_name,
            action=lambda: logger.info(f"Running task: {task_name}"),
            interval=interval,
            description=description
        )
        
        self.tasks[task_name] = task
        
        return ModuleResult(
            status=ResultStatus.SUCCESS,
            message=f"Task '{task_name}' scheduled",
            data={
                "task_name": task_name,
                "interval": interval,
                "next_run": task.next_run.isoformat()
            }
        )
    
    def _list_tasks(self) -> ModuleResult:
        """List all scheduled tasks"""
        tasks_info = []
        
        for task_name, task in self.tasks.items():
            tasks_info.append({
                "name": task_name,
                "enabled": task.enabled,
                "interval": task.interval,
                "description": task.description,
                "last_run": task.last_run.isoformat() if task.last_run else None,
                "next_run": task.next_run.isoformat(),
                "run_count": task.run_count,
                "error_count": task.error_count
            })
        
        return ModuleResult(
            status=ResultStatus.SUCCESS,
            message=f"Listed {len(tasks_info)} tasks",
            data={"tasks": tasks_info}
        )
    
    def _enable_task(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Enable a task"""
        task_name = parameters.get("name")
        
        if not task_name or task_name not in self.tasks:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message=f"Task '{task_name}' not found",
                data={}
            )
        
        self.tasks[task_name].enabled = True
        
        return ModuleResult(
            status=ResultStatus.SUCCESS,
            message=f"Task '{task_name}' enabled",
            data={"task_name": task_name}
        )
    
    def _disable_task(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Disable a task"""
        task_name = parameters.get("name")
        
        if not task_name or task_name not in self.tasks:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message=f"Task '{task_name}' not found",
                data={}
            )
        
        self.tasks[task_name].enabled = False
        
        return ModuleResult(
            status=ResultStatus.SUCCESS,
            message=f"Task '{task_name}' disabled",
            data={"task_name": task_name}
        )
    
    def _run_task(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Run a task immediately"""
        task_name = parameters.get("name")
        
        if not task_name or task_name not in self.tasks:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message=f"Task '{task_name}' not found",
                data={}
            )
        
        task = self.tasks[task_name]
        success = task.execute()
        
        status = ResultStatus.SUCCESS if success else ResultStatus.FAILED
        
        return ModuleResult(
            status=status,
            message=f"Task '{task_name}' executed",
            data={
                "task_name": task_name,
                "success": success,
                "run_count": task.run_count
            }
        )
    
    def _remove_task(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Remove a task"""
        task_name = parameters.get("name")
        
        if not task_name or task_name not in self.tasks:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message=f"Task '{task_name}' not found",
                data={}
            )
        
        del self.tasks[task_name]
        
        return ModuleResult(
            status=ResultStatus.SUCCESS,
            message=f"Task '{task_name}' removed",
            data={"task_name": task_name}
        )
    
    def _start_scheduler(self) -> ModuleResult:
        """Start the task scheduler"""
        if self.running:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Scheduler already running",
                data={}
            )
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        return ModuleResult(
            status=ResultStatus.SUCCESS,
            message="Scheduler started",
            data={"running": True}
        )
    
    def _stop_scheduler(self) -> ModuleResult:
        """Stop the task scheduler"""
        if not self.running:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Scheduler not running",
                data={}
            )
        
        self.running = False
        
        return ModuleResult(
            status=ResultStatus.SUCCESS,
            message="Scheduler stopped",
            data={"running": False}
        )
    
    def _get_task_info(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Get information about a specific task"""
        task_name = parameters.get("name")
        
        if not task_name or task_name not in self.tasks:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message=f"Task '{task_name}' not found",
                data={}
            )
        
        task = self.tasks[task_name]
        
        data = {
            "name": task.name,
            "enabled": task.enabled,
            "interval": task.interval,
            "description": task.description,
            "last_run": task.last_run.isoformat() if task.last_run else None,
            "next_run": task.next_run.isoformat(),
            "run_count": task.run_count,
            "error_count": task.error_count
        }
        
        return ModuleResult(
            status=ResultStatus.SUCCESS,
            message=f"Task info for '{task_name}'",
            data=data
        )
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        logger.info("Scheduler started")
        
        while self.running:
            try:
                # Check each task
                for task in self.tasks.values():
                    if task.should_run():
                        task.execute()
                
                # Sleep briefly to avoid busy waiting
                time.sleep(1)
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
        
        logger.info("Scheduler stopped")


class CronManager:
    """Manages cron jobs for system-level scheduling"""
    
    @staticmethod
    def add_cron_job(schedule: str, command: str, description: str = "") -> bool:
        """
        Add a cron job
        
        Args:
            schedule: Cron schedule (e.g., "0 * * * *" for hourly)
            command: Command to execute
            description: Job description
            
        Returns:
            True if successful
        """
        try:
            # Get current crontab
            result = subprocess.run(
                ["crontab", "-l"],
                capture_output=True,
                text=True
            )
            
            current_crontab = result.stdout if result.returncode == 0 else ""
            
            # Add new job
            new_job = f"{schedule} {command} # {description}\n"
            updated_crontab = current_crontab + new_job
            
            # Write updated crontab
            process = subprocess.Popen(
                ["crontab", "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            process.communicate(input=updated_crontab)
            
            if process.returncode == 0:
                logger.info(f"Cron job added: {description}")
                return True
            else:
                logger.error("Failed to add cron job")
                return False
        except Exception as e:
            logger.error(f"Error adding cron job: {e}")
            return False
    
    @staticmethod
    def list_cron_jobs() -> List[str]:
        """List all cron jobs"""
        try:
            result = subprocess.run(
                ["crontab", "-l"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return result.stdout.strip().split("\n")
            else:
                return []
        except Exception as e:
            logger.error(f"Error listing cron jobs: {e}")
            return []
    
    @staticmethod
    def remove_cron_job(job_description: str) -> bool:
        """Remove a cron job by description"""
        try:
            result = subprocess.run(
                ["crontab", "-l"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return False
            
            current_crontab = result.stdout
            
            # Filter out the job
            lines = current_crontab.split("\n")
            updated_lines = [
                line for line in lines
                if job_description not in line
            ]
            
            updated_crontab = "\n".join(updated_lines)
            
            # Write updated crontab
            process = subprocess.Popen(
                ["crontab", "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            process.communicate(input=updated_crontab)
            
            if process.returncode == 0:
                logger.info(f"Cron job removed: {job_description}")
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Error removing cron job: {e}")
            return False


if __name__ == "__main__":
    module = AutomationModule()
    print("Automation Module Test")
    print(f"Supported actions: {module.get_supported_actions()}")
