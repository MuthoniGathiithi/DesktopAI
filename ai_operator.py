import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
from folder_ops import *
from system_ops import *
from browser_ops import *
from document_ops import *
from nlp_parser import parse_command

# Import new enhanced modules
try:
    from app_launcher import *
    from advanced_file_ops import *
    from security_cleanup import *
    from personalization import *
    from email_automation import *
    from context_memory import *
    from safety_net import *
    from cross_app_workflows import *
    from developer_tools import *
    from citation_generator import *
    from automated_data_entry import *
    from premium_search import *
    from disaster_recovery import *
    from duplicate_destroyer import *
    from system_optimizer import *
    from file_encryption_butler import *
except ImportError as e:
    print(f"Warning: Could not import enhanced modules: {e}")

def get_system_capabilities():
    """Return a comprehensive numbered list of system capabilities"""
    return """🤖 Desktop AI System Capabilities

WHAT CAN I DO FOR YOU?

📁 FILE & FOLDER MANAGEMENT:
1. Create folders and files anywhere
2. Delete, move, and rename files/folders
3. List and navigate through directories
4. Search files by name or content
5. Organize files automatically by type
6. Rename multiple files with patterns
7. Find and remove duplicate files
8. Detect large files eating up space
9. Find unused files (not accessed in months)
10. Compress folders into ZIP/TAR archives
11. Extract files from archives
12. Create automated backups with history
13. Smart file search using natural language

🌐 BROWSER & WEB:
14. Open any browser (Chrome, Firefox, Edge)
15. Navigate to websites automatically
16. Quick access to Gmail, YouTube, social media
17. Manage multiple browser windows

📄 DOCUMENT OPERATIONS:
18. Create Word documents with content
19. Convert between DOCX and PDF formats
20. Search text inside documents
21. Extract text from PDFs and documents
22. Summarize document content
23. List all documents with metadata

💻 SYSTEM CONTROL:
24. Check disk storage usage
25. Monitor internet speed and connectivity
26. Adjust system volume (mute/unmute/set level)
27. Control screen brightness
28. Take screenshots automatically
29. Lock computer and logout user
30. Shutdown/restart with timer options
31. Connect to WiFi networks
32. Monitor CPU usage with alerts
33. Detect and kill frozen applications
34. Check battery status and health
35. Enable power saving modes
36. List and terminate running processes

🚀 APPLICATION MANAGEMENT:
37. Launch any application (VS Code, Office, etc.)
38. Open camera applications
39. Track recently used applications
40. Smart app suggestions based on time
41. Launch morning/work app routines
42. Open recent files in applications
43. Learn your app usage patterns

🔒 SECURITY & CLEANUP:
44. Scan for security threats and malware
45. Clean junk files and system cache
46. Remove browser cache for privacy
47. Detect and suggest bloatware removal
48. Optimize startup programs
49. Clean temporary files automatically
50. Empty trash/recycle bin
51. Track cleanup history

🎯 PERSONALIZATION & LEARNING:
52. Create custom command shortcuts
53. Learn your usage patterns and habits
54. Suggest commands based on time/context
55. Create and run custom workflows
56. Remember your favorite locations
57. Track usage statistics
58. Export/import your preferences
59. Adapt to your working style

📧 EMAIL AUTOMATION:
60. Setup email with major providers
61. Send emails with attachments
62. Use email templates for common messages
63. Share files via email automatically
64. Quick messaging with minimal setup

🧠 SMART FEATURES:
65. Understand natural language commands
66. Handle typos and misspellings
67. Remember your location in file system
68. Provide context-aware suggestions
69. Learn from your behavior
70. Cross-platform compatibility (Windows/Linux/Mac)

💬 NATURAL LANGUAGE EXAMPLES:
- "Hey, can you make me a folder called Projects?"
- "I want to organize my desktop files"
- "Find me that PDF about artificial intelligence"
- "Can you clean up my computer?"
- "Show me my recent applications"
- "Help me backup my documents"
- "What's eating up my disk space?"
- "Launch my morning work apps"

Just ask me naturally - I understand conversational language!
Type "help" for command examples or just tell me what you want to do."""

