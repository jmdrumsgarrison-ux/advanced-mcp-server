#!/usr/bin/env python3
"""
Advanced MCP Server - Setup Script
Provides package installation and configuration management
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    directories = ["backups", "sessions", "logs"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/ directory")

def setup_environment():
    """Setup environment configuration"""
    print("\n🔧 Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env from template")
        print("⚠️  Please edit .env file with your API keys")
        return True
    elif env_file.exists():
        print("✅ .env file already exists")
        return True
    else:
        print("❌ No .env.example template found")
        return False

def test_imports():
    """Test if all modules can be imported"""
    print("\n🧪 Testing imports...")
    
    # Test standard library imports
    try:
        import json
        import asyncio
        import logging
        print("✅ Standard library modules available")
    except ImportError as e:
        print(f"❌ Standard library import error: {e}")
        return False
    
    # Test our custom modules
    custom_modules = [
        "api_manager",
        "rules_engine", 
        "session_manager",
        "file_operations",
        "auth_manager"
    ]
    
    for module in custom_modules:
        try:
            __import__(module)
            print(f"✅ {module} imported successfully")
        except ImportError as e:
            print(f"⚠️  {module} import failed: {e}")
    
    return True

def generate_claude_config():
    """Generate Claude Desktop configuration"""
    print("\n⚙️  Generating Claude Desktop configuration...")
    
    current_path = Path.cwd().absolute()
    main_py_path = current_path / "main.py"
    
    config = {
        "mcpServers": {
            "advanced-mcp-server": {
                "command": "python",
                "args": [str(main_py_path)]
            }
        }
    }
    
    config_file = Path("claude_desktop_config.json")
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Generated {config_file}")
    print("\n📋 To integrate with Claude Desktop:")
    print("1. Locate your Claude Desktop config file:")
    if os.name == 'nt':  # Windows
        config_path = "%APPDATA%\\Claude\\claude_desktop_config.json"
    else:  # macOS/Linux
        config_path = "~/Library/Application Support/Claude/claude_desktop_config.json"
    
    print(f"   {config_path}")
    print(f"2. Merge the contents of {config_file} into your config")
    print("3. Restart Claude Desktop")

def test_server():
    """Test server initialization"""
    print("\n🚀 Testing server initialization...")
    
    try:
        # Test basic server creation without running
        from main import AdvancedMCPServer
        server = AdvancedMCPServer()
        print("✅ Server initialized successfully")
        return True
    except Exception as e:
        print(f"⚠️  Server initialization warning: {e}")
        print("This may be due to missing MCP dependencies - install them before running")
        return False

def main():
    """Main setup function"""
    print("🚀 Advanced MCP Server Setup")
    print("=" * 50)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Install dependencies
    if success and not install_dependencies():
        success = False
    
    # Create directories
    if success:
        create_directories()
    
    # Setup environment
    if success and not setup_environment():
        success = False
    
    # Test imports
    if success:
        test_imports()
    
    # Generate Claude config
    if success:
        generate_claude_config()
    
    # Test server
    if success:
        test_server()
    
    # Final status
    print("\n" + "=" * 50)
    if success:
        print("🎉 Setup completed successfully!")
        print("\n📝 Next steps:")
        print("1. Edit .env file with your API keys")
        print("2. Configure Claude Desktop (see claude_desktop_config.json)")
        print("3. Test the server: python main.py")
        print("4. Check README.md for detailed usage instructions")
    else:
        print("❌ Setup completed with errors")
        print("Please review the error messages above and resolve issues")
    
    print("\n📖 For help and documentation, see README.md")

if __name__ == "__main__":
    main()
