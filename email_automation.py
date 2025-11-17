import smtplib
import os
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# ==================== EMAIL AUTOMATION ====================

class EmailAutomation:
    def __init__(self):
        self.config_file = os.path.join(os.path.expanduser("~"), ".desktop_ai_email_config.json")
        self.email_config = self._load_email_config()
        
    def _load_email_config(self):
        """Load email configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        
        return {
            "smtp_server": "",
            "smtp_port": 587,
            "email": "",
            "password": "",  # Note: Should use app passwords for security
            "name": ""
        }
    
    def _save_email_config(self):
        """Save email configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.email_config, f, indent=2)
        except Exception as e:
            print(f"Error saving email config: {e}")
    
    def setup_email(self, email, password, smtp_server=None, smtp_port=587, name=None):
        """Setup email configuration"""
        try:
            self.email_config["email"] = email
            self.email_config["password"] = password
            self.email_config["name"] = name or email.split("@")[0]
            self.email_config["smtp_port"] = smtp_port
            
            # Auto-detect SMTP server based on email domain
            if smtp_server is None:
                domain = email.split("@")[1].lower()
                if "gmail" in domain:
                    smtp_server = "smtp.gmail.com"
                elif "outlook" in domain or "hotmail" in domain:
                    smtp_server = "smtp-mail.outlook.com"
                elif "yahoo" in domain:
                    smtp_server = "smtp.mail.yahoo.com"
                else:
                    smtp_server = f"smtp.{domain}"
            
            self.email_config["smtp_server"] = smtp_server
            self._save_email_config()
            
            return f"Email configured successfully for {email}"
        except Exception as e:
            return f"Error setting up email: {str(e)}"
    
    def send_email(self, to_email, subject, body, attachments=None):
        """Send an email"""
        try:
            if not self.email_config["email"] or not self.email_config["password"]:
                return "Email not configured. Use 'setup email' command first."
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.email_config['name']} <{self.email_config['email']}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments if any
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.email_config["smtp_server"], self.email_config["smtp_port"])
            server.starttls()
            server.login(self.email_config["email"], self.email_config["password"])
            
            text = msg.as_string()
            server.sendmail(self.email_config["email"], to_email, text)
            server.quit()
            
            return f"Email sent successfully to {to_email}"
        
        except Exception as e:
            return f"Error sending email: {str(e)}"
    
    def send_quick_email(self, to_email, message):
        """Send a quick email with minimal setup"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        subject = f"Quick message from Desktop AI - {timestamp}"
        return self.send_email(to_email, subject, message)
    
    def send_file_via_email(self, to_email, file_path, message=""):
        """Send a file via email"""
        try:
            if not os.path.exists(file_path):
                return f"File {file_path} does not exist"
            
            filename = os.path.basename(file_path)
            subject = f"File: {filename}"
            body = message or f"Attached file: {filename}\n\nSent via Desktop AI on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            return self.send_email(to_email, subject, body, [file_path])
        
        except Exception as e:
            return f"Error sending file: {str(e)}"
    
    def get_email_templates(self):
        """Get predefined email templates"""
        templates = {
            "meeting_request": {
                "subject": "Meeting Request - {topic}",
                "body": """Hi {name},

I would like to schedule a meeting to discuss {topic}.

Proposed time: {time}
Duration: {duration}
Location/Link: {location}

Please let me know if this works for you.

Best regards,
{sender_name}"""
            },
            "follow_up": {
                "subject": "Follow-up: {topic}",
                "body": """Hi {name},

I wanted to follow up on our previous discussion about {topic}.

{message}

Please let me know if you have any questions.

Best regards,
{sender_name}"""
            },
            "file_share": {
                "subject": "Sharing: {filename}",
                "body": """Hi {name},

I'm sharing the attached file: {filename}

{description}

Please let me know if you have any questions.

