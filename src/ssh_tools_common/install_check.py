#!/usr/bin/env python3
"""
Installation check utilities for SSH Tools Suite
"""

import sys
from typing import List, Tuple


def check_third_party_tools() -> Tuple[bool, List[str]]:
    """Check if required third-party tools are installed.
    
    Returns:
        Tuple of (all_installed, missing_tools)
    """
    try:
        from third_party_installer.core.installer import ThirdPartyInstaller
        
        installer = ThirdPartyInstaller()
        missing_tools = installer.get_missing_required_tools()
        
        # Get display names
        missing_display_names = []
        for tool_name in missing_tools:
            if tool_name in installer.tools_config:
                missing_display_names.append(installer.tools_config[tool_name].display_name)
            else:
                missing_display_names.append(tool_name)
        
        return len(missing_tools) == 0, missing_display_names
        
    except ImportError:
        # If third_party_installer is not available, assume not installed
        return False, ["Third Party Installer module not found"]
    except Exception:
        # If any error occurs, assume not installed
        return False, ["Error checking installation status"]


def ensure_third_party_tools_installed(app_name: str = "SSH Tools Suite") -> bool:
    """Ensure required third-party tools are installed.
    
    Args:
        app_name: Name of the application being launched
        
    Returns:
        True if all tools are installed, False otherwise
    """
    all_installed, missing_tools = check_third_party_tools()
    
    if not all_installed:
        print(f"❌ {app_name} cannot start - Missing required tools")
        print("=" * 60)
        print("The following required tools are not installed:")
        for tool in missing_tools:
            print(f"  • {tool}")
        print()
        print("To install these tools, run:")
        print("  python -m third_party_installer")
        print("  or")
        print("  third-party-installer")
        print()
        print("Installation must be completed before using SSH Tools Suite.")
        return False
    
    return True


def main():
    """Main function for command-line checking."""
    all_installed, missing_tools = check_third_party_tools()
    
    if all_installed:
        print("✅ All required third-party tools are installed!")
        sys.exit(0)
    else:
        print("❌ Missing required third-party tools:")
        for tool in missing_tools:
            print(f"  • {tool}")
        print()
        print("Run 'python -m third_party_installer' to install missing tools.")
        sys.exit(1)


if __name__ == "__main__":
    main()
