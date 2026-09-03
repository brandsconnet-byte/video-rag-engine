"""Pytest configuration and shared fixtures."""

import pytest
import numpy as np
from unittest.mock import Mock


@pytest.fixture
def sample_scenes():
    """Provide sample scene data for tests."""
    return [
        {
            "scene_id": 0,
            "start_time": 0.0,
            "end_time": 5.0,
            "duration": 5.0,
            "video_path": "test_video.mp4",
            "yolo_tags": ["car", "person"],
            "embedding": np.random.randn(768).astype(np.float32)
        },
        {
            "scene_id": 1,
            "start_time": 10.0,
            "end_time": 20.0,
            "duration": 10.0,
            "video_path": "test_video.mp4",
            "yolo_tags": ["dog", "tree"],
            "embedding": np.random.randn(768).astype(np.float32)
        },
        {
            "scene_id": 2,
            "start_time": 25.0,
            "end_time": 35.0,
            "duration": 10.0,
            "video_path": "test_video.mp4",
            "yolo_tags": ["car", "building"],
            "embedding": np.random.randn(768).astype(np.float32)
        }
    ]


@pytest.fixture
def mock_video_capture():
    """Provide a mock OpenCV VideoCapture."""
    cap = Mock()
    cap.get.side_effect = lambda prop: {
        5: 30.0,   # CAP_PROP_FPS
        7: 900     # CAP_PROP_FRAME_COUNT
    }.get(prop, 0)
    cap.read.return_value = (True, np.zeros((1080, 1920, 3), dtype=np.uint8))
    cap.set.return_value = True
    return cap


@pytest.fixture
def default_config():
    """Provide default configuration dictionary."""
    return {
        "scene_detection": {
            "sensitivity": "balanced",
            "min_scene_length": 0.5
        },
        "dual_brain": {
            "yolo": {
                "model_size": "nano",
                "confidence_threshold": 0.5
            },
            "siglip": {
                "model_variant": "base",
                "embedding_dim": 768
            }
        },
        "vector_database": {
            "db_path": "./test_rag.db",
            "vector_search": {
                "k_nearest": 10,
                "similarity_threshold": 0.5
            },
            "hybrid_search": {
                "vector_weight": 0.6,
                "tag_weight": 0.4
            }
        },
        "intelligent_router": {
            "duration_threshold": 30,
            "ffmpeg": {"codec": "copy"},
            "auto_editor": {"motion_threshold": 0.02},
            "edl_export": {"format": "fcpxml"}
        },
        "output": {
            "output_dir": "./test_output",
            "organize_by_query": True
        },
        "logging": {
            "level": "INFO",
            "console_output": False
        }
    }
