#!/usr/bin/env python3
"""
Setup and Test Script for Reconnaissance Agent

This script helps you set up and test the reconnaissance agent.
"""

import asyncio
import subprocess
import sys
import os
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def check_amass_installation():
    """Check if Amass is installed."""
    try:
        result = subprocess.run(
            ["amass", "version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Amass installed: {version}")
            return True
        else:
            print("❌ Amass not found or not working")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Amass not found in PATH")
        print("📖 Install from: https://github.com/owasp-amass/amass")
        return False


def check_dependencies():
    """Check if Python dependencies are installed."""
    try:
        import crewai
        import crewai_tools
        import loguru
        print("✅ Core dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Run: pip install -r requirements.txt")
        return False


def setup_directories():
    """Create necessary directories."""
    directories = ["logs", "mcp"]
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created directory: {directory}")
        else:
            print(f"✅ Directory exists: {directory}")


async def test_mcp_connection():
    """Test MCP connection."""
    print("\n🔧 Testing MCP connection...")
    
    try:
        from src.reconnaissance_agent import AmassServerManager
        
        server_manager = AmassServerManager("./mcp")
        
        # Test server startup
        print("  Starting Amass MCP server...")
        success = await server_manager.start_server()
        
        if success:
            print("  ✅ Server started successfully")
            await asyncio.sleep(2)
            
            # Test server shutdown
            print("  Stopping server...")
            await server_manager.stop_server()
            print("  ✅ Server stopped successfully")
            return True
        else:
            print("  ❌ Failed to start MCP server")
            return False
            
    except Exception as e:
        print(f"  ❌ MCP test failed: {e}")
        return False


async def run_basic_test():
    """Run a basic reconnaissance test."""
    print("\n🕵️ Running basic reconnaissance test...")
    
    try:
        from src.reconnaissance_agent import run_reconnaissance
        
        print("  Testing with example.com (passive only)...")
        result = await run_reconnaissance(
            domain="example.com",
            comprehensive=False,
            auto_manage_servers=True,
            working_directory="./mcp"
        )
        
        if result and "Error" not in result:
            print("  ✅ Basic reconnaissance test passed")
            return True
        else:
            print("  ❌ Reconnaissance test failed")
            print(f"  Result: {result[:200]}...")
            return False
            
    except Exception as e:
        print(f"  ❌ Reconnaissance test failed: {e}")
        return False


async def main():
    """Main setup and test function."""
    
    print("🔍 Reconnaissance Agent - Setup and Test")
    print("=" * 50)
    
    # Check system requirements
    print("\n📋 Checking system requirements...")
    
    checks = [
        check_python_version(),
        check_amass_installation(),
        check_dependencies()
    ]
    
    if not all(checks):
        print("\n❌ Some requirements are not met. Please fix the issues above.")
        return False
    
    # Setup directories
    print("\n📁 Setting up directories...")
    setup_directories()
    
    # Test MCP connection
    mcp_test = await test_mcp_connection()
    
    if not mcp_test:
        print("\n❌ MCP connection test failed.")
        print("💡 Make sure:")
        print("   - Amass is properly installed")
        print("   - All dependencies are installed")
        print("   - You're running from the project root directory")
        return False
    
    # Run basic functionality test
    basic_test = await run_basic_test()
    
    if not basic_test:
        print("\n❌ Basic functionality test failed.")
        return False
    
    # All tests passed
    print("\n🎉 Setup and tests completed successfully!")
    print("\n📝 Next steps:")
    print("   1. Test connection: python test_mcp_connection.py --quick")
    print("   2. Run reconnaissance: python main.py example.com")
    print("   3. See examples: python examples/basic_usage.py")
    print("\n📖 Documentation: README.md")
    
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Setup failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
