#!/usr/bin/env python3
"""
Setup script to create necessary directories and files
"""

import os
from pathlib import Path

def setup_directories():
    """Create necessary directory structure"""
    
    directories = [
        "config",
        "data/input",
        "data/output",
        "src/metrics"
    ]
    
    print("Setting up directory structure...")
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {directory}")
    
    print("\n✅ Directory structure created successfully!")
    
    # Check if config file exists
    config_path = "config/metrics_config.yaml"
    if not os.path.exists(config_path):
        print(f"⚠ Config file missing: {config_path}")
        print("Please create the metrics_config.yaml file in the config directory")
    else:
        print(f"✓ Config file exists: {config_path}")

if __name__ == "__main__":
    setup_directories()