"""Example: EDL/XML generation for professional editing."""

from src.pipeline import VideoPipeline


def main():
    # Initialize pipeline
    pipeline = VideoPipeline(config_path="config/default.yaml")
    
    # Process video
    video_path = "path/to/your/video.mp4"
    result = pipeline.process(video_path)
    table_name = result['table_name']
    
    print("\n=== EDL/XML Export for Professional Editing ===")
    
    # Search for specific scenes
    queries = [
        "Ferrari driving",
        "drone shot",
        "car close-up"
    ]
    
    search_results = pipeline.search(queries, table_name, batch_process=True)
    
    # Flatten results
    all_results = []
    for result_list in search_results:
        all_results.extend(result_list)
    
    if all_results:
        print(f"Found {len(all_results)} scenes")
        
        # Generate EDL for DaVinci Resolve
        print("\nGenerating EDL for DaVinci Resolve...")
        edl_path = pipeline.generate_edl(all_results, "./output/timeline.xml")
        
        print(f"✅ EDL generated: {edl_path}")
        print("\n📝 You can now:")
        print("  1. Open DaVinci Resolve")
        print(f"  2. Import the XML file: {edl_path}")
        print("  3. Timeline will be built with all detected scenes")
        print("  4. Color grade, add music, and finalize your edit")
    else:
        print("❌ No matching scenes found")


if __name__ == "__main__":
    main()
