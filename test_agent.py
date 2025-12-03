#!/usr/bin/env python3
"""
Test suite for Linux Desktop AI Agent
"""

import sys
import logging
from linux_desktop_agent import LinuxDesktopAgent
from module_framework import ResultStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentTester:
    """Test suite for the agent"""
    
    def __init__(self):
        self.agent = LinuxDesktopAgent()
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def test_command(self, command: str, expected_status: str = None) -> bool:
        """Test a single command"""
        print(f"\n{'='*60}")
        print(f"Testing: {command}")
        print('='*60)
        
        try:
            result = self.agent.process_command(command)
            
            print(f"Status: {result.get('status')}")
            print(f"Message: {result.get('message')}")
            print(f"Confidence: {result.get('confidence', 0):.1%}")
            
            if expected_status and result.get('status') != expected_status:
                print(f"❌ FAILED: Expected {expected_status}, got {result.get('status')}")
                self.failed += 1
                return False
            
            if result.get('status') in ['success', 'partial']:
                print("✓ PASSED")
                self.passed += 1
                return True
            else:
                print("❌ FAILED")
                self.failed += 1
                return False
        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.failed += 1
            return False
    
    def run_system_tests(self):
        """Test system monitoring commands"""
        print("\n" + "="*60)
        print("SYSTEM MONITORING TESTS")
        print("="*60)
        
        commands = [
            "check my system health",
            "what's my cpu usage",
            "how much disk space do i have",
            "show me the top processes",
        ]
        
        for cmd in commands:
            self.test_command(cmd)
    
    def run_file_tests(self):
        """Test file management commands"""
        print("\n" + "="*60)
        print("FILE MANAGEMENT TESTS")
        print("="*60)
        
        commands = [
            "find large files in my home",
            "search for pdf files",
        ]
        
        for cmd in commands:
            self.test_command(cmd)
    
    def run_network_tests(self):
        """Test network commands"""
        print("\n" + "="*60)
        print("NETWORK TESTS")
        print("="*60)
        
        commands = [
            "test my internet connection",
            "check my network interfaces",
        ]
        
        for cmd in commands:
            self.test_command(cmd)
    
    def run_package_tests(self):
        """Test package management commands"""
        print("\n" + "="*60)
        print("PACKAGE MANAGEMENT TESTS")
        print("="*60)
        
        commands = [
            "check for updates",
            "list installed packages",
        ]
        
        for cmd in commands:
            self.test_command(cmd)
    
    def run_security_tests(self):
        """Test security commands"""
        print("\n" + "="*60)
        print("SECURITY TESTS")
        print("="*60)
        
        commands = [
            "check firewall status",
            "check my ssh keys",
        ]
        
        for cmd in commands:
            self.test_command(cmd)
    
    def run_developer_tests(self):
        """Test developer tool commands"""
        print("\n" + "="*60)
        print("DEVELOPER TOOLS TESTS")
        print("="*60)
        
        commands = [
            "check if port 8000 is available",
            "find port conflicts",
        ]
        
        for cmd in commands:
            self.test_command(cmd)
    
    def test_module_registration(self):
        """Test module registration"""
        print("\n" + "="*60)
        print("MODULE REGISTRATION TEST")
        print("="*60)
        
        modules = self.agent.registry.list_modules()
        print(f"Registered modules: {len(modules)}")
        
        for module in modules:
            print(f"  ✓ {module['name']} (v{module['version']})")
        
        if len(modules) >= 7:
            print("✓ PASSED: All modules registered")
            self.passed += 1
            return True
        else:
            print(f"❌ FAILED: Expected 7 modules, got {len(modules)}")
            self.failed += 1
            return False
    
    def test_llama_integration(self):
        """Test Llama integration"""
        print("\n" + "="*60)
        print("LLAMA INTEGRATION TEST")
        print("="*60)
        
        try:
            # Test command parsing
            parsed = self.agent.llama.parse_command("check my system health")
            
            print(f"Action: {parsed.action}")
            print(f"Category: {parsed.category}")
            print(f"Confidence: {parsed.confidence:.1%}")
            
            if parsed.confidence > 0.3:
                print("✓ PASSED: Llama parsing working")
                self.passed += 1
                return True
            else:
                print("❌ FAILED: Low confidence")
                self.failed += 1
                return False
        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.failed += 1
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Total: {self.passed + self.failed}")
        
        if self.failed == 0:
            print("\n✓ ALL TESTS PASSED!")
            return 0
        else:
            print(f"\n❌ {self.failed} test(s) failed")
            return 1
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("LINUX DESKTOP AI AGENT - TEST SUITE")
        print("="*60)
        
        # Core tests
        self.test_module_registration()
        self.test_llama_integration()
        
        # Feature tests
        self.run_system_tests()
        self.run_file_tests()
        self.run_network_tests()
        self.run_package_tests()
        self.run_security_tests()
        self.run_developer_tests()
        
        # Print summary
        return self.print_summary()


def main():
    """Main test runner"""
    tester = AgentTester()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
