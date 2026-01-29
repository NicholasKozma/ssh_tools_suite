# SSH Tunnel Manager - Style Customization Guide

## Quick Start

The SSH Tunnel Manager now uses a centralized styling system that makes it easy to customize the look and feel of the application.

## File Structure

```
src/ssh_tunnel_manager/gui/
└── styles/
    ├── __init__.py           # Package init
    └── modern_style.py       # Main stylesheet (customize here!)
```

## Changing Colors

### Method 1: Update the COLORS Dictionary

Edit `modern_style.py` and modify the `COLORS` dictionary:

```python
COLORS = {
    # Change primary color from blue to purple
    'primary': '#9C27B0',           # Material Purple
    'primary_dark': '#7B1FA2',      
    'primary_light': '#BA68C8',
    
    # Change success color
    'secondary': '#00BCD4',         # Material Cyan
    'secondary_dark': '#0097A7',
    
    # Keep warnings and errors
    'warning': '#FF9800',
    'error': '#F44336',
    
    # ... rest of colors
}
```

### Method 2: Create a Theme System

Add to `modern_style.py`:

```python
THEMES = {
    'blue': {
        'primary': '#2196F3',
        'primary_dark': '#1976D2',
        'primary_light': '#64B5F6',
    },
    'purple': {
        'primary': '#9C27B0',
        'primary_dark': '#7B1FA2',
        'primary_light': '#BA68C8',
    },
    'green': {
        'primary': '#4CAF50',
        'primary_dark': '#388E3C',
        'primary_light': '#81C784',
    }
}

def get_stylesheet(theme='blue'):
    """Get stylesheet with selected theme."""
    colors = THEMES.get(theme, THEMES['blue'])
    # Update COLORS dict
    COLORS.update(colors)
    return MAIN_STYLESHEET
```

Then in `main_window.py`:

```python
# Apply purple theme
self.setStyleSheet(get_stylesheet('purple'))
```

## Customizing Specific Components

### Buttons

Find the `QPushButton` section in `MAIN_STYLESHEET`:

```python
QPushButton {{
    background-color: #FFFFFF;      # Change button background
    border: 2px solid #E0E0E0;      # Change border thickness/color
    border-radius: 8px;             # Make more/less rounded
    padding: 10px 20px;             # Adjust button size
    font-weight: 600;               # Make text bolder
    min-height: 40px;               # Make buttons taller
}}

QPushButton:hover {{
    background-color: #FF5722;      # Custom hover color
    transform: scale(1.05);         # Add subtle grow effect
}}
```

### Table

Customize the table appearance:

```python
QTableWidget {{
    background-color: #FAFAFA;      # Lighter background
    border: 3px solid #2196F3;      # Thicker blue border
    border-radius: 12px;            # More rounded corners
    gridline-color: #2196F3;        # Blue grid lines (if shown)
}}

QHeaderView::section {{
    background-color: #1565C0;      # Darker blue header
    color: #FFFFFF;                  # White text
    padding: 15px;                   # More padding
    font-size: 11pt;                 # Larger font
    font-weight: 700;                # Bolder text
}}
```

### Log Widget

Customize the terminal-like log:

```python
QTextEdit {{
    background-color: #000000;      # Pure black background
    color: #00FF00;                  # Matrix green text
    border: 2px solid #00FF00;      # Green border
    border-radius: 8px;
    padding: 12px;
    font-family: 'Courier New';     # Different monospace font
    font-size: 11pt;                 # Larger text
}}
```

## Adding New Button Styles

In `toolbar.py`, you can create custom button styles:

```python
def _create_styled_button(self, text: str, style: str = "default") -> QPushButton:
    button = QPushButton(text)
    button.setMinimumHeight(36)
    button.setCursor(Qt.PointingHandCursor)
    
    # Add your custom styles
    if style == "primary":
        button.setObjectName("primary")
    elif style == "success":
        button.setObjectName("success")
    elif style == "danger":
        button.setObjectName("danger")
    elif style == "custom_purple":  # New custom style!
        button.setObjectName("custom_purple")
    
    return button
```

Then add the style to `modern_style.py`:

```python
/* Custom purple button */
QPushButton#custom_purple {{
    background-color: #9C27B0;
    border-color: #9C27B0;
    color: white;
    font-weight: 600;
}}

QPushButton#custom_purple:hover {{
    background-color: #7B1FA2;
}}
```

## Dark Mode

### Creating a Dark Theme

Add this function to `modern_style.py`:

```python
DARK_COLORS = {
    'primary': '#42A5F5',
    'primary_dark': '#1976D2',
    'primary_light': '#90CAF9',
    
    'bg_primary': '#1E1E1E',
    'bg_secondary': '#2D2D30',
    'bg_dark': '#1E1E1E',
    'bg_darker': '#121212',
    
    'text_primary': '#E0E0E0',
    'text_secondary': '#B0B0B0',
    'text_light': '#FFFFFF',
    
    'border': '#3F3F46',
}

def get_dark_stylesheet():
    """Get dark mode stylesheet."""
    # Replace colors in MAIN_STYLESHEET
    dark_style = MAIN_STYLESHEET
    for key, value in DARK_COLORS.items():
        dark_style = dark_style.replace(COLORS[key], value)
    return dark_style
```

