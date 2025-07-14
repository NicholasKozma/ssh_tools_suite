# RTSP Streaming Guide

Complete guide for RTSP streaming capabilities in SSH Tools Suite.

## Overview

Real-Time Streaming Protocol (RTSP) support in SSH Tools Suite enables secure access to video streams through SSH tunnels. This guide covers setup, configuration, and troubleshooting of RTSP streaming.

## RTSP Basics

### What is RTSP?

RTSP is a network control protocol for controlling streaming media servers. It's commonly used for:

- **IP Cameras**: Security and surveillance systems
- **Video Servers**: Media streaming servers
- **Live Streaming**: Real-time video/audio streaming
- **Remote Monitoring**: Accessing cameras over networks

### RTSP URLs

Common RTSP URL formats:

```
rtsp://camera.example.com:554/stream1
rtsp://admin:password@192.168.1.100:554/live
rtsp://camera.local:8554/stream/live.sdp
```

## SSH Tunnel Setup for RTSP

### Basic RTSP Tunnel Configuration

```python
from ssh_tunnel_manager.core.models import TunnelConfig

rtsp_tunnel = TunnelConfig(
    name="security-camera-1",
    description="Main entrance security camera",
    ssh_host="gateway.company.com",
    ssh_username="camera_user",
    ssh_key_path="~/.ssh/id_rsa_cameras",
    local_port=8554,
    remote_host="camera1.internal.company.com",
    remote_port=554,
    tags=["rtsp", "camera", "security"]
)
```

### Multiple Camera Setup

```python
# Camera 1 - Main entrance
camera1_tunnel = TunnelConfig(
    name="camera-entrance",
    ssh_host="gateway.company.com",
    ssh_username="camera_user",
    local_port=8554,
    remote_host="camera1.internal",
    remote_port=554
)

# Camera 2 - Parking lot
camera2_tunnel = TunnelConfig(
    name="camera-parking",
    ssh_host="gateway.company.com", 
    ssh_username="camera_user",
    local_port=8555,
    remote_host="camera2.internal",
    remote_port=554
)

# Camera 3 - Back entrance
camera3_tunnel = TunnelConfig(
    name="camera-back",
    ssh_host="gateway.company.com",
    ssh_username="camera_user", 
    local_port=8556,
    remote_host="camera3.internal",
    remote_port=554
)
```

## RTSP Viewer Integration

### Built-in RTSP Viewer

The SSH Tunnel Manager includes an integrated RTSP viewer:

```python
from ssh_tunnel_manager.utils.rtsp_viewer import RTSPViewer

# Create RTSP viewer instance
viewer = RTSPViewer()

# Open stream through tunnel
stream_url = "rtsp://localhost:8554/stream1"
viewer.open_stream(stream_url)

# Configure viewer settings
viewer.set_buffer_size(1024 * 1024)  # 1MB buffer
viewer.set_timeout(30)  # 30 second timeout
viewer.enable_audio(True)
```

### Viewer Controls

```python
# Playback controls
viewer.play()
viewer.pause()
viewer.stop()

# Stream quality
viewer.set_quality("high")  # high, medium, low
viewer.set_resolution(1920, 1080)

# Recording
viewer.start_recording("camera1_recording.mp4")
viewer.stop_recording()

# Snapshots
viewer.take_snapshot("camera1_snapshot.jpg")
```

## VLC Media Player Integration

### Using VLC for RTSP Streams

VLC Media Player provides excellent RTSP support:

1. **Install VLC** through Third Party Installer:
   ```python
   from third_party_installer.core.installer import ThirdPartyInstaller
   
   installer = ThirdPartyInstaller()
   installer.install_tool('vlc')
   ```

2. **Open RTSP stream** in VLC:
   - Media → Open Network Stream
   - Enter: `rtsp://localhost:8554/stream1`
   - Click Play

### VLC Command Line

