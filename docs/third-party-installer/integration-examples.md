# Third Party Installer - Integration Examples

Real-world examples of integrating the Third Party Installer into different types of applications.

## Desktop Application Integration

### Qt/PySide6 Application

```python
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                               QWidget, QPushButton, QProgressBar, 
                               QTextEdit, QLabel, QMessageBox)
from PySide6.QtCore import QThread, Signal, QTimer
from third_party_installer.core.installer import ThirdPartyInstaller, InstallationStatus

class InstallerWorker(QThread):
    progress_updated = Signal(int, str)
    installation_finished = Signal(str, bool, str)
    all_finished = Signal(bool)
    
    def __init__(self, tools_to_install):
        super().__init__()
        self.tools_to_install = tools_to_install
        self.installer = ThirdPartyInstaller()
    
    def run(self):
        """Install tools in background thread"""
        success_count = 0
        
        for tool_name in self.tools_to_install:
            def progress_callback(percent, message):
                self.progress_updated.emit(percent, f"{tool_name}: {message}")
            
            try:
                success = self.installer.install_tool(tool_name, progress_callback)
                if success:
                    success_count += 1
                    self.installation_finished.emit(tool_name, True, "Installation successful")
                else:
                    self.installation_finished.emit(tool_name, False, "Installation failed")
                    
            except Exception as e:
                self.installation_finished.emit(tool_name, False, str(e))
        
        all_success = success_count == len(self.tools_to_install)
        self.all_finished.emit(all_success)

class MyApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.installer = ThirdPartyInstaller()
        self.setup_ui()
        self.check_dependencies()
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("My Application")
        self.setGeometry(100, 100, 600, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Status label
        self.status_label = QLabel("Checking dependencies...")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        layout.addWidget(self.log_text)
        
        # Control buttons
        self.install_button = QPushButton("Install Missing Dependencies")
        self.install_button.clicked.connect(self.install_dependencies)
        layout.addWidget(self.install_button)
        
        self.start_button = QPushButton("Start Application")
        self.start_button.clicked.connect(self.start_main_application)
        self.start_button.setEnabled(False)
        layout.addWidget(self.start_button)
    
    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        missing_tools = self.installer.get_missing_required_tools()
        
        if not missing_tools:
            self.status_label.setText("✓ All dependencies are installed")
            self.install_button.setVisible(False)
            self.start_button.setEnabled(True)
            self.log_text.append("All required tools are available")
        else:
            self.status_label.setText(f"⚠ Missing {len(missing_tools)} required dependencies")
            self.log_text.append(f"Missing tools: {', '.join(missing_tools)}")
    
    def install_dependencies(self):
        """Install missing dependencies"""
        missing_tools = self.installer.get_missing_required_tools()
        
        if not missing_tools:
            return
        
        # Disable UI during installation
        self.install_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setText("Installing dependencies...")
        
        # Start installation in background thread
        self.worker = InstallerWorker(missing_tools)
        self.worker.progress_updated.connect(self.on_progress_updated)
        self.worker.installation_finished.connect(self.on_tool_installed)
        self.worker.all_finished.connect(self.on_all_installations_finished)
        self.worker.start()
    
    def on_progress_updated(self, percent, message):
        """Handle progress updates"""
        self.progress_bar.setValue(percent)
        self.log_text.append(f"[{percent:3d}%] {message}")
        
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def on_tool_installed(self, tool_name, success, message):
        """Handle individual tool installation completion"""
        if success:
            self.log_text.append(f"✓ {tool_name}: {message}")
        else:
            self.log_text.append(f"✗ {tool_name}: {message}")
    
    def on_all_installations_finished(self, all_success):
        """Handle completion of all installations"""
        self.progress_bar.setVisible(False)
        self.install_button.setEnabled(True)
        
        if all_success:
            self.status_label.setText("✓ All dependencies installed successfully")
            self.start_button.setEnabled(True)
            self.install_button.setVisible(False)
            
            QMessageBox.information(self, "Success", 
                                  "All dependencies have been installed successfully!")
        else:
            self.status_label.setText("⚠ Some installations failed")
            QMessageBox.warning(self, "Warning", 
                              "Some dependency installations failed. Check the log for details.")
    
    def start_main_application(self):
        """Start the main application functionality"""
        if self.installer.is_installation_complete():
            self.log_text.append("Starting main application...")
            # Your main application logic here
            QMessageBox.information(self, "Application Started", 
                                  "Main application is now running!")
        else:
            QMessageBox.warning(self, "Dependencies Missing", 
                              "Cannot start application - missing dependencies.")

def main():
    app = QApplication(sys.argv)
    window = MyApplication()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
```