Usage:

```python
# In main_window.py
self.setStyleSheet(get_dark_stylesheet())
```

## Font Customization

Change fonts globally:

```python
QWidget {{
    font-family: 'Roboto', 'Helvetica', sans-serif;  # Modern font
    font-size: 11pt;                                  # Larger default
}}

/* Monospace for technical content */
QTextEdit {{
    font-family: 'Fira Code', 'JetBrains Mono', 'Consolas';
    font-size: 10pt;
}}

/* Headers */
QHeaderView::section {{
    font-family: 'Roboto Condensed', 'Arial Narrow';
    font-size: 10pt;
    font-weight: 700;
}}
```

## Animation Effects

Add hover animations:

```python
QPushButton {{
    transition: all 0.3s ease;  # Smooth transitions
}}

QPushButton:hover {{
    transform: translateY(-2px);  # Lift effect
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);  # Shadow
}}
```

## Spacing Adjustments

Make the UI more compact or spacious:

```python
# Compact Mode
QHBoxLayout {{
    spacing: 4px;
}}
QVBoxLayout {{
    spacing: 4px;
}}
QWidget {{
    padding: 4px;
    margin: 2px;
}}

# Spacious Mode
QHBoxLayout {{
    spacing: 16px;
}}
QVBoxLayout {{
    spacing: 16px;
}}
QWidget {{
    padding: 16px;
    margin: 8px;
}}
```

## Log Message Colors

Customize log colors in `log_widget.py`:

```python
def log(self, message: str):
    if 'error' in message.lower():
        color = '#FF1744'  # Brighter red
        prefix = '🔥'      # Fire emoji
    elif 'success' in message.lower():
        color = '#00E676'  # Neon green
        prefix = '🎉'      # Party emoji
    # ... etc
```

## Custom Icons

Replace emoji icons with custom images:

```python
# In toolbar.py
def _create_styled_button(self, text: str, style: str = "default"):
    button = QPushButton()
    
    # Use custom icon instead of emoji
    if "Add" in text:
        icon = QIcon("path/to/add-icon.png")
        button.setIcon(icon)
        button.setText("Add")
    
    return button
```

## Tips for Custom Styling

1. **Test Changes**: Run the app after each change
2. **Use Variables**: Define colors once, reuse everywhere
3. **Follow Hierarchy**: Keep visual hierarchy clear
4. **Accessibility**: Ensure sufficient color contrast
5. **Consistency**: Use the same spacing/radius values
6. **Performance**: Avoid complex gradients/shadows

## Common Customizations

### Increase All Font Sizes (+2pt)
```python
# Find all font-size: XXpt and increase by 2
font-size: 12pt;  # was 10pt
font-size: 13pt;  # was 11pt
```

### Make Everything More Rounded
```python
# Increase all border-radius values
border-radius: 12px;  # was 6px
border-radius: 16px;  # was 8px
```

### Add More Padding
```python
# Increase padding everywhere
padding: 12px 20px;  # was 8px 16px
padding: 16px;       # was 12px
```

### Brighter Colors
```python
COLORS = {
    'primary': '#42A5F5',      # Lighter blue
    'secondary': '#66BB6A',    # Lighter green
    'error': '#EF5350',        # Lighter red
}
```

## Testing Your Changes

1. Save your changes to `modern_style.py`
2. Run the application:
   ```bash
   python ssh_tunnel_manager_app.py
   ```
3. Check all screens and interactions
4. Test hover states and disabled states
5. Verify readability and contrast

## Reverting Changes

Keep a backup of the original `modern_style.py`:
```bash
cp modern_style.py modern_style.py.backup
```

Or use git:
```bash
git checkout modern_style.py
```

## Getting Help

- Check `ui-enhancements-summary.md` for design overview
- See `ui-before-after.md` for comparison
- Qt documentation: https://doc.qt.io/qt-6/stylesheet.html
- Material Design colors: https://material.io/design/color/

## Advanced: Runtime Theme Switching

Add to `main_window.py`:

```python
def switch_theme(self, theme_name: str):
    """Switch application theme at runtime."""
    self.setStyleSheet(get_stylesheet(theme_name))
    self.log(f"Switched to {theme_name} theme")
```

Add a menu item:

```python
# In _setup_menu()
view_menu = menubar.addMenu("View")

blue_theme = QAction("Blue Theme", self)
blue_theme.triggered.connect(lambda: self.switch_theme('blue'))
view_menu.addAction(blue_theme)

purple_theme = QAction("Purple Theme", self)
purple_theme.triggered.connect(lambda: self.switch_theme('purple'))
view_menu.addAction(purple_theme)
```

Enjoy customizing your SSH Tunnel Manager! 🎨