```bash
# Basic RTSP playback
vlc rtsp://localhost:8554/stream1

# Record stream to file
vlc rtsp://localhost:8554/stream1 --sout=file/mp4:recording.mp4

# Multiple streams in playlist
vlc rtsp://localhost:8554/camera1 rtsp://localhost:8555/camera2

# Stream with specific options
vlc rtsp://localhost:8554/stream1 --network-caching=1000 --rtsp-tcp
```

### VLC Automation

```python
import subprocess

def open_rtsp_in_vlc(rtsp_url: str, fullscreen: bool = False):
    """Open RTSP stream in VLC"""
    cmd = ["vlc", rtsp_url]
    
    if fullscreen:
        cmd.append("--fullscreen")
    
    # Additional VLC options
    cmd.extend([
        "--network-caching=1000",  # 1 second network cache
        "--rtsp-tcp",              # Use TCP for RTSP
        "--intf=dummy",            # No interface for automation
    ])
    
    return subprocess.Popen(cmd)

# Usage
vlc_process = open_rtsp_in_vlc("rtsp://localhost:8554/camera1", fullscreen=True)
```

## Advanced RTSP Configuration

### RTSP over TCP

For better reliability through SSH tunnels:

```python
rtsp_tunnel = TunnelConfig(
    name="camera-tcp",
    # ... other config ...
    tunnel_options={
        "rtsp_transport": "tcp",
        "network_caching": 1000
    }
)
```

### Authentication

```python
# RTSP with authentication
authenticated_tunnel = TunnelConfig(
    name="secure-camera",
    description="Camera with authentication",
    ssh_host="gateway.company.com",
    local_port=8554,
    remote_host="secure-camera.internal",
    remote_port=554,
    rtsp_username="camera_admin",
    rtsp_password="secure_password"
)
```

### Stream Multiplexing

```python
def create_camera_bank(base_port: int, camera_configs: list):
    """Create multiple camera tunnels"""
    tunnels = []
    
    for i, camera in enumerate(camera_configs):
        tunnel = TunnelConfig(
            name=f"camera-{camera['name']}",
            description=f"Camera: {camera['description']}",
            ssh_host=camera['gateway'],
            ssh_username="camera_user",
            local_port=base_port + i,
            remote_host=camera['host'],
            remote_port=camera.get('port', 554),
            tags=["rtsp", "camera", camera.get('location', 'unknown')]
        )
        tunnels.append(tunnel)
    
    return tunnels

# Camera configuration
cameras = [
    {"name": "entrance", "description": "Main entrance", "host": "cam1.internal", "gateway": "gw1.company.com"},
    {"name": "parking", "description": "Parking lot", "host": "cam2.internal", "gateway": "gw1.company.com"},
    {"name": "warehouse", "description": "Warehouse floor", "host": "cam3.internal", "gateway": "gw2.company.com"}
]

camera_tunnels = create_camera_bank(8554, cameras)
```

## Stream Recording and Processing

### Recording Streams

```python
import cv2

def record_rtsp_stream(rtsp_url: str, output_file: str, duration: int = 60):
    """Record RTSP stream using OpenCV"""
    cap = cv2.VideoCapture(rtsp_url)
    
    # Get stream properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))
    
    start_time = time.time()
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        out.write(frame)
        
        # Check duration
        if time.time() - start_time > duration:
            break
    
    cap.release()
    out.release()

# Usage
record_rtsp_stream("rtsp://localhost:8554/camera1", "security_recording.mp4", 300)  # 5 minutes
```

### Motion Detection