## Web Application Integration

### Flask Web Service

```python
from flask import Flask, jsonify, request, render_template
from third_party_installer.core.installer import ThirdPartyInstaller, InstallationStatus
import threading
import queue
import uuid

app = Flask(__name__)
installer = ThirdPartyInstaller()

# Store installation progress for each session
installation_sessions = {}

class InstallationSession:
    def __init__(self, session_id):
        self.session_id = session_id
        self.progress = 0
        self.message = ""
        self.status = "pending"
        self.results = {}

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('installer_dashboard.html')

@app.route('/api/tools/status')
def get_tools_status():
    """Get status of all tools"""
    status_dict = installer.get_all_tools_status()
    
    tools_info = {}
    for tool_name, status in status_dict.items():
        tool = installer.tools_config[tool_name]
        tools_info[tool_name] = {
            'display_name': tool.display_name,
            'description': tool.description,
            'required': tool.required,
            'status': status.value
        }
    
    return jsonify(tools_info)

@app.route('/api/tools/<tool_name>/install', methods=['POST'])
def install_tool(tool_name):
    """Install a specific tool"""
    if tool_name not in installer.tools_config:
        return jsonify({'error': 'Tool not found'}), 404
    
    # Create installation session
    session_id = str(uuid.uuid4())
    session = InstallationSession(session_id)
    installation_sessions[session_id] = session
    
    def install_worker():
        """Background installation worker"""
        def progress_callback(percent, message):
            session.progress = percent
            session.message = message
        
        try:
            session.status = "installing"
            success = installer.install_tool(tool_name, progress_callback)
            session.status = "completed" if success else "failed"
            session.results[tool_name] = success
            
        except Exception as e:
            session.status = "error"
            session.message = str(e)
    
    # Start installation in background
    thread = threading.Thread(target=install_worker)
    thread.daemon = True
    thread.start()
    
    return jsonify({'session_id': session_id})

@app.route('/api/install/batch', methods=['POST'])
def install_multiple_tools():
    """Install multiple tools"""
    data = request.get_json()
    tool_names = data.get('tools', [])
    
    if not tool_names:
        return jsonify({'error': 'No tools specified'}), 400
    
    # Validate tool names
    invalid_tools = [name for name in tool_names if name not in installer.tools_config]
    if invalid_tools:
        return jsonify({'error': f'Invalid tools: {invalid_tools}'}), 400
    
    # Create installation session
    session_id = str(uuid.uuid4())
    session = InstallationSession(session_id)
    installation_sessions[session_id] = session
    
    def batch_install_worker():
        """Background batch installation worker"""
        session.status = "installing"
        
        for i, tool_name in enumerate(tool_names):
            def progress_callback(percent, message):
                # Calculate overall progress
                tool_progress = (i * 100 + percent) / len(tool_names)
                session.progress = int(tool_progress)
                session.message = f"{tool_name}: {message}"
            
            try:
                success = installer.install_tool(tool_name, progress_callback)
                session.results[tool_name] = success
                
            except Exception as e:
                session.results[tool_name] = False
                session.message = f"Error installing {tool_name}: {e}"
        
        # Determine overall status
        all_success = all(session.results.values())
        session.status = "completed" if all_success else "partial"
        session.progress = 100
    
    # Start batch installation in background
    thread = threading.Thread(target=batch_install_worker)
    thread.daemon = True
    thread.start()
    
    return jsonify({'session_id': session_id})

@app.route('/api/install/status/<session_id>')
def get_installation_status(session_id):
    """Get installation progress and status"""
    session = installation_sessions.get(session_id)
    
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify({
        'session_id': session_id,
        'status': session.status,
        'progress': session.progress,
        'message': session.message,
        'results': session.results
    })

@app.route('/api/install/required')
def install_required_tools():
    """Install all missing required tools"""
    missing_tools = installer.get_missing_required_tools()
    
    if not missing_tools:
        return jsonify({'message': 'All required tools are already installed'})
    
    # Use batch installation for required tools
    return install_multiple_tools_internal(missing_tools)

def install_multiple_tools_internal(tool_names):
    """Internal method for batch installation"""
    session_id = str(uuid.uuid4())
    session = InstallationSession(session_id)
    installation_sessions[session_id] = session
    
    def worker():
        session.status = "installing"
        
        for i, tool_name in enumerate(tool_names):
            def progress_callback(percent, message):
                tool_progress = (i * 100 + percent) / len(tool_names)
                session.progress = int(tool_progress)
                session.message = f"{tool_name}: {message}"
            
            try:
                success = installer.install_tool(tool_name, progress_callback)
                session.results[tool_name] = success
            except Exception as e:
                session.results[tool_name] = False
        
        all_success = all(session.results.values())
        session.status = "completed" if all_success else "partial"
        session.progress = 100
    
    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
    
    return jsonify({'session_id': session_id})

# HTML Template (save as templates/installer_dashboard.html)
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Third Party Installer Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .tool { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
        .status-installed { background-color: #d4edda; }
        .status-not-installed { background-color: #f8d7da; }
        .progress { width: 100%; height: 20px; margin: 10px 0; }
        button { padding: 10px 15px; margin: 5px; cursor: pointer; }
        .log { background-color: #f8f9fa; padding: 10px; font-family: monospace; max-height: 200px; overflow-y: auto; }
    </style>
</head>
<body>
    <h1>Third Party Installer Dashboard</h1>
    
    <div>
        <button onclick="refreshStatus()">Refresh Status</button>
        <button onclick="installRequired()">Install Required Tools</button>
    </div>
    
    <div id="tools-container"></div>
    
    <div id="installation-progress" style="display: none;">
        <h3>Installation Progress</h3>
        <progress id="progress-bar" class="progress" value="0" max="100"></progress>
        <div id="progress-message">Preparing installation...</div>
    </div>
    
    <div id="log-container">
        <h3>Installation Log</h3>
        <div id="log" class="log"></div>
    </div>

    <script>
        let currentSessionId = null;
        let statusCheckInterval = null;
        
        function refreshStatus() {
            fetch('/api/tools/status')
                .then(response => response.json())
                .then(data => displayTools(data))
                .catch(error => console.error('Error:', error));
        }
        
        function displayTools(tools) {
            const container = document.getElementById('tools-container');
            container.innerHTML = '';
            
            Object.entries(tools).forEach(([toolName, tool]) => {
                const toolDiv = document.createElement('div');
                toolDiv.className = `tool status-${tool.status.replace('_', '-')}`;
                
                toolDiv.innerHTML = `
                    <h3>${tool.display_name}</h3>
                    <p>${tool.description}</p>
                    <p><strong>Status:</strong> ${tool.status}</p>
                    <p><strong>Required:</strong> ${tool.required ? 'Yes' : 'No'}</p>
                    ${tool.status === 'NOT_INSTALLED' ? 
                        `<button onclick="installTool('${toolName}')">Install</button>` : ''}
                `;
                
                container.appendChild(toolDiv);
            });
        }
        
        function installTool(toolName) {
            fetch(`/api/tools/${toolName}/install`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            })
            .then(response => response.json())
            .then(data => {
                if (data.session_id) {
                    startProgressMonitoring(data.session_id);
                }
            })
            .catch(error => console.error('Error:', error));
        }
        
        function installRequired() {
            fetch('/api/install/required', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            })
            .then(response => response.json())
            .then(data => {
                if (data.session_id) {
                    startProgressMonitoring(data.session_id);
                }
            })
            .catch(error => console.error('Error:', error));
        }
        
        function startProgressMonitoring(sessionId) {
            currentSessionId = sessionId;
            document.getElementById('installation-progress').style.display = 'block';
            
            statusCheckInterval = setInterval(() => {
                checkInstallationStatus(sessionId);
            }, 1000);
        }
        
        function checkInstallationStatus(sessionId) {
            fetch(`/api/install/status/${sessionId}`)
                .then(response => response.json())
                .then(data => {
                    updateProgress(data);
                    
                    if (data.status === 'completed' || data.status === 'failed' || data.status === 'partial') {
                        clearInterval(statusCheckInterval);
                        setTimeout(() => {
                            document.getElementById('installation-progress').style.display = 'none';
                            refreshStatus();
                        }, 2000);
                    }
                })
                .catch(error => console.error('Error:', error));
        }
        
        function updateProgress(data) {
            document.getElementById('progress-bar').value = data.progress;
            document.getElementById('progress-message').textContent = data.message;
            
            // Add to log
            const log = document.getElementById('log');
            log.innerHTML += `<div>[${new Date().toLocaleTimeString()}] ${data.message}</div>`;
            log.scrollTop = log.scrollHeight;
        }
        
        // Initial load
        refreshStatus();
    </script>
</body>
</html>
'''

# Save template
import os
os.makedirs('templates', exist_ok=True)
with open('templates/installer_dashboard.html', 'w') as f:
    f.write(DASHBOARD_TEMPLATE)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

## Command Line Interface Integration

### CLI Application with Rich Progress

```python
import click
import rich
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
from third_party_installer.core.installer import ThirdPartyInstaller, InstallationStatus

