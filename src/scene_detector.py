"""Scene detection using PySceneDetect."""

import os
from typing import List, Dict, Any, Tuple
from loguru import logger

try:
    from scenedetect import detect, AdaptiveDetector, FrameTimecode
except ImportError:
    logger.warning("PySceneDetect not installed. Install with: pip install scenedetect[opencv]")


class SceneDetector:
    """Detects scene boundaries using adaptive content detection."""

    SENSITIVITY_THRESHOLDS = {
        "conservative": 27.0,  # High threshold, fewer scenes
        "balanced": 25.0,      # Medium threshold
        "aggressive": 23.0,    # Low threshold, more scenes
    }

    def __init__(self, config: Dict[str, Any]):
        """Initialize scene detector.
        
        Args:
            config: Configuration dictionary for scene detection
        """
        self.sensitivity = config.get("sensitivity", "balanced")
        self.custom_threshold = config.get("custom_threshold")
        self.adaptive_threshold = config.get("adaptive_threshold", True)
        self.min_scene_length = config.get("min_scene_length", 0.5)
        self.keyframes_per_scene = config.get("keyframes_per_scene", 1)
        self.keyframe_interval = config.get("keyframe_interval_seconds")
        
        # Determine threshold
        self.threshold = self.custom_threshold or self.SENSITIVITY_THRESHOLDS.get(self.sensitivity, 25.0)
        logger.info(f"Scene detector initialized with threshold: {self.threshold}")

    def detect(self, video_path: str) -> List[Dict[str, Any]]:
        """Detect scenes in video file.
        
        Args:
            video_path: Path to video file
            
        Returns:
            List of detected scenes with metadata
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")
        
        logger.info(f"Detecting scenes in: {video_path}")
        
        try:
            # Detect scenes using adaptive detector
            scenes = detect(video_path, AdaptiveDetector(threshold=self.threshold))
            
            if not scenes:
                logger.warning("No scenes detected. Using entire video as one scene.")
                return self._create_fallback_scene(video_path)
            
            # Process scenes
            processed_scenes = []
            for i, (start, end) in enumerate(scenes):
                duration = (end - start).get_seconds()
                
                # Filter out very short scenes
                if duration < self.min_scene_length:
                    logger.debug(f"Skipping scene {i} (too short: {duration}s)")
                    continue
                
                scene = {
                    "scene_id": i,
                    "start_time": start.get_seconds(),
                    "end_time": end.get_seconds(),
                    "duration": duration,
                    "video_path": video_path,
                }
                processed_scenes.append(scene)
            
            logger.info(f"Detected {len(processed_scenes)} scenes")
            return processed_scenes
        
        except Exception as e:
            logger.error(f"Scene detection failed: {e}")
            raise

    def _create_fallback_scene(self, video_path: str) -> List[Dict[str, Any]]:
        """Create fallback scene if detection fails.
        
        Args:
            video_path: Path to video file
            
        Returns:
            List with single scene covering entire video
        """
        try:
            import cv2
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            
            duration = total_frames / fps if fps > 0 else 0
            
            return [{
                "scene_id": 0,
                "start_time": 0.0,
                "end_time": duration,
                "duration": duration,
                "video_path": video_path,
            }]
        except Exception as e:
            logger.error(f"Fallback scene creation failed: {e}")
            raise
