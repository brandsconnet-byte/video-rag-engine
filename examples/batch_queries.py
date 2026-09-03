"""Example: Batch query processing with hybrid search."""

from src.pipeline import VideoPipeline
from src.vector_database import VectorDatabase
import yaml


def main():
    # Load config
    with open("config/default.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize pipeline
    pipeline = VideoPipeline(config_path="config/default.yaml")
    vector_db = VectorDatabase(config["vector_database"])
    
    # Process video (if not already done)
    video_path = "path/to/your/video.mp4"
    result = pipeline.process(video_path)
    table_name = result['table_name']
    
    print("\n=== Batch Query Processing ===")
    
    # Define multiple queries to process simultaneously
    batch_queries = [
        "Ferrari driving fast",
        "drone aerial shot",
        "car wheel tire",
        "water spray washing",
        "person standing",
    ]
    
    print(f"Processing {len(batch_queries)} queries in batch...")
    batch_results = pipeline.search(batch_queries, table_name, batch_process=True)
    
    # Display results
    print(f"\n{'Query':<30} {'Matches':<10} {'Top Match Duration':<20}")
    print("-" * 60)
    
    for query, results in zip(batch_queries, batch_results):
        num_matches = len(results)
        if results:
            top_match_duration = results[0].get('duration', 0)
            print(f"{query:<30} {num_matches:<10} {top_match_duration:.2f}s")
        else:
            print(f"{query:<30} {0:<10} N/A")
    
    # Example of hybrid search (vector + tag filtering)
    print("\n=== Hybrid Search Example ===")
    query = "car scene"
    tags = ["car", "person"]
    
    print(f"Query: {query}")
    print(f"Filter tags: {tags}")
    
    hybrid_results = vector_db.hybrid_search(query, tags, table_name)
    
    print(f"\n✅ Found {len(hybrid_results)} scenes matching both vector and tags")
    for result in hybrid_results[:5]:
        print(f"  Scene {result.get('scene_id')}: {result.get('start_time', 0):.2f}s - {result.get('end_time', 0):.2f}s")


if __name__ == "__main__":
    main()