console = Console()

@click.group()
def cli():
    """SSH Tools Suite Third Party Installer CLI"""
    pass

@cli.command()
def status():
    """Show status of all tools"""
    installer = ThirdPartyInstaller()
    
    table = Table(title="Tool Installation Status")
    table.add_column("Tool", style="cyan", no_wrap=True)
    table.add_column("Status", style="magenta")
    table.add_column("Required", style="green")
    table.add_column("Description", style="white")
    
    for tool_name, tool in installer.tools_config.items():
        status = installer.get_tool_status(tool_name)
        
        # Color code status
        if status == InstallationStatus.INSTALLED:
            status_text = "[green]✓ Installed[/green]"
        elif status == InstallationStatus.NOT_INSTALLED:
            status_text = "[red]✗ Not Installed[/red]"
        elif status == InstallationStatus.INSTALLATION_FAILED:
            status_text = "[yellow]⚠ Failed[/yellow]"
        else:
            status_text = "[blue]? Unknown[/blue]"
        
        required_text = "[green]Yes[/green]" if tool.required else "[dim]No[/dim]"
        
        table.add_row(
            tool.display_name,
            status_text,
            required_text,
            tool.description[:50] + "..." if len(tool.description) > 50 else tool.description
        )
    
    console.print(table)
    
    # Summary
    missing_required = installer.get_missing_required_tools()
    if missing_required:
        console.print(Panel(
            f"[red]Missing {len(missing_required)} required tools: {', '.join(missing_required)}[/red]",
            title="⚠ Warning"
        ))
    else:
        console.print(Panel(
            "[green]All required tools are installed[/green]",
            title="✓ Success"
        ))

