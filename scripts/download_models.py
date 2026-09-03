#!/usr/bin/env python3
"""Download and cache AI models for offline use."""

import sys
import os
from pathlib import Path


def download_models():
    """Download required AI models."""
    print("🤖 Downloading Video RAG Engine AI Models...")
    print("This may take 5-15 minutes depending on internet speed\n")
    
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__} available")
        
        if torch.cuda.is_available():
            print(f"✅ CUDA {torch.version.cuda} available (GPU acceleration enabled)")
        else:
            print("⚠️  CUDA not available (will use CPU)")
        
    except ImportError:
        print("❌ PyTorch not installed. Run: pip install -r requirements.txt")
        sys.exit(1)
    
    try:
        from ultralytics import YOLO
        print("\n📥 Downloading YOLOv8 models...")
        
        models = ["yolov8n.pt", "yolov8s.pt", "yolov8m.pt", "yolov8l.pt"]
        for model in models:
            print(f"  Downloading {model}...")
            YOLO(model)
            print(f"  ✅ {model} downloaded")
        
    except Exception as e:
        print(f"❌ YOLOv8 download failed: {e}")
        sys.exit(1)
    
    try:
        from transformers import AutoModel, AutoProcessor
        print("\n📥 Downloading SigLIP models...")
        
        models = [
            "google/siglip-so400m-patch14-224",  # tiny
            "google/siglip-base-patch16-224",     # base
            "google/siglip-large-patch16-384",    # large
        ]
        
        for model in models:
            print(f"  Downloading {model}...")
            AutoModel.from_pretrained(model)
            AutoProcessor.from_pretrained(model)
            print(f"  ✅ {model} downloaded")
        
    except Exception as e:
        print(f"❌ SigLIP download failed: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ All models downloaded successfully!")
    print("\nModels are cached locally for offline use.")
    print("Cache location: ~/.cache/huggingface/hub/")
    print()


if __name__ == "__main__":
    download_models()
