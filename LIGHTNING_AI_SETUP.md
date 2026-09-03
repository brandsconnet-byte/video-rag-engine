# Lightning AI Setup Guide

## Why Lightning AI?

| Feature | Back4App | Lightning AI |
|---------|----------|--------------|
| GPU | No | Yes (T4/V100/A100) |
| PyTorch | Download 670MB | Pre-installed |
| CUDA | No | Yes |
| AI Model Speed | Very slow | Fast |
| Storage | Limited | 100GB+ |
| Cost | Free tier limited | Free credits |

## Quick Start

### 1. Sign Up
- Go to https://lightning.ai
- Sign up with GitHub

### 2. Create Studio
```bash
# In Lightning AI terminal
git clone https://github.com/brandsconnet-byte/video-rag-engine.git
cd video-rag-engine

# Install dependencies (torch already installed)
pip install -r requirements-lightning.txt

# Download AI models
python scripts/download_models.py

# Run the app
python app.py
```

### 3. Run with GPU
```bash
# In Lightning AI, select GPU from the machine options
# Then run:
python main.py process --video your_video.mp4
```

### 4. Deploy as App (Optional)
```bash
lightning run app lightning_app.py
```

## File Structure for Lightning AI

```
video-rag-engine/
├── requirements-lightning.txt   # Without torch (pre-installed)
├── lightning_app.py             # Lightning AI app config
├── LIGHTNING_AI_SETUP.md        # This file
├── app.py                       # Flask web UI
├── main.py                      # CLI
└── src/                         # Core modules
```

## Performance Comparison

| Operation | CPU (Back4App) | GPU (Lightning) |
|-----------|---------------|-----------------|
| Scene Detection (1hr video) | ~10 min | ~2 min |
| YOLOv8 Processing | ~30 min | ~3 min |
| SigLIP Embedding | ~20 min | ~2 min |
| Total Pipeline | ~1 hour | ~7 min |

## Persistent Storage

Lightning AI provides persistent storage at:
- `/home/jovyan/` - Your home directory
- `/data/` - Shared data storage

Store your videos and database here:
```bash
mkdir -p /data/videos /data/database
```

## Environment Variables

Set these in Lightning AI studio settings:
```
VIDEO_RAG_DB_PATH=/data/database
VIDEO_RAG_OUTPUT=/data/output
```

## Troubleshooting

**"CUDA out of memory"**
→ Use smaller YOLO model: `yolov8n.pt` instead of `yolov8m.pt`

**"Model download slow"**
→ Models are cached in `~/.cache/` after first download

**"LanceDB errors"**
→ Ensure write permissions: `chmod 777 /data/database`

## Next Steps

1. Upload test videos to `/data/videos/`
2. Process: `python main.py process --video /data/videos/test.mp4`
3. Search: `python main.py search --table scenes_test --query "car"`
4. Extract: `python main.py extract --video test.mp4 --table scenes_test --query "car"`
