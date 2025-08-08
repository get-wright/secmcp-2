"""
Setup script for Reconnaissance Agent
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="reconnaissance-agent",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A specialized CrewAI agent for subdomain reconnaissance using Amass MCP server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/reconnaissance-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Topic :: Internet :: Name Service (DNS)",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.991",
        ]
    },
    entry_points={
        "console_scripts": [
            "recon-agent=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.txt"],
    },
    keywords="reconnaissance, subdomain, enumeration, amass, crewai, mcp, security",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/reconnaissance-agent/issues",
        "Source": "https://github.com/yourusername/reconnaissance-agent",
        "Documentation": "https://github.com/yourusername/reconnaissance-agent#readme",
    },
)
