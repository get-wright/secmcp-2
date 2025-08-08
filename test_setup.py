#!/usr/bin/env python3
"""
Test script to validate the CrewAI Subdomain Enumeration setup
"""

import sys
import os
import subprocess
import importlib.util
from pathlib import Path

def test_python_version():
    """Test if Python version is compatible"""
    print("🐍 Testing Python version...")
    version = sys.version_info
    
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible")
        print("Please upgrade to Python 3.8 or higher")
        return False

def test_amass_installation():
    """Test if Amass is installed and accessible"""
    print("🔍 Testing Amass installation...")
    
    try:
        result = subprocess.run(["amass", "-version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Amass is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Amass is installed but not working properly")
            return False
    except FileNotFoundError:
        print("❌ Amass not found in PATH")
        print("Please install Amass using: ./scripts/install_amass.sh")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Amass command timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing Amass: {e}")
        return False

def test_dependencies():
    """Test if required Python dependencies are available"""
    print("📦 Testing Python dependencies...")
    
    required_packages = [
        "crewai",
        "langchain", 
        "pydantic",
        "yaml",
        "requests",
        "aiohttp"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == "yaml":
                import yaml
            else:
                importlib.import_module(package)
            print(f"✅ {package} is available")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\\n📋 Install missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def test_file_structure():
    """Test if all required files are present"""
    print("📁 Testing file structure...")
    
    required_files = [
        "main.py",
        "requirements.txt",
        "config/mcp_servers.yaml",
        "src/__init__.py",
        "src/mcp_client.py",
        "src/subdomain_agent.py",
        "mcp/__init__.py",
        "mcp/amass_mcp_server.py"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} is missing")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\\n❌ Missing files: {missing_files}")
        return False
    
    return True

def test_configuration():
    """Test if configuration files are valid"""
    print("⚙️ Testing configuration...")
    
    try:
        import yaml
        with open("config/mcp_servers.yaml", 'r') as f:
            config = yaml.safe_load(f)
        
        # Basic validation
        if "mcp_servers" in config and isinstance(config["mcp_servers"], list):
            print(f"✅ Configuration file is valid with {len(config['mcp_servers'])} servers")
            return True
        else:
            print("❌ Configuration file is invalid")
            return False
            
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return False

def test_imports():
    """Test if our modules can be imported"""
    print("🔧 Testing module imports...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, os.getcwd())
        
        from src.mcp_client import MCPClient
        print("✅ MCPClient import successful")
        
        from src.subdomain_agent import SubdomainEnumerationAgent
        print("✅ SubdomainEnumerationAgent import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_mcp_server():
    """Test if MCP server can be initialized"""
    print("🖥️ Testing MCP server initialization...")
    
    try:
        # Test basic server import
        sys.path.insert(0, os.getcwd())
        import mcp.amass_mcp_server
        print("✅ MCP server module loads successfully")
        return True
        
    except Exception as e:
        print(f"❌ MCP server error: {e}")
        return False

def run_basic_test():
    """Run a basic end-to-end test"""
    print("🧪 Running basic functionality test...")
    
    try:
        sys.path.insert(0, os.getcwd())
        from src.mcp_client import MCPClient
        
        # Create client (should not fail)
        client = MCPClient()
        print("✅ MCPClient creation successful")
        
        # Test configuration loading
        if client.servers:
            print(f"✅ Configuration loaded with {len(client.servers)} servers")
        else:
            print("⚠️ No servers configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 CrewAI Subdomain Enumeration Agent - Setup Test")
    print("=" * 60)
    
    tests = [
        ("Python Version", test_python_version),
        ("Amass Installation", test_amass_installation),
        ("Python Dependencies", test_dependencies),
        ("File Structure", test_file_structure),
        ("Configuration", test_configuration),
        ("Module Imports", test_imports),
        ("MCP Server", test_mcp_server),
        ("Basic Functionality", run_basic_test),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\\n🔍 {test_name}")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\\n📈 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\\n🎉 All tests passed! The system is ready to use.")
        print("\\n🚀 Try running: python main.py example.com")
    else:
        print("\\n⚠️  Some tests failed. Please fix the issues before using the system.")
        print("\\n📋 Common fixes:")
        print("  - Install missing dependencies: pip install -r requirements.txt")
        print("  - Install Amass: ./scripts/install_amass.sh")
        print("  - Check file permissions and paths")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
