"""Tests for export manager module."""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from src.export_manager import ExportManager


class TestExportManager:
    """Test cases for ExportManager."""

    def test_init_default_config(self):
        """Test initialization with default config."""
        output_config = {}
        router_config = {}
        
        manager = ExportManager(output_config, router_config)
        
        assert manager.output_dir == "./extracted_clips"
        assert manager.organize_by_query == True
        assert manager.preserve_metadata == True

    def test_init_custom_config(self):
        """Test initialization with custom config."""
        output_config = {
            "output_dir": "./custom_output",
            "organize_by_query": False,
            "preserve_metadata": False
        }
        router_config = {"ffmpeg": {"codec": "libx264"}}
        
        manager = ExportManager(output_config, router_config)
        
        assert manager.output_dir == "./custom_output"
        assert manager.organize_by_query == False
        assert manager.preserve_metadata == False

    @patch("os.makedirs")
    def test_output_directory_created(self, mock_makedirs):
        """Test that output directory is created on init."""
        ExportManager({"output_dir": "./test_output"}, {})
        mock_makedirs.assert_called_with("./test_output", exist_ok=True)

    @patch("ffmpeg.input")
    @patch("os.makedirs")
    def test_extract_with_ffmpeg_success(self, mock_makedirs, mock_ffmpeg_input):
        """Test successful FFmpeg extraction."""
        mock_stream = Mock()
        mock_output = Mock()
        mock_output.run = Mock(return_value=(None, None))
        mock_stream.output = Mock(return_value=mock_output)
        mock_ffmpeg_input.return_value = mock_stream
        
        manager = ExportManager({}, {})
        result = manager.extract_with_ffmpeg("test.mp4", 10.0, 20.0, "./output")
        
        assert result is not None
        assert "clip_10_20.mp4" in result
        mock_ffmpeg_input.assert_called_once()

    @patch("shutil.which")
    @patch("subprocess.run")
    @patch("os.makedirs")
    def test_extract_with_auto_editor_fallback(self, mock_makedirs, mock_run, mock_which):
        """Test auto-editor fallback when not installed."""
        mock_which.return_value = None  # auto-editor not found
        
        manager = ExportManager({}, {})
        
        with patch.object(manager, 'extract_with_ffmpeg', return_value="fallback.mp4") as mock_ffmpeg:
            result = manager.extract_with_auto_editor("test.mp4", 10.0, 60.0, "./output")
            
            assert result == "fallback.mp4"
            mock_ffmpeg.assert_called_once()

    @patch("shutil.which")
    @patch("subprocess.run")
    @patch("os.path.exists")
    @patch("os.remove")
    @patch("os.makedirs")
    def test_extract_with_auto_editor_success(self, mock_makedirs, mock_remove, mock_exists, mock_run, mock_which):
        """Test successful auto-editor extraction."""
        mock_which.return_value = "/usr/bin/auto-editor"
        mock_exists.return_value = True
        
        manager = ExportManager({}, {"auto_editor": {"margin": "0.2sec"}})
        result = manager.extract_with_auto_editor("test.mp4", 10.0, 60.0, "./output")
        
        assert result is not None
        assert "clip_optimized" in result
        # Should call ffmpeg then auto-editor
        assert mock_run.call_count >= 2

    def test_generate_generic_edl(self):
        """Test generic EDL generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.edl")
            
            results = [
                {"scene_id": 0, "start_time": 0.0, "end_time": 5.0, "yolo_tags": ["car"]},
                {"scene_id": 1, "start_time": 10.0, "end_time": 15.0, "yolo_tags": ["person", "dog"]}
            ]
            
            manager = ExportManager({}, {})
            result = manager._generate_generic_edl(results, output_path)
            
            assert result == output_path
            assert os.path.exists(output_path)
            
            with open(output_path, 'r') as f:
                content = f.read()
                assert "TITLE: Video RAG Engine Export" in content
                assert "001  AX" in content
                assert "002  AX" in content
                assert "car" in content
                assert "person" in content

    def test_generate_edl_format_selection(self):
        """Test EDL format selection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExportManager({}, {})
            
            results = [{"scene_id": 0, "start_time": 0.0, "end_time": 5.0}]
            
            # Test generic EDL
            generic_path = os.path.join(tmpdir, "generic.edl")
            result = manager.generate_edl(results, generic_path, format_type="edl")
            assert result is not None
            
            # Test FCPXML (may fail without lxml, should fallback)
            fcpxml_path = os.path.join(tmpdir, "test.fcpxml")
            result = manager.generate_edl(results, fcpxml_path, format_type="fcpxml")
            # Should either succeed or fallback to generic
            assert result is not None

    def test_generate_edl_empty_results(self):
        """Test EDL generation with empty results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "empty.edl")
            
            manager = ExportManager({}, {})
            result = manager._generate_generic_edl([], output_path)
            
            assert result == output_path
            assert os.path.exists(output_path)
            
            with open(output_path, 'r') as f:
                content = f.read()
                assert "TITLE: Video RAG Engine Export" in content

    def test_generate_edl_failure(self):
        """Test EDL generation failure handling."""
        manager = ExportManager({}, {})
        
        # Try to write to invalid path
        result = manager.generate_edl([], "/invalid/path/test.edl")
        assert result is None
