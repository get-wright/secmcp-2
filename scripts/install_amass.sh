#!/bin/bash
"""
Installation script for Amass tool
Supports Linux, macOS, and provides instructions for Windows
"""

set -e

echo "🔧 Installing Amass for Subdomain Enumeration"
echo "============================================="

# Detect operating system
OS=$(uname -s)
ARCH=$(uname -m)

case $OS in
    "Linux")
        echo "📦 Detected Linux system"
        
        # Check if running as root or with sudo
        if [[ $EUID -eq 0 ]]; then
            SUDO=""
        else
            SUDO="sudo"
        fi
        
        # Try different package managers
        if command -v apt-get &> /dev/null; then
            echo "🐧 Using apt package manager"
            $SUDO apt-get update
            $SUDO apt-get install -y amass
        elif command -v yum &> /dev/null; then
            echo "🎩 Using yum package manager"
            $SUDO yum install -y amass
        elif command -v dnf &> /dev/null; then
            echo "🎩 Using dnf package manager"
            $SUDO dnf install -y amass
        elif command -v pacman &> /dev/null; then
            echo "🏔️ Using pacman package manager"
            $SUDO pacman -S --noconfirm amass
        else
            echo "⚠️  No supported package manager found"
            install_from_source
        fi
        ;;
        
    "Darwin")
        echo "🍎 Detected macOS system"
        
        if command -v brew &> /dev/null; then
            echo "🍺 Using Homebrew"
            brew install amass
        else
            echo "⚠️  Homebrew not found. Installing Homebrew first..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            brew install amass
        fi
        ;;
        
    "CYGWIN"*|"MINGW"*|"MSYS"*)
        echo "🪟 Detected Windows system"
        echo "For Windows, please download Amass from:"
        echo "https://github.com/OWASP/Amass/releases"
        echo "Extract the binary and add it to your PATH"
        exit 1
        ;;
        
    *)
        echo "❓ Unknown operating system: $OS"
        install_from_source
        ;;
esac

install_from_source() {
    echo "🛠️ Installing from source using Go"
    
    # Check if Go is installed
    if ! command -v go &> /dev/null; then
        echo "❌ Go is not installed. Please install Go first:"
        echo "https://golang.org/doc/install"
        exit 1
    fi
    
    echo "📦 Installing Amass from source..."
    go install -v github.com/OWASP/Amass/v3/...@master
    
    # Add GOPATH/bin to PATH if not already there
    GOPATH=$(go env GOPATH)
    if [[ ":$PATH:" != *":$GOPATH/bin:"* ]]; then
        echo "⚠️  Adding $GOPATH/bin to PATH"
        echo "export PATH=$PATH:$GOPATH/bin" >> ~/.bashrc
        echo "Please run: source ~/.bashrc"
    fi
}

# Verify installation
echo ""
echo "🔍 Verifying Amass installation..."

if command -v amass &> /dev/null; then
    echo "✅ Amass installed successfully!"
    echo "📋 Version information:"
    amass -version
    
    echo ""
    echo "🎯 Basic usage examples:"
    echo "  amass enum -d example.com"
    echo "  amass enum -passive -d example.com"
    echo "  amass enum -active -d example.com"
else
    echo "❌ Amass installation failed or not found in PATH"
    echo "Please check the installation and ensure Amass is in your PATH"
    exit 1
fi

echo ""
echo "🚀 Amass installation complete!"
echo "You can now use the CrewAI Subdomain Enumeration Agent"
