import os
import subprocess
import platform
import webbrowser
import time

# ==================== BROWSER OPERATIONS ====================

def open_browser(browser_name="default", url=None):
    """Open a browser with optional URL"""
    try:
        if url is None:
            url = "about:blank"
        
        browser_name = browser_name.lower()
        
        if browser_name == "firefox":
            return open_firefox(url)
        elif browser_name == "chrome":
            return open_chrome(url)
        elif browser_name == "edge":
            return open_edge(url)
        else:
            # Use default browser
            webbrowser.open(url)
            return f"Opened {url} in default browser"
    
    except Exception as e:
        return f"Error opening browser: {str(e)}"

def open_firefox(url="about:blank"):
    """Open Firefox browser with specified URL"""
    try:
        if platform.system().lower() == "windows":
            # Try common Firefox paths on Windows
            firefox_paths = [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
                r"C:\Users\%USERNAME%\AppData\Local\Mozilla Firefox\firefox.exe"
            ]
            
            for path in firefox_paths:
                expanded_path = os.path.expandvars(path)
                if os.path.exists(expanded_path):
                    subprocess.Popen([expanded_path, url])
                    return f"Firefox opened with {url}"
            
            # Try using system PATH
            try:
                subprocess.Popen(["firefox", url])
                return f"Firefox opened with {url}"
            except FileNotFoundError:
                return "Firefox not found. Please install Firefox or use default browser."
        
        else:
            # Linux/Mac
            try:
                subprocess.Popen(["firefox", url])
                return f"Firefox opened with {url}"
            except FileNotFoundError:
                return "Firefox not found. Please install Firefox or use default browser."
    
    except Exception as e:
        return f"Error opening Firefox: {str(e)}"

def open_chrome(url="about:blank"):
    """Open Chrome browser with specified URL"""
    try:
        if platform.system().lower() == "windows":
            # Try common Chrome paths on Windows
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Users\%USERNAME%\AppData\Local\Google\Chrome\Application\chrome.exe"
            ]
            
            for path in chrome_paths:
                expanded_path = os.path.expandvars(path)
                if os.path.exists(expanded_path):
                    subprocess.Popen([expanded_path, url])
                    return f"Chrome opened with {url}"
            
            # Try using system PATH
            try:
                subprocess.Popen(["chrome", url])
                return f"Chrome opened with {url}"
            except FileNotFoundError:
                return "Chrome not found. Please install Chrome or use default browser."
        
        else:
            # Linux/Mac
            chrome_commands = ["google-chrome", "chromium-browser", "chromium"]
            
            for cmd in chrome_commands:
                try:
                    subprocess.Popen([cmd, url])
                    return f"Chrome opened with {url}"
                except FileNotFoundError:
                    continue
            
            return "Chrome not found. Please install Chrome/Chromium or use default browser."
    
    except Exception as e:
        return f"Error opening Chrome: {str(e)}"

def open_edge(url="about:blank"):
    """Open Microsoft Edge browser with specified URL"""
    try:
        if platform.system().lower() == "windows":
            # Try Edge paths on Windows
            edge_paths = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            ]
            
            for path in edge_paths:
                if os.path.exists(path):
                    subprocess.Popen([path, url])
                    return f"Edge opened with {url}"
            
            # Try using system PATH
            try:
                subprocess.Popen(["msedge", url])
                return f"Edge opened with {url}"
            except FileNotFoundError:
                return "Edge not found. Please install Edge or use default browser."
        
        else:
            # Linux Edge
            try:
                subprocess.Popen(["microsoft-edge", url])
                return f"Edge opened with {url}"
            except FileNotFoundError:
                return "Edge not found. Please install Edge or use default browser."
    
    except Exception as e:
        return f"Error opening Edge: {str(e)}"

# ==================== QUICK ACCESS FUNCTIONS ====================

def open_gmail(browser="default"):
    """Open Gmail in specified browser"""
    gmail_url = "https://mail.google.com"
    return open_browser(browser, gmail_url)

def open_youtube(browser="default"):
    """Open YouTube in specified browser"""
    youtube_url = "https://www.youtube.com"
    return open_browser(browser, youtube_url)

def open_google(browser="default"):
    """Open Google in specified browser"""
    google_url = "https://www.google.com"
    return open_browser(browser, google_url)

def open_facebook(browser="default"):
    """Open Facebook in specified browser"""
    facebook_url = "https://www.facebook.com"
    return open_browser(browser, facebook_url)

def open_twitter(browser="default"):
    """Open Twitter/X in specified browser"""
    twitter_url = "https://www.twitter.com"
    return open_browser(browser, twitter_url)

