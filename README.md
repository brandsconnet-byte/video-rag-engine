# Video RAG Engine 🎬

A unified video processing pipeline that intelligently detects scenes, extracts clips, and auto-edits footage using AI-powered indexing and hybrid search.

## Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────┐
│ VIDEO RAG ENGINE: The Unified Pipeline                          │
└─────────────────────────────────────────────────────────────────┘

[3-Hour Low-Res Video]
         ↓
    [STEP 1: Scene Detection]
    PySceneDetect → Keyframes + Scene Boundaries
         ↓
    [STEP 2: Dual-Brain AI Indexing]
    YOLOv8 (Object Tags) + SigLIP (Vector Embeddings)
         ↓
    [STEP 3: Hybrid Vector Database]
    LanceDB → Searchable Scene Index
         ↓
    [STEP 4: Intelligent Routing & Export]
         ├─→ Route A: Short Clips (< 30s) → FFmpeg Direct Extract
         ├─→ Route B: Long Clips (> 30s) → auto-editor (Auto Speed/Cut)
         └─→ Route C: Pro Export → EDL/XML for DaVinci/Premiere
```

## Features

✅ **Scene Detection**: Automatically detects cuts and transitions  
✅ **Dual AI Indexing**: Object detection + semantic embeddings  
✅ **Hybrid Search**: Query by objects AND visual concepts simultaneously  
✅ **Smart Routing**: Auto-decides between FFmpeg, auto-editor, or pro export  
✅ **Configurable**: Tunable sensitivity, model selection, batch limits  
✅ **Batch Processing**: Process multiple queries at once  

## Quick Start

### Installation

```bash
git clone https://github.com/brandsconnet-byte/video-rag-engine.git
cd video-rag-engine
pip install -r requirements.txt
```

### Basic Usage

```bash
python main.py --video path/to/video.mp4 --config config/default.yaml
```

### Search & Extract

```bash
python main.py \
  --video path/to/video.mp4 \
  --query "drone shot with car" \
  --config config/default.yaml \
  --output ./extracted_clips
```

## Configuration

All settings are in `config/default.yaml`:

- **Scene Detection**: Sensitivity levels (conservative, balanced, aggressive)
- **AI Models**: YOLOv8 sizes (nano, small, medium, large) and SigLIP variants
- **Database**: Batch query limits, vector dimensions, search thresholds
- **Output**: Clip extraction settings, EDL format preferences

## File Structure

```
video-rag-engine/
├── README.md
├── requirements.txt
├── config/
│   └── default.yaml                 # Main configuration
├── src/
│   ├── pipeline.py                  # Main orchestration
│   ├── scene_detector.py            # PySceneDetect wrapper
│   ├── dual_brain_processor.py      # YOLOv8 + SigLIP
│   ├── vector_database.py           # LanceDB manager
│   ├── intelligent_router.py        # Routing logic
│   └── export_manager.py            # FFmpeg, auto-editor, EDL
├── scripts/
│   ├── setup.py                     # Installation script
│   └── download_models.py           # Pre-download AI models
└── examples/
    ├── basic_extraction.py          # Simple clip extraction
    ├── batch_queries.py             # Multiple simultaneous searches
    └── pro_export.py                # EDL/XML generation
```

## Dependencies

- **PySceneDetect**: Scene boundary detection
- **YOLOv8**: Real-time object detection
- **SigLIP**: Vision-language semantic embeddings
- **LanceDB**: Vector database for hybrid search
- **FFmpeg**: Fast clip extraction
- **auto-editor**: Automatic silence/motion-based editing
- **lxml**: EDL/XML generation

## Roadmap

- [ ] Support for GPU acceleration (CUDA/Metal)
- [ ] Web UI for interactive scene browsing
- [ ] Real-time processing pipeline
- [ ] Multi-format output (MP4, MOV, ProRes)
- [ ] Cloud storage integration (S3, GCS)
- [ ] Webhook support for automation

## License

MIT

## Author

Built by brandsconnet-byte
