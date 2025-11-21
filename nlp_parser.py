from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re

# Import new modules
try:
    from app_launcher import *
    from advanced_file_ops import *
    from security_cleanup import *
    from personalization import *
    from email_automation import *
except ImportError as e:
    print(f"Warning: Could not import some modules: {e}")

# Define action words and their synonyms
ACTION_WORDS = {
    "create": ["create", "make", "new", "add", "build"],
    "delete": ["delete", "remove", "del", "erase", "destroy"],
    "list": ["list", "show", "display", "see", "view"],
    "navigate": ["go", "open", "enter", "cd", "navigate", "move"],
    "back": ["back", "return", "previous"],
    "move": ["move", "transfer", "relocate"],
    "rename": ["rename", "change"],
    "search": ["search", "find", "look"],
    "where": ["where", "location", "current"],
    "check": ["check", "test", "verify", "status"],
    "connect": ["connect", "join", "link"],
    "adjust": ["adjust", "set", "change", "modify"],
    "take": ["take", "capture", "grab"],
    "kill": ["kill", "stop", "end", "terminate"],
    "shutdown": ["shutdown", "poweroff", "turnoff"],
    "restart": ["restart", "reboot", "reset"],
    "cancel": ["cancel", "abort", "stop"],
    "open": ["open", "launch", "start", "run"],
    "close": ["close", "quit", "exit"],
    "convert": ["convert", "transform", "change"],
    "extract": ["extract", "get", "pull"],
    "summarize": ["summarize", "summary", "brief"],
    # New actions for enhanced features
    "lock": ["lock", "secure"],
    "logout": ["logout", "signout", "logoff"],
    "organize": ["organize", "sort", "arrange"],
    "compress": ["compress", "zip", "archive"],
    "backup": ["backup", "save", "copy"],
    "clean": ["clean", "cleanup", "clear"],
    "scan": ["scan", "detect", "check"],
    "optimize": ["optimize", "improve", "enhance"],
    "monitor": ["monitor", "watch", "track"],
    "suggest": ["suggest", "recommend", "propose"],
    "learn": ["learn", "remember", "save"],
    "send": ["send", "email", "mail"],
    "setup": ["setup", "configure", "install"]
}

# Target words (what we're acting on)
TARGET_WORDS = ["folder", "directory", "dir", "folders", "directories", "file", "files"]

# Location words
LOCATION_WORDS = ["home", "desktop", "documents", "downloads", "pictures", "music", "videos", "root", "at", "in", "to"]

# System target words
SYSTEM_WORDS = ["storage", "disk", "space", "internet", "speed", "wifi", "network", "volume", "sound", "audio", "screenshot", "screen", "processes", "process", "system", "computer", "brightness", "battery", "cpu", "memory", "power"]

# Browser target words
BROWSER_WORDS = ["browser", "firefox", "chrome", "edge", "gmail", "google", "youtube", "facebook", "twitter", "linkedin", "github", "stackoverflow"]

# Document target words
DOCUMENT_WORDS = ["document", "word", "docx", "pdf", "doc", "text", "file"]

# Application target words
APP_WORDS = ["app", "application", "program", "software", "vscode", "code", "word", "excel", "powerpoint", "outlook", "teams", "slack", "discord", "spotify", "vlc", "calculator", "notepad", "camera"]

# File operation target words
FILE_OP_WORDS = ["duplicates", "large", "unused", "junk", "cache", "temp", "bloatware", "virus", "malware", "threats"]

# Personalization target words
PERSONAL_WORDS = ["shortcut", "workflow", "habit", "pattern", "preference", "favorite", "suggestion", "stats", "history"]

# Email target words
EMAIL_WORDS = ["email", "mail", "message", "template", "attachment"]

def preprocess_natural_language(user_input):
    """Preprocess natural language input to extract intent"""
    text = user_input.lower().strip()
    
    # Handle conversational starters
    conversational_starters = [
        "hey", "hi", "hello", "can you", "could you", "would you", "please",
        "i want to", "i need to", "i would like to", "help me", "make me",
        "do this", "can it", "is it possible", "how do i", "how can i"
    ]
    
    # Remove conversational starters
    for starter in conversational_starters:
        if text.startswith(starter):
            text = text[len(starter):].strip()
        # Also handle mid-sentence patterns
        text = text.replace(f" {starter} ", " ")
    
    # Handle question patterns
    question_patterns = [
        ("can you make me a", "create"),
        ("make me a", "create"),
        ("create me a", "create"),
        ("i want to create", "create"),
        ("i need to make", "create"),
        ("help me create", "create"),
        ("help me make", "create"),
        ("can you open", "open"),
        ("open up", "open"),
        ("i want to open", "open"),
        ("launch", "open"),
        ("start", "open"),
        ("run", "open"),
        ("show me", "list"),
        ("display", "list"),
        ("let me see", "list"),
        ("i want to see", "list"),
        ("what are my", "list"),
        ("list my", "list"),
        ("find me", "search"),
        ("look for", "search"),
        ("search for", "search"),
        ("can you find", "search"),
        ("where is", "search"),
        ("locate", "search"),
        ("delete this", "delete"),
        ("remove this", "delete"),
        ("get rid of", "delete"),
        ("clean up", "clean"),
        ("tidy up", "organize"),
        ("sort out", "organize"),
        ("organize my", "organize"),
        ("fix my", "optimize"),
        ("speed up", "optimize"),
        ("make faster", "optimize"),
        ("improve", "optimize"),
        ("secure my", "scan"),
        ("protect my", "scan"),
        ("check for viruses", "scan"),
        ("scan my", "scan"),
        ("backup my", "backup"),
        ("save my", "backup"),
        ("copy my", "backup"),
        ("compress", "compress"),
        ("zip", "compress"),
        ("archive", "compress"),
        ("extract", "extract"),
        ("unzip", "extract"),
        ("what can you do", "capabilities"),
        ("what do you do", "capabilities"),
        ("help", "capabilities"),
        ("features", "capabilities")
    ]
    
    # Apply pattern replacements
    for pattern, replacement in question_patterns:
        if pattern in text:
            text = text.replace(pattern, replacement)
    
    # Handle "what can you do" type questions
    capability_questions = [
        "what can you do", "what are your features", "what do you do",
        "help me", "what's possible", "show capabilities", "list features"
    ]
    
    for question in capability_questions:
        if question in text:
            return "list capabilities"
    
    return text

