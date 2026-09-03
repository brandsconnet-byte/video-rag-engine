#!/usr/bin/env python3
"""Main entry point for Video RAG Engine."""

import click
import sys
from pathlib import Path
from loguru import logger

from src.pipeline import VideoPipeline


@click.group()
def cli():
    """Video RAG Engine - Unified Video Processing Pipeline"""
    pass


@cli.command()
@click.option(
    "--video",
    required=True,
    type=click.Path(exists=True),
    help="Path to input video file"
)
@click.option(
    "--config",
    default="config/default.yaml",
    type=click.Path(exists=True),
    help="Path to configuration file"
)
@click.option(
    "--output",
    default="./extracted_clips",
    type=click.Path(),
    help="Output directory for extracted clips"
)
def process(video: str, config: str, output: str):
    """Process a video through the entire pipeline.
    
    Performs scene detection, AI indexing, and database storage.
    """
    try:
        click.echo(f"🎬 Video RAG Engine - Processing: {video}")
        click.echo(f"📋 Using config: {config}")
        click.echo(f"💾 Output dir: {output}")
        click.echo()
        
        pipeline = VideoPipeline(config)
        result = pipeline.process(video, output)
        
        click.echo()
        click.echo(click.style("✅ Processing Complete!", fg="green", bold=True))
        click.echo(f"Scenes detected: {result['num_scenes']}")
        click.echo(f"Database table: {result['table_name']}")
        click.echo(f"Time elapsed: {result['elapsed_time']:.2f}s")
        
    except Exception as e:
        click.echo(click.style(f"❌ Error: {e}", fg="red"), err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--table",
    required=True,
    help="LanceDB table name to search in"
)
@click.option(
    "--query",
    required=True,
    help="Search query (e.g., 'drone shot with car')"
)
@click.option(
    "--config",
    default="config/default.yaml",
    type=click.Path(exists=True),
    help="Path to configuration file"
)
@click.option(
    "--limit",
    default=10,
    type=int,
    help="Maximum results to return"
)
def search(table: str, query: str, config: str, limit: int):
    """Search for scenes in the database.
    
    Example: video-rag-engine search --table scenes_myvideo --query "drone shot"
    """
    try:
        click.echo(f"🔍 Searching: {query}")
        click.echo(f"📊 Table: {table}")
        click.echo()
        
        pipeline = VideoPipeline(config)
        results = pipeline.search([query], table, batch_process=False)
        
        if results and results[0]:
            click.echo(click.style(f"Found {len(results[0])} matching scenes:", fg="green", bold=True))
            for i, result in enumerate(results[0][:limit], 1):
                click.echo(f"\n{i}. Scene {result.get('scene_id')}")
                click.echo(f"   Time: {result.get('start_time', 0):.2f}s - {result.get('end_time', 0):.2f}s")
                click.echo(f"   Duration: {result.get('duration', 0):.2f}s")
                click.echo(f"   Tags: {', '.join(result.get('yolo_tags', []))}")
        else:
            click.echo(click.style("No matching scenes found.", fg="yellow"))
        
    except Exception as e:
        click.echo(click.style(f"❌ Error: {e}", fg="red"), err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--video",
    required=True,
    type=click.Path(exists=True),
    help="Path to input video file"
)
@click.option(
    "--table",
    required=True,
    help="LanceDB table name to search in"
)
@click.option(
    "--query",
    required=True,
    help="Search query"
)
@click.option(
    "--output",
    default="./extracted_clips",
    type=click.Path(),
    help="Output directory for extracted clips"
)
@click.option(
    "--config",
    default="config/default.yaml",
    type=click.Path(exists=True),
    help="Path to configuration file"
)
def extract(video: str, table: str, query: str, output: str, config: str):
    """Search for scenes and extract matching clips.
    
    Example: video-rag-engine extract --video video.mp4 --table scenes_video --query "car"
    """
    try:
        click.echo(f"🎬 Video: {video}")
        click.echo(f"🔍 Query: {query}")
        click.echo(f"📊 Table: {table}")
        click.echo()
        
        pipeline = VideoPipeline(config)
        
        # Search
        click.echo("Searching for matching scenes...")
        results = pipeline.search([query], table, batch_process=False)
        
        if not results or not results[0]:
            click.echo(click.style("No matching scenes found.", fg="yellow"))
            return
        
        click.echo(f"Found {len(results[0])} matches. Extracting clips...\n")
        
        # Extract
        extracted = pipeline.extract_clips(results[0], video, output)
        
        click.echo()
        click.echo(click.style(f"✅ Extracted {len(extracted)} clips!", fg="green", bold=True))
        for clip in extracted:
            click.echo(f"\n📹 Scene {clip['scene_id']}")
            click.echo(f"   Route: {clip['route']}")
            click.echo(f"   Duration: {clip['original_duration']:.2f}s")
            click.echo(f"   Output: {clip['clip_path']}")
        
    except Exception as e:
        click.echo(click.style(f"❌ Error: {e}", fg="red"), err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--table",
    required=True,
    help="LanceDB table name"
)
@click.option(
    "--query",
    required=True,
    help="Search query"
)
@click.option(
    "--output",
    default="./output.xml",
    type=click.Path(),
    help="Output EDL/XML file path"
)
@click.option(
    "--config",
    default="config/default.yaml",
    type=click.Path(exists=True),
    help="Path to configuration file"
)
def edl(table: str, query: str, output: str, config: str):
    """Generate EDL/XML for professional editing.
    
    Example: video-rag-engine edl --table scenes_video --query "car" --output timeline.xml
    """
    try:
        click.echo(f"🎞️ Generating EDL for: {query}")
        click.echo(f"📊 Table: {table}")
        click.echo()
        
        pipeline = VideoPipeline(config)
        
        # Search
        results = pipeline.search([query], table, batch_process=False)
        
        if not results or not results[0]:
            click.echo(click.style("No matching scenes found.", fg="yellow"))
            return
        
        # Generate EDL
        edl_path = pipeline.generate_edl(results[0], output)
        
        click.echo()
        click.echo(click.style(f"✅ EDL Generated!", fg="green", bold=True))
        click.echo(f"📄 Output: {edl_path}")
        click.echo(f"📊 Scenes: {len(results[0])}")
        
    except Exception as e:
        click.echo(click.style(f"❌ Error: {e}", fg="red"), err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--config",
    default="config/default.yaml",
    type=click.Path(exists=True),
    help="Path to configuration file"
)
def info(config: str):
    """Display system information and configuration."""
    try:
        import yaml
        
        click.echo(click.style("Video RAG Engine - System Info", fg="cyan", bold=True))
        click.echo()
        
        with open(config, 'r') as f:
            cfg = yaml.safe_load(f)
        
        click.echo("📋 Scene Detection:")
        sd = cfg.get('scene_detection', {})
        click.echo(f"  - Sensitivity: {sd.get('sensitivity', 'N/A')}")
        click.echo(f"  - Threshold: {sd.get('custom_threshold', sd.get('SENSITIVITY_THRESHOLDS', {}).get(sd.get('sensitivity', 'balanced'), 'N/A'))}")
        
        click.echo("\n🧠 AI Models:")
        yolo = cfg.get('dual_brain', {}).get('yolo', {})
        siglip = cfg.get('dual_brain', {}).get('siglip', {})
        click.echo(f"  - YOLOv8: {yolo.get('model_size', 'N/A')}")
        click.echo(f"  - SigLIP: {siglip.get('model_variant', 'N/A')}")
        
        click.echo("\n💾 Database:")
        db = cfg.get('vector_database', {})
        click.echo(f"  - Path: {db.get('db_path', 'N/A')}")
        click.echo(f"  - Search method: {db.get('vector_search', {}).get('search_method', 'N/A')}")
        
        click.echo("\n⚙️ Routing:")
        router = cfg.get('intelligent_router', {})
        click.echo(f"  - Duration threshold: {router.get('duration_threshold', 'N/A')}s")
        click.echo(f"  - FFmpeg codec: {router.get('ffmpeg', {}).get('codec', 'N/A')}")
        
    except Exception as e:
        click.echo(click.style(f"❌ Error: {e}", fg="red"), err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
