"""Tests for intelligent router module."""

import pytest
from src.intelligent_router import IntelligentRouter


class TestIntelligentRouter:
    """Test cases for IntelligentRouter."""

    def test_init_default_config(self):
        """Test initialization with default config."""
        config = {}
        router = IntelligentRouter(config)
        
        assert router.duration_threshold == 30
        assert router.ffmpeg_config == {}
        assert router.auto_editor_config == {}
        assert router.edl_config == {}

    def test_init_custom_config(self):
        """Test initialization with custom config."""
        config = {
            "duration_threshold": 60,
            "ffmpeg": {"codec": "libx264"},
            "auto_editor": {"motion_threshold": 0.05},
            "edl_export": {"format": "premiere"}
        }
        router = IntelligentRouter(config)
        
        assert router.duration_threshold == 60
        assert router.ffmpeg_config == {"codec": "libx264"}
        assert router.auto_editor_config == {"motion_threshold": 0.05}
        assert router.edl_config == {"format": "premiere"}

    def test_route_short_clip(self):
        """Test routing for short clips (< threshold)."""
        router = IntelligentRouter({"duration_threshold": 30})
        
        result = router.route(15.0)
        assert result == "ffmpeg_direct"
        
        result = router.route(29.9)
        assert result == "ffmpeg_direct"

    def test_route_long_clip(self):
        """Test routing for long clips (> threshold)."""
        router = IntelligentRouter({"duration_threshold": 30})
        
        result = router.route(30.0)
        assert result == "auto_editor"
        
        result = router.route(120.0)
        assert result == "auto_editor"

    def test_route_pro_export_forced(self):
        """Test forced pro export route."""
        router = IntelligentRouter({"duration_threshold": 30})
        
        result = router.route(15.0, force_pro=True)
        assert result == "pro_export"
        
        result = router.route(120.0, force_pro=True)
        assert result == "pro_export"

    def test_route_pro_export_config(self):
        """Test pro export when configured to always use it."""
        router = IntelligentRouter({
            "duration_threshold": 30,
            "edl_export": {"force_pro_export": True}
        })
        
        result = router.route(15.0)
        assert result == "pro_export"

    def test_should_export_pro_default(self):
        """Test pro export recommendation with default settings."""
        router = IntelligentRouter({})
        
        # Default min_clips_for_pro is 10
        assert router.should_export_pro(num_clips=5) == False
        assert router.should_export_pro(num_clips=10) == True
        assert router.should_export_pro(num_clips=20) == True

    def test_should_export_pro_configured(self):
        """Test pro export recommendation with custom threshold."""
        router = IntelligentRouter({
            "edl_export": {"min_clips_for_pro": 5}
        })
        
        assert router.should_export_pro(num_clips=3) == False
        assert router.should_export_pro(num_clips=5) == True

    def test_should_export_pro_always(self):
        """Test pro export when always enabled."""
        router = IntelligentRouter({
            "edl_export": {"always_pro": True}
        })
        
        assert router.should_export_pro(num_clips=1) == True
        assert router.should_export_pro(num_clips=0) == True

    def test_get_ffmpeg_config(self):
        """Test getting FFmpeg configuration."""
        config = {"ffmpeg": {"codec": "libx264", "crf": 18}}
        router = IntelligentRouter(config)
        
        assert router.get_ffmpeg_config() == {"codec": "libx264", "crf": 18}

    def test_get_auto_editor_config(self):
        """Test getting auto-editor configuration."""
        config = {"auto_editor": {"motion_threshold": 0.02}}
        router = IntelligentRouter(config)
        
        assert router.get_auto_editor_config() == {"motion_threshold": 0.02}

    def test_get_edl_config(self):
        """Test getting EDL configuration."""
        config = {"edl_export": {"format": "fcpxml"}}
        router = IntelligentRouter(config)
        
        assert router.get_edl_config() == {"format": "fcpxml"}
