"""Main pipeline orchestration - ties all components together."""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml
from loguru import logger
import time

from src.scene_detector import SceneDetector
from src.dual_brain_processor import DualBrainProcessor
from src.vector_database import VectorDatabase
from src.intelligent_router import IntelligentRouter
from src.export_manager import ExportManager


class VideoPipeline:
    """Main orchestration class for the Video RAG Engine.
    
    Coordinates scene detection, AI indexing, database storage, and intelligent routing.
    """

    def __init__(self, config_path: str = "config/default.yaml"):
        """Initialize the pipeline with configuration.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config = self._load_config(config_path)
        self._setup_logging()
        
        # Initialize components
        self.scene_detector = SceneDetector(self.config["scene_detection"])
        self.dual_brain = DualBrainProcessor(self.config["dual_brain"])
        self.vector_db = VectorDatabase(
            self.config["vector_database"],
            siglip_model=self.dual_brain.siglip_model,
            siglip_processor=self.dual_brain.siglip_processor
        )
        self.router = IntelligentRouter(self.config["intelligent_router"])
        self.export_manager = ExportManager(self.config["output"], self.config["intelligent_router"])
        
        logger.info("Video RAG Engine initialized successfully")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load YAML configuration file.
        
        Args:
            config_path: Path to YAML file
            
        Returns:
            Configuration dictionary
        """
        if not os.path.exists(config_path):
            logger.error(f"Config file not found: {config_path}")
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        
        logger.info(f"Loaded configuration from {config_path}")
        return config

    def _setup_logging(self):
        """Configure logging based on configuration."""
        log_config = self.config.get("logging", {})
        log_level = log_config.get("level", "INFO")
        log_file = log_config.get("log_file", "video_rag_engine.log")
        
        logger.remove()  # Remove default handler
        logger.add(
            log_file,
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
        )
        
        if log_config.get("console_output", True):
            logger.add(
                lambda msg: print(msg, end=""),
                level=log_level,
                format="<level>{level: <8}</level> | {message}"
            )

    def process(self, video_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Process a video through the entire pipeline.
        
        Args:
            video_path: Path to input video file
            output_dir: Optional output directory override
            
        Returns:
            Pipeline results dictionary
        """
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        logger.info(f"Starting pipeline for video: {video_path}")
        start_time = time.time()
        
        try:
            # Step 1: Scene Detection
            logger.info("[Step 1/4] Detecting scenes...")
            scenes = self.scene_detector.detect(video_path)
            logger.info(f"Detected {len(scenes)} scenes")
            
            # Step 2: Dual-Brain AI Indexing
            logger.info("[Step 2/4] Processing scenes with YOLOv8 + SigLIP...")
            indexed_scenes = self.dual_brain.process_scenes(scenes, video_path)
            logger.info(f"Indexed {len(indexed_scenes)} scenes with AI")
            
            # Step 3: Vector Database Storage
            logger.info("[Step 3/4] Storing scenes in vector database...")
            table_name = self.vector_db.store_scenes(indexed_scenes, video_path)
            logger.info(f"Stored scenes in table: {table_name}")
            
            # Results
            elapsed_time = time.time() - start_time
            logger.info(f"Pipeline completed in {elapsed_time:.2f} seconds")
            
            return {
                "status": "success",
                "video_path": video_path,
                "num_scenes": len(indexed_scenes),
                "table_name": table_name,
                "elapsed_time": elapsed_time,
                "scenes": indexed_scenes
            }
        
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise

    def search(self, queries: List[str], table_name: str, batch_process: bool = True) -> List[Dict[str, Any]]:
        """Search for scenes matching queries.
        
        Args:
            queries: List of search queries (text or object+concept)
            table_name: LanceDB table to search in
            batch_process: Whether to process queries in batch
            
        Returns:
            List of matching scene results
        """
        logger.info(f"Searching for {len(queries)} queries in {table_name}")
        start_time = time.time()
        
        try:
            results = self.vector_db.batch_search(queries, table_name) if batch_process else []
            
            if not batch_process:
                results = []
                for query in queries:
                    result = self.vector_db.search(query, table_name)
                    results.append(result)
            
            elapsed_time = time.time() - start_time
            logger.info(f"Search completed in {elapsed_time:.2f} seconds")
            
            return results
        
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

    def extract_clips(self, results: List[Dict[str, Any]], video_path: str, output_dir: Optional[str] = None):
        """Extract clips based on search results.
        
        Args:
            results: Search results from vector database
            video_path: Path to source video
            output_dir: Optional output directory override
        """
        logger.info(f"Extracting {len(results)} clips from {video_path}")
        output_dir = output_dir or self.config["output"]["output_dir"]
        
        try:
            extracted_clips = []
            
            for result in results:
                # Route based on duration
                route = self.router.route(result["duration"])
                logger.info(f"Routing clip {result['scene_id']} to {route}")
                
                # Export based on route
                if route == "ffmpeg_direct":
                    clip_path = self.export_manager.extract_with_ffmpeg(
                        video_path,
                        result["start_time"],
                        result["end_time"],
                        output_dir
                    )
                elif route == "auto_editor":
                    clip_path = self.export_manager.extract_with_auto_editor(
                        video_path,
                        result["start_time"],
                        result["end_time"],
                        output_dir
                    )
                else:
                    clip_path = None
                
                if clip_path:
                    extracted_clips.append({
                        "scene_id": result["scene_id"],
                        "clip_path": clip_path,
                        "route": route,
                        "original_duration": result["duration"]
                    })
            
            logger.info(f"Successfully extracted {len(extracted_clips)} clips")
            return extracted_clips
        
        except Exception as e:
            logger.error(f"Clip extraction failed: {e}")
            raise

    def generate_edl(self, results: List[Dict[str, Any]], output_path: str):
        """Generate EDL/XML for professional editing.
        
        Args:
            results: Search results from vector database
            output_path: Path to save EDL/XML file
        """
        logger.info(f"Generating EDL/XML to {output_path}")
        
        try:
            edl_path = self.export_manager.generate_edl(results, output_path)
            logger.info(f"EDL generated: {edl_path}")
            return edl_path
        
        except Exception as e:
            logger.error(f"EDL generation failed: {e}")
            raise