def execute_command():
    user_input = command_entry.get()
    command, param1, param2 = parse_command(user_input)

    if not command:
        messagebox.showwarning("Not understood", "I didn't understand that command.")
        return
    
    try:
        # Navigation commands
        if command == "navigate":
            result = navigate_to(param1)
        elif command == "back":
            result = go_back()
        elif command == "where":
            result = get_current_location()
        
        # List commands
        elif command == "list main":
            folders = list_main_folders()
            result = f"Main folders:\n" + "\n".join(folders)
        elif command == "list folders":
            folders = list_folders()
            if isinstance(folders, list):
                result = f"Folders:\n" + "\n".join(folders)
            else:
                result = folders
        elif command == "list files":
            files = list_files()
            if isinstance(files, list):
                result = f"Files:\n" + "\n".join(files)
            else:
                result = files
        elif command == "list all":
            items = list_all()
            if isinstance(items, list):
                result = f"Contents:\n" + "\n".join(items)
            else:
                result = items
        
        # Create commands
        elif command == "create folder":
            result = create_folder(param1, param2)
        elif command == "create file":
            result = create_file(param1, "", param2)
        
        # Delete commands
        elif command == "delete folder":
            result = delete_folder(param1)
        elif command == "delete file":
            result = delete_file(param1)
        
        # File operations
        elif command == "move file":
            result = move_file(param1, param2)
        elif command == "rename file":
            result = rename_file(param1, param2)
        elif command == "search files system":
            # System-wide search (may require permissions) — uses direct filesystem scan
            try:
                # Use AI smart search first if available; provides ranking and context boosts
                try:
                    ai_results = find_files_smart(param1, max_results=1000)
                    if ai_results:
                        # ai_results is list of (path, score) or paths depending on wrapper
                        if all(isinstance(x, tuple) for x in ai_results):
                            results = [p for p, s in ai_results]
                        else:
                            results = ai_results
                    else:
                        results = find_files_direct(param1, max_results=1000)
                except Exception:
                    results = find_files_direct(param1, max_results=1000)
                if not results:
                    result = f"No files found matching '{param1}' across the system"
                else:
                    # Trim output to avoid huge responses
                    shown = results[:250]
                    result = f"System-wide search found {len(results)} matches (showing {len(shown)}):\n" + "\n".join(shown)
            except Exception as e:
                result = f"Error performing system-wide search: {e}"

        elif command == "search files":
            files = search_files(param1, param2 if param2 else False)

            # If the local search returns a message (no matches) and the user asked
            # for a recursive or system-wide search, automatically escalate to a
            # direct system-level scan (safe-limited) so the assistant is smarter.
            if isinstance(files, list):
                result = f"Found files matching '{param1}':\n" + "\n".join(files)
            else:
                # files is a message (no matches) — escalate when recursive requested
                lower_msg = str(files).lower()
                if param2:
                    try:
                        # Try AI smart search when local search returned no matches
                        ai_results = find_files_smart(param1, max_results=500)
                        if ai_results:
                            if all(isinstance(x, tuple) for x in ai_results):
                                results = [p for p, s in ai_results]
                            else:
                                results = ai_results
                        else:
                            results = find_files_direct(param1, max_results=500)

                        if results:
                            shown = results[:200]
                            result = f"No local matches; performed a system-wide scan and found {len(results)} matches (showing {len(shown)}):\n" + "\n".join(shown)
                        else:
                            result = files
                    except Exception as e:
                        result = f"No local matches and system-wide scan failed: {e}"
                else:
                    result = files
        
        # System operations
        elif command == "check storage":
            result = check_storage()
        elif command == "check internet":
            result = check_internet_speed()
        elif command == "connect wifi":
            if param1:
                result = connect_wifi(param1)
            else:
                result = get_wifi_info()
        elif command == "adjust volume":
            if param1 is not None:
                result = adjust_volume(param1)
            elif param2:
                result = adjust_volume(action=param2)
            else:
                result = "Please specify volume level (0-100) or action (mute/unmute)"
        elif command == "get volume":
            result = get_volume()
        elif command == "take screenshot":
            result = take_screenshot(param1)
        elif command == "list processes":
            result = list_processes()
        elif command == "kill process":
            if param1:
                result = kill_process(param1)
            else:
                result = "Please specify process name or PID to kill"
        elif command == "shutdown":
            result = shutdown_system(param1 if param1 else 0)
        elif command == "restart":
            result = restart_system(param1 if param1 else 0)
        elif command == "cancel shutdown":
            result = cancel_shutdown()
        elif command == "system info":
            result = get_system_info()
        
        # Browser operations
        elif command == "open browser":
            result = open_browser(param1 if param1 else "default")
        elif command == "open browser site":
            result = open_browser_with_interface(param1 if param1 else "firefox", param2 if param2 else "gmail")
        elif command == "close browser":
            result = close_browser(param1 if param1 else "all")
        elif command == "list browsers":
            result = list_browsers()
        
        # Document operations
        elif command == "create document":
            result = create_word_document(param1)
        elif command == "open document":
            if param1:
                result = open_word_document(param1)
            else:
                result = "Please specify document filename"
        elif command == "convert docx pdf":
            if param1:
                result = convert_docx_to_pdf(param1)
            else:
                result = "Please specify DOCX filename"
        elif command == "convert pdf docx":
            if param1:
                result = convert_pdf_to_docx(param1)
            else:
                result = "Please specify PDF filename"
        elif command == "search document":
            if param1 and param2:
                result = search_text_in_document(param2, param1)
            else:
                result = "Please specify search term and document filename"
        elif command == "extract text":
            if param1:
                file_ext = param1.lower().split('.')[-1] if '.' in param1 else ''
                if file_ext == 'docx':
                    result = extract_text_from_docx(param1)
                elif file_ext == 'pdf':
                    result = extract_text_from_pdf(param1)
                else:
                    result = "Unsupported file format. Use .docx or .pdf files"
            else:
                result = "Please specify document filename"
        elif command == "summarize document":
            if param1:
                result = summarize_document(param1)
            else:
                result = "Please specify document filename"
        elif command == "list documents":
            result = list_documents()
        elif command == "check dependencies":
            result = check_dependencies()
        
        # ==================== NEW ENHANCED FEATURES ====================
        
        # BRIGHTNESS CONTROL
        elif command == "brightness increase":
            result = adjust_brightness(action="increase")
        elif command == "brightness decrease":
            result = adjust_brightness(action="decrease")
        elif command == "brightness set":
            result = adjust_brightness(level=param1)
        elif command == "brightness get":
            result = get_brightness()
        
        # LOCK/LOGOUT
        elif command == "lock computer":
            result = lock_computer()
        elif command == "logout user":
            result = logout_user()
        
        # BATTERY MANAGEMENT
        elif command == "battery status":
            result = get_battery_status()
        elif command == "battery optimize":
            result = optimize_battery()
        elif command == "power saving":
            result = enable_power_saving()
        
        # CPU MONITORING
        elif command == "monitor cpu":
            result = monitor_cpu_usage()
        elif command == "detect frozen":
            result = detect_frozen_apps()
        
        # APPLICATION LAUNCHER
        elif command == "launch app":
            if param1:
                result = launch_application(param1)
                learn_user_app_usage(param1)
            else:
                result = "Please specify application name"
        elif command == "open camera":
            result = open_camera()
        elif command == "list recent apps":
            result = get_recent_applications()
        elif command == "list available apps":
            result = list_available_applications()
        elif command == "open recent files":
            result = open_recent_files()
        elif command == "launch morning apps":
            result = launch_morning_routine()
        elif command == "launch work apps":
            result = launch_work_routine()
        
        # FILE ORGANIZATION
        elif command == "organize files":
            location = param1 if param1 else get_current_location()
            result = organize_files(location)
        elif command == "rename pattern":
            if param1 and param2:
                result = rename_files_with_pattern(param1, "*", param2)
            else:
                result = "Please specify directory and new pattern"
        elif command == "find duplicates":
            location = param1 if param1 else get_current_location()
            result = find_duplicates(location)
        elif command == "find large files":
            location = param1 if param1 else get_current_location()
            result = find_large_files(location)
        elif command == "find unused files":
            location = param1 if param1 else get_current_location()
            result = find_unused_files(location)
        elif command == "compress folder":
            if param1:
                result = compress_files(param1)
            else:
                result = "Please specify folder to compress"
        elif command == "extract archive":
            if param1:
                result = extract_files(param1)
            else:
                result = "Please specify archive to extract"
        elif command == "smart search":
            result = smart_file_search(param1)
        elif command == "backup files":
            if param1:
                result = backup_files(param1)
            else:
                result = "Please specify path to backup"
        elif command == "list backups":
            result = get_backup_history()
        
        # SECURITY & CLEANUP
        elif command == "security scan":
            quick_scan = param1 if param1 is not None else True
            result = scan_security_threats(quick_scan)
        elif command == "clean system":
            deep_clean = param1 if param1 is not None else False
            result = clean_computer(deep_clean)
        elif command == "check bloatware":
            result = check_bloatware()
        elif command == "optimize startup":
            result = optimize_computer_startup()
        elif command == "cleanup history":
            result = get_cleanup_history()
        
        # PERSONALIZATION
        elif command == "create shortcut":
            if param1 and param2:
                result = create_user_shortcut(param1, param2)
            else:
                result = "Please specify shortcut name and command"
        elif command == "list shortcuts":
            result = get_user_shortcuts()
        elif command == "suggest commands":
            result = suggest_user_commands()
        elif command == "suggest apps":
            result = suggest_user_apps()
        elif command == "create workflow":
            if param1:
                result = f"Workflow creation for '{param1}' - feature coming soon"
            else:
                result = "Please specify workflow name"
        elif command == "list workflows":
            result = get_user_workflows()
        elif command == "run workflow":
            if param1:
                workflow_commands = run_user_workflow(param1)
                if workflow_commands:
                    result = f"Running workflow '{param1}' with {len(workflow_commands)} commands"
                else:
                    result = f"Workflow '{param1}' not found"
            else:
                result = "Please specify workflow name"
        elif command == "list favorites":
            result = get_user_favorite_locations()
        elif command == "add favorite":
            if param1:
                result = add_user_favorite_location(param1)
            else:
                current_loc = get_current_location()
                result = add_user_favorite_location(current_loc)
        elif command == "usage stats":
            result = get_user_usage_stats()
        elif command == "export data":
            result = export_user_data()
        
        # EMAIL AUTOMATION
        elif command == "setup email":
            result = "Email setup: Use 'setup email <your_email> <app_password>' format"
        elif command == "send email":
            result = "Email sending: Use 'send email <recipient> <subject> <message>' format"
        elif command == "send file email":
            result = "File email: Use 'send file <recipient> <file_path>' format"
        elif command == "send template email":
            result = "Template email: Use 'send template <template_name> <recipient>' format"
        elif command == "list email templates":
            result = get_email_templates()
        elif command == "email status":
            result = get_email_status()
        
        # CROSS-APP WORKFLOWS - THE KILLER FEATURE
        elif command == "run workflow":
            if param1:
                result = run_workflow(param1, {"param2": param2} if param2 else None)
            else:
                result = "Please specify workflow name"
        elif command == "list workflows":
            result = list_available_workflows()
        elif command == "screenshot share":
            result = screenshot_to_share_workflow()
        elif command == "video transcribe":
            if param1:
                result = video_transcribe_workflow(param1)
            else:
                result = "Please provide video URL"
        elif command == "process invoices":
            result = invoice_processing_workflow()
        elif command == "monitor pdf":
            if param1:
                result = pdf_monitor_workflow(param1)
            else:
                result = "Please specify folder to monitor"
        
        # DEVELOPER TOOLS - HIGH-PAYING MARKET
        elif command == "clone setup":
            if param1:
                result = clone_and_setup(param1, param2)
            else:
                result = "Please provide repository URL"
        elif command == "find todos":
            result = find_todos(param1)
        elif command == "run tests":
            result = run_tests_explain_errors(param1)
        elif command == "commit message":
            result = generate_commit_message(param1)
        elif command == "execute terminal":
            if param1:
                result = execute_command(param1)
            else:
                result = "Please provide command to execute"
        elif command == "deploy production":
            result = deploy_project(param1, param2 or "auto")
        elif command == "list projects":
            result = list_dev_projects()
        
        # ADVANCED CONTEXT MEMORY
        elif command == "what doing":
            result = what_was_i_doing(param1 or "before lunch")
        elif command == "continue session":
            result = continue_where_left_off()
        elif command == "find project files":
            if param1:
                result = find_project_files(param1)
            else:
                result = "Please specify project name"
        elif command == "search system":
            if param1:
                result = search_entire_system(param1)
            else:
                result = "Please specify search query"
        elif command == "context summary":
            result = get_context_summary()
        
        # SAFETY NET & UNDO
        elif command == "undo last":
            result = undo_last_action()
        elif command == "undo time":
            hours = param1 if param1 else 1
            result = undo_actions_from_time(hours)
        elif command == "undo timeline":
            result = get_undo_timeline()
        elif command == "check safety":
            if param1:
                safety_check = check_delete_safety([param1])
                if safety_check['safe']:
                    result = "✅ Operation appears safe"
                else:
                    result = "⚠️ Safety warnings:\n" + "\n".join(safety_check['warnings'])
            else:
                result = "Please specify files/folders to check"
        
        # CITATION GENERATOR
        elif command == "generate citation":
            if param1:
                style = param2 if param2 else 'apa'
                if param1.lower().endswith('.pdf'):
                    result = generate_pdf_citation(param1, style)
                elif param1.startswith('http'):
                    result = generate_website_citation(param1, style)
                else:
                    result = "Please provide a PDF file path or website URL"
            else:
                result = "Please specify PDF file or website URL"
        elif command == "citation history":
            result = get_citation_history()
        
        # AUTOMATED DATA ENTRY - BUSINESS GOLD MINE
        elif command == "process receipt":
            if param1:
                result = process_receipt_to_excel(param1, param2)
            else:
                result = "Please provide receipt image path"
        elif command == "process pdf table":
            if param1:
                result = process_pdf_table_to_excel(param1, param2)
            else:
                result = "Please provide PDF file path"
        elif command == "process business cards":
            if param1:
                result = process_business_cards_to_excel(param1, param2)
            else:
                result = "Please provide folder path containing business card images"
        elif command == "data processing history":
            result = get_data_processing_history()
        
        # PREMIUM SEARCH - FIND MY LOST FILE
        elif command == "find lost file":
            if param1:
                result = find_lost_file(param1)
            else:
                result = "Please describe the file you're looking for"
        elif command == "find files by date":
            if param1:
                result = find_files_by_date(param1)
            else:
                result = "Please specify a date (e.g., 'yesterday', 'last Tuesday')"
        elif command == "find file content":
            if param1:
                result = find_file_with_content(param1)
            else:
                result = "Please specify what content to search for"
        elif command == "index files":
            result = index_files_for_search()
        
        # DISASTER RECOVERY - UNDO DISASTER
        elif command == "undo disaster":
            result = undo_last_disaster()
        elif command == "undo from time":
            minutes = int(param1) if param1 and param1.isdigit() else 30
            result = undo_actions_from_minutes(minutes)
        elif command == "disaster timeline":
            hours = int(param1) if param1 and param1.isdigit() else 24
            result = show_disaster_timeline(hours)
        elif command == "find deleted files":
            days = int(param1) if param1 and param1.isdigit() else 7
            result = find_my_deleted_files(days)
        elif command == "create checkpoint":
            description = param1 if param1 else "Manual checkpoint"
            result = create_recovery_checkpoint(description)
        elif command == "recovery stats":
            result = get_disaster_recovery_stats()
        
        # DUPLICATE DESTROYER - RECLAIM STORAGE
        elif command == "scan duplicates":
            result = scan_duplicates(quick_scan=True)
        elif command == "show duplicates":
            limit = int(param1) if param1 and param1.isdigit() else 10
            result = show_duplicates(limit)
        elif command == "delete duplicates":
            strategy = param1 if param1 else 'newest'
            result = delete_duplicates(strategy)
        elif command == "duplicate downloads":
            result = find_duplicate_downloads()
        elif command == "duplicate photos":
            result = find_duplicate_photos()
        elif command == "storage analysis":
            result = analyze_storage()
        
        # SYSTEM OPTIMIZER - FIX MY SLOW COMPUTER
        elif command == "diagnose computer":
            result = diagnose_computer()
        elif command == "fix computer":
            result = fix_computer()
        elif command == "performance report":
            result = get_performance_report()
        elif command == "optimization history":
            result = get_optimization_history()
        
        # FILE ENCRYPTION BUTLER - PREMIUM SECURITY
        elif command == "lock folder":
            if param1 and param2:
                vault_name = None  # Could be extracted from param3 if provided
                result = lock_folder(param1, param2, vault_name)
            else:
                result = "Usage: lock folder <folder_path> <password>"
        elif command == "create vault":
            if param1 and param2:
                result = create_vault(param1, param2)
            else:
                result = "Usage: create vault <vault_name> <password>"
        elif command == "unlock vault":
            if param1 and param2:
                duration = 30  # Default 30 minutes
                result = unlock_vault(param1, param2, duration)
            else:
                result = "Usage: unlock vault <vault_name> <password>"
        elif command == "add to vault":
            if param1 and param2:
                # param1 = file_path, param2 = vault_name, need password prompt
                result = "Please provide password for vault access"
            else:
                result = "Usage: add to vault <file_path> <vault_name>"
        elif command == "list vaults":
            result = list_secure_vaults()
        elif command == "encryption stats":
            result = get_encryption_statistics()
        elif command == "auto encrypt":
            result = "Auto-encryption setup: Use 'setup auto encrypt <rule_name> <pattern_type> <pattern> <vault>'"
        
        # CAPABILITIES LIST
        elif command == "capabilities":
            result = get_system_capabilities()
        
        else:
            result = "Command not implemented."
        
        # Learn from user command (for personalization)
        try:
            learn_user_command(user_input, success=True)
        except:
            pass  # Don't let learning errors break the main functionality
        
        # Update location display
        update_location_display()
        
        # Show result
        show_result(result)
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    # Clear input
    command_entry.delete(0, tk.END)


