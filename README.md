# Linux Desktop AI Agent

A powerful, intelligent desktop automation agent for Linux/Ubuntu systems that combines natural language understanding with robust system task execution. Built with Python and powered by locally-installed Llama models, this agent can understand complex requests and perform a wide range of system operations.

## 🎯 Features

### Core Capabilities
- **Natural Language Understanding**: Uses Llama 3.1 8B for intelligent command parsing and contextual understanding
- **Modular Architecture**: Pluggable modules for different system tasks
- **Smart Automation**: Executes complex system tasks through natural language
- **Task Execution**: Performs real system operations beyond just conversation
- **Local Processing**: All AI processing happens locally with Ollama
- **Privacy-Focused**: No data leaves your machine

### System Modules

#### 1. **System Cleanup Module**
- Clear package manager cache (apt/dnf/pacman)
- Remove temporary files
- Clear thumbnail cache
- Remove old kernel versions
- Clear browser caches
- Empty trash
- Clean up old logs
- Full system cleanup with space reporting

#### 2. **System Monitor Module**
- Real-time CPU monitoring
- Memory and swap usage tracking
- Disk space monitoring
- System temperature monitoring
- Process monitoring and top processes
- Battery status (for laptops)
- Network interface information
- Overall system health scoring

#### 3. **Network Module**
- **Internet Connectivity**
  - Check internet connection status
  - Test connection to specific hosts/ports
  - Monitor connection stability
  - Detect network outages

- **Performance Testing**
  - Run speed tests (download/upload/ping)
  - Measure latency to common services
  - Test DNS resolution times
  - Check packet loss

- **WiFi Management**
  - Check WiFi signal strength
  - List available networks
  - Monitor connection quality
  - Troubleshoot connectivity issues

- **Advanced Diagnostics**
  - Traceroute to diagnose routing issues
  - Netstat for connection monitoring
  - DNS resolution testing
  - Check open ports and services

#### 4. **File Manager Module**
- **File Organization**
  - Organize downloads by file type (Documents, Images, Archives, etc.)
  - Create smart folder structures based on content
  - Sort photos by date using EXIF data
  - Move files by extension to appropriate folders

- **File Operations**
  - Batch rename files using patterns
  - Find and remove duplicate files (hash-based comparison)
  - Compress old or large files (zip, tar.gz)
  - Find and manage large files
  - Clean up empty folders

- **Search & Analysis**
  - Advanced file search with filters (size, date, type)
  - Find recently modified files
  - Search by content within files
  - Generate disk usage reports

- **Batch Processing**
  - Apply actions to multiple files
  - Convert between file formats
  - Resize images in bulk
  - Update file metadata

#### 5. **Package Manager Module**
- Install packages
- Remove packages
- Update system packages
- Upgrade all packages
- Search for packages
- List installed packages
- Check for updates
- Fix broken packages
- Remove unused packages
- Get package information

#### 6. **Security Module**
- Malware scanning (ClamAV)
- File permission auditing
- Firewall status checking
- Failed login monitoring
- SSH key security checks
- Rootkit detection (rkhunter)
- Security update checking
- User account auditing
- Sudo access verification
- Comprehensive security reports

#### 7. **Developer Tools Module**
- Git repository management
- Docker container and image management
- Python virtual environment creation
- Port availability checking
- Development server management
- Database backup functionality
- Port conflict detection

## 📋 Prerequisites

### Required
- **Linux/Ubuntu System** (20.04 LTS or later recommended)
- **Python 3.8+** (with pip)
- **Ollama 0.13.0+** (for local LLM inference with Llama 3.1 8B)
- **sudo access** (required for system-level operations)
- **Basic terminal knowledge** (for troubleshooting)

### Recommended Dependencies
- **File Operations**
  - `exifread`: For reading photo metadata
  - `python-magic`: For accurate file type detection
  - `pillow`: For image processing

- **Network Tools**
  - `speedtest-cli`: For internet speed testing
  - `python-nmap`: For network scanning
  - `dnspython`: For DNS operations

- **System Utilities**
  - `notify-send`: For desktop notifications
  - `ClamAV`: For malware scanning
  - `rkhunter`: For rootkit detection
  - `htop`: For system monitoring

## 🚀 Installation

### Step 1: Install Ollama 0.13.0

```bash
# Download and install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# In another terminal, pull Llama 3.1 8B model
ollama pull llama3.1:8b

# Verify Ollama version (expected: 0.13.0)
ollama --version
```

### Step 2: Install Python Dependencies

```bash
cd /home/muthoni/DesktopAI

# Install required packages
pip install -r requirements_linux.txt

# Or install individually
pip install psutil requests speedtest-cli
```