```python
def detect_motion_rtsp(rtsp_url: str, sensitivity: float = 0.1):
    """Basic motion detection on RTSP stream"""
    cap = cv2.VideoCapture(rtsp_url)
    
    # Background subtractor
    backSub = cv2.createBackgroundSubtractorMOG2()
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Apply background subtraction
        fgMask = backSub.apply(frame)
        
        # Calculate motion percentage
        motion_pixels = cv2.countNonZero(fgMask)
        total_pixels = fgMask.shape[0] * fgMask.shape[1]
        motion_percentage = motion_pixels / total_pixels
        
        if motion_percentage > sensitivity:
            print(f"Motion detected: {motion_percentage:.2%}")
            # Trigger action (save frame, send alert, etc.)
            cv2.imwrite(f"motion_{int(time.time())}.jpg", frame)
        
        # Display frame (optional)
        cv2.imshow('RTSP Stream', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
```

## Multi-Stream Dashboard

### Creating a Video Wall

```python
import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk

class RTSPDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("RTSP Camera Dashboard")
        self.cameras = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dashboard UI"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Camera grid
        self.camera_frame = ttk.Frame(main_frame)
        self.camera_frame.pack(fill=tk.BOTH, expand=True)
        
        # Control panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Add Camera", command=self.add_camera).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="Start All", command=self.start_all).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="Stop All", command=self.stop_all).pack(side=tk.LEFT)
    
    def add_camera(self, name: str, rtsp_url: str, position: tuple):
        """Add camera to dashboard"""
        camera_widget = CameraWidget(self.camera_frame, name, rtsp_url)
        camera_widget.grid(row=position[0], column=position[1], padx=2, pady=2)
        self.cameras[name] = camera_widget
    
    def start_all(self):
        """Start all camera streams"""
        for camera in self.cameras.values():
            camera.start_stream()
    
    def stop_all(self):
        """Stop all camera streams"""
        for camera in self.cameras.values():
            camera.stop_stream()

class CameraWidget(ttk.Frame):
    def __init__(self, parent, name: str, rtsp_url: str):
        super().__init__(parent)
        self.name = name
        self.rtsp_url = rtsp_url
        self.cap = None
        self.is_running = False
        
        self.setup_widget()
    
    def setup_widget(self):
        """Setup camera widget"""
        # Title
        ttk.Label(self, text=self.name).pack()
        
        # Video canvas
        self.canvas = tk.Canvas(self, width=320, height=240, bg='black')
        self.canvas.pack()
        
        # Controls
        control_frame = ttk.Frame(self)
        control_frame.pack()
        
        ttk.Button(control_frame, text="Start", command=self.start_stream).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="Stop", command=self.stop_stream).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="Snapshot", command=self.take_snapshot).pack(side=tk.LEFT)
    
    def start_stream(self):
        """Start RTSP stream"""
        if not self.is_running:
            self.cap = cv2.VideoCapture(self.rtsp_url)
            self.is_running = True
            self.update_frame()
    
    def stop_stream(self):
        """Stop RTSP stream"""
        self.is_running = False
        if self.cap:
            self.cap.release()
    
    def update_frame(self):
        """Update video frame"""
        if self.is_running and self.cap:
            ret, frame = self.cap.read()
            if ret:
                # Resize frame
                frame = cv2.resize(frame, (320, 240))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to PIL and display
                image = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image)
                
                self.canvas.delete("all")
                self.canvas.create_image(160, 120, image=photo)
                self.canvas.image = photo
            
            # Schedule next frame
            self.after(33, self.update_frame)  # ~30 FPS
    
    def take_snapshot(self):
        """Take snapshot of current frame"""
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                filename = f"{self.name}_{int(time.time())}.jpg"
                cv2.imwrite(filename, frame)
                print(f"Snapshot saved: {filename}")

# Usage
dashboard = RTSPDashboard()

# Add cameras
dashboard.add_camera("Entrance", "rtsp://localhost:8554/camera1", (0, 0))
dashboard.add_camera("Parking", "rtsp://localhost:8555/camera2", (0, 1))
dashboard.add_camera("Warehouse", "rtsp://localhost:8556/camera3", (1, 0))
dashboard.add_camera("Exit", "rtsp://localhost:8557/camera4", (1, 1))

dashboard.root.mainloop()
```