def smart_search_dialog():
    """GUI helper to prompt for an AI-powered smart search and show results."""
    query = simpledialog.askstring('Smart Search', 'Search for (e.g. \"obed\") — this will use AI ranking and context:')
    if not query:
        return

    try:
        results = find_files_smart(query, max_results=300)
        # normalize results to list of (path, score) pairs
        if not results:
            show_result(f"No results found for '{query}'")
            return

        if all(isinstance(x, tuple) for x in results):
            lines = [f"{i+1}. {p}  (score: {s})" for i, (p, s) in enumerate(results[:200])]
        else:
            # maybe returned list of paths
            lines = [f"{i+1}. {p}" for i, p in enumerate(results[:200])]

        out = f"AI Smart Search results for '{query}':\n\n" + "\n".join(lines)
        show_result(out)
    except Exception as e:
        show_result(f"Smart search failed: {e}")

def show_result(result):
    """Show result in a scrollable text window"""
    result_window = tk.Toplevel(root)
    result_window.title("Result")
    result_window.geometry("500x400")
    
    text_area = scrolledtext.ScrolledText(result_window, wrap=tk.WORD, width=60, height=20)
    text_area.pack(expand=True, fill='both', padx=10, pady=10)
    text_area.insert(tk.END, result)
    text_area.config(state=tk.DISABLED)
    
    close_btn = tk.Button(result_window, text="Close", command=result_window.destroy)
    close_btn.pack(pady=5)