### Step 3: Install System Dependencies

```bash
# For Ubuntu/Debian
sudo apt update
sudo apt install -y \
    python3-pip \
    python3-dev \
    libnotify-bin \
    clamav \
    rkhunter \
    wireless-tools \
    net-tools

# Optional: For speedtest
pip install speedtest-cli
```

### Step 4: Make Agent Executable

```bash
chmod +x /home/muthoni/DesktopAI/linux_desktop_agent.py
```

## 💻 Usage

### Interactive Mode

Start the agent in interactive mode for a conversational experience:

```bash
# Start the agent
python3 agent_core.py
```

In interactive mode, you can have natural conversations with the agent or give it commands to execute system tasks. Type `quit` to exit or `help` to see available commands.

### Command Examples

Simply type commands naturally in the interactive mode:

#### File Management
```
organize my downloads
find duplicate files in ~/Pictures
compress all PDFs in ~/Documents
sort my photos by date in ~/Pictures
find large files larger than 100MB
create a project folder structure
search for .conf files
```

#### Network Operations
```
test my internet speed
check my internet connection
show me my WiFi signal strength
run network diagnostics
check if google.com is resolving
ping github.com
run traceroute to example.com
```

#### System Management
```
check my system health
what's my CPU usage
show me disk space usage
list top processes by CPU
check system temperature
update all system packages
clean up temporary files
```

#### Package Management
```
install htop
update my system packages
list installed packages
search for python packages
remove old unused packages
fix broken packages
check for security updates
```

#### Security
```
scan for malware
check firewall status
check for security updates
check file permissions
check SSH keys
```

#### Developer Tools
```
git pull all repos
docker clean
check ports
create venv
```

## 🎯 Quick Start

1. **Start the agent:**
   ```bash
   python3 agent_core.py
   ```

2. **Type a command naturally:**
   ```
   You: organize my downloads
   Agent: ✅ Organized 15 files in Downloads into categories!
   ```

3. **Have a conversation:**
   ```
   You: how are you
   Agent: I'm running great! Your system looks healthy. CPU: 10.6%, RAM: 77.9%
   ```

4. **Exit anytime:**
   ```
   You: quit
   Agent: Goodbye! Have a great day! 👋
   ```

## 📚 Troubleshooting

### Missing Dependencies
If you see errors about missing modules:

```bash
# Install optional dependencies
pip install speedtest-cli exifread dnspython

# Or install all at once
pip install -r requirements.txt
```

### Permission Errors
Some operations require sudo. The agent will prompt you if needed:

```bash
# Grant sudo access for specific commands
sudo visudo
# Add: your_username ALL=(ALL) NOPASSWD: /usr/bin/apt, /usr/bin/docker, etc.
```

### Ollama Not Running
Make sure Ollama is running:

```bash
# Start Ollama service
ollama serve

# In another terminal, pull the model if needed
ollama pull llama3.1:8b
```

## 📝 Configuration

Create `~/.config/linux-agent/config.json` to customize:

```json
{
  "ollama_host": "localhost",
  "ollama_port": 11434,
  "model": "llama3.1:8b",
  "timeout": 120,
  "auto_cleanup_threshold": 90,
  "notification_level": "info"
}
```

## 📊 Architecture

The agent uses a modular architecture with the following components:

- **AgentCore**: Main conversational engine with NLP and command routing
- **Pattern Detection**: Fast keyword-based command identification
- **Module Handlers**: Specialized handlers for each task category
- **Error Handling**: Graceful fallbacks for missing dependencies

## 🎓 How It Works

### 1. Command Understanding
The agent uses pattern matching and Llama 3.1 for natural language understanding:
- Detects commands using keyword patterns (fast)
- Falls back to LLM for complex commands
- Extracts parameters from user input
- Maintains conversation history

### 2. Task Execution
Commands are routed to appropriate handlers:
- **System Monitoring** → CPU, RAM, disk, temperature checks
- **File Management** → Organization, deduplication, compression
- **Network Tools** → Speed tests, DNS, connectivity checks
- **Package Management** → Install, update, remove packages
- **Security** → Scanning, firewall, permissions
- **Developer Tools** → Git, Docker, ports, virtual environments

## 🔐 Security Considerations

- All processing is local (no cloud)
- Requires sudo for system operations
- SSH key permissions are validated
- Firewall status is monitored
- Malware scanning available (with ClamAV)

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Version**: 2.0.0  
**Last Updated**: December 2024  
**Compatibility**: Linux/Ubuntu 20.04+  
**Python**: 3.8+  
**Model**: Llama 3.1 8B (via Ollama)
