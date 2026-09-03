"""Example: Basic clip extraction workflow."""

from src.pipeline import VideoPipeline
from pathlib import Path


def main():
    # Initialize pipeline with default config
    pipeline = VideoPipeline(config_path="config/default.yaml")
    
    # Process video
    video_path = "path/to/your/video.mp4"
    output_dir = "./extracted_clips"
    
    print("\n=== STEP 1: Process Video ===")
    result = pipeline.process(video_path, output_dir)
    print(f"✅ Processed {result['num_scenes']} scenes")
    print(f"📊 Database table: {result['table_name']}")
    
    # Search for specific scenes
    print("\n=== STEP 2: Search for Scenes ===")
    table_name = result['table_name']
    queries = [
        "Ferrari driving",
        "drone shot with car",
        "tire washing"
    ]
    
    search_results = pipeline.search(queries, table_name, batch_process=True)
    
    # Flatten results from batch search
    all_results = []
    for result_list in search_results:
        all_results.extend(result_list)
    
    print(f"✅ Found {len(all_results)} total matching scenes")
    
    # Extract clips
    print("\n=== STEP 3: Extract Clips ===")
    extracted_clips = pipeline.extract_clips(all_results, video_path, output_dir)
    
    print(f"✅ Extracted {len(extracted_clips)} clips")
    for clip in extracted_clips:
        print(f"  📹 {clip['clip_path']} ({clip['original_duration']:.2f}s)")


if __name__ == "__main__":
    main()
