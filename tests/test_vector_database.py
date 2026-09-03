"""Tests for vector database module."""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from src.vector_database import VectorDatabase


class TestVectorDatabase:
    """Test cases for VectorDatabase."""

    @patch("lancedb.connect")
    def test_init_default_config(self, mock_connect):
        """Test initialization with default config."""
        config = {"db_path": "./test.db"}
        db = VectorDatabase(config)
        
        assert db.db_path == "./test.db"
        assert db.auto_table_naming == True
        assert db.table_prefix == "scenes_"
        mock_connect.assert_called_once_with("./test.db")

    @patch("lancedb.connect")
    def test_init_with_siglip_model(self, mock_connect):
        """Test initialization with cached SigLIP model."""
        config = {"db_path": "./test.db"}
        mock_model = Mock()
        mock_processor = Mock()
        
        db = VectorDatabase(config, siglip_model=mock_model, siglip_processor=mock_processor)
        
        assert db._siglip_model == mock_model
        assert db._siglip_processor == mock_processor

    @patch("lancedb.connect")
    def test_store_scenes(self, mock_connect):
        """Test storing scenes in database."""
        mock_db = Mock()
        mock_table = Mock()
        mock_db.create_table.return_value = mock_table
        mock_connect.return_value = mock_db
        
        config = {"db_path": "./test.db", "auto_table_naming": True, "table_prefix": "scenes_"}
        db = VectorDatabase(config)
        
        scenes = [
            {
                "scene_id": 0,
                "start_time": 0.0,
                "end_time": 5.0,
                "duration": 5.0,
                "video_path": "test.mp4",
                "yolo_tags": ["car"],
                "embedding": np.array([0.1, 0.2, 0.3], dtype=np.float32)
            }
        ]
        
        table_name = db.store_scenes(scenes, "test.mp4")
        
        assert table_name == "scenes_test"
        mock_db.create_table.assert_called_once()

    @patch("lancedb.connect")
    def test_store_scenes_custom_prefix(self, mock_connect):
        """Test storing scenes with custom table prefix."""
        mock_db = Mock()
        mock_connect.return_value = mock_db
        
        config = {
            "db_path": "./test.db",
            "auto_table_naming": False,
            "table_prefix": "custom_"
        }
        db = VectorDatabase(config)
        
        scenes = [{"scene_id": 0, "start_time": 0.0, "end_time": 5.0, "duration": 5.0, "video_path": "test.mp4"}]
        
        table_name = db.store_scenes(scenes, "test.mp4")
        
        assert table_name == "custom_"

    @patch("lancedb.connect")
    def test_generate_query_embedding_with_cached_model(self, mock_connect):
        """Test query embedding with cached model."""
        mock_model = Mock()
        mock_processor = Mock()
        
        # Mock the processor and model outputs
        mock_inputs = {"input_ids": Mock()}
        mock_processor.return_value = mock_inputs
        
        mock_outputs = Mock()
        mock_outputs.pooler_output = Mock()
        mock_outputs.pooler_output.__getitem__ = Mock(return_value=Mock())
        mock_model.return_value = mock_outputs
        
        config = {"db_path": "./test.db"}
        db = VectorDatabase(config, siglip_model=mock_model, siglip_processor=mock_processor)
        
        # Mock torch.no_grad context
        with patch("torch.no_grad"):
            embedding = db._generate_query_embedding("test query")
            
            assert isinstance(embedding, np.ndarray)
            assert embedding.dtype == np.float32

    @patch("lancedb.connect")
    def test_generate_query_embedding_loads_model(self, mock_connect):
        """Test query embedding loads model when not cached."""
        config = {"db_path": "./test.db"}
        db = VectorDatabase(config)
        
        assert db._siglip_model is None
        assert db._siglip_processor is None
        
        with patch("transformers.AutoProcessor.from_pretrained") as mock_proc, \
             patch("transformers.AutoModel.from_pretrained") as mock_model, \
             patch("torch.no_grad"):
            
            mock_processor = Mock()
            mock_proc.return_value = mock_processor
            
            mock_model_instance = Mock()
            mock_outputs = Mock()
            mock_outputs.pooler_output = Mock()
            mock_outputs.pooler_output.__getitem__ = Mock(return_value=Mock())
            mock_model_instance.return_value = mock_outputs
            mock_model.return_value = mock_model_instance
            
            embedding = db._generate_query_embedding("test query")
            
            # Model should now be loaded
            assert db._siglip_model is not None
            assert db._siglip_processor is not None

    @patch("lancedb.connect")
    def test_generate_query_embedding_failure(self, mock_connect):
        """Test query embedding failure handling."""
        config = {"db_path": "./test.db"}
        db = VectorDatabase(config)
        
        with patch("transformers.AutoProcessor.from_pretrained", side_effect=Exception("Model not found")):
            embedding = db._generate_query_embedding("test query")
            
            # Should return zero vector on failure
            assert isinstance(embedding, np.ndarray)
            assert len(embedding) == 768
            assert np.all(embedding == 0)

    @patch("lancedb.connect")
    def test_search(self, mock_connect):
        """Test vector search."""
        mock_db = Mock()
        mock_table = Mock()
        
        # Mock search results
        mock_results = [
            {"scene_id": 0, "start_time": 0.0, "_distance": 0.8},
            {"scene_id": 1, "start_time": 10.0, "_distance": 0.6}
        ]
        mock_search = Mock()
        mock_search.limit.return_value.to_list.return_value = mock_results
        mock_table.search.return_value = mock_search
        mock_db.open_table.return_value = mock_table
        mock_connect.return_value = mock_db
        
        config = {
            "db_path": "./test.db",
            "vector_search": {"k_nearest": 10, "similarity_threshold": 0.5}
        }
        db = VectorDatabase(config)
        
        with patch.object(db, '_generate_query_embedding', return_value=np.array([0.1, 0.2, 0.3])):
            results = db.search("test query", "scenes_test")
            
            assert len(results) == 2
            assert results[0]["scene_id"] == 0

    @patch("lancedb.connect")
    def test_batch_search(self, mock_connect):
        """Test batch search."""
        mock_db = Mock()
        mock_connect.return_value = mock_db
        
        config = {
            "db_path": "./test.db",
            "vector_search": {"batch_size": 2}
        }
        db = VectorDatabase(config)
        
        with patch.object(db, 'search', return_value=[{"scene_id": 0}]):
            queries = ["query1", "query2", "query3"]
            results = db.batch_search(queries, "scenes_test")
            
            assert len(results) == 3
            assert all(len(r) == 1 for r in results)

    @patch("lancedb.connect")
    def test_hybrid_search(self, mock_connect):
        """Test hybrid search with tags."""
        mock_db = Mock()
        mock_table = Mock()
        
        mock_results = [
            {"scene_id": 0, "start_time": 0.0, "_distance": 0.8, "yolo_tags": ["car", "person"]},
            {"scene_id": 1, "start_time": 10.0, "_distance": 0.7, "yolo_tags": ["dog"]}
        ]
        mock_search = Mock()
        mock_search.limit.return_value.to_list.return_value = mock_results
        mock_table.search.return_value = mock_search
        mock_db.open_table.return_value = mock_table
        mock_connect.return_value = mock_db
        
        config = {
            "db_path": "./test.db",
            "vector_search": {"k_nearest": 10},
            "hybrid_search": {"vector_weight": 0.6, "tag_weight": 0.4}
        }
        db = VectorDatabase(config)
        
        with patch.object(db, '_generate_query_embedding', return_value=np.array([0.1, 0.2, 0.3])):
            results = db.hybrid_search("car scene", ["car"], "scenes_test")
            
            # Should only return results with matching tags
            assert len(results) == 1
            assert results[0]["scene_id"] == 0
            assert "hybrid_score" in results[0]
