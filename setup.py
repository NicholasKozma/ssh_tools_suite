#!/usr/bin/env python3
"""
Setup script for SSH Tunnel Manager
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "docs" / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = requirements_file.read_text(encoding="utf-8").strip().split("\n")

setup(
    name="ssh-tunnel-manager",
    version="1.0.0",
    author="Nicholas Kozma",
    author_email="Nicholas.Kozma@us.bosch.com",
    description="SSH Tunnel Manager - Comprehensive SSH tunnel management application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NicholasKozma/ssh_tools_suite",
    project_urls={
        "Bug Reports": "https://github.com/NicholasKozma/ssh_tools_suite/issues",
        "Source": "https://github.com/NicholasKozma/ssh_tools_suite",
        "Documentation": "https://ssh-tunnel-manager.readthedocs.io/",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    package_data={
        "ssh_tunnel_manager": ["*.md", "*.txt", "*.ini"],
        "ssh_installer": ["*.md", "*.txt", "*.ini"],
        "third_party_installer": ["*.md", "*.txt", "*.ini"],
        "ssh_tools_common": ["*.md", "*.txt", "*.ini"],
    },
    data_files=[
        ("licenses", ["licenses/THIRD_PARTY_LICENSES.md"]),
    ],
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "mkdocs>=1.4.0",
            "mkdocs-material>=8.0.0",
        ],
        "gui": [
            "PySide6>=6.4.0",
        ],
        "rtsp": [
            "opencv-python>=4.6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ssh-tunnel-manager=ssh_tunnel_manager.__main__:main",
            "third-party-installer=third_party_installer.__main__:main",
        ],
        "gui_scripts": [
            "ssh-tunnel-manager-gui=ssh_tunnel_manager.gui.__main__:main",
            "third-party-installer-gui=third_party_installer.gui.main_window:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "Topic :: Security",
        "Topic :: Multimedia :: Video",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Win32 (MS Windows)",
    ],
    python_requires=">=3.8",
    keywords="ssh tunnel manager rtsp streaming network security proxy port-forwarding gui",
    license="MIT",
    zip_safe=False,
)
