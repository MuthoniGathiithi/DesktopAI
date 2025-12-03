#!/usr/bin/env python3
"""
Linux Desktop AI Agent - Main Integration
Intelligent desktop automation using Llama
"""

import sys
import json
import logging
import argparse
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# Import core components
from llama_integration import LlamaIntegration, CommandParsed
from module_framework import get_registry, ModuleResult, ResultStatus

# Import all modules
from system_cleanup_module import SystemCleanupModule
from system_monitor_module import SystemMonitorModule
from network_module import NetworkModule
from file_manager_module import FileManagerModule
from package_manager_module import PackageManagerModule
from security_module import SecurityModule
from developer_tools_module import DeveloperToolsModule
from automation_module import AutomationModule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/linux_desktop_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LinuxDesktopAgent:
    """
    Main Linux Desktop AI Agent
    Orchestrates all modules and handles user commands
    """
    
    def __init__(self):
        """Initialize the agent"""
        logger.info("Initializing Linux Desktop AI Agent...")
        
        # Initialize Llama integration
        self.llama = LlamaIntegration()
        
        # Initialize module registry
        self.registry = get_registry()
        
        # Register all modules
        self._register_modules()
        
        # Configuration
        self.config_dir = Path.home() / ".config" / "linux-desktop-agent"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Linux Desktop AI Agent initialized successfully")
    
    def _register_modules(self):
        """Register all available modules"""
        modules = [
            SystemCleanupModule(),
            SystemMonitorModule(),
            NetworkModule(),
            FileManagerModule(),
            PackageManagerModule(),
            SecurityModule(),
            DeveloperToolsModule(),
            AutomationModule()
        ]
        
        for module in modules:
            self.registry.register(module)
            logger.info(f"Registered module: {module.name}")
    
    def process_command(self, user_input: str) -> Dict[str, Any]:
        """
        Process user command
        
        Args:
            user_input: User's natural language command
            
        Returns:
            Result dictionary with action, status, and data
        """
        logger.info(f"Processing command: {user_input}")
        
        # Parse command using Llama
        parsed = self.llama.parse_command(user_input)
        
        if parsed.confidence < 0.3:
            # Ask for clarification
            question, suggestions = self.llama.handle_unclear_command(user_input)
            return {
                "status": "unclear",
                "message": question,
                "suggestions": suggestions,
                "confidence": parsed.confidence
            }
        
        # Treat missing or generic categories as unclear commands
        if not parsed.category or parsed.category.lower() == "help":
            question, suggestions = self.llama.handle_unclear_command(user_input)
            return {
                "status": "unclear",
                "message": question,
                "suggestions": suggestions,
                "confidence": parsed.confidence
            }

        # Get module for this command category
        module = self.registry.get_module_by_category(parsed.category)
        
        if not module:
            return {
                "status": "error",
                "message": f"No module found for category: {parsed.category}",
                "category": parsed.category
            }
        
        # Execute action
        result = self.registry.execute(
            module.name,
            parsed.action,
            parsed.parameters
        )
        
        return {
            "status": result.status.value,
            "message": result.message,
            "data": result.data,
            "error": result.error,
            "execution_time": result.execution_time,
            "category": parsed.category,
            "action": parsed.action,
            "confidence": parsed.confidence
        }
    
    def interactive_mode(self):
        """Run interactive command loop"""
        print("\n" + "="*60)
        print("Linux Desktop AI Agent - Interactive Mode")
        print("="*60)
        print("Type 'help' for commands, 'quit' to exit\n")
        
        while True:
            try:
                user_input = input("agent> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == "quit":
                    print("Goodbye!")
                    break
                
                if user_input.lower() == "help":
                    self._show_help()
                    continue
                
                if user_input.lower() == "status":
                    self._show_status()
                    continue
                
                if user_input.lower() == "modules":
                    self._list_modules()
                    continue
                
                # Process command
                result = self.process_command(user_input)
                self._print_result(result)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                print(f"Error: {e}")
    
    def _show_help(self):
        """Show help information"""
        help_text = """
Available Commands:
  help              - Show this help message
  status            - Show system status
  modules           - List available modules
  quit              - Exit the agent

Example Commands:
  "check my system health"
  "clean up my downloads folder"
  "install python3-pip"
  "what's my disk usage"
  "organize my photos by date"
  "test internet connectivity"
  "find large files in my home"
  "scan for security issues"
  "check for updates"

Natural Language Processing:
  The agent understands natural language commands and will:
  1. Parse your intent
  2. Extract parameters
  3. Route to appropriate module
  4. Execute the action
  5. Return results
        """
        print(help_text)
    
    def _show_status(self):
        """Show system status"""
        print("\n" + "="*60)
        print("System Status")
        print("="*60)
        
        # Get system health
        monitor = self.registry.get_module("system_monitor")
        if monitor:
            result = monitor.execute("get_system_health", {})
            if result.status == ResultStatus.SUCCESS:
                health = result.data
                print(f"Health Score: {health.get('health_score', 'N/A')}/100")
                print(f"CPU Usage: {health.get('cpu', {}).get('usage_percent', 'N/A')}%")
                print(f"Memory Usage: {health.get('memory', {}).get('percent', 'N/A')}%")
                
                if health.get('warnings'):
                    print(f"Warnings: {', '.join(health['warnings'])}")
        print()
    
    def _list_modules(self):
        """List all available modules"""
        print("\n" + "="*60)
        print("Available Modules")
        print("="*60)
        
        modules = self.registry.list_modules()
        for module in modules:
            print(f"\n{module['name']} (v{module['version']})")
            print(f"  Description: {module['description']}")
            print(f"  Enabled: {module['enabled']}")
            print(f"  Actions: {', '.join(module['supported_actions'][:3])}...")
        print()
    
    def _print_result(self, result: Dict[str, Any]):
        """Pretty print result"""
        print("\n" + "-"*60)
        print(f"Status: {result.get('status', 'unknown').upper()}")
        print(f"Message: {result.get('message', 'No message')}")
        
        if result.get('category'):
            print(f"Category: {result['category']}")
        
        if result.get('action'):
            print(f"Action: {result['action']}")
        
        if result.get('confidence'):
            print(f"Confidence: {result['confidence']:.1%}")
        
        if result.get('error'):
            print(f"Error: {result['error']}")
        
        if result.get('data'):
            print(f"Data: {json.dumps(result['data'], indent=2, default=str)}")
        
        if result.get('execution_time'):
            print(f"Execution Time: {result['execution_time']:.2f}s")
        print("-"*60 + "\n")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "modules": self.registry.get_stats(),
            "learning_patterns": self.llama.get_learning_stats(),
            "command_history_count": len(self.llama.command_history)
        }
    
    def explain_error(self, error_message: str) -> str:
        """Explain an error message"""
        return self.llama.explain_error(error_message)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Linux Desktop AI Agent - Intelligent automation using Llama"
    )
    parser.add_argument(
        "command",
        nargs="?",
        help="Command to execute (or 'interactive' for interactive mode)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show agent statistics"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize agent
    agent = LinuxDesktopAgent()
    
    # Show stats if requested
    if args.stats:
        stats = agent.get_stats()
        print(json.dumps(stats, indent=2, default=str))
        return
    
    # Interactive mode if no command
    if not args.command or args.command == "interactive":
        agent.interactive_mode()
        return
    
    # Process single command
    result = agent.process_command(args.command)
    
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        agent._print_result(result)


if __name__ == "__main__":
    main()
