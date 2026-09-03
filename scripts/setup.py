#!/usr/bin/env python3
"""Setup and installation script for Video RAG Engine."""

import os
import sys
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Execute a shell command and handle errors."""
    print(f"\n📦 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} complete")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False


def main():
    print("\n🎬 Video RAG Engine - Setup Script")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Create directories
    print("\n📁 Creating directories...")
    dirs = ["config", "src", "examples", "scripts", "extracted_clips", "debug_frames"]
    for d in dirs:
        Path(d).mkdir(exist_ok=True)
    print("✅ Directories created")
    
    # Install dependencies
    print("\n📚 Installing dependencies...")
    
    if not run_command("pip install --upgrade pip", "Upgrading pip"):
        sys.exit(1)
    
    if not run_command("pip install -r requirements.txt", "Installing core dependencies"):
        sys.exit(1)
    
    # Download models (optional)
    print("\n🤖 Downloading AI models (optional)...")
    print("   This may take several minutes on first run")
    
    try:
        import torch
        from ultralytics import YOLO
        from transformers import CLIPModel
        
        print("   Downloading YOLOv8 medium...")
        YOLO("yolov8m.pt")
        print("   ✅ YOLOv8 downloaded")
        
        print("   Downloading SigLIP...")
        CLIPModel.from_pretrained("google/siglip-base-patch16-256")
        print("   ✅ SigLIP downloaded")
        
    except Exception as e:
        print(f"   ⚠️  Model download failed (will download on first use): {e}")
    
    # Create example configs
    print("\n⚙️  Creating example configurations...")
    try:
        subprocess.run([sys.executable, "scripts/create_configs.py"], check=False)
        print("✅ Example configs created")
    except Exception as e:
        print(f"⚠️  Config creation failed: {e}")
    
    # Final message
    print("\n" + "=" * 50)
    print("✅ Setup Complete!")
    print("\n📖 Quick Start:")
    print("   1. Process a video:")
    print("      python main.py process --video path/to/video.mp4")
    print("\n   2. Search for scenes:")
    print("      python main.py search --table scenes_video --query 'drone shot'")
    print("\n   3. Extract matching clips:")
    print("      python main.py extract --video video.mp4 --table scenes_video --query 'car'")
    print("\n   4. View configuration:")
    print("      python main.py info")
    print("\n📚 For more examples, see examples/ directory")
    print("\n")


if __name__ == "__main__":
    main()