def find_best_action(user_input):
    """Find the best matching action from user input"""
    # Preprocess natural language
    processed_input = preprocess_natural_language(user_input)
    
    # Handle capability questions
    if processed_input == "list capabilities":
        return "capabilities"
    
    words = processed_input.lower().split()
    
    # Check for specific patterns first
    if any(phrase in user_input.lower() for phrase in ["where am i", "current location", "where"]):
        return "where"
    
    # Check for system-specific patterns
    if any(phrase in user_input.lower() for phrase in ["internet speed", "network speed", "connection speed"]):
        return "check"
    
    if any(phrase in user_input.lower() for phrase in ["take screenshot", "capture screen"]):
        return "take"
    
    for action, synonyms in ACTION_WORDS.items():
        for word in words:
            # Check each word against action synonyms
            best_match = process.extractOne(word, synonyms, scorer=fuzz.ratio)
            if best_match and best_match[1] >= 70:  # 70% similarity threshold
                return action
    return None

def find_target_word(user_input):
    """Find if user mentioned folder/directory"""
    words = user_input.lower().split()
    
    for word in words:
        best_match = process.extractOne(word, TARGET_WORDS, scorer=fuzz.ratio)
        if best_match and best_match[1] >= 70:  # 70% similarity for "folder"
            return True
    return False

def find_system_word(user_input):
    """Find if user mentioned system-related words"""
    words = user_input.lower().split()
    
    for word in words:
        best_match = process.extractOne(word, SYSTEM_WORDS, scorer=fuzz.ratio)
        if best_match and best_match[1] >= 70:
            return best_match[0]
    return None

def find_browser_word(user_input):
    """Find if user mentioned browser-related words"""
    words = user_input.lower().split()
    
    for word in words:
        best_match = process.extractOne(word, BROWSER_WORDS, scorer=fuzz.ratio)
        if best_match and best_match[1] >= 70:
            return best_match[0]
    return None

def find_document_word(user_input):
    """Find if user mentioned document-related words"""
    words = user_input.lower().split()
    
    best_match = process.extractOne(" ".join(words), DOCUMENT_WORDS, scorer=fuzz.partial_ratio)
    if best_match and best_match[1] > 70:
        return best_match[0]
    return None

def find_app_word(user_input):
    """Find if user mentioned application-related words"""
    words = user_input.lower().split()
    
    best_match = process.extractOne(" ".join(words), APP_WORDS, scorer=fuzz.partial_ratio)
    if best_match and best_match[1] > 70:
        return best_match[0]
    return None

def find_file_op_word(user_input):
    """Find if user mentioned file operation-related words"""
    words = user_input.lower().split()
    
    best_match = process.extractOne(" ".join(words), FILE_OP_WORDS, scorer=fuzz.partial_ratio)
    if best_match and best_match[1] > 70:
        return best_match[0]
    return None

def find_personal_word(user_input):
    """Find if user mentioned personalization-related words"""
    words = user_input.lower().split()
    
    best_match = process.extractOne(" ".join(words), PERSONAL_WORDS, scorer=fuzz.partial_ratio)
    if best_match and best_match[1] > 70:
        return best_match[0]
    return None

def find_email_word(user_input):
    """Find if user mentioned email-related words"""
    words = user_input.lower().split()
    
    best_match = process.extractOne(" ".join(words), EMAIL_WORDS, scorer=fuzz.partial_ratio)
    if best_match and best_match[1] > 70:
        return best_match[0]
    return None

