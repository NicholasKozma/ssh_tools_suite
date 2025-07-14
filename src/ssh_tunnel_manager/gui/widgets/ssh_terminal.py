#!/usr/bin/env python3
"""
SSH Tunnel Manager - SSH Terminal Widget
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QPlainTextEdit
)
from PySide6.QtCore import Signal, QProcess, QTimer
from PySide6.QtGui import QFont

from ...core.constants import (
    SSH_PASSWORD_PROMPTS, SSH_STDERR_PASSWORD_PROMPTS, 
    SSH_CONFIRMATION_PROMPTS, SSH_ERROR_PATTERNS,
    CONSOLE_FONT, CONSOLE_FONT_SIZE, TERMINAL_STYLE, INPUT_HIDE_DELAY
)


class SSHTerminalWidget(QWidget):
    """Embedded terminal widget for SSH password input."""
    
    password_entered = Signal(str)  # Signal when password is entered
    process_finished = Signal(int)  # Signal when SSH process finishes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the terminal UI."""
        layout = QVBoxLayout(self)
        
        # Terminal output area
        self.output_text = QPlainTextEdit()
        self.output_text.setFont(QFont(CONSOLE_FONT, CONSOLE_FONT_SIZE))
        self.output_text.setStyleSheet(TERMINAL_STYLE)
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)
        
        # Input area
        input_layout = QHBoxLayout()
        self.input_label = QLabel("Input:")
        self.input_line = QLineEdit()
        self.input_line.setEchoMode(QLineEdit.Password)
        self.input_line.returnPressed.connect(self.send_input)
        self.input_line.setPlaceholderText("Enter password or type 'yes'/'no' for confirmations")
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_input)
        
        # Toggle password visibility button
        self.toggle_visibility_button = QPushButton("👁")
        self.toggle_visibility_button.setMaximumWidth(30)
        self.toggle_visibility_button.clicked.connect(self.toggle_password_visibility)
        self.toggle_visibility_button.setToolTip("Toggle password visibility")
        
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.toggle_visibility_button)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)
        
        # Initially show input for better user experience
        self.set_input_visible(True)
        
        # Add initial help text
        self.append_output("SSH Terminal Ready")
        self.append_output("Enter your SSH password below when prompted.")
        self.append_output("This terminal will automatically detect password prompts and accept input.")
        self.append_output("=" * 50)
    
    def set_input_visible(self, visible: bool):
        """Show/hide password input."""
        self.input_label.setVisible(visible)
        self.input_line.setVisible(visible)
        self.send_button.setVisible(visible)
        self.toggle_visibility_button.setVisible(visible)
        if visible:
            # Force focus and ensure the input is ready
            self.input_line.setFocus()
            self.input_line.activateWindow()
            # Make sure the input field is clear and ready
            if not self.input_line.text():
                self.input_line.setPlaceholderText("Type your password here and press Enter")
    
    def toggle_password_visibility(self):
        """Toggle between showing and hiding password text."""
        if self.input_line.echoMode() == QLineEdit.Password:
            self.input_line.setEchoMode(QLineEdit.Normal)
            self.toggle_visibility_button.setText("🙈")
        else:
            self.input_line.setEchoMode(QLineEdit.Password)
            self.toggle_visibility_button.setText("👁")
    
    def append_output(self, text: str):
        """Add text to terminal output."""
        self.output_text.appendPlainText(text)
        # Auto-scroll to bottom
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def send_input(self):
        """Send password input to SSH process."""
        input_text = self.input_line.text()
        if self.process and input_text:
            try:
                # Send input to SSH process
                self.process.write(input_text.encode() + b'\n')
                self.process.waitForBytesWritten()
                
                # Clear input
                self.input_line.clear()
                
                # Show what was sent (hide passwords, show confirmations)
                if input_text.lower() in ['yes', 'no', 'y', 'n']:
                    self.append_output(f"Sent: {input_text}")
                else:
                    self.append_output("Password sent...")
                
                # Emit signal for password tracking
                if input_text.lower() not in ['yes', 'no', 'y', 'n']:
                    self.password_entered.emit(input_text)
                
                # Keep input visible for a moment in case more prompts come
                QTimer.singleShot(INPUT_HIDE_DELAY, lambda: self.set_input_visible(False))
                
            except Exception as e:
                self.append_output(f"Error sending input: {e}")
    
    def start_ssh_process(self, cmd: list[str]) -> QProcess:
        """Start SSH process and handle I/O."""
        self.process = QProcess(self)
        self.process.setProgram(cmd[0])
        self.process.setArguments(cmd[1:])
        
        # Connect signals
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        
        self.append_output(f"Starting SSH: {' '.join(cmd)}")
        self.process.start()
        
        return self.process
    
    def handle_stdout(self):
        """Handle SSH process stdout."""
        data = self.process.readAllStandardOutput().data().decode()
        self.append_output(data)
        
        # Make input field visible and focused when any output appears
        # This ensures users can always type if needed
        if data.strip():
            self.set_input_visible(True)
        
        # Sometimes password prompts come through stdout too
        data_lower = data.lower().strip()
        
        if any(prompt in data_lower for prompt in SSH_PASSWORD_PROMPTS):
            self.set_input_visible(True)
            self.append_output("👆 Password prompt detected - please enter your password below:")
        
        # Check for confirmation prompts in stdout too
        if any(prompt in data_lower for prompt in SSH_CONFIRMATION_PROMPTS):
            self.set_input_visible(True)
            self.append_output("👆 SSH confirmation required - type 'yes' or 'no':")
    
    def handle_stderr(self):
        """Handle SSH process stderr."""
        data = self.process.readAllStandardError().data().decode()
        self.append_output(data)
        
        # Make input field visible when any stderr output appears
        # SSH password prompts often come through stderr
        if data.strip():
            self.set_input_visible(True)
        
        # Check if password is being requested
        data_lower = data.lower().strip()
        
        # Check for any password-related prompts
        if any(prompt in data_lower for prompt in SSH_STDERR_PASSWORD_PROMPTS):
            self.set_input_visible(True)
            self.append_output("👆 Password prompt detected - please enter your password below:")
        
        # Also check if SSH is asking for confirmation
        if any(prompt in data_lower for prompt in SSH_CONFIRMATION_PROMPTS):
            self.set_input_visible(True)
            self.append_output("👆 SSH confirmation required - type 'yes' or 'no':")
        
        # Check for SSH error messages
        if any(error in data_lower for error in SSH_ERROR_PATTERNS):
            self.append_output("⚠️  SSH connection issue detected. Check your credentials and network connection.")
    
    def handle_finished(self, exit_code: int):
        """Handle SSH process completion."""
        self.append_output(f"SSH process finished with exit code: {exit_code}")
        self.set_input_visible(False)
        self.process_finished.emit(exit_code)
    
    def stop_process(self):
        """Stop the SSH process."""
        if self.process:
            self.process.kill()
            self.process = None
    
    def clear_output(self):
        """Clear the terminal output."""
        self.output_text.clear()
        self.append_output("SSH Terminal Ready")
        self.append_output("=" * 50)