## Performance Optimization

### Stream Quality Settings

```python
def optimize_rtsp_settings(tunnel_config: TunnelConfig, quality: str = "medium"):
    """Optimize RTSP settings based on quality preference"""
    
    quality_settings = {
        "low": {
            "resolution": "640x480",
            "bitrate": "512k",
            "fps": 15,
            "buffer_size": 512 * 1024
        },
        "medium": {
            "resolution": "1280x720", 
            "bitrate": "2M",
            "fps": 25,
            "buffer_size": 1024 * 1024
        },
        "high": {
            "resolution": "1920x1080",
            "bitrate": "5M", 
            "fps": 30,
            "buffer_size": 2048 * 1024
        }
    }
    
    settings = quality_settings.get(quality, quality_settings["medium"])
    tunnel_config.rtsp_settings = settings
    
    return tunnel_config
```

### Bandwidth Management

```python
def calculate_bandwidth_requirements(camera_configs: list):
    """Calculate total bandwidth requirements"""
    total_bandwidth = 0
    
    for config in camera_configs:
        settings = config.get('rtsp_settings', {})
        bitrate = settings.get('bitrate', '2M')
        
        # Convert bitrate to bps
        if bitrate.endswith('k'):
            bps = int(bitrate[:-1]) * 1000
        elif bitrate.endswith('M'):
            bps = int(bitrate[:-1]) * 1000000
        else:
            bps = int(bitrate)
        
        total_bandwidth += bps
    
    return total_bandwidth

def recommend_tunnel_compression(bandwidth_mbps: float):
    """Recommend SSH compression based on bandwidth"""
    if bandwidth_mbps > 10:
        return False  # No compression for high bandwidth
    elif bandwidth_mbps > 5:
        return True   # Enable compression for medium bandwidth
    else:
        return True   # Definitely use compression for low bandwidth
```

## Troubleshooting RTSP

### Common Issues

#### Stream Not Loading

**Symptoms:**
- Black screen in viewer
- Connection timeout errors
- "Stream not available" messages

**Solutions:**

1. **Verify tunnel is active**:
   ```python
   tunnel_status = tunnel_manager.get_tunnel_status("camera-tunnel")
   print(f"Tunnel status: {tunnel_status}")
   ```

2. **Test direct connection**:
   ```bash
   # Test without tunnel
   ffplay rtsp://camera.internal:554/stream1
   
   # Test through tunnel
   ffplay rtsp://localhost:8554/stream1
   ```

3. **Check camera accessibility**:
   ```bash
   # From SSH server
   telnet camera.internal 554
   ```

#### Poor Video Quality

**Solutions:**

1. **Increase buffer size**:
   ```python
   viewer.set_buffer_size(4 * 1024 * 1024)  # 4MB
   ```

2. **Enable TCP mode**:
   ```python
   viewer.set_transport_mode("tcp")
   ```

3. **Adjust network caching**:
   ```python
   viewer.set_network_caching(2000)  # 2 seconds
   ```

#### High Latency

**Solutions:**

1. **Reduce buffer size**:
   ```python
   viewer.set_buffer_size(256 * 1024)  # 256KB
   ```

2. **Enable low-latency mode**:
   ```python
   viewer.enable_low_latency(True)
   ```

3. **Use UDP transport** (if stable network):
   ```python
   viewer.set_transport_mode("udp")
   ```

## Security Considerations

### RTSP Security

1. **Use strong authentication** on cameras
2. **Change default passwords** immediately
3. **Enable HTTPS/TLS** where supported
4. **Regular firmware updates** for cameras
5. **Network segmentation** for camera networks

### SSH Tunnel Security

1. **Use key-based authentication** for SSH
2. **Restrict SSH user permissions**
3. **Enable SSH connection logging**
4. **Monitor tunnel usage**

This comprehensive RTSP guide enables secure and efficient video streaming through SSH tunnels using the SSH Tools Suite.
