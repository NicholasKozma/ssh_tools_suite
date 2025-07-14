#!/usr/bin/env python3
"""
SSH Tunnel Manager - Network Scanner
Provides ping and port scanning capabilities for network diagnostics
"""

import socket
import subprocess
import threading
import platform
import time
from typing import List, Tuple, Optional, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QSpinBox, QCheckBox, QProgressBar, QTabWidget, QWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QComboBox,
    QSplitter, QMessageBox, QApplication
)
from PySide6.QtCore import QThread, Signal, Qt, QTimer
from PySide6.QtGui import QFont, QColor


class PingWorker(QThread):
    """Worker thread for ping operations."""
    
    ping_result = Signal(str, bool, float)  # host, success, response_time
    ping_finished = Signal()
    
    def __init__(self, host: str, count: int = 4):
        super().__init__()
        self.host = host
        self.count = count
        self.running = True
    
    def run(self):
        """Run ping operation."""
        try:
            system = platform.system().lower()
            
            if system == "windows":
                cmd = ["ping", "-n", str(self.count), self.host]
            else:
                cmd = ["ping", "-c", str(self.count), self.host]
            
            for i in range(self.count):
                if not self.running:
                    break
                
                start_time = time.time()
                try:
                    if system == "windows":
                        result = subprocess.run(
                            ["ping", "-n", "1", self.host],
                            capture_output=True, text=True, timeout=5
                        )
                        success = result.returncode == 0
                    else:
                        result = subprocess.run(
                            ["ping", "-c", "1", "-W", "5", self.host],
                            capture_output=True, text=True, timeout=5
                        )
                        success = result.returncode == 0
                    
                    response_time = (time.time() - start_time) * 1000  # Convert to ms
                    self.ping_result.emit(self.host, success, response_time)
                    
                except (subprocess.TimeoutExpired, Exception):
                    self.ping_result.emit(self.host, False, 0.0)
                
                if i < self.count - 1:  # Don't sleep after last ping
                    time.sleep(1)
        
        except Exception as e:
            self.ping_result.emit(self.host, False, 0.0)
        
        finally:
            self.ping_finished.emit()
    
    def stop(self):
        """Stop the ping operation."""
        self.running = False


class PortScanWorker(QThread):
    """Worker thread for port scanning operations."""
    
    port_result = Signal(str, int, bool, str)  # host, port, open, service
    scan_progress = Signal(int)  # current port number
    scan_finished = Signal()
    
    def __init__(self, host: str, start_port: int, end_port: int, timeout: float = 1.0):
        super().__init__()
        self.host = host
        self.start_port = start_port
        self.end_port = end_port
        self.timeout = timeout
        self.running = True
        
        # Common service mappings
        self.services = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
            80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 993: "IMAPS",
            995: "POP3S", 3389: "RDP", 5432: "PostgreSQL", 3306: "MySQL",
            1433: "MSSQL", 5900: "VNC", 8080: "HTTP-Alt", 8443: "HTTPS-Alt",
            554: "RTSP", 1723: "PPTP", 1194: "OpenVPN", 500: "IPSec",
            4500: "IPSec-NAT", 135: "RPC", 139: "NetBIOS", 445: "SMB",
            389: "LDAP", 636: "LDAPS", 161: "SNMP", 162: "SNMP-Trap",
            69: "TFTP", 123: "NTP", 179: "BGP", 515: "LPD", 631: "IPP",
            993: "IMAPS", 995: "POP3S", 587: "SMTP-Sub", 465: "SMTPS"
        }
    
    def run(self):
        """Run port scan operation."""
        try:
            total_ports = self.end_port - self.start_port + 1
            
            # Use ThreadPoolExecutor for concurrent scanning
            with ThreadPoolExecutor(max_workers=50) as executor:
                # Submit all port scan tasks
                future_to_port = {
                    executor.submit(self._scan_port, port): port
                    for port in range(self.start_port, self.end_port + 1)
                }
                
                completed = 0
                for future in as_completed(future_to_port):
                    if not self.running:
                        break
                    
                    port = future_to_port[future]
                    try:
                        is_open = future.result()
                        service = self.services.get(port, "Unknown")
                        self.port_result.emit(self.host, port, is_open, service)
                    except Exception as e:
                        self.port_result.emit(self.host, port, False, "Error")
                    
                    completed += 1
                    self.scan_progress.emit(port)
        
        except Exception as e:
            pass
        
        finally:
            self.scan_finished.emit()
    
    def _scan_port(self, port: int) -> bool:
        """Scan a single port."""
        if not self.running:
            return False
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.host, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def stop(self):
        """Stop the port scan operation."""
        self.running = False