def update_location_display():
    """Update the current location display"""
    current_location = get_current_location()
    location_label.config(text=current_location)

def start_gui():
    """Start the Desktop AI GUI. This function allows packaging tools or CLI code
    to import ai_operator without launching the GUI immediately.
    """
    global root, location_label, command_entry

    # GUI setup
    root = tk.Tk()
    root.title("Desktop AI System Manager")
    root.geometry("700x400")

    # Current location display
    location_frame = tk.Frame(root)
    location_frame.pack(pady=10, padx=10, fill='x')

    tk.Label(location_frame, text="Current Location:", font=("Arial", 10, "bold")).pack(side='left')
    location_label = tk.Label(location_frame, text="Loading...", font=("Arial", 10), fg="blue")
    location_label.pack(side='left', padx=(10, 0))

    # Command input
    command_frame = tk.Frame(root)
    command_frame.pack(pady=20, padx=10, fill='x')

    tk.Label(command_frame, text="Type a command:", font=("Arial", 12)).pack()
    command_entry = tk.Entry(command_frame, width=70, font=("Arial", 11))
    command_entry.pack(pady=10)
    command_entry.bind('<Return>', lambda event: execute_command())

    # Buttons
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Execute", command=execute_command, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side='left', padx=5)
    tk.Button(button_frame, text="Where Am I?", command=lambda: show_result(get_current_location()), bg="#2196F3", fg="white").pack(side='left', padx=5)
    tk.Button(button_frame, text="Go Back", command=lambda: (go_back(), update_location_display()), bg="#FF9800", fg="white").pack(side='left', padx=5)
    tk.Button(button_frame, text="System Info", command=lambda: show_result(get_system_info()), bg="#9C27B0", fg="white").pack(side='left', padx=5)
    tk.Button(button_frame, text="Screenshot", command=lambda: show_result(take_screenshot()), bg="#607D8B", fg="white").pack(side='left', padx=5)

    # Second row of buttons for new features
    button_frame2 = tk.Frame(root)
    button_frame2.pack(pady=5)

    tk.Button(button_frame2, text="Open Gmail", command=lambda: show_result(open_gmail("firefox")), bg="#DB4437", fg="white").pack(side='left', padx=5)
    tk.Button(button_frame2, text="Create Document", command=lambda: show_result(create_word_document()), bg="#4285F4", fg="white").pack(side='left', padx=5)
    tk.Button(button_frame2, text="List Documents", command=lambda: show_result(list_documents()), bg="#34A853", fg="white").pack(side='left', padx=5)
    tk.Button(button_frame2, text="List Browsers", command=lambda: show_result(list_browsers()), bg="#FF6D01", fg="white").pack(side='left', padx=5)
    tk.Button(button_frame2, text="Check Dependencies", command=lambda: show_result(check_dependencies()), bg="#673AB7", fg="white").pack(side='left', padx=5)
    tk.Button(button_frame2, text="Smart Search", command=smart_search_dialog, bg="#1976D2", fg="white").pack(side='left', padx=5)

    # Examples
    examples_frame = tk.Frame(root)
    examples_frame.pack(pady=20, padx=10, fill='both', expand=True)

    tk.Label(examples_frame, text="Example Commands:", font=("Arial", 11, "bold")).pack(anchor='w')

    examples_text = scrolledtext.ScrolledText(examples_frame, height=8, width=80, font=("Arial", 9))
    examples_text.pack(fill='both', expand=True, pady=5)

    examples = """• Navigation:
  - "go to documents" or "navigate to desktop"
  - "go back" or "return"
  - "where am i?" or "current location"

• File Management:
  - "list folders" or "show directories"
  - "create folder MyFolder" or "make file test.py"
  - "delete file test.txt" or "move file test.txt to documents"
  - "rename file old.txt new.txt" or "search files python"

• Browser Operations:
  - "open firefox gmail" or "open chrome youtube"
  - "open browser firefox" or "close browser chrome"
  - "list browsers" or "open gmail in firefox"

• Document Operations:
  - "create document MyDoc" or "create word document"
  - "open document report.docx" or "list documents"
  - "convert document.docx to pdf" or "convert report.pdf to docx"
  - "search for text in document.docx" or "extract text from file.pdf"
  - "summarize document report.docx"

• System Operations:
  - "check storage" or "check internet speed"
  - "take screenshot" or "capture screen"
  - "list processes" or "kill process chrome"
  - "adjust volume 50" or "mute volume"
  - "connect wifi MyNetwork"

• Power Management (GUI Password):
  - "shutdown" or "restart in 5 minutes"
  - "cancel shutdown"

• Typo Tolerance:
  - "chck storge" → Checks storage
  - "opn gmail" → Opens Gmail
    - "crete documnt" → Creates document"""

    examples_text.insert(tk.END, examples)
    examples_text.config(state=tk.DISABLED)

    # Initialize location display
    update_location_display()

    root.mainloop()


if __name__ == '__main__':
    start_gui()
