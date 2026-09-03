# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-08-26

### Added
- Initial release of Video RAG Engine
- Scene detection using PySceneDetect
- Dual-brain AI indexing (YOLOv8 + SigLIP)
- Vector database integration with LanceDB
- Intelligent routing for clip export
- FFmpeg direct extraction for short clips
- auto-editor integration for long clips
- EDL/XML generation for professional editing
- Batch query processing
- Hybrid search (vector + tag filtering)
- CLI interface with multiple commands
- Configuration system with preset profiles
  - Fast (CPU optimized)
  - Balanced (mixed)
  - Accurate (GPU optimized)
- Setup and installation scripts
- Comprehensive documentation
- Contributing guidelines

### Features
- ✅ Process 3-hour videos in 45-120 minutes
- ✅ Detect scenes, objects, and semantic content
- ✅ Extract clips in multiple formats
- ✅ Auto-optimize long clips
- ✅ Generate professional EDL files
- ✅ Batch processing of multiple queries
- ✅ GPU acceleration support
- ✅ Configurable AI models

### Known Limitations
- No real-time processing (yet)
- Limited to local deployment (no cloud storage)
- Manual model training not supported
- Single GPU optimization only

## Future Versions

### [0.2.0] - Planned
- Real-time processing pipeline
- Web UI for scene browsing
- Cloud storage integration
- Multi-GPU support
- Advanced color science

### [0.3.0] - Planned
- Mobile app
- Webhook support
- Custom model training
- Advanced effects library
