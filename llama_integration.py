#!/usr/bin/env python3
"""
Llama Integration Module for Desktop AI Agent
Handles communication with locally installed Llama model
"""

import subprocess
import json
import logging
import re
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

SUPPORTED_OLLAMA_VERSION = "0.13.0"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class CommandParsed:
    """Represents a parsed command from user input"""
    action: str
    category: str
    parameters: Dict[str, str]
    confidence: float
    raw_input: str
    timestamp: datetime


class LlamaIntegration:
    """
    Manages communication with Llama model for NLP processing
    Requires: ollama installed and running locally
    """

    def __init__(self, model: str = "llama3.1:8b", host: str = "localhost", port: int = 11434):
        """
        Initialize Llama integration
        
        Args:
            model: Llama model to use (default: llama3.1:8b)
            host: Ollama server host (default: localhost)
            port: Ollama server port (default: 11434)
        """
        self.model = model
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.command_history: List[CommandParsed] = []
        self.learning_patterns: Dict[str, int] = {}
        
        # Verify Ollama is running
        if not self._check_ollama_running():
            logger.warning(f"Ollama not running at {self.base_url}")
            logger.info("Start Ollama with: ollama serve")
        else:
            self._ensure_supported_version()
        
        self._initialize_system_prompt()

    def _check_ollama_running(self) -> bool:
        """Check if Ollama service is running"""
        try:
            result = subprocess.run(
                ["curl", "-s", f"{self.base_url}/api/tags"],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error checking Ollama: {e}")
            return False

    def _ensure_supported_version(self):
        """Warn if Ollama version doesn't match supported version"""
        installed_version = self._get_ollama_version()
        if not installed_version:
            logger.warning(
                f"Unable to detect Ollama version (expected {SUPPORTED_OLLAMA_VERSION})."
            )
            return

        comparison = self._compare_versions(installed_version, SUPPORTED_OLLAMA_VERSION)
        if comparison < 0:
            logger.warning(
                f"Ollama {installed_version} detected, but {SUPPORTED_OLLAMA_VERSION} "
                "or newer is required. Please update Ollama."
            )
        elif comparison > 0:
            logger.info(
                f"Ollama {installed_version} detected (newer than supported "
                f"{SUPPORTED_OLLAMA_VERSION}). Proceed with caution."
            )
        else:
            logger.info(f"Ollama {installed_version} detected (supported).")

    def _get_ollama_version(self) -> Optional[str]:
        """Return installed Ollama version (if available)"""
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode != 0:
                return None

            output = (result.stdout or result.stderr or "").strip()
            match = re.search(r"(\d+\.\d+\.\d+)", output)
            if match:
                return match.group(1)
        except FileNotFoundError:
            logger.warning("Ollama CLI not found in PATH.")
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to check Ollama version: {e}")
        return None

    @staticmethod
    def _compare_versions(current: str, expected: str) -> int:
        """Compare semantic versions. Returns -1, 0, or 1."""
        def normalize(version: str) -> Tuple[int, int, int]:
            parts = version.split(".")
            return tuple(int(part) for part in (parts + ["0", "0", "0"])[:3])
        
        current_parts = normalize(current)
        expected_parts = normalize(expected)
        if current_parts < expected_parts:
            return -1
        if current_parts > expected_parts:
            return 1
        return 0

    def _initialize_system_prompt(self):
        """Initialize system prompt for command understanding"""
        self.system_prompt = """You are a Linux desktop AI agent. Respond only with valid JSON."""

    def query_llama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Send query to Llama model via Ollama API
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt override
            
        Returns:
            Model response
        """
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": f"{system_prompt or self.system_prompt}\n\nUser: {prompt}",
                "stream": False
            }
            
            logger.debug(f"Querying Llama with prompt: {prompt[:50]}...")
            response = requests.post(url, json=payload, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "").strip()
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text[:200]}")
                return ""
        except requests.Timeout:
            logger.error("Llama query timeout (exceeded 120 seconds)")
            return ""
        except requests.ConnectionError as e:
            logger.error(f"Failed to connect to Ollama at {self.base_url}: {e}")
            return ""
        except Exception as e:
            logger.error(f"Error querying Llama: {e}")
            return ""

    def parse_command(self, user_input: str) -> CommandParsed:
        """
        Parse user command using Llama
        
        Args:
            user_input: Raw user input
            
        Returns:
            Parsed command with action, category, parameters
        """
        prompt = f"""Analyze this user command and extract the action, category, and parameters.
Command: "{user_input}"

Respond ONLY with valid JSON (no markdown, no code blocks):
{{
    "action": "specific action",
    "category": "category name",
    "parameters": {{}},
    "confidence": 0.95,
    "reasoning": "brief explanation"
}}"""
        
        response = self.query_llama(prompt)
        
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(response)
            
            action = data.get("action") or "unknown"
            category = data.get("category") or "help"
            parameters = data.get("parameters") or {}

            parsed = CommandParsed(
                action=action,
                category=category,
                parameters=parameters,
                confidence=float(data.get("confidence", 0.5)),
                raw_input=user_input,
                timestamp=datetime.now()
            )
            
            # Learn from this command
            self._learn_pattern(parsed)
            self.command_history.append(parsed)
            
            return parsed
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Llama response: {e}")
            logger.debug(f"Response was: {response}")
            
            # Fallback parsing
            return CommandParsed(
                action="unknown",
                category="help",
                parameters={},
                confidence=0.0,
                raw_input=user_input,
                timestamp=datetime.now()
            )

    def _learn_pattern(self, command: CommandParsed):
        """Learn from parsed commands to improve future predictions"""
        pattern_key = f"{command.category}:{command.action}"
        self.learning_patterns[pattern_key] = self.learning_patterns.get(pattern_key, 0) + 1

    def classify_command(self, user_input: str) -> str:
        """
        Classify user command into a category
        
        Args:
            user_input: Raw user input
            
        Returns:
            Command category
        """
        prompt = f"""Classify this command into ONE category:
Command: "{user_input}"

Categories: system_control, file_management, package_management, security, network, monitoring, developer, automation, cleanup, help

Respond with ONLY the category name, nothing else."""
        
        response = self.query_llama(prompt).strip().lower()
        
        valid_categories = [
            "system_control", "file_management", "package_management",
            "security", "network", "monitoring", "developer",
            "automation", "cleanup", "help"
        ]
        
        for category in valid_categories:
            if category in response:
                return category
        
        return "help"

    def extract_parameters(self, user_input: str, category: str) -> Dict[str, str]:
        """
        Extract parameters from user input for specific category
        
        Args:
            user_input: Raw user input
            category: Command category
            
        Returns:
            Dictionary of extracted parameters
        """
        prompt = f"""Extract parameters from this {category} command:
Command: "{user_input}"

Return ONLY valid JSON with parameter names and values:
{{"param1": "value1", "param2": "value2"}}"""
        
        response = self.query_llama(prompt)
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
        except json.JSONDecodeError:
            return {}

    def handle_unclear_command(self, user_input: str) -> Tuple[str, List[str]]:
        """
        Handle unclear commands by asking for clarification
        
        Args:
            user_input: Unclear user input
            
        Returns:
            Clarification message and suggested options
        """
        prompt = f"""The user said: "{user_input}"
This is unclear. Generate:
1. A clarification question
2. 3 possible interpretations

Respond in JSON:
{{
    "question": "clarification question",
    "suggestions": ["option1", "option2", "option3"]
}}"""
        
        response = self.query_llama(prompt)
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data.get("question", "Could you clarify?"), data.get("suggestions", [])
        except json.JSONDecodeError:
            pass
        
        return "Could you clarify what you want to do?", []

    def get_command_history(self, limit: int = 10) -> List[CommandParsed]:
        """Get recent command history"""
        return self.command_history[-limit:]

    def get_learning_stats(self) -> Dict[str, int]:
        """Get learning pattern statistics"""
        return self.learning_patterns.copy()

    def suggest_next_action(self, context: str) -> str:
        """
        Suggest next action based on context and patterns
        
        Args:
            context: Current system context
            
        Returns:
            Suggested action
        """
        prompt = f"""Based on this system context, suggest the next maintenance action:
Context: {context}

Respond with a single actionable suggestion."""
        
        return self.query_llama(prompt)

    def explain_error(self, error_message: str) -> str:
        """
        Explain a system error in simple terms
        
        Args:
            error_message: Error message to explain
            
        Returns:
            Simple explanation
        """
        prompt = f"""Explain this Linux error in simple terms:
Error: {error_message}

Provide a brief, user-friendly explanation."""
        
        return self.query_llama(prompt)


def test_llama_integration():
    """Test Llama integration"""
    print("Testing Llama Integration...")
    
    llama = LlamaIntegration()
    
    # Test queries
    test_commands = [
        "check my system health",
        "clean up my downloads folder",
        "install python3-pip",
        "what's my disk usage",
        "organize my photos by date"
    ]
    
    for cmd in test_commands:
        print(f"\nCommand: {cmd}")
        parsed = llama.parse_command(cmd)
        print(f"  Action: {parsed.action}")
        print(f"  Category: {parsed.category}")
        print(f"  Parameters: {parsed.parameters}")
        print(f"  Confidence: {parsed.confidence}")


if __name__ == "__main__":
    test_llama_integration()
