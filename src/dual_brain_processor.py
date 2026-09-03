"""Dual-brain AI indexing: YOLOv8 + SigLIP semantic embeddings."""

import os
from typing import List, Dict, Any, Tuple
import numpy as np
from loguru import logger

try:
    from ultralytics import YOLO
except ImportError:
    logger.warning("YOLOv8 not installed. Install with: pip install ultralytics")

try:
    from PIL import Image
except ImportError:
    logger.warning("Pillow not installed. Install with: pip install Pillow")

try:
    import torch
    from transformers import AutoProcessor, AutoModel
except ImportError:
    logger.warning("Transformers not installed. Install with: pip install transformers torch")


class DualBrainProcessor:
    """Processes scenes using YOLOv8 (object detection) and SigLIP (semantic embeddings)."""

    MODEL_SIZES = {
        "yolo": ["nano", "small", "medium", "large", "xlarge"],
        "siglip": ["tiny", "base", "large"]
    }

    def __init__(self, config: Dict[str, Any]):
        """Initialize dual-brain processor.
        
        Args:
            config: Configuration dictionary
        """
        self.yolo_config = config.get("yolo", {})
        self.siglip_config = config.get("siglip", {})
        
        # Initialize models
        self.yolo_model = self._init_yolo()
        self.siglip_model, self.siglip_processor = self._init_siglip()
        
        logger.info("Dual-brain processor initialized")

    def _init_yolo(self):
        """Initialize YOLOv8 model.
        
        Returns:
            YOLOv8 model instance
        """
        model_size = self.yolo_config.get("model_size", "medium")
        use_gpu = self.yolo_config.get("use_gpu", True)
        device = self.yolo_config.get("device")
        
        try:
            model = YOLO(f"yolov8{model_size}.pt")
            
            if device:
                model.to(device)
            elif use_gpu:
                model.to("cuda" if torch.cuda.is_available() else "cpu")
            
            logger.info(f"YOLOv8 {model_size} loaded on {model.device}")
            return model
        except Exception as e:
            logger.error(f"Failed to load YOLOv8: {e}")
            raise

    def _init_siglip(self):
        """Initialize SigLIP model.
        
        Returns:
            Tuple of (model, processor)
        """
        model_variant = self.siglip_config.get("model_variant", "base")
        use_gpu = self.siglip_config.get("use_gpu", True)
        
        try:
            # Official SigLIP models from Google
            model_map = {
                "tiny": "google/siglip-so400m-patch14-224",
                "base": "google/siglip-base-patch16-224",
                "large": "google/siglip-large-patch16-384"
            }
            model_name = model_map.get(model_variant, "google/siglip-base-patch16-224")
            
            processor = AutoProcessor.from_pretrained(model_name)
            model = AutoModel.from_pretrained(model_name)
            
            if use_gpu and torch.cuda.is_available():
                model = model.cuda()
            
            logger.info(f"SigLIP {model_variant} loaded from {model_name}")
            return model, processor
        except Exception as e:
            logger.error(f"Failed to load SigLIP: {e}")
            raise

    def process_scenes(self, scenes: List[Dict[str, Any]], video_path: str) -> List[Dict[str, Any]]:
        """Process scenes through both AI models.
        
        Args:
            scenes: List of scene dictionaries from detector
            video_path: Path to video file
            
        Returns:
            List of scenes with AI annotations
        """
        logger.info(f"Processing {len(scenes)} scenes through dual-brain")
        
        import cv2
        processed_scenes = []
        
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            for scene in scenes:
                logger.debug(f"Processing scene {scene['scene_id']}")
                
                # Extract keyframe
                keyframe = self._extract_keyframe(cap, scene["start_time"], fps)
                
                if keyframe is None:
                    logger.warning(f"Failed to extract keyframe for scene {scene['scene_id']}")
                    continue
                
                # YOLOv8: Object detection
                yolo_tags = self._detect_objects(keyframe)
                
                # SigLIP: Semantic embedding
                embedding = self._generate_embedding(keyframe)
                
                # Combine results
                enriched_scene = scene.copy()
                enriched_scene["yolo_tags"] = yolo_tags
                enriched_scene["embedding"] = embedding
                enriched_scene["keyframe"] = keyframe
                
                processed_scenes.append(enriched_scene)
            
            cap.release()
            logger.info(f"Processed {len(processed_scenes)} scenes")
            return processed_scenes
        
        except Exception as e:
            logger.error(f"Scene processing failed: {e}")
            raise

    def _extract_keyframe(self, cap, timestamp: float, fps: float):
        """Extract a single keyframe at timestamp.
        
        Args:
            cap: OpenCV video capture object
            timestamp: Time in seconds
            fps: Frames per second
            
        Returns:
            Keyframe as numpy array or None
        """
        try:
            frame_num = int(timestamp * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            
            if ret:
                return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return None
        except Exception as e:
            logger.error(f"Keyframe extraction failed: {e}")
            return None

    def _detect_objects(self, frame) -> List[str]:
        """Detect objects in frame using YOLOv8.
        
        Args:
            frame: Image frame (numpy array)
            
        Returns:
            List of detected object names
        """
        try:
            results = self.yolo_model(frame, verbose=False)
            
            tags = []
            confidence_threshold = self.yolo_config.get("confidence_threshold", 0.5)
            
            for r in results:
                for box in r.boxes:
                    if box.conf[0] >= confidence_threshold:
                        class_name = r.names[int(box.cls[0])]
                        tags.append(class_name)
            
            return list(set(tags))  # Remove duplicates
        except Exception as e:
            logger.error(f"Object detection failed: {e}")
            return []

    def _generate_embedding(self, frame) -> np.ndarray:
        """Generate semantic embedding using SigLIP.
        
        Args:
            frame: Image frame (numpy array)
            
        Returns:
            Embedding vector
        """
        try:
            # Convert to PIL Image
            pil_image = Image.fromarray(frame)
            
            # Process and generate embedding using SigLIP
            inputs = self.siglip_processor(images=pil_image, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.siglip_model.vision_model(**inputs)
                # SigLIP uses pooled_output from vision model
                embedding = outputs.pooler_output if hasattr(outputs, 'pooler_output') else outputs.last_hidden_state[:, 0, :]
            
            # Normalize embedding
            embedding = embedding[0].cpu().numpy()
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding.astype(np.float32)
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            # Get actual embedding dimension from config or default
            embedding_dim = self.siglip_config.get("embedding_dim", 768)
            return np.zeros(embedding_dim, dtype=np.float32)  # Default to zero vector
