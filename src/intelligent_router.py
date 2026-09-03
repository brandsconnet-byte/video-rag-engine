"""Intelligent routing logic for clip export."""

from typing import Dict, Any, Literal
from loguru import logger


class IntelligentRouter:
    """Routes clips to appropriate export method based on duration and properties."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize intelligent router.
        
        Args:
            config: Router configuration
        """
        self.duration_threshold = config.get("duration_threshold", 30)
        self.ffmpeg_config = config.get("ffmpeg", {})
        self.auto_editor_config = config.get("auto_editor", {})
        self.edl_config = config.get("edl_export", {})
        
        logger.info(f"Intelligent router initialized with threshold: {self.duration_threshold}s")

    def route(self, duration: float, force_pro: bool = False) -> Literal["ffmpeg_direct", "auto_editor", "pro_export"]:
        """Route clip based on duration and configuration.
        
        Args:
            duration: Clip duration in seconds
            force_pro: Force pro_export route regardless of duration
            
        Returns:
            Route name: 'ffmpeg_direct', 'auto_editor', or 'pro_export'
        """
        # Check if pro export is forced (e.g., for EDL generation)
        if force_pro or self.edl_config.get("force_pro_export", False):
            logger.debug(f"Clip ({duration}s) → Pro export (EDL/XML)")
            return "pro_export"
        
        if duration < self.duration_threshold:
            logger.debug(f"Short clip ({duration}s) → FFmpeg direct extract")
            return "ffmpeg_direct"
        else:
            logger.debug(f"Long clip ({duration}s) → auto-editor optimization")
            return "auto_editor"
    
    def should_export_pro(self, num_clips: int = 0) -> bool:
        """Determine if pro export should be used based on context.
        
        Args:
            num_clips: Number of clips being exported
            
        Returns:
            True if pro export is recommended
        """
        # Pro export is recommended for large batches or when EDL is explicitly enabled
        min_clips_for_pro = self.edl_config.get("min_clips_for_pro", 10)
        return num_clips >= min_clips_for_pro or self.edl_config.get("always_pro", False)

    def get_ffmpeg_config(self) -> Dict[str, Any]:
        """Get FFmpeg configuration for this route.
        
        Returns:
            FFmpeg configuration
        """
        return self.ffmpeg_config

    def get_auto_editor_config(self) -> Dict[str, Any]:
        """Get auto-editor configuration for this route.
        
        Returns:
            auto-editor configuration
        """
        return self.auto_editor_config

    def get_edl_config(self) -> Dict[str, Any]:
        """Get EDL export configuration.
        
        Returns:
            EDL configuration
        """
        return self.edl_config
