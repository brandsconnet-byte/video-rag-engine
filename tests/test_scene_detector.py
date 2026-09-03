"""Tests for scene detection module."""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from src.scene_detector import SceneDetector


class TestSceneDetector:
    """Test cases for SceneDetector."""

    def test_init_default_config(self):
        """Test initialization with default config."""
        config = {}
        detector = SceneDetector(config)
        
        assert detector.sensitivity == "balanced"
        assert detector.threshold == 25.0
        assert detector.min_scene_length == 0.5

    def test_init_custom_threshold(self):
        """Test initialization with custom threshold."""
        config = {
            "sensitivity": "aggressive",
            "custom_threshold": 20.0,
            "min_scene_length": 1.0
        }
        detector = SceneDetector(config)
        
        assert detector.sensitivity == "aggressive"
        assert detector.threshold == 20.0
        assert detector.min_scene_length == 1.0

    def test_init_sensitivity_thresholds(self):
        """Test sensitivity threshold mapping."""
        conservative = SceneDetector({"sensitivity": "conservative"})
        balanced = SceneDetector({"sensitivity": "balanced"})
        aggressive = SceneDetector({"sensitivity": "aggressive"})
        
        assert conservative.threshold == 27.0
        assert balanced.threshold == 25.0
        assert aggressive.threshold == 23.0

    @patch("src.scene_detector.detect")
    @patch("os.path.exists")
    def test_detect_success(self, mock_exists, mock_detect):
        """Test successful scene detection."""
        mock_exists.return_value = True
        
        # Mock scene detection results
        mock_start = Mock()
        mock_start.get_seconds.return_value = 0.0
        mock_end = Mock()
        mock_end.get_seconds.return_value = 5.0
        
        mock_detect.return_value = [(mock_start, mock_end)]
        
        detector = SceneDetector({})
        scenes = detector.detect("test_video.mp4")
        
        assert len(scenes) == 1
        assert scenes[0]["scene_id"] == 0
        assert scenes[0]["start_time"] == 0.0
        assert scenes[0]["end_time"] == 5.0
        assert scenes[0]["duration"] == 5.0

    @patch("src.scene_detector.detect")
    @patch("os.path.exists")
    def test_detect_filters_short_scenes(self, mock_exists, mock_detect):
        """Test that very short scenes are filtered out."""
        mock_exists.return_value = True
        
        mock_start = Mock()
        mock_start.get_seconds.return_value = 0.0
        mock_end = Mock()
        mock_end.get_seconds.return_value = 0.1  # Very short scene
        
        mock_detect.return_value = [(mock_start, mock_end)]
        
        detector = SceneDetector({"min_scene_length": 0.5})
        scenes = detector.detect("test_video.mp4")
        
        assert len(scenes) == 0  # Scene should be filtered out

    @patch("src.scene_detector.detect")
    @patch("os.path.exists")
    def test_detect_empty_results_fallback(self, mock_exists, mock_detect):
        """Test fallback when no scenes detected."""
        mock_exists.return_value = True
        mock_detect.return_value = []
        
        detector = SceneDetector({})
        
        with patch("cv2.VideoCapture") as mock_cap:
            mock_instance = Mock()
            mock_instance.get.side_effect = [30.0, 300]  # fps, total_frames
            mock_instance.release = Mock()
            mock_cap.return_value = mock_instance
            
            scenes = detector.detect("test_video.mp4")
            
            assert len(scenes) == 1
            assert scenes[0]["scene_id"] == 0
            assert scenes[0]["duration"] == 10.0  # 300 frames / 30 fps

    @patch("os.path.exists")
    def test_detect_file_not_found(self, mock_exists):
        """Test error when video file doesn't exist."""
        mock_exists.return_value = False
        
        detector = SceneDetector({})
        
        with pytest.raises(FileNotFoundError):
            detector.detect("nonexistent.mp4")

    def test_create_fallback_scene(self):
        """Test fallback scene creation."""
        detector = SceneDetector({})
        
        with patch("cv2.VideoCapture") as mock_cap:
            mock_instance = Mock()
            mock_instance.get.side_effect = [25.0, 500]  # fps, total_frames
            mock_instance.release = Mock()
            mock_cap.return_value = mock_instance
            
            scenes = detector._create_fallback_scene("test.mp4")
            
            assert len(scenes) == 1
            assert scenes[0]["start_time"] == 0.0
            assert scenes[0]["duration"] == 20.0  # 500 / 25