def open_linkedin(browser="default"):
    """Open LinkedIn in specified browser"""
    linkedin_url = "https://www.linkedin.com"
    return open_browser(browser, linkedin_url)

def open_github(browser="default"):
    """Open GitHub in specified browser"""
    github_url = "https://www.github.com"
    return open_browser(browser, github_url)

def open_stackoverflow(browser="default"):
    """Open Stack Overflow in specified browser"""
    stackoverflow_url = "https://stackoverflow.com"
    return open_browser(browser, stackoverflow_url)

# ==================== BROWSER WITH INTERFACE WORDS ====================

def open_browser_with_interface(browser="firefox", site="gmail"):
    """Open browser with interface showing specific site"""
    try:
        site = site.lower()
        browser = browser.lower()
        
        # Map sites to their URLs and interface descriptions
        sites_map = {
            "gmail": {
                "url": "https://mail.google.com",
                "interface": "Gmail interface with inbox, compose, and email management"
            },
            "google": {
                "url": "https://www.google.com", 
                "interface": "Google search interface with search bar and options"
            },
            "youtube": {
                "url": "https://www.youtube.com",
                "interface": "YouTube interface with videos, subscriptions, and trending"
            },
            "facebook": {
                "url": "https://www.facebook.com",
                "interface": "Facebook interface with news feed, messages, and notifications"
            },
            "twitter": {
                "url": "https://www.twitter.com",
                "interface": "Twitter interface with timeline, tweets, and trending topics"
            },
            "linkedin": {
                "url": "https://www.linkedin.com",
                "interface": "LinkedIn interface with professional network and job listings"
            }
        }
        
        if site not in sites_map:
            return f"Site '{site}' not recognized. Available sites: {', '.join(sites_map.keys())}"
        
        site_info = sites_map[site]
        result = open_browser(browser, site_info["url"])
        
        # Add interface description to result
        if "opened" in result.lower():
            result += f"\n\nInterface: {site_info['interface']}"
        
        return result
    
    except Exception as e:
        return f"Error opening browser with interface: {str(e)}"

# ==================== BROWSER MANAGEMENT ====================

def close_browser(browser_name="all"):
    """Close browser processes"""
    try:
        browser_name = browser_name.lower()
        
        if platform.system().lower() == "windows":
            if browser_name == "firefox" or browser_name == "all":
                subprocess.run(["taskkill", "/f", "/im", "firefox.exe"], capture_output=True)
            if browser_name == "chrome" or browser_name == "all":
                subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], capture_output=True)
            if browser_name == "edge" or browser_name == "all":
                subprocess.run(["taskkill", "/f", "/im", "msedge.exe"], capture_output=True)
        else:
            if browser_name == "firefox" or browser_name == "all":
                subprocess.run(["pkill", "firefox"], capture_output=True)
            if browser_name == "chrome" or browser_name == "all":
                subprocess.run(["pkill", "chrome"], capture_output=True)
                subprocess.run(["pkill", "chromium"], capture_output=True)
            if browser_name == "edge" or browser_name == "all":
                subprocess.run(["pkill", "msedge"], capture_output=True)
        
        return f"Closed {browser_name} browser(s)"
    
    except Exception as e:
        return f"Error closing browser: {str(e)}"

def list_browsers():
    """List available browsers on the system"""
    try:
        available_browsers = []
        
        if platform.system().lower() == "windows":
            # Check Windows browsers
            firefox_paths = [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
            ]
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ]
            edge_paths = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            ]
            
            for path in firefox_paths:
                if os.path.exists(path):
                    available_browsers.append("Firefox")
                    break
            
            for path in chrome_paths:
                if os.path.exists(path):
                    available_browsers.append("Chrome")
                    break
            
            for path in edge_paths:
                if os.path.exists(path):
                    available_browsers.append("Edge")
                    break
        
        else:
            # Check Linux browsers
            browsers_to_check = [
                ("firefox", "Firefox"),
                ("google-chrome", "Chrome"),
                ("chromium-browser", "Chromium"),
                ("microsoft-edge", "Edge")
            ]
            
            for cmd, name in browsers_to_check:
                try:
                    subprocess.run(["which", cmd], capture_output=True, check=True)
                    available_browsers.append(name)
                except subprocess.CalledProcessError:
                    pass
        
        if available_browsers:
            return f"Available browsers: {', '.join(available_browsers)}"
        else:
            return "No browsers found. Using system default browser."
    
    except Exception as e:
        return f"Error listing browsers: {str(e)}"