Best regards,
{sender_name}"""
            }
        }
        
        result = "Available Email Templates:\n\n"
        for template_name, template in templates.items():
            result += f"**{template_name.replace('_', ' ').title()}**\n"
            result += f"Subject: {template['subject']}\n"
            result += f"Preview: {template['body'][:100]}...\n\n"
        
        return result
    
    def send_template_email(self, template_name, to_email, **kwargs):
        """Send email using a template"""
        templates = {
            "meeting_request": {
                "subject": "Meeting Request - {topic}",
                "body": """Hi {name},

I would like to schedule a meeting to discuss {topic}.

Proposed time: {time}
Duration: {duration}
Location/Link: {location}

Please let me know if this works for you.

Best regards,
{sender_name}"""
            },
            "follow_up": {
                "subject": "Follow-up: {topic}",
                "body": """Hi {name},

I wanted to follow up on our previous discussion about {topic}.

{message}

Please let me know if you have any questions.

Best regards,
{sender_name}"""
            },
            "file_share": {
                "subject": "Sharing: {filename}",
                "body": """Hi {name},

I'm sharing the attached file: {filename}

{description}

Please let me know if you have any questions.

Best regards,
{sender_name}"""
            }
        }
        
        try:
            if template_name not in templates:
                return f"Template '{template_name}' not found"
            
            template = templates[template_name]
            
            # Add default sender name
            kwargs["sender_name"] = kwargs.get("sender_name", self.email_config["name"])
            
            # Format template
            subject = template["subject"].format(**kwargs)
            body = template["body"].format(**kwargs)
            
            return self.send_email(to_email, subject, body)
        
        except KeyError as e:
            return f"Missing template parameter: {e}"
        except Exception as e:
            return f"Error sending template email: {str(e)}"
    
    def schedule_email(self, to_email, subject, body, send_time):
        """Schedule an email to be sent later (basic implementation)"""
        # This is a simple implementation - in production, you'd want a proper scheduler
        try:
            scheduled_email = {
                "to": to_email,
                "subject": subject,
                "body": body,
                "send_time": send_time,
                "created": datetime.now().isoformat()
            }
            
            # Save to scheduled emails file
            scheduled_file = os.path.join(os.path.expanduser("~"), ".desktop_ai_scheduled_emails.json")
            scheduled_emails = []
            
            if os.path.exists(scheduled_file):
                with open(scheduled_file, 'r') as f:
                    scheduled_emails = json.load(f)
            
            scheduled_emails.append(scheduled_email)
            
            with open(scheduled_file, 'w') as f:
                json.dump(scheduled_emails, f, indent=2)
            
            return f"Email scheduled to be sent to {to_email} at {send_time}"
        
        except Exception as e:
            return f"Error scheduling email: {str(e)}"
    
    def get_email_status(self):
        """Get email configuration status"""
        if self.email_config["email"]:
            return f"""Email Configuration:
✓ Email: {self.email_config['email']}
✓ SMTP Server: {self.email_config['smtp_server']}
✓ Port: {self.email_config['smtp_port']}
✓ Name: {self.email_config['name']}

Status: Ready to send emails"""
        else:
            return """Email Configuration:
✗ Not configured

Use 'setup email <your_email> <password>' to configure email sending."""

# ==================== GLOBAL INSTANCE ====================

email_automation = EmailAutomation()

# ==================== CONVENIENCE FUNCTIONS ====================

def setup_user_email(email, password, smtp_server=None, smtp_port=587, name=None):
    """Setup email configuration"""
    return email_automation.setup_email(email, password, smtp_server, smtp_port, name)

def send_user_email(to_email, subject, body, attachments=None):
    """Send an email"""
    return email_automation.send_email(to_email, subject, body, attachments)

def send_quick_message(to_email, message):
    """Send quick email"""
    return email_automation.send_quick_email(to_email, message)

def send_file_email(to_email, file_path, message=""):
    """Send file via email"""
    return email_automation.send_file_via_email(to_email, file_path, message)

def get_email_templates():
    """Get email templates"""
    return email_automation.get_email_templates()

def send_template_email(template_name, to_email, **kwargs):
    """Send template email"""
    return email_automation.send_template_email(template_name, to_email, **kwargs)

def get_email_status():
    """Get email status"""
    return email_automation.get_email_status()
