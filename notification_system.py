#!/usr/bin/env python3
"""
Notification System for Linux Desktop AI Agent
Handles desktop notifications, alerts, and logging
"""

import subprocess
import logging
import smtplib
from typing import Optional, List
from enum import Enum
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class NotificationSystem:
    """
    Notification system for desktop alerts
    Supports desktop notifications, email, and sound alerts
    """
    
    def __init__(self, config: Optional[dict] = None):
        """
        Initialize notification system
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.notifications_enabled = self.config.get("notifications_enabled", True)
        self.notification_type = self.config.get("notification_type", "desktop")
        self.email_address = self.config.get("email_address")
        
        self.notification_history: List[dict] = []
        self.max_history = 100
    
    def notify(self, title: str, message: str, 
               priority: NotificationPriority = NotificationPriority.NORMAL,
               sound: bool = False) -> bool:
        """
        Send notification
        
        Args:
            title: Notification title
            message: Notification message
            priority: Notification priority
            sound: Whether to play sound
            
        Returns:
            True if successful
        """
        if not self.notifications_enabled:
            return False
        
        # Log to history
        self._add_to_history(title, message, priority)
        
        success = False
        
        # Send desktop notification
        if self.notification_type in ["desktop", "both"]:
            success = self._send_desktop_notification(title, message, priority)
        
        # Send email notification
        if self.notification_type in ["email", "both"] and self.email_address:
            self._send_email_notification(title, message, priority)
        
        # Play sound if requested
        if sound:
            self._play_sound(priority)
        
        return success
    
    def _send_desktop_notification(self, title: str, message: str,
                                   priority: NotificationPriority) -> bool:
        """Send desktop notification using notify-send"""
        try:
            urgency_map = {
                NotificationPriority.LOW: "low",
                NotificationPriority.NORMAL: "normal",
                NotificationPriority.HIGH: "critical",
                NotificationPriority.CRITICAL: "critical"
            }
            
            urgency = urgency_map.get(priority, "normal")
            
            cmd = [
                "notify-send",
                "-u", urgency,
                "-t", "5000",
                title,
                message
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=10)
            
            if result.returncode == 0:
                logger.info(f"Desktop notification sent: {title}")
                return True
            else:
                logger.warning(f"Failed to send desktop notification: {result.stderr.decode()}")
                return False
        except FileNotFoundError:
            logger.warning("notify-send not found. Install with: sudo apt install libnotify-bin")
            return False
        except Exception as e:
            logger.error(f"Error sending desktop notification: {e}")
            return False
    
    def _send_email_notification(self, title: str, message: str,
                                priority: NotificationPriority):
        """Send email notification"""
        try:
            # This requires email configuration
            # For now, just log it
            logger.info(f"Email notification would be sent to {self.email_address}: {title}")
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
    
    def _play_sound(self, priority: NotificationPriority):
        """Play sound alert"""
        try:
            sound_file = self._get_sound_file(priority)
            
            # Try to play with paplay
            subprocess.run(
                ["paplay", sound_file],
                capture_output=True,
                timeout=5
            )
        except Exception as e:
            logger.debug(f"Could not play sound: {e}")
    
    def _get_sound_file(self, priority: NotificationPriority) -> str:
        """Get sound file for priority"""
        sound_map = {
            NotificationPriority.LOW: "/usr/share/sounds/freedesktop/stereo/complete.oga",
            NotificationPriority.NORMAL: "/usr/share/sounds/freedesktop/stereo/complete.oga",
            NotificationPriority.HIGH: "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga",
            NotificationPriority.CRITICAL: "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga"
        }
        
        return sound_map.get(priority, "/usr/share/sounds/freedesktop/stereo/complete.oga")
    
    def _add_to_history(self, title: str, message: str, priority: NotificationPriority):
        """Add notification to history"""
        notification = {
            "timestamp": datetime.now().isoformat(),
            "title": title,
            "message": message,
            "priority": priority.name
        }
        
        self.notification_history.append(notification)
        
        # Keep history size limited
        if len(self.notification_history) > self.max_history:
            self.notification_history = self.notification_history[-self.max_history:]
    
    def get_history(self, limit: int = 20) -> List[dict]:
        """Get notification history"""
        return self.notification_history[-limit:]
    
    def clear_history(self):
        """Clear notification history"""
        self.notification_history.clear()


class AlertManager:
    """Manages system alerts based on thresholds"""
    
    def __init__(self, notification_system: NotificationSystem, config: Optional[dict] = None):
        """
        Initialize alert manager
        
        Args:
            notification_system: Notification system instance
            config: Configuration dictionary
        """
        self.notification_system = notification_system
        self.config = config or {}
        
        self.cpu_threshold = self.config.get("cpu_threshold", 80.0)
        self.memory_threshold = self.config.get("memory_threshold", 80.0)
        self.disk_threshold = self.config.get("disk_threshold", 85.0)
        
        self.alert_history = {}
    
    def check_cpu(self, cpu_usage: float) -> bool:
        """Check CPU usage and alert if needed"""
        if cpu_usage > self.cpu_threshold:
            self.notification_system.notify(
                "High CPU Usage",
                f"CPU usage is {cpu_usage:.1f}%",
                NotificationPriority.HIGH
            )
            return True
        return False
    
    def check_memory(self, memory_usage: float) -> bool:
        """Check memory usage and alert if needed"""
        if memory_usage > self.memory_threshold:
            self.notification_system.notify(
                "High Memory Usage",
                f"Memory usage is {memory_usage:.1f}%",
                NotificationPriority.HIGH
            )
            return True
        return False
    
    def check_disk(self, disk_usage: float) -> bool:
        """Check disk usage and alert if needed"""
        if disk_usage > self.disk_threshold:
            self.notification_system.notify(
                "Disk Space Low",
                f"Disk usage is {disk_usage:.1f}%",
                NotificationPriority.CRITICAL
            )
            return True
        return False
    
    def check_security_issue(self, issue: str) -> bool:
        """Alert on security issue"""
        self.notification_system.notify(
            "Security Alert",
            issue,
            NotificationPriority.CRITICAL,
            sound=True
        )
        return True
    
    def check_update_available(self, package_count: int) -> bool:
        """Alert on available updates"""
        if package_count > 0:
            self.notification_system.notify(
                "Updates Available",
                f"{package_count} package updates available",
                NotificationPriority.NORMAL
            )
            return True
        return False


def test_notifications():
    """Test notification system"""
    print("Testing Notification System...")
    
    notif_system = NotificationSystem({
        "notifications_enabled": True,
        "notification_type": "desktop"
    })
    
    # Test different priority levels
    priorities = [
        (NotificationPriority.LOW, "Low Priority Test"),
        (NotificationPriority.NORMAL, "Normal Priority Test"),
        (NotificationPriority.HIGH, "High Priority Test"),
        (NotificationPriority.CRITICAL, "Critical Priority Test")
    ]
    
    for priority, message in priorities:
        print(f"Sending {priority.name} notification...")
        notif_system.notify(
            "Test Notification",
            message,
            priority
        )
    
    # Show history
    print("\nNotification History:")
    for notif in notif_system.get_history():
        print(f"  [{notif['priority']}] {notif['title']}: {notif['message']}")


if __name__ == "__main__":
    test_notifications()
