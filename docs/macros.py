"""
MkDocs macros for dynamic content generation.
"""

import requests
import os


def define_env(env):
    """Define macros for MkDocs."""
    
    @env.macro
    def pypi_version(package_name="ssh-tools-suite"):
        """Get the latest version from PyPI."""
        try:
            response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data["info"]["version"]
        except:
            pass
        
        # Fallback to environment variable or default
        return os.environ.get("PACKAGE_VERSION", "1.0.1")
    
    @env.macro
    def pip_install_cmd(package_name="ssh-tools-suite"):
        """Generate pip install command with latest version."""
        version = pypi_version(package_name)
        return f"pip install {package_name}=={version}"
    
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
