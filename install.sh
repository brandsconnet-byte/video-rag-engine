#!/bin/bash
# Auto-install and run Video RAG Engine

echo ""
echo "🎬 Video RAG Engine - Auto Installation"
echo "======================================="
echo ""

# Check if Docker is installed
if command -v docker &> /dev/null; then
    echo "✅ Docker found"
    
    echo "\n🐳 Building Docker image..."
    docker build -t video-rag-engine .
    
    echo "\n🚀 Starting container..."
    docker run -p 5000:5000 \
      -v $(pwd)/uploaded_videos:/app/uploaded_videos \
      -v $(pwd)/extracted_clips:/app/extracted_clips \
      video-rag-engine
else
    echo "⚠️  Docker not found. Installing dependencies locally...\n"
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 not found. Please install Python 3.8+"
        exit 1
    fi
    
    echo "✅ Python $(python3 --version) found\n"
    
    # Create virtual environment
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    # Install dependencies
    echo "\n📥 Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install flask
    
    # Download models
    echo "\n🤖 Downloading AI models..."
    python3 scripts/download_models.py
    
    # Run application
    echo "\n🚀 Starting application...\n"
    python3 app.py
fi
