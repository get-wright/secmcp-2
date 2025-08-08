#!/usr/bin/env python3
"""
Setup script for CrewAI Subdomain Enumeration Agent
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file) as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="crewai-subdomain-enumeration",
    version="1.0.0",
    description="CrewAI agent for subdomain enumeration using MCP servers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Cybersecurity Specialist",
    author_email="security@example.com",
    url="https://github.com/example/crewai-subdomain-enumeration",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json"],
    },
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Internet :: Name Service (DNS)",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="crewai, subdomain, enumeration, security, reconnaissance, mcp, amass",
    entry_points={
        "console_scripts": [
            "subdomain-enum=main:main",
        ],
    },
)