class NetworkScannerDialog(QDialog):
    """Network scanner dialog with ping and port scan capabilities."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Network Scanner & Port Discovery")
        self.setGeometry(200, 200, 900, 700)
        self.setModal(False)  # Allow interaction with main window
        
        # Worker threads
        self.ping_worker = None
        self.port_worker = None
        
        self._setup_ui()
        self._setup_connections()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Ping tab
        self.ping_tab = self._create_ping_tab()
        self.tab_widget.addTab(self.ping_tab, "🏓 Ping Tool")
        
        # Port scan tab
        self.port_tab = self._create_port_scan_tab()
        self.tab_widget.addTab(self.port_tab, "🔍 Port Scanner")
        
        # Close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        self.close_button = QPushButton("Close")
        close_layout.addWidget(self.close_button)
        layout.addLayout(close_layout)
    
    def _create_ping_tab(self) -> QWidget:
        """Create the ping tool tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Input section
        input_group = QGroupBox("Ping Configuration")
        input_layout = QVBoxLayout(input_group)
        
        # Host input
        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel("Host/IP:"))
        self.ping_host_edit = QLineEdit()
        self.ping_host_edit.setPlaceholderText("Enter hostname or IP address (e.g., google.com, 8.8.8.8)")
        host_layout.addWidget(self.ping_host_edit)
        input_layout.addLayout(host_layout)
        
        # Count input
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("Count:"))
        self.ping_count_spin = QSpinBox()
        self.ping_count_spin.setRange(1, 100)
        self.ping_count_spin.setValue(4)
        count_layout.addWidget(self.ping_count_spin)
        count_layout.addStretch()
        
        # Continuous ping checkbox
        self.continuous_ping_check = QCheckBox("Continuous Ping")
        count_layout.addWidget(self.continuous_ping_check)
        
        input_layout.addLayout(count_layout)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.ping_start_button = QPushButton("Start Ping")
        self.ping_stop_button = QPushButton("Stop Ping")
        self.ping_stop_button.setEnabled(False)
        self.ping_clear_button = QPushButton("Clear Results")
        
        button_layout.addWidget(self.ping_start_button)
        button_layout.addWidget(self.ping_stop_button)
        button_layout.addWidget(self.ping_clear_button)
        button_layout.addStretch()
        
        input_layout.addLayout(button_layout)
        layout.addWidget(input_group)
        
        # Results section
        results_group = QGroupBox("Ping Results")
        results_layout = QVBoxLayout(results_group)
        
        # Statistics
        stats_layout = QHBoxLayout()
        self.ping_stats_label = QLabel("Ready to ping...")
        stats_layout.addWidget(self.ping_stats_label)
        results_layout.addLayout(stats_layout)
        
        # Results text area
        self.ping_results = QTextEdit()
        self.ping_results.setReadOnly(True)
        self.ping_results.setFont(QFont("Consolas", 9))
        results_layout.addWidget(self.ping_results)
        
        layout.addWidget(results_group)
        
        return tab
    
    def _create_port_scan_tab(self) -> QWidget:
        """Create the port scanner tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Input section
        input_group = QGroupBox("Port Scan Configuration")
        input_layout = QVBoxLayout(input_group)
        
        # Host input
        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel("Host/IP:"))
        self.scan_host_edit = QLineEdit()
        self.scan_host_edit.setPlaceholderText("Enter hostname or IP address")
        host_layout.addWidget(self.scan_host_edit)
        input_layout.addLayout(host_layout)
        
        # Port range
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port Range:"))
        self.start_port_spin = QSpinBox()
        self.start_port_spin.setRange(1, 65535)
        self.start_port_spin.setValue(1)
        port_layout.addWidget(self.start_port_spin)
        
        port_layout.addWidget(QLabel("to"))
        self.end_port_spin = QSpinBox()
        self.end_port_spin.setRange(1, 65535)
        self.end_port_spin.setValue(1000)
        port_layout.addWidget(self.end_port_spin)
        
        # Quick presets
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Quick Scan:"))
        
        self.common_ports_button = QPushButton("Common Ports")
        self.common_ports_button.setToolTip("Scan common service ports (21,22,23,25,53,80,110,143,443,993,995,3389)")
        preset_layout.addWidget(self.common_ports_button)
        
        self.web_ports_button = QPushButton("Web Ports")
        self.web_ports_button.setToolTip("Scan web-related ports (80,443,8080,8443,8000,3000,5000,9000)")
        preset_layout.addWidget(self.web_ports_button)
        
        self.db_ports_button = QPushButton("Database Ports")
        self.db_ports_button.setToolTip("Scan database ports (3306,5432,1433,1521,6379,27017)")
        preset_layout.addWidget(self.db_ports_button)
        
        preset_layout.addStretch()
        
        input_layout.addLayout(port_layout)
        input_layout.addLayout(preset_layout)
        
        # Timeout setting
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Timeout (sec):"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 10)
        self.timeout_spin.setValue(2)
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addStretch()
        input_layout.addLayout(timeout_layout)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.scan_start_button = QPushButton("Start Scan")
        self.scan_stop_button = QPushButton("Stop Scan")
        self.scan_stop_button.setEnabled(False)
        self.scan_clear_button = QPushButton("Clear Results")
        
        button_layout.addWidget(self.scan_start_button)
        button_layout.addWidget(self.scan_stop_button)
        button_layout.addWidget(self.scan_clear_button)
        button_layout.addStretch()
        
        input_layout.addLayout(button_layout)
        layout.addWidget(input_group)
        
        # Progress bar
        self.scan_progress = QProgressBar()
        self.scan_progress.setVisible(False)
        layout.addWidget(self.scan_progress)
        
        # Results section
        results_splitter = QSplitter(Qt.Vertical)
        
        # Open ports table
        open_group = QGroupBox("Open Ports")
        open_layout = QVBoxLayout(open_group)
        
        self.open_ports_table = QTableWidget()
        self.open_ports_table.setColumnCount(3)
        self.open_ports_table.setHorizontalHeaderLabels(["Port", "Service", "Status"])
        self.open_ports_table.horizontalHeader().setStretchLastSection(True)
        open_layout.addWidget(self.open_ports_table)
        
        # Statistics
        self.scan_stats_label = QLabel("Ready to scan...")
        open_layout.addWidget(self.scan_stats_label)
        
        results_splitter.addWidget(open_group)
        
        # Scan log
        log_group = QGroupBox("Scan Log")
        log_layout = QVBoxLayout(log_group)
        
        self.scan_log = QTextEdit()
        self.scan_log.setReadOnly(True)
        self.scan_log.setFont(QFont("Consolas", 8))
        self.scan_log.setMaximumHeight(150)
        log_layout.addWidget(self.scan_log)
        
        results_splitter.addWidget(log_group)
        
        layout.addWidget(results_splitter)
        
        return tab
    
    def _setup_connections(self):
        """Setup signal connections."""
        # Ping tab connections
        self.ping_start_button.clicked.connect(self._start_ping)
        self.ping_stop_button.clicked.connect(self._stop_ping)
        self.ping_clear_button.clicked.connect(self._clear_ping_results)
        self.ping_host_edit.returnPressed.connect(self._start_ping)
        
        # Port scan tab connections
        self.scan_start_button.clicked.connect(self._start_port_scan)
        self.scan_stop_button.clicked.connect(self._stop_port_scan)
        self.scan_clear_button.clicked.connect(self._clear_scan_results)
        self.scan_host_edit.returnPressed.connect(self._start_port_scan)
        
        # Preset buttons
        self.common_ports_button.clicked.connect(self._set_common_ports)
        self.web_ports_button.clicked.connect(self._set_web_ports)
        self.db_ports_button.clicked.connect(self._set_db_ports)
        
        # Close button
        self.close_button.clicked.connect(self.close)
    
    def _start_ping(self):
        """Start ping operation."""
        host = self.ping_host_edit.text().strip()
        if not host:
            QMessageBox.warning(self, "Input Error", "Please enter a host or IP address.")
            return
        
        count = self.ping_count_spin.value() if not self.continuous_ping_check.isChecked() else 999999
        
        self.ping_start_button.setEnabled(False)
        self.ping_stop_button.setEnabled(True)
        
        self.ping_results.append(f"Starting ping to {host}...\n")
        
        self.ping_worker = PingWorker(host, count)
        self.ping_worker.ping_result.connect(self._handle_ping_result)
        self.ping_worker.ping_finished.connect(self._ping_finished)
        self.ping_worker.start()
        
        # Initialize stats
        self.ping_sent = 0
        self.ping_received = 0
        self.ping_times = []
    
    def _stop_ping(self):
        """Stop ping operation."""
        if self.ping_worker:
            self.ping_worker.stop()
    
    def _ping_finished(self):
        """Handle ping operation completion."""
        self.ping_start_button.setEnabled(True)
        self.ping_stop_button.setEnabled(False)
        
        if self.ping_worker:
            self.ping_worker.wait()
            self.ping_worker = None
        
        # Show final statistics
        if self.ping_times:
            avg_time = sum(self.ping_times) / len(self.ping_times)
            min_time = min(self.ping_times)
            max_time = max(self.ping_times)
            
            loss_rate = ((self.ping_sent - self.ping_received) / self.ping_sent) * 100 if self.ping_sent > 0 else 0
            
            self.ping_results.append(f"\n--- Ping Statistics ---")
            self.ping_results.append(f"Packets: Sent = {self.ping_sent}, Received = {self.ping_received}, Lost = {self.ping_sent - self.ping_received} ({loss_rate:.1f}% loss)")
            self.ping_results.append(f"Round-trip times: Min = {min_time:.1f}ms, Max = {max_time:.1f}ms, Avg = {avg_time:.1f}ms\n")
    
    def _handle_ping_result(self, host: str, success: bool, response_time: float):
        """Handle individual ping result."""
        self.ping_sent += 1
        
        if success:
            self.ping_received += 1
            self.ping_times.append(response_time)
            self.ping_results.append(f"Reply from {host}: time={response_time:.1f}ms")
        else:
            self.ping_results.append(f"Request timeout for {host}")
        
        # Update statistics
        loss_rate = ((self.ping_sent - self.ping_received) / self.ping_sent) * 100 if self.ping_sent > 0 else 0
        self.ping_stats_label.setText(f"Sent: {self.ping_sent}, Received: {self.ping_received}, Loss: {loss_rate:.1f}%")
        
        # Auto-scroll to bottom
        cursor = self.ping_results.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.ping_results.setTextCursor(cursor)
    
    def _clear_ping_results(self):
        """Clear ping results."""
        self.ping_results.clear()
        self.ping_stats_label.setText("Ready to ping...")
    
    def _start_port_scan(self):
        """Start port scan operation."""
        host = self.scan_host_edit.text().strip()
        if not host:
            QMessageBox.warning(self, "Input Error", "Please enter a host or IP address.")
            return
        
        start_port = self.start_port_spin.value()
        end_port = self.end_port_spin.value()
        
        if start_port > end_port:
            QMessageBox.warning(self, "Input Error", "Start port must be less than or equal to end port.")
            return
        
        timeout = self.timeout_spin.value()
        
        self.scan_start_button.setEnabled(False)
        self.scan_stop_button.setEnabled(True)
        self.scan_progress.setVisible(True)
        self.scan_progress.setRange(start_port, end_port)
        
        # Clear previous results
        self.open_ports_table.setRowCount(0)
        self.scan_log.clear()
        
        self.scan_log.append(f"Starting port scan on {host}:{start_port}-{end_port}...")
        
        self.port_worker = PortScanWorker(host, start_port, end_port, timeout)
        self.port_worker.port_result.connect(self._handle_port_result)
        self.port_worker.scan_progress.connect(self._update_scan_progress)
        self.port_worker.scan_finished.connect(self._scan_finished)
        self.port_worker.start()
        
        # Initialize stats
        self.scanned_ports = 0
        self.open_ports_count = 0
        self.total_ports = end_port - start_port + 1
    
    def _stop_port_scan(self):
        """Stop port scan operation."""
        if self.port_worker:
            self.port_worker.stop()
    
    def _scan_finished(self):
        """Handle scan operation completion."""
        self.scan_start_button.setEnabled(True)
        self.scan_stop_button.setEnabled(False)
        self.scan_progress.setVisible(False)
        
        if self.port_worker:
            self.port_worker.wait()
            self.port_worker = None
        
        self.scan_log.append(f"\nScan completed. Found {self.open_ports_count} open ports out of {self.scanned_ports} scanned.")
    
    def _handle_port_result(self, host: str, port: int, is_open: bool, service: str):
        """Handle individual port scan result."""
        self.scanned_ports += 1
        
        if is_open:
            self.open_ports_count += 1
            
            # Add to open ports table
            row = self.open_ports_table.rowCount()
            self.open_ports_table.insertRow(row)
            
            port_item = QTableWidgetItem(str(port))
            service_item = QTableWidgetItem(service)
            status_item = QTableWidgetItem("Open")
            status_item.setBackground(QColor(144, 238, 144))  # Light green
            
            self.open_ports_table.setItem(row, 0, port_item)
            self.open_ports_table.setItem(row, 1, service_item)
            self.open_ports_table.setItem(row, 2, status_item)
            
            self.scan_log.append(f"Port {port} ({service}) - OPEN")
        
        # Update statistics
        self.scan_stats_label.setText(f"Scanned: {self.scanned_ports}/{self.total_ports}, Open: {self.open_ports_count}")
    
    def _update_scan_progress(self, current_port: int):
        """Update scan progress."""
        self.scan_progress.setValue(current_port)
    
    def _clear_scan_results(self):
        """Clear scan results."""
        self.open_ports_table.setRowCount(0)
        self.scan_log.clear()
        self.scan_stats_label.setText("Ready to scan...")
    
    def _set_common_ports(self):
        """Set common ports range."""
        # Most common service ports
        common_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 3389, 5432, 3306]
        self._set_custom_ports(common_ports)
    
    def _set_web_ports(self):
        """Set web-related ports."""
        web_ports = [80, 443, 8080, 8443, 8000, 3000, 5000, 9000, 8008, 8888]
        self._set_custom_ports(web_ports)
    
    def _set_db_ports(self):
        """Set database ports."""
        db_ports = [3306, 5432, 1433, 1521, 6379, 27017, 5984, 9200, 11211]
        self._set_custom_ports(db_ports)
    
    def _set_custom_ports(self, ports: List[int]):
        """Set custom port range for scanning specific ports."""
        if ports:
            min_port = min(ports)
            max_port = max(ports)
            self.start_port_spin.setValue(min_port)
            self.end_port_spin.setValue(max_port)
            
            # Log which ports will be scanned
            port_list = ", ".join(map(str, sorted(ports)))
            self.scan_log.append(f"Quick scan preset selected. Will scan ports: {port_list}")
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        # Stop any running operations
        if self.ping_worker:
            self.ping_worker.stop()
            self.ping_worker.wait()
        
        if self.port_worker:
            self.port_worker.stop()
            self.port_worker.wait()
        
        event.accept()


class NetworkScannerManager:
    """Manager class for network scanning functionality."""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.dialog = None
    
    def show_scanner(self):
        """Show the network scanner dialog."""
        if self.dialog is None:
            self.dialog = NetworkScannerDialog(self.parent)
        
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()
    
    def scan_host_quick(self, host: str) -> Dict:
        """Quick scan of a host (ping + common ports) - returns results."""
        results = {
            'host': host,
            'ping_success': False,
            'ping_time': 0.0,
            'open_ports': []
        }
        
        # Quick ping test
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            # Try to resolve hostname and connect to a common port
            result = sock.connect_ex((host, 80))
            sock.close()
            
            if result == 0:
                results['ping_success'] = True
                results['ping_time'] = (time.time() - start_time) * 1000
        except Exception:
            pass
        
        # Quick port scan of most common ports
        common_ports = [21, 22, 23, 25, 53, 80, 135, 139, 443, 445, 3389]
        
        def scan_port(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                sock.close()
                return port if result == 0 else None
            except Exception:
                return None
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(scan_port, port) for port in common_ports]
            for future in as_completed(futures):
                port = future.result()
                if port:
                    results['open_ports'].append(port)
        
        return results
