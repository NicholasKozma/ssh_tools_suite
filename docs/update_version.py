"""
Dynamic version fetcher for MkDocs documentation.
This script fetches the latest version from PyPI and updates documentation.
"""

import requests
import json
import os
import re
from pathlib import Path


def get_latest_pypi_version(package_name="ssh-tools-suite"):
    """Fetch the latest version from PyPI."""
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
        response.raise_for_status()
        data = response.json()
        return data["info"]["version"]
    except Exception as e:
        print(f"Error fetching version from PyPI: {e}")
        return None


def get_github_latest_release(repo="NicholasKozma/ssh_tools_suite"):
    """Fetch the latest release from GitHub."""
    try:
        response = requests.get(f"https://api.github.com/repos/{repo}/releases/latest")
        response.raise_for_status()
        data = response.json()
        return data["tag_name"].lstrip("v")
    except Exception as e:
        print(f"Error fetching release from GitHub: {e}")
        return None


def update_version_in_file(file_path, version):
    """Update version references in a documentation file."""
    if not os.path.exists(file_path):
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update pip install commands
    content = re.sub(
        r'pip install ssh-tools-suite(?:==[\d\.]+)?',
        f'pip install ssh-tools-suite=={version}',
        content
    )
    
    # Update download links
    content = re.sub(
        r'SSH-Tunnel-Manager-v\*\.\*\.\*',
        f'SSH-Tunnel-Manager-v{version}',
        content
    )
    content = re.sub(
        r'SSH-Tools-Installer-v\*\.\*\.\*',
        f'SSH-Tools-Installer-v{version}',
        content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True


def main():
    """Main function to update documentation."""
    print("🔍 Fetching latest version information...")
    
    # Get version from PyPI (primary source)
    pypi_version = get_latest_pypi_version()
    
    # Fallback to GitHub if PyPI fails
    if not pypi_version:
        print("⚠️  PyPI version fetch failed, trying GitHub...")
        pypi_version = get_github_latest_release()
    
    if not pypi_version:
        print("❌ Could not fetch version information")
        return False
    
    print(f"📦 Latest version: {pypi_version}")
    
    # Files to update
    docs_files = [
        "docs/index.md",
        "docs/getting-started/installation.md",
        "docs/getting-started/quick-start.md",
    ]
    
    updated_files = []
    for file_path in docs_files:
        if update_version_in_file(file_path, pypi_version):
            updated_files.append(file_path)
            print(f"✅ Updated {file_path}")
        else:
            print(f"⚠️  Skipped {file_path} (not found)")
    
    if updated_files:
        print(f"🎉 Successfully updated {len(updated_files)} files with version {pypi_version}")
        return True
    else:
        print("ℹ️  No files were updated")
        return False


if __name__ == "__main__":
    main()