@cli.command()
@click.argument('tool_name')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def install(tool_name, verbose):
    """Install a specific tool"""
    installer = ThirdPartyInstaller()
    
    if tool_name not in installer.tools_config:
        console.print(f"[red]Error: Tool '{tool_name}' not found[/red]")
        available_tools = list(installer.tools_config.keys())
        console.print(f"Available tools: {', '.join(available_tools)}")
        return
    
    tool = installer.tools_config[tool_name]
    
    # Check current status
    current_status = installer.get_tool_status(tool_name)
    if current_status == InstallationStatus.INSTALLED:
        console.print(f"[green]{tool.display_name} is already installed[/green]")
        return
    
    console.print(f"Installing [cyan]{tool.display_name}[/cyan]...")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        task = progress.add_task(f"Installing {tool.display_name}", total=100)
        
        def progress_callback(percent, message):
            progress.update(task, completed=percent)
            if verbose:
                progress.update(task, description=f"{tool.display_name}: {message}")
        
        try:
            success = installer.install_tool(tool_name, progress_callback)
            
            if success:
                console.print(f"[green]✓ Successfully installed {tool.display_name}[/green]")
            else:
                console.print(f"[red]✗ Failed to install {tool.display_name}[/red]")
                
        except Exception as e:
            console.print(f"[red]Error during installation: {e}[/red]")

