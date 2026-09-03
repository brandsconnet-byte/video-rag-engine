#!/usr/bin/env python3
"""Benchmark script to test pipeline performance."""

import time
import os
from src.pipeline import VideoPipeline


def benchmark():
    """Run performance benchmarks on a test video."""
    print("\n🏃 Video RAG Engine - Performance Benchmark")
    print("=" * 50)
    
    # Test video path (user should provide)
    video_path = input("Enter path to test video: ").strip()
    
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        return
    
    configs = [
        ("config/fast.yaml", "⚡ Fast"),
        ("config/balanced.yaml", "⚖️  Balanced"),
        ("config/accurate.yaml", "🎯 Accurate"),
    ]
    
    results = []
    
    for config_path, label in configs:
        if not os.path.exists(config_path):
            print(f"⚠️  Config not found: {config_path}")
            continue
        
        print(f"\n{label}")
        print("-" * 50)
        
        pipeline = VideoPipeline(config_path)
        
        start = time.time()
        result = pipeline.process(video_path)
        elapsed = time.time() - start
        
        results.append({
            "config": label,
            "elapsed": elapsed,
            "scenes": result["num_scenes"],
        })
        
        print(f"Time: {elapsed:.2f}s")
        print(f"Scenes: {result['num_scenes']}")
        print(f"FPS: {result['num_scenes'] / elapsed:.1f} scenes/sec")
    
    # Summary
    print("\n" + "=" * 50)
    print("\n📊 Benchmark Summary:")
    print(f"\n{'Config':<20} {'Time':<12} {'Scenes':<10}")
    print("-" * 42)
    
    for r in results:
        print(f"{r['config']:<20} {r['elapsed']:.2f}s{'':<8} {r['scenes']:<10}")
    
    print()


if __name__ == "__main__":
    benchmark()
