# Installation & Getting Started

## Quick Start (5 minutes)

### 1. Clone & Setup

```bash
git clone https://github.com/brandsconnet-byte/video-rag-engine.git
cd video-rag-engine
python scripts/setup.py
```

This will:
- Install all dependencies
- Create necessary directories
- Download AI models (YOLOv8, SigLIP)
- Generate example configurations

### 2. Process Your First Video

```bash
python main.py process --video path/to/video.mp4
```

This will:
- Detect scenes in your video
- Run YOLOv8 + SigLIP on keyframes
- Create a searchable LanceDB database
- Print the table name for queries

### 3. Search for Scenes

```bash
python main.py search --table scenes_video --query "drone shot"
```

Returns matching scenes with timestamps and objects detected.

### 4. Extract Matching Clips

```bash
python main.py extract \
  --video path/to/video.mp4 \
  --table scenes_video \
  --query "car"
```

Clips are automatically routed:
- **Short clips (< 30s)** → FFmpeg direct extract
- **Long clips (> 30s)** → auto-editor (auto-speed/cut)

### 5. Generate EDL for Pro Editing

```bash
python main.py edl \
  --table scenes_video \
  --query "drone" \
  --output timeline.xml
```

Open `timeline.xml` in DaVinci Resolve or Premiere Pro.

---

## Installation Options

### Option A: Standard Installation

```bash
pip install -r requirements.txt
python scripts/setup.py
```

### Option B: Development Installation

```bash
pip install -r requirements.txt -r requirements-dev.txt
python scripts/setup.py
```

Includes testing, linting, and documentation tools.

### Option C: Manual Installation

```bash
# Core dependencies
pip install scenedetect[opencv]==0.6.1
pip install ultralytics==8.1.0
pip install torch torchvision
pip install transformers==4.36.0
pip install lancedb==0.3.0
pip install ffmpeg-python==0.2.1
pip install PyYAML click loguru

# Optional: GPU support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

## System Requirements

### Minimum
- Python 3.8+
- 8GB RAM
- 5GB disk space (for models)

### Recommended
- Python 3.9+
- 16GB RAM
- NVIDIA GPU with 6GB+ VRAM (CUDA 11.8+)
- 10GB disk space

### Supported OS
- Linux (Ubuntu 20.04+)
- macOS (Intel & Apple Silicon)
- Windows 10/11

---

## Configuration

### Pre-Built Configs

**Fast (CPU)**
```bash
python main.py process --video video.mp4 --config config/fast.yaml
```

**Balanced (Mixed)**
```bash
python main.py process --video video.mp4 --config config/balanced.yaml
```

**Accurate (GPU)**
```bash
python main.py process --video video.mp4 --config config/accurate.yaml
```

### Custom Configuration

Edit `config/default.yaml` to customize:
- Scene detection sensitivity (conservative/balanced/aggressive)
- AI model sizes (nano to xlarge)
- Database search settings
- Output preferences

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'ultralytics'"

```bash
pip install ultralytics
```

### "CUDA out of memory"

Use a smaller model:
```bash
# In config/default.yaml, change:
dual_brain:
  yolo:
    model_size: "small"  # was: large
  siglip:
    model_variant: "tiny"  # was: base
```

### "Scene detection found 0 scenes"

Adjust sensitivity:
```bash
# In config/default.yaml, change:
scene_detection:
  sensitivity: "aggressive"  # was: balanced
```

### Models downloading slowly

Pre-download them:
```bash
python scripts/download_models.py
```

---

## Next Steps

- 📖 Check out [examples/](examples/) for workflow examples
- ⚙️ Customize [config/default.yaml](config/default.yaml)
- 🚀 See [CLI reference](#cli-reference) below

---

## CLI Reference

```bash
# Process video through full pipeline
python main.py process \
  --video path/to/video.mp4 \
  --config config/default.yaml \
  --output ./extracted_clips

# Search in database
python main.py search \
  --table scenes_video \
  --query "drone shot" \
  --limit 10

# Search and extract clips
python main.py extract \
  --video path/to/video.mp4 \
  --table scenes_video \
  --query "car" \
  --output ./clips

# Generate EDL/XML
python main.py edl \
  --table scenes_video \
  --query "drone" \
  --output timeline.xml

# Show system info
python main.py info --config config/default.yaml
```

---

## Performance Tips

### Speed Optimization
1. Use `config/fast.yaml` for quick processing
2. Lower `min_scene_length` in config
3. Use smaller video resolution
4. Reduce `batch_size` if running on CPU

### Quality Optimization
1. Use `config/accurate.yaml` for best results
2. Increase `confidence_threshold` for objects
3. Use full resolution video
4. Process on GPU if available

### Memory Optimization
1. Process video in chunks
2. Clear cache: `rm -rf ~/.cache/huggingface/hub/`
3. Reduce `batch_size` in config

---

Have questions? Open an issue on GitHub!