@cli.command()
@click.option('--required-only', is_flag=True, help='Install only required tools')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def install_all(required_only, verbose):
    """Install all missing tools"""
    installer = ThirdPartyInstaller()
    
    if required_only:
        tools_to_install = installer.get_missing_required_tools()
        console.print(f"Installing {len(tools_to_install)} required tools...")
    else:
        all_status = installer.get_all_tools_status()
        tools_to_install = [
            name for name, status in all_status.items()
            if status == InstallationStatus.NOT_INSTALLED
        ]
        console.print(f"Installing {len(tools_to_install)} missing tools...")
    
    if not tools_to_install:
        console.print("[green]All tools are already installed[/green]")
        return
    
    success_count = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        for i, tool_name in enumerate(tools_to_install):
            tool = installer.tools_config[tool_name]
            task = progress.add_task(f"Installing {tool.display_name}", total=100)
            
            def progress_callback(percent, message):
                progress.update(task, completed=percent)
                if verbose:
                    progress.update(task, description=f"{tool.display_name}: {message}")
            
            try:
                success = installer.install_tool(tool_name, progress_callback)
                
                if success:
                    success_count += 1
                    progress.update(task, description=f"[green]✓ {tool.display_name}[/green]")
                else:
                    progress.update(task, description=f"[red]✗ {tool.display_name}[/red]")
                    
            except Exception as e:
                progress.update(task, description=f"[red]✗ {tool.display_name}: {e}[/red]")
    
    # Summary
    if success_count == len(tools_to_install):
        console.print(Panel(
            f"[green]Successfully installed all {success_count} tools[/green]",
            title="✓ Installation Complete"
        ))
    else:
        failed_count = len(tools_to_install) - success_count
        console.print(Panel(
            f"[yellow]Installed {success_count} tools, {failed_count} failed[/yellow]",
            title="⚠ Partial Success"
        ))

@cli.command()
@click.option('--proxy-server', help='Proxy server address')
@click.option('--proxy-port', type=int, help='Proxy server port')
@click.option('--proxy-username', help='Proxy username')
@click.option('--proxy-password', help='Proxy password', hide_input=True)
@click.option('--use-px', is_flag=True, help='Use PX corporate proxy')
def configure(proxy_server, proxy_port, proxy_username, proxy_password, use_px):
    """Configure installer settings"""
    installer = ThirdPartyInstaller()
    
    if use_px:
        installer.proxy_config = {
            'enabled': True,
            'use_px': True,
            'px_port': 3128
        }
        console.print("[green]Configured to use PX corporate proxy[/green]")
    
    elif proxy_server:
        installer.proxy_config = {
            'enabled': True,
            'auto_detect': False,
            'server': proxy_server,
            'port': proxy_port or 8080,
            'username': proxy_username,
            'password': proxy_password
        }
        console.print(f"[green]Configured manual proxy: {proxy_server}:{proxy_port or 8080}[/green]")
    
    else:
        installer.proxy_config = {
            'enabled': True,
            'auto_detect': True
        }
        console.print("[green]Configured to auto-detect system proxy[/green]")

@cli.command()
def doctor():
    """Run diagnostics and health checks"""
    installer = ThirdPartyInstaller()
    
    console.print(Panel("Running Installation Diagnostics", title="🔍 Doctor"))
    
    # System information
    import platform
    import sys
    console.print(f"Operating System: {platform.platform()}")
    console.print(f"Python Version: {sys.version}")
    console.print()
    
    # Network connectivity
    console.print("Testing network connectivity...")
    import urllib.request
    
    test_urls = [
        'https://github.com',
        'https://download.videolan.org',
        'https://download.sysinternals.com'
    ]
    
    for url in test_urls:
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                if response.getcode() == 200:
                    console.print(f"  [green]✓[/green] {url}")
                else:
                    console.print(f"  [yellow]⚠[/yellow] {url} (HTTP {response.getcode()})")
        except Exception as e:
            console.print(f"  [red]✗[/red] {url} ({str(e)[:50]})")
    
    console.print()
    
    # Tool status
    console.print("Checking tool installations...")
    all_status = installer.get_all_tools_status()
    
    for tool_name, status in all_status.items():
        tool = installer.tools_config[tool_name]
        
        if status == InstallationStatus.INSTALLED:
            console.print(f"  [green]✓[/green] {tool.display_name}")
        elif status == InstallationStatus.NOT_INSTALLED and tool.required:
            console.print(f"  [red]✗[/red] {tool.display_name} (required)")
        elif status == InstallationStatus.NOT_INSTALLED:
            console.print(f"  [dim]○[/dim] {tool.display_name} (optional)")
        else:
            console.print(f"  [yellow]⚠[/yellow] {tool.display_name} ({status.value})")
    
    # Recommendations
    missing_required = installer.get_missing_required_tools()
    if missing_required:
        console.print()
        console.print(Panel(
            f"Run: [bold]installer install-all --required-only[/bold]\n"
            f"To install missing required tools: {', '.join(missing_required)}",
            title="💡 Recommendation"
        ))

