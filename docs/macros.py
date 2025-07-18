"""
MkDocs macros for dynamic content generation.
"""

import requests
import os
import subprocess
import re


def define_env(env):
    """Define macros for MkDocs."""
    
    def get_git_tag_version():
        """Get version from current Git tag if available."""
        try:
            # Check if we're on a tag
            result = subprocess.run(
                ["git", "describe", "--exact-match", "--tags", "HEAD"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                tag = result.stdout.strip()
                # Extract version from tag (remove 'v' prefix if present)
                if tag.startswith('v'):
                    return tag[1:]
                return tag
        except:
            pass
        
        # Try to get version from environment variable (for CI)
        env_version = os.environ.get("PACKAGE_VERSION")
        if env_version:
            return env_version
            
        return None
    
    @env.macro
    def pypi_version(package_name="ssh-tools-suite"):
        """Get the latest version, preferring Git tag over PyPI."""
        # First try to get version from Git tag (for builds from tags)
        git_version = get_git_tag_version()
        if git_version:
            return git_version
            
        # Fallback to PyPI API
        try:
            response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data["info"]["version"]
        except:
            pass
        
        # Final fallback - use a generic placeholder instead of old version
        return "latest"
    
    @env.macro
    def pip_install_cmd(package_name="ssh-tools-suite"):
        """Generate pip install command with latest version."""
        version = pypi_version(package_name)
        if version == "latest" or not version:
            return f"pip install {package_name}"
        return f"pip install {package_name}=={version}"
    
    @env.macro
    def pip_install_dev():
        """Generate pip install command with dev dependencies."""
        version = pypi_version()
        if version == "latest" or not version:
            return "pip install ssh-tools-suite[dev]"
        return f"pip install ssh-tools-suite[dev]=={version}"
    
    @env.macro
    def pip_install_docs():
        """Generate pip install command with docs dependencies."""
        version = pypi_version()
        if version == "latest" or not version:
            return "pip install ssh-tools-suite[docs]"
        return f"pip install ssh-tools-suite[docs]=={version}"
    
    @env.macro
    def pip_install_all():
        """Generate pip install command with all dependencies."""
        version = pypi_version()
        if version == "latest" or not version:
            return "pip install ssh-tools-suite[dev,docs]"
        return f"pip install ssh-tools-suite[dev,docs]=={version}"
    
    @env.macro
    def download_filename(base_name="SSH-Tunnel-Manager"):
        """Generate download filename with current version."""
        version = pypi_version()
        if version == "latest" or not version:
            return f"{base_name}-latest-Windows.zip"
        return f"{base_name}-v{version}-Windows.zip"
    
    @env.macro
    def download_link(filename_template):
        """Generate download links with current version."""
        version = pypi_version()
        return filename_template.replace("*.*.*", version)
    
    @env.macro
    def github_release_url(repo="NicholasKozma/ssh_tools_suite"):
        """Generate GitHub releases URL."""
        return f"https://github.com/{repo}/releases/latest"
    
    @env.macro
    def pypi_url(package_name="ssh-tools-suite"):
        """Generate PyPI package URL."""
        return f"https://pypi.org/project/{package_name}/"
