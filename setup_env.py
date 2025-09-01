#!/usr/bin/env python3
"""
Environment Setup Script for Places Management System

This script helps users set up their environment configuration by copying
the example file and providing guidance on required variables.
"""

import os
import shutil
from pathlib import Path

def setup_environment():
    """Set up the environment configuration file."""
    print("🗺️ Places Management System - Environment Setup")
    print("=" * 50)
    
    # Check if .env file already exists
    env_file = Path(".env")
    example_file = Path("env.example")
    
    if env_file.exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            print("Setup cancelled. Your existing .env file is preserved.")
            return
    
    # Copy example file
    if example_file.exists():
        shutil.copy2(example_file, env_file)
        print("✅ Created .env file from env.example")
    else:
        print("❌ env.example file not found!")
        return
    
    print("\n📋 Environment Configuration Summary:")
    print("-" * 40)
    
    # Read and display the configuration
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            if '=' in line:
                key, value = line.split('=', 1)
                if 'password' in key.lower() or 'token' in key.lower():
                    # Mask sensitive values
                    masked_value = '*' * min(len(value), 8) + '...' if len(value) > 8 else '*' * len(value)
                    print(f"  {key}: {masked_value}")
                else:
                    print(f"  {key}: {value}")
    
    print("\n🔧 Next Steps:")
    print("1. Review and modify the .env file if needed")
    print("2. Set DEBUG=True to enable performance logging")
    print("3. Update OLA Maps API credentials if needed")
    print("4. Run: streamlit run app.py")
    
    print("\n✅ Environment setup completed!")

if __name__ == "__main__":
    setup_environment()