def extract_name(user_input, action):
    """Extract file/folder name using multiple strategies"""
    words = user_input.lower().split()
    
    # Strategy 1: Look for pattern after target keyword
    patterns = [
        r'(?:folder|directory|dir)\s+(?:called\s+|named\s+)?(\w+)',
        r'(?:file)\s+(?:called\s+|named\s+)?(\w+(?:\.\w+)?)',
        r'(?:called|named)\s+(\w+(?:\.\w+)?)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, user_input.lower())
        if match:
            return match.group(1)
    
    # Strategy 2: Take the last word if it's not reserved
    if len(words) >= 2:
        last_word = words[-1]
        all_reserved_words = get_all_reserved_words()
        
        if last_word not in all_reserved_words:
            return last_word
    
    # Strategy 3: Look for word after action words
    for i, word in enumerate(words):
        for synonyms in ACTION_WORDS.values():
            best_match = process.extractOne(word, synonyms, scorer=fuzz.ratio)
            if best_match and best_match[1] >= 70:
                # Found action word, look for name after it
                for j in range(i + 1, len(words)):
                    candidate = words[j]
                    all_reserved_words = get_all_reserved_words()
                    if candidate not in all_reserved_words:
                        return candidate
    
    return None

def extract_location(user_input):
    """Extract location from user input"""
    words = user_input.lower().split()
    
    # Look for location indicators
    location_indicators = ["at", "in", "to"]
    
    for i, word in enumerate(words):
        if word in location_indicators and i + 1 < len(words):
            next_word = words[i + 1]
            if next_word in LOCATION_WORDS:
                return next_word
    
    # Direct location mention
    for word in words:
        if word in LOCATION_WORDS and word not in ["at", "in", "to"]:
            return word
    
    return None

def extract_two_names(user_input):
    """Extract two names for operations like rename or move"""
    words = user_input.lower().split()
    all_reserved_words = get_all_reserved_words()
    
    # Find non-reserved words that could be names
    potential_names = []
    for word in words:
        if word not in all_reserved_words and len(word) > 1:
            potential_names.append(word)
    
    if len(potential_names) >= 2:
        return potential_names[0], potential_names[1]
    elif len(potential_names) == 1:
        return potential_names[0], None
    
    return None, None

def get_all_reserved_words():
    """Get all reserved words that shouldn't be considered as names"""
    all_reserved_words = []
    for synonyms in ACTION_WORDS.values():
        all_reserved_words.extend(synonyms)
    all_reserved_words.extend(TARGET_WORDS)
    all_reserved_words.extend(LOCATION_WORDS)
    all_reserved_words.extend(SYSTEM_WORDS)
    all_reserved_words.extend(BROWSER_WORDS)
    all_reserved_words.extend(DOCUMENT_WORDS)
    return all_reserved_words

def parse_command(user_input):
    """
    Parse user input and detect intent with comprehensive command support
    """
    if not user_input.strip():
        return None, None, None
    
    # Store original input for parameter extraction
    original_input = user_input
    
    # Find the action using preprocessed input
    action = find_best_action(user_input)
    if not action:
        return None, None, None
    
    # Handle different command types
    
    # WHERE AM I / CURRENT LOCATION
    if action == "where":
        return "where", None, None
    
    # GO BACK
    if action == "back":
        return "back", None, None
    
    # NAVIGATION COMMANDS
    if action == "navigate":
        location = extract_location(user_input)
        if location:
            return "navigate", location, None
        else:
            return None, None, None
    
    # LIST COMMANDS
    if action == "list":
        has_target = find_target_word(user_input)
        if has_target:
            # Determine if listing files or folders
            if "file" in user_input.lower():
                return "list files", None, None
            elif "folder" in user_input.lower() or "director" in user_input.lower():
                return "list folders", None, None
            else:
                return "list all", None, None
        else:
            # Default to listing main folders if no target specified
            return "list main", None, None
    
    # SEARCH COMMANDS
    if action == "search":
        name = extract_name(user_input, action)
        if name:
            # Check if recursive search is requested
            recursive = any(word in user_input.lower() for word in ["everywhere", "all", "recursive", "subfolder"])
            return "search files", name, recursive
        else:
            return None, None, None
    
    # RENAME COMMANDS
    if action == "rename":
        old_name, new_name = extract_two_names(user_input)
        if old_name and new_name:
            return "rename file", old_name, new_name
        else:
            return None, None, None
    
    # MOVE COMMANDS
    if action == "move":
        file_name = extract_name(user_input, action)
        location = extract_location(user_input)
        if file_name and location:
            return "move file", file_name, location
        else:
            return None, None, None
    
    # CREATE COMMANDS
    if action == "create":
        has_target = find_target_word(user_input)
        name = extract_name(user_input, action)
        location = extract_location(user_input)
        
        if name:
            if "file" in user_input.lower() or "." in name:
                return "create file", name, location
            else:
                return "create folder", name, location
        else:
            return None, None, None
    
    # DELETE COMMANDS
    if action == "delete":
        has_target = find_target_word(user_input)
        name = extract_name(user_input, action)
        
        if name:
            if "file" in user_input.lower() or "." in name:
                return "delete file", name, None
            else:
                return "delete folder", name, None
        else:
            return None, None, None
    
    # SYSTEM COMMANDS
    
    # CHECK COMMANDS (storage, internet, etc.)
    if action == "check":
        system_target = find_system_word(user_input)
        if system_target:
            if system_target in ["storage", "disk", "space"]:
                return "check storage", None, None
            elif system_target in ["internet", "speed"]:
                return "check internet", None, None
            elif system_target in ["processes", "process"]:
                return "list processes", None, None
            elif system_target == "system":
                return "system info", None, None
        return None, None, None
    
    # CONNECT COMMANDS (WiFi)
    if action == "connect":
        if "wifi" in user_input.lower() or "network" in user_input.lower():
            network_name = extract_name(user_input, action)
            return "connect wifi", network_name, None
        return None, None, None
    
    # ADJUST COMMANDS (volume)
    if action == "adjust":
        if "volume" in user_input.lower() or "sound" in user_input.lower():
            # Extract volume level or action
            words = user_input.lower().split()
            for word in words:
                if word.isdigit():
                    return "adjust volume", int(word), None
                elif word in ["mute", "unmute"]:
                    return "adjust volume", None, word
            return "get volume", None, None
        return None, None, None
    
    # TAKE COMMANDS (screenshot)
    if action == "take":
        if "screenshot" in user_input.lower() or "screen" in user_input.lower():
            filename = extract_name(user_input, action)
            return "take screenshot", filename, None
        return None, None, None
    
    # KILL COMMANDS (processes)
    if action == "kill":
        if "process" in user_input.lower():
            process_name = extract_name(user_input, action)
            return "kill process", process_name, None
        return None, None, None
    
    # SHUTDOWN COMMANDS
    if action == "shutdown":
        # Extract delay if specified
        words = user_input.lower().split()
        for i, word in enumerate(words):
            if word.isdigit():
                return "shutdown", int(word), None
            elif word in ["in", "after"] and i + 1 < len(words) and words[i + 1].isdigit():
                return "shutdown", int(words[i + 1]), None
        return "shutdown", 0, None
    
    # RESTART COMMANDS
    if action == "restart":
        # Extract delay if specified
        words = user_input.lower().split()
        for i, word in enumerate(words):
            if word.isdigit():
                return "restart", int(word), None
            elif word in ["in", "after"] and i + 1 < len(words) and words[i + 1].isdigit():
                return "restart", int(words[i + 1]), None
        return "restart", 0, None
    
    # CANCEL COMMANDS
    if action == "cancel":
        if "shutdown" in user_input.lower() or "restart" in user_input.lower():
            return "cancel shutdown", None, None
        return None, None, None
    
    # BROWSER COMMANDS
    if action == "open":
        browser_target = find_browser_word(user_input)
        if browser_target:
            # Determine browser and site
            browsers = ["firefox", "chrome", "edge"]
            sites = ["gmail", "google", "youtube", "facebook", "twitter", "linkedin", "github", "stackoverflow"]
            
            browser = "default"
            site = None
            
            # Find browser
            for b in browsers:
                if b in user_input.lower():
                    browser = b
                    break
            
            # Find site
            for s in sites:
                if s in user_input.lower():
                    site = s
                    break
            
            if site:
                return "open browser site", browser, site
            elif browser_target in browsers:
                return "open browser", browser_target, None
            else:
                return "open browser site", browser, browser_target
        return None, None, None
    
    if action == "close":
        browser_target = find_browser_word(user_input)
        if browser_target and browser_target in ["browser", "firefox", "chrome", "edge"]:
            return "close browser", browser_target, None
        return None, None, None
    
    # DOCUMENT COMMANDS
    if action == "create":
        doc_target = find_document_word(user_input)
        if doc_target and doc_target in ["document", "word", "docx"]:
            name = extract_name(user_input, action)
            return "create document", name, None
        # Fall through to existing create logic if not document
    
    if action == "open":
        doc_target = find_document_word(user_input)
        if doc_target:
            filename = extract_name(user_input, action)
            if filename:
                return "open document", filename, None
        # Fall through to existing open logic if not document
    
    if action == "convert":
        if "docx" in user_input.lower() and "pdf" in user_input.lower():
            filename = extract_name(user_input, action)
            if "to pdf" in user_input.lower():
                return "convert docx pdf", filename, None
            elif "to docx" in user_input.lower():
                return "convert pdf docx", filename, None
        return None, None, None
    
    if action == "search":
        doc_target = find_document_word(user_input)
        if doc_target:
            # Extract search term and filename
            words = user_input.lower().split()
            search_term = None
            filename = None
            
            # Look for "search for X in Y" pattern
            if "for" in words and "in" in words:
                for_idx = words.index("for")
                in_idx = words.index("in")
                if for_idx < in_idx:
                    search_term = " ".join(words[for_idx + 1:in_idx])
                    filename = " ".join(words[in_idx + 1:])
            
            if search_term and filename:
                return "search document", search_term, filename
        # Fall through to existing search logic if not document search
    
    if action == "extract":
        doc_target = find_document_word(user_input)
        if doc_target:
            filename = extract_name(user_input, action)
            if filename:
                return "extract text", filename, None
        return None, None, None
    
    if action == "summarize":
        doc_target = find_document_word(user_input)
        if doc_target:
            filename = extract_name(user_input, action)
            if filename:
                return "summarize document", filename, None
        return None, None, None
    
    if action == "list":
        doc_target = find_document_word(user_input)
        if doc_target:
            return "list documents", None, None
        # Fall through to existing list logic if not document list
    
    # ==================== NEW ENHANCED FEATURES ====================
    
    # BRIGHTNESS CONTROL
    if action == "adjust" and "brightness" in user_input.lower():
        if "increase" in user_input.lower():
            return "brightness increase", None, None
        elif "decrease" in user_input.lower():
            return "brightness decrease", None, None
        else:
            # Extract brightness level
            words = user_input.lower().split()
            for word in words:
                if word.isdigit():
                    return "brightness set", int(word), None
        return "brightness get", None, None
    
    # LOCK/LOGOUT COMMANDS
    if action == "lock":
        if "computer" in user_input.lower() or "screen" in user_input.lower():
            return "lock computer", None, None
    
    if action == "logout":
        return "logout user", None, None
    
    # BATTERY COMMANDS
    if action == "check" and "battery" in user_input.lower():
        return "battery status", None, None
    
    if action == "optimize" and "battery" in user_input.lower():
        return "battery optimize", None, None
    
    # CPU MONITORING
    if action == "monitor" and "cpu" in user_input.lower():
        return "monitor cpu", None, None
    
    if action == "check" and ("frozen" in user_input.lower() or "stuck" in user_input.lower()):
        return "detect frozen", None, None
    
    # POWER SAVING
    if "power" in user_input.lower() and "saving" in user_input.lower():
        return "power saving", None, None
    
    # APPLICATION LAUNCHER
    if action == "open" or action == "launch":
        app_target = find_app_word(user_input)
        if app_target:
            return "launch app", app_target, None
        
        # Check for camera
        if "camera" in user_input.lower():
            return "open camera", None, None
    
    if action == "list" and ("apps" in user_input.lower() or "applications" in user_input.lower()):
        if "recent" in user_input.lower():
            return "list recent apps", None, None
        else:
            return "list available apps", None, None
    
    if "recent" in user_input.lower() and "files" in user_input.lower():
        return "open recent files", None, None
    
    if "morning" in user_input.lower() and ("apps" in user_input.lower() or "routine" in user_input.lower()):
        return "launch morning apps", None, None
    
    if "work" in user_input.lower() and ("apps" in user_input.lower() or "routine" in user_input.lower()):
        return "launch work apps", None, None
    
    # FILE ORGANIZATION
    if action == "organize":
        if "files" in user_input.lower():
            return "organize files", extract_location(user_input), None
        elif "desktop" in user_input.lower():
            return "organize files", "desktop", None
        elif "downloads" in user_input.lower():
            return "organize files", "downloads", None
    
    if action == "rename" and "pattern" in user_input.lower():
        # Extract directory and patterns
        return "rename pattern", extract_location(user_input), extract_name(user_input, action)
    
    # DUPLICATE FILES
    if action == "find" and "duplicates" in user_input.lower():
        return "find duplicates", extract_location(user_input), None
    
    # LARGE FILES
    if action == "find" and "large" in user_input.lower():
        return "find large files", extract_location(user_input), None
    
    # UNUSED FILES
    if action == "find" and "unused" in user_input.lower():
        return "find unused files", extract_location(user_input), None
    
    # COMPRESSION
    if action == "compress":
        return "compress folder", extract_location(user_input), None
    
    if action == "extract":
        return "extract archive", extract_name(user_input, action), None
    
    # NATURAL LANGUAGE SEARCH
    if action == "search" or action == "find":
        # Check if it's a natural language query
        if any(word in user_input.lower() for word in ["about", "pdf", "image", "photo", "document", "video"]):
            return "smart search", user_input, None
    
    # BACKUP
    if action == "backup":
        return "backup files", extract_location(user_input), None
    
    if action == "list" and "backup" in user_input.lower():
        return "list backups", None, None
    
    # SECURITY & CLEANUP
    if action == "scan":
        if "security" in user_input.lower() or "virus" in user_input.lower() or "threats" in user_input.lower():
            quick = "quick" in user_input.lower()
            return "security scan", quick, None
    
    if action == "clean":
        if "computer" in user_input.lower() or "system" in user_input.lower():
            deep = "deep" in user_input.lower()
            return "clean system", deep, None
    
    if action == "check" and "bloatware" in user_input.lower():
        return "check bloatware", None, None
    
    if action == "optimize" and ("startup" in user_input.lower() or "boot" in user_input.lower()):
        return "optimize startup", None, None
    
    if action == "list" and "cleanup" in user_input.lower():
        return "cleanup history", None, None
    
    # PERSONALIZATION
    if action == "create" and "shortcut" in user_input.lower():
        # Extract shortcut name and command
        words = user_input.split()
        try:
            shortcut_idx = next(i for i, word in enumerate(words) if "shortcut" in word.lower())
            if shortcut_idx + 1 < len(words):
                shortcut_name = words[shortcut_idx + 1]
                command = " ".join(words[shortcut_idx + 2:]) if shortcut_idx + 2 < len(words) else None
                return "create shortcut", shortcut_name, command
        except:
            pass
    
    if action == "list" and "shortcuts" in user_input.lower():
        return "list shortcuts", None, None
    
    if action == "suggest":
        if "commands" in user_input.lower():
            return "suggest commands", None, None
        elif "apps" in user_input.lower():
            return "suggest apps", None, None
    
    if action == "create" and "workflow" in user_input.lower():
        return "create workflow", extract_name(user_input, action), None
    
    if action == "list" and "workflows" in user_input.lower():
        return "list workflows", None, None
    
    if "run workflow" in user_input.lower():
        return "run workflow", extract_name(user_input, "run"), None
    
    if action == "list" and ("favorites" in user_input.lower() or "favourite" in user_input.lower()):
        return "list favorites", None, None
    
    if "add favorite" in user_input.lower():
        return "add favorite", extract_location(user_input), None
    
    if action == "list" and "stats" in user_input.lower():
        return "usage stats", None, None
    
    if "export data" in user_input.lower():
        return "export data", None, None
    
    # EMAIL AUTOMATION
    if action == "setup" and "email" in user_input.lower():
        return "setup email", None, None
    
    if action == "send" and ("email" in user_input.lower() or "mail" in user_input.lower()):
        if "file" in user_input.lower():
            return "send file email", None, None
        elif "template" in user_input.lower():
            return "send template email", None, None
        else:
            return "send email", None, None
    
    if action == "list" and ("templates" in user_input.lower() or "email" in user_input.lower()):
        return "list email templates", None, None
    
    if action == "check" and "email" in user_input.lower():
        return "email status", None, None
    
    # ==================== CROSS-APP WORKFLOWS ====================
    
    if "screenshot" in user_input.lower() and ("share" in user_input.lower() or "upload" in user_input.lower()):
        return "screenshot share", None, None
    
    if "video" in user_input.lower() and "transcribe" in user_input.lower():
        # Extract URL if provided
        words = user_input.split()
        url = None
        for word in words:
            if "http" in word or "youtube" in word or "youtu.be" in word:
                url = word
                break
        return "video transcribe", url, None
    
    if "invoice" in user_input.lower() and ("process" in user_input.lower() or "extract" in user_input.lower()):
        return "process invoices", None, None
    
    if "monitor" in user_input.lower() and "pdf" in user_input.lower():
        folder = extract_location(user_input)
        return "monitor pdf", folder, None
    
    if action == "run" and "workflow" in user_input.lower():
        workflow_name = extract_name(user_input, "run")
        return "run workflow", workflow_name, None
    
    if action == "list" and "workflow" in user_input.lower():
        return "list workflows", None, None
    
    # ==================== DEVELOPER TOOLS ====================
    
    if "clone" in user_input.lower() and ("setup" in user_input.lower() or "repo" in user_input.lower()):
        # Extract repo URL
        words = user_input.split()
        repo_url = None
        project_name = None
        
        for word in words:
            if "github.com" in word or "gitlab.com" in word or ".git" in word:
                repo_url = word
            elif word not in get_all_reserved_words() and len(word) > 2 and not repo_url:
                project_name = word
        
        return "clone setup", repo_url, project_name
    
    if action == "find" and "todo" in user_input.lower():
        project_path = extract_location(user_input)
        return "find todos", project_path, None
    
    if action == "run" and "test" in user_input.lower():
        project_path = extract_location(user_input)
        return "run tests", project_path, None
    
    if "commit" in user_input.lower() and "message" in user_input.lower():
        project_path = extract_location(user_input)
        return "commit message", project_path, None
    
    if "deploy" in user_input.lower() and ("production" in user_input.lower() or "prod" in user_input.lower()):
        project_path = extract_location(user_input)
        platform = None
        if "vercel" in user_input.lower():
            platform = "vercel"
        elif "heroku" in user_input.lower():
            platform = "heroku"
        elif "netlify" in user_input.lower():
            platform = "netlify"
        return "deploy production", project_path, platform
    
    if action == "list" and ("project" in user_input.lower() or "repo" in user_input.lower()):
        return "list projects", None, None
    
    if "terminal" in user_input.lower() or "execute" in user_input.lower():
        # Extract command after "execute" or "terminal"
        words = user_input.split()
        if "execute" in words:
            idx = words.index("execute")
            if idx + 1 < len(words):
                command = " ".join(words[idx + 1:])
                return "execute terminal", command, None
        elif "terminal" in words:
            idx = words.index("terminal")
            if idx + 1 < len(words):
                command = " ".join(words[idx + 1:])
                return "execute terminal", command, None
    
    # ==================== ADVANCED CONTEXT MEMORY ====================
    
    if "what was i doing" in user_input.lower() or "what doing" in user_input.lower():
        time_ref = "before lunch"  # default
        if "morning" in user_input.lower():
            time_ref = "morning"
        elif "yesterday" in user_input.lower():
            time_ref = "yesterday"
        elif "hour" in user_input.lower():
            time_ref = "hour ago"
        return "what doing", time_ref, None
    
    if "continue where" in user_input.lower() or "continue session" in user_input.lower():
        return "continue session", None, None
    
    if "find" in user_input.lower() and "project" in user_input.lower() and "related" in user_input.lower():
        project_name = extract_name(user_input, "find")
        return "find project files", project_name, None
    
    if "search entire" in user_input.lower() or "search system" in user_input.lower():
        query = extract_name(user_input, "search")
        return "search system", query, None
    
    if "context" in user_input.lower() and "summary" in user_input.lower():
        return "context summary", None, None
    
    # ==================== SAFETY NET & UNDO ====================
    
    if "undo" in user_input.lower():
        if "last" in user_input.lower():
            return "undo last", None, None
        elif "hour" in user_input.lower():
            # Extract number of hours
            words = user_input.split()
            hours = 1
            for word in words:
                if word.isdigit():
                    hours = int(word)
                    break
            return "undo time", hours, None
        elif "timeline" in user_input.lower():
            return "undo timeline", None, None
    
    if "check" in user_input.lower() and "safe" in user_input.lower():
        file_path = extract_location(user_input)
        return "check safety", file_path, None
    
    # ==================== CITATION GENERATOR ====================
    
    if "citation" in user_input.lower() or "cite" in user_input.lower():
        if "generate" in user_input.lower() or "create" in user_input.lower():
            # Extract file path or URL
            words = user_input.split()
            source = None
            style = None
            
            for word in words:
                if word.lower().endswith('.pdf') or word.startswith('http'):
                    source = word
                elif word.lower() in ['apa', 'mla', 'chicago', 'harvard', 'ieee']:
                    style = word.lower()
            
            if not source:
                source = extract_location(user_input)
            
            return "generate citation", source, style
        
        elif "history" in user_input.lower():
            return "citation history", None, None
    
    # ==================== AUTOMATED DATA ENTRY ====================
    
    if "receipt" in user_input.lower() and ("process" in user_input.lower() or "extract" in user_input.lower()):
        image_path = extract_location(user_input)
        output_path = None
        
        # Check if output path is specified
        if "to" in user_input.lower():
            words = user_input.split()
            to_index = -1
            for i, word in enumerate(words):
                if word.lower() == "to":
                    to_index = i
                    break
            
            if to_index != -1 and to_index + 1 < len(words):
                output_path = words[to_index + 1]
        
        return "process receipt", image_path, output_path
    
    if "pdf" in user_input.lower() and "table" in user_input.lower() and ("extract" in user_input.lower() or "convert" in user_input.lower()):
        pdf_path = extract_location(user_input)
        output_path = None
        
        # Check if output path is specified
        if "to" in user_input.lower():
            words = user_input.split()
            to_index = -1
            for i, word in enumerate(words):
                if word.lower() == "to":
                    to_index = i
                    break
            
            if to_index != -1 and to_index + 1 < len(words):
                output_path = words[to_index + 1]
        
        return "process pdf table", pdf_path, output_path
    
    if "business card" in user_input.lower() and ("process" in user_input.lower() or "extract" in user_input.lower()):
        folder_path = extract_location(user_input)
        output_path = None
        
        # Check if output path is specified
        if "to" in user_input.lower():
            words = user_input.split()
            to_index = -1
            for i, word in enumerate(words):
                if word.lower() == "to":
                    to_index = i
                    break
            
            if to_index != -1 and to_index + 1 < len(words):
                output_path = words[to_index + 1]
        
        return "process business cards", folder_path, output_path
    
    if "data" in user_input.lower() and ("history" in user_input.lower() or "processing" in user_input.lower()):
        return "data processing history", None, None
    
    # ==================== PREMIUM SEARCH - FIND MY LOST FILE ====================
    
    if "find" in user_input.lower() and ("lost" in user_input.lower() or "missing" in user_input.lower() or "where is" in user_input.lower()):
        # Extract file description
        description = user_input.lower()
        # Remove command words
        for word in ["find", "lost", "missing", "where", "is", "my", "the"]:
            description = description.replace(word, "")
        description = description.strip()
        
        return "find lost file", description, None
    
    if "find files" in user_input.lower() and ("date" in user_input.lower() or "yesterday" in user_input.lower() or "tuesday" in user_input.lower() or "last week" in user_input.lower()):
        # Extract date description
        date_words = ["yesterday", "last tuesday", "last week", "this morning", "last month"]
        date_desc = None
        
        for date_word in date_words:
            if date_word in user_input.lower():
                date_desc = date_word
                break
        
        if not date_desc:
            date_desc = extract_name(user_input, "find")
        
        return "find files by date", date_desc, None
    
    if "find" in user_input.lower() and ("content" in user_input.lower() or "contains" in user_input.lower() or "mentioned" in user_input.lower()):
        content_desc = extract_name(user_input, "find")
        return "find file content", content_desc, None
    
    if "index" in user_input.lower() and "files" in user_input.lower():
        return "index files", None, None
    
    # ==================== DISASTER RECOVERY - UNDO DISASTER ====================
    
    if "undo" in user_input.lower() and ("disaster" in user_input.lower() or "everything" in user_input.lower() or "last action" in user_input.lower()):
        return "undo disaster", None, None
    
    if "undo" in user_input.lower() and ("from" in user_input.lower() or "minutes" in user_input.lower() or "time" in user_input.lower()):
        # Extract time period
        words = user_input.split()
        minutes = 30  # default
        
        for i, word in enumerate(words):
            if word.isdigit():
                minutes = int(word)
                break
            elif word in ["hour", "hours"]:
                if i > 0 and words[i-1].isdigit():
                    minutes = int(words[i-1]) * 60
                else:
                    minutes = 60
                break
        
        return "undo from time", str(minutes), None
    
    if "disaster" in user_input.lower() and "timeline" in user_input.lower():
        hours = 24
        words = user_input.split()
        for word in words:
            if word.isdigit():
                hours = int(word)
                break
        
        return "disaster timeline", str(hours), None
    
    if "find" in user_input.lower() and "deleted" in user_input.lower():
        days = 7
        words = user_input.split()
        for word in words:
            if word.isdigit():
                days = int(word)
                break
        
        return "find deleted files", str(days), None
    
    if "create" in user_input.lower() and "checkpoint" in user_input.lower():
        description = extract_name(user_input, "create")
        return "create checkpoint", description, None
    
    if "recovery" in user_input.lower() and ("stats" in user_input.lower() or "statistics" in user_input.lower()):
        return "recovery stats", None, None
    
    # ==================== DUPLICATE DESTROYER - RECLAIM STORAGE ====================
    
    if "scan" in user_input.lower() and "duplicate" in user_input.lower():
        return "scan duplicates", None, None
    
    if "show" in user_input.lower() and "duplicate" in user_input.lower():
        limit = 10
        words = user_input.split()
        for word in words:
            if word.isdigit():
                limit = int(word)
                break
        
        return "show duplicates", str(limit), None
    
    if "delete" in user_input.lower() and "duplicate" in user_input.lower():
        strategy = "newest"  # default
        if "oldest" in user_input.lower():
            strategy = "oldest"
        elif "shortest" in user_input.lower():
            strategy = "shortest_path"
        
        return "delete duplicates", strategy, None
    
    if "duplicate" in user_input.lower() and "download" in user_input.lower():
        return "duplicate downloads", None, None
    
    if "duplicate" in user_input.lower() and ("photo" in user_input.lower() or "image" in user_input.lower()):
        return "duplicate photos", None, None
    
    if "storage" in user_input.lower() and ("analysis" in user_input.lower() or "analyze" in user_input.lower()):
        return "storage analysis", None, None
    
    # ==================== SYSTEM OPTIMIZER - FIX MY SLOW COMPUTER ====================
    
    if "diagnose" in user_input.lower() or ("why" in user_input.lower() and "slow" in user_input.lower()):
        return "diagnose computer", None, None
    
    if "fix" in user_input.lower() and ("computer" in user_input.lower() or "everything" in user_input.lower() or "slow" in user_input.lower()):
        return "fix computer", None, None
    
    if "performance" in user_input.lower() and "report" in user_input.lower():
        return "performance report", None, None
    
    if "optimization" in user_input.lower() and "history" in user_input.lower():
        return "optimization history", None, None
    
    # ==================== FILE ENCRYPTION BUTLER - PREMIUM SECURITY ====================
    
    if "lock" in user_input.lower() and "folder" in user_input.lower():
        # Extract folder path and password
        folder_path = extract_location(user_input)
        
        # For security, password should be prompted separately in production
        # For demo, we'll extract from command if provided
        words = user_input.split()
        password = None
        
        # Look for password after "password" keyword
        if "password" in user_input.lower():
            password_index = -1
            for i, word in enumerate(words):
                if word.lower() == "password":
                    password_index = i
                    break
            
            if password_index != -1 and password_index + 1 < len(words):
                password = words[password_index + 1]
        
        return "lock folder", folder_path, password
    
    if "create" in user_input.lower() and ("vault" in user_input.lower() or "secure" in user_input.lower()):
        vault_name = extract_name(user_input, "create")
        
        # Extract password if provided
        words = user_input.split()
        password = None
        
        if "password" in user_input.lower():
            password_index = -1
            for i, word in enumerate(words):
                if word.lower() == "password":
                    password_index = i
                    break
            
            if password_index != -1 and password_index + 1 < len(words):
                password = words[password_index + 1]
        
        return "create vault", vault_name, password
    
    if "unlock" in user_input.lower() and "vault" in user_input.lower():
        vault_name = extract_name(user_input, "unlock")
        
        # Extract password if provided
        words = user_input.split()
        password = None
        
        if "password" in user_input.lower():
            password_index = -1
            for i, word in enumerate(words):
                if word.lower() == "password":
                    password_index = i
                    break
            
            if password_index != -1 and password_index + 1 < len(words):
                password = words[password_index + 1]
        
        return "unlock vault", vault_name, password
    
    if "add" in user_input.lower() and "vault" in user_input.lower():
        file_path = extract_location(user_input)
        vault_name = extract_name(user_input, "vault")
        
        return "add to vault", file_path, vault_name
    
    if "list" in user_input.lower() and ("vault" in user_input.lower() or "secure" in user_input.lower()):
        return "list vaults", None, None
    
    if "encryption" in user_input.lower() and ("stats" in user_input.lower() or "statistics" in user_input.lower()):
        return "encryption stats", None, None
    
    if "auto" in user_input.lower() and ("encrypt" in user_input.lower() or "encryption" in user_input.lower()):
        return "auto encrypt", None, None
    
    return None, None, None