if __name__ == '__main__':
    cli()
```

## CI/CD Pipeline Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/setup-dependencies.yml
name: Setup Dependencies

on:
  workflow_call:
    inputs:
      install-optional:
        description: 'Install optional tools'
        required: false
        default: false
        type: boolean

jobs:
  setup-dependencies:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install SSH Tools Suite
      run: |
        pip install -e .
    
    - name: Check existing tools
      id: check-tools
      run: |
        python -c "
        from third_party_installer.core.installer import ThirdPartyInstaller
        installer = ThirdPartyInstaller()
        missing = installer.get_missing_required_tools()
        print(f'missing={len(missing) > 0}')
        print(f'tools={missing}')
        " >> $GITHUB_OUTPUT
    
    - name: Install required dependencies
      if: steps.check-tools.outputs.missing == 'true'
      run: |
        python -m third_party_installer --silent --required-only
    
    - name: Install optional dependencies
      if: inputs.install-optional
      run: |
        python -m third_party_installer --silent --all
    
    - name: Verify installation
      run: |
        python -c "
        from third_party_installer.core.installer import ThirdPartyInstaller
        installer = ThirdPartyInstaller()
        if installer.is_installation_complete():
            print('✓ All required tools installed')
        else:
            missing = installer.get_missing_required_tools()
            print(f'✗ Missing tools: {missing}')
            exit(1)
        "
    
    - name: Cache installed tools
      uses: actions/cache@v3
      with:
        path: |
          C:\Program Files\PsTools
          C:\Program Files\VideoLAN
          C:\ffmpeg
        key: ssh-tools-dependencies-${% raw %}{{ runner.os }}{% endraw %}-${% raw %}{{ hashFiles('**/requirements.txt') }}{% endraw %}
```

### Docker Integration

```dockerfile
# Dockerfile with dependency installation
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy application
WORKDIR /app
COPY . .

# Install Python dependencies
RUN pip install -e .

# Install third-party tools
RUN python -m third_party_installer --silent --required-only

# Verify installation
RUN python -c "
from third_party_installer.core.installer import ThirdPartyInstaller; \
installer = ThirdPartyInstaller(); \
assert installer.is_installation_complete(), 'Missing required tools'"

# Set up entrypoint
ENTRYPOINT ["python", "-m", "ssh_tunnel_manager"]
```

### Jenkins Pipeline

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Setup Dependencies') {
            steps {
                script {
                    // Install SSH Tools Suite
                    bat 'pip install -e .'
                    
                    // Check and install dependencies
                    def result = bat(
                        script: 'python -c "from third_party_installer.core.installer import ThirdPartyInstaller; installer = ThirdPartyInstaller(); print(len(installer.get_missing_required_tools()))"',
                        returnStdout: true
                    ).trim()
                    
                    if (result.toInteger() > 0) {
                        echo "Installing missing dependencies..."
                        bat 'python -m third_party_installer --silent --required-only'
                    } else {
                        echo "All dependencies already installed"
                    }
                    
                    // Verify installation
                    bat '''
                        python -c "
                        from third_party_installer.core.installer import ThirdPartyInstaller
                        installer = ThirdPartyInstaller()
                        assert installer.is_installation_complete(), 'Installation incomplete'
                        print('All dependencies verified')
                        "
                    '''
                }
            }
        }
        
        stage('Test Application') {
            steps {
                bat 'python -m pytest tests/'
            }
        }
        
        stage('Build Application') {
            steps {
                bat 'python setup.py bdist_wheel'
            }
        }
    }
    
    post {
        always {
            // Archive installation logs
            archiveArtifacts artifacts: 'logs/**/*.log', allowEmptyArchive: true
        }
        failure {
            // On failure, collect diagnostic information
            bat '''
                python -c "
                from third_party_installer.core.installer import ThirdPartyInstaller
                installer = ThirdPartyInstaller()
                status = installer.get_all_tools_status()
                for tool, stat in status.items():
                    print(f'{tool}: {stat.value}')
                "
            '''
        }
    }
}
```

These integration examples demonstrate how to effectively embed the Third Party Installer into various types of applications and development workflows, providing users with a seamless dependency management experience.
