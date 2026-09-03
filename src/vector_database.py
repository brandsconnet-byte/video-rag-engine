"""Vector database management using LanceDB."""

import os
from typing import List, Dict, Any, Optional
import numpy as np
from loguru import logger

try:
    import lancedb
except ImportError:
    logger.warning("LanceDB not installed. Install with: pip install lancedb")

try:
    import torch
    from transformers import AutoProcessor, AutoModel
except ImportError:
    logger.warning("Transformers not installed. Install with: pip install transformers torch")


class VectorDatabase:
    """Manages vector storage and hybrid search using LanceDB."""

    def __init__(self, config: Dict[str, Any], siglip_model=None, siglip_processor=None):
        """Initialize vector database.
        
        Args:
            config: Configuration dictionary
            siglip_model: Pre-loaded SigLIP model for query embeddings
            siglip_processor: Pre-loaded SigLIP processor
        """
        self.db_path = config.get("db_path", "./video_rag.db")
        self.auto_table_naming = config.get("auto_table_naming", True)
        self.table_prefix = config.get("table_prefix", "scenes_")
        self.search_config = config.get("vector_search", {})
        self.hybrid_config = config.get("hybrid_search", {})
        
        # Connect to database
        self.db = lancedb.connect(self.db_path)
        logger.info(f"Connected to LanceDB at {self.db_path}")
        
        # Cache SigLIP model for query embeddings
        self._siglip_model = siglip_model
        self._siglip_processor = siglip_processor
        self._siglip_model_name = "google/siglip-base-patch16-224"

    def store_scenes(self, scenes: List[Dict[str, Any]], video_path: str) -> str:
        """Store indexed scenes in vector database.
        
        Args:
            scenes: List of processed scenes with embeddings
            video_path: Path to source video
            
        Returns:
            Table name
        """
        # Generate table name
        if self.auto_table_naming:
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            table_name = f"{self.table_prefix}{video_name}"
        else:
            table_name = self.table_prefix
        
        try:
            # Prepare data for storage
            data = []
            for scene in scenes:
                data.append({
                    "scene_id": scene["scene_id"],
                    "start_time": scene["start_time"],
                    "end_time": scene["end_time"],
                    "duration": scene["duration"],
                    "video_path": scene["video_path"],
                    "yolo_tags": scene.get("yolo_tags", []),
                    "embedding": scene.get("embedding", np.zeros(768, dtype=np.float32)),
                })
            
            # Create or overwrite table
            table = self.db.create_table(table_name, data=data, mode="overwrite")
            
            logger.info(f"Stored {len(data)} scenes in table '{table_name}'")
            return table_name
        
        except Exception as e:
            logger.error(f"Failed to store scenes: {e}")
            raise

    def search(self, query: str, table_name: str) -> List[Dict[str, Any]]:
        """Search for scenes matching a query.
        
        Args:
            query: Search query (text description)
            table_name: LanceDB table name
            
        Returns:
            List of matching scenes
        """
        try:
            table = self.db.open_table(table_name)
            
            # Generate query embedding
            query_embedding = self._generate_query_embedding(query)
            
            # Vector search
            k = self.search_config.get("k_nearest", 10)
            results = table.search(query_embedding).limit(k).to_list()
            
            # Filter by threshold
            threshold = self.search_config.get("similarity_threshold", 0.5)
            filtered_results = [r for r in results if r.get("_distance", 0) >= threshold]
            
            logger.info(f"Found {len(filtered_results)} matching scenes for query: '{query}'")
            return filtered_results
        
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def batch_search(self, queries: List[str], table_name: str) -> List[List[Dict[str, Any]]]:
        """Perform multiple searches at once.
        
        Args:
            queries: List of search queries
            table_name: LanceDB table name
            
        Returns:
            List of result lists (one per query)
        """
        batch_size = self.search_config.get("batch_size", 32)
        results_all = []
        
        try:
            for i in range(0, len(queries), batch_size):
                batch = queries[i:i+batch_size]
                logger.debug(f"Processing batch {i//batch_size + 1} ({len(batch)} queries)")
                
                for query in batch:
                    results = self.search(query, table_name)
                    results_all.append(results)
            
            logger.info(f"Batch search completed for {len(queries)} queries")
            return results_all
        
        except Exception as e:
            logger.error(f"Batch search failed: {e}")
            raise

    def hybrid_search(self, query: str, tags: List[str], table_name: str) -> List[Dict[str, Any]]:
        """Perform hybrid search (vector + tag filtering).
        
        Args:
            query: Text query for semantic search
            tags: YOLO tags to filter by
            table_name: LanceDB table name
            
        Returns:
            List of matching scenes
        """
        try:
            table = self.db.open_table(table_name)
            
            # Generate query embedding
            query_embedding = self._generate_query_embedding(query)
            
            # Vector search
            k = self.search_config.get("k_nearest", 10)
            results = table.search(query_embedding).limit(k).to_list()
            
            # Filter by tags
            vector_weight = self.hybrid_config.get("vector_weight", 0.6)
            tag_weight = self.hybrid_config.get("tag_weight", 0.4)
            
            filtered_results = []
            for r in results:
                scene_tags = r.get("yolo_tags", [])
                tag_match = any(tag in scene_tags for tag in tags)
                
                if tag_match:
                    # Score combination
                    vector_score = r.get("_distance", 0) * vector_weight
                    tag_score = tag_weight if tag_match else 0
                    r["hybrid_score"] = vector_score + tag_score
                    filtered_results.append(r)
            
            # Sort by hybrid score
            filtered_results = sorted(filtered_results, key=lambda x: x.get("hybrid_score", 0), reverse=True)
            
            logger.info(f"Hybrid search found {len(filtered_results)} scenes")
            return filtered_results
        
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            return []

    def _generate_query_embedding(self, query: str) -> np.ndarray:
        """Generate embedding for text query using cached SigLIP model.
        
        Args:
            query: Text query
            
        Returns:
            Query embedding vector
        """
        try:
            # Use cached model if available, otherwise load once
            if self._siglip_model is None or self._siglip_processor is None:
                logger.debug("Loading SigLIP model for query embedding (first time)")
                self._siglip_processor = AutoProcessor.from_pretrained(self._siglip_model_name)
                self._siglip_model = AutoModel.from_pretrained(self._siglip_model_name)
            
            inputs = self._siglip_processor(text=[query], return_tensors="pt")
            
            with torch.no_grad():
                outputs = self._siglip_model.text_model(**inputs)
                # SigLIP uses pooled_output from text model
                embedding = outputs.pooler_output if hasattr(outputs, 'pooler_output') else outputs.last_hidden_state[:, 0, :]
            
            embedding = embedding[0].cpu().numpy()
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding.astype(np.float32)
        except Exception as e:
            logger.error(f"Query embedding generation failed: {e}")
            embedding_dim = 768
            return np.zeros(embedding_dim, dtype=np.float32)
