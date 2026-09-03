#!/usr/bin/env python3
"""Create example configuration files for different use cases."""

import yaml
import os


def create_fast_config():
    """Config optimized for speed (CPU processing)."""
    return {
        "scene_detection": {
            "sensitivity": "aggressive",
            "min_scene_length": 1.0,
        },
        "dual_brain": {
            "yolo": {
                "model_size": "nano",
                "use_gpu": False,
                "confidence_threshold": 0.5,
            },
            "siglip": {
                "model_variant": "tiny",
                "use_gpu": False,
                "batch_size": 16,
            },
        },
        "vector_database": {
            "db_path": "./video_rag_fast.db",
            "vector_search": {
                "search_method": "ivf",
                "k_nearest": 5,
                "similarity_threshold": 0.5,
            },
        },
    }


def create_accurate_config():
    """Config optimized for accuracy (GPU processing)."""
    return {
        "scene_detection": {
            "sensitivity": "conservative",
            "min_scene_length": 0.3,
        },
        "dual_brain": {
            "yolo": {
                "model_size": "large",
                "use_gpu": True,
                "confidence_threshold": 0.3,
            },
            "siglip": {
                "model_variant": "large",
                "use_gpu": True,
                "batch_size": 64,
            },
        },
        "vector_database": {
            "db_path": "./video_rag_accurate.db",
            "vector_search": {
                "search_method": "exhaustive",
                "k_nearest": 20,
                "similarity_threshold": 0.3,
            },
        },
    }


def create_balanced_config():
    """Config balanced between speed and accuracy."""
    return {
        "scene_detection": {
            "sensitivity": "balanced",
            "min_scene_length": 0.5,
        },
        "dual_brain": {
            "yolo": {
                "model_size": "medium",
                "use_gpu": True,
                "confidence_threshold": 0.5,
            },
            "siglip": {
                "model_variant": "base",
                "use_gpu": True,
                "batch_size": 32,
            },
        },
        "vector_database": {
            "db_path": "./video_rag_balanced.db",
            "vector_search": {
                "search_method": "ivf",
                "k_nearest": 10,
                "similarity_threshold": 0.5,
            },
        },
    }


def save_config(config, filename):
    """Save config to YAML file."""
    os.makedirs("config", exist_ok=True)
    
    with open(f"config/{filename}", 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print(f"✅ Created: config/{filename}")


if __name__ == "__main__":
    print("Creating example configurations...\n")
    
    save_config(create_fast_config(), "fast.yaml")
    save_config(create_accurate_config(), "accurate.yaml")
    save_config(create_balanced_config(), "balanced.yaml")
    
    print("\n📖 Usage:")
    print("  python main.py process --video video.mp4 --config config/fast.yaml")
    print("  python main.py process --video video.mp4 --config config/accurate.yaml")
    print("  python main.py process --video video.mp4 --config config/balanced.yaml")
