#!/bin/bash
# Use ngrok to access localhost from anywhere (no deployment needed!)

echo ""
echo "🎬 Video RAG Engine - Instant Cloud Access via ngrok"
echo "======================================================"
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "📥 Installing ngrok..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install ngrok
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if ! command -v wget &> /dev/null; then
            sudo apt-get install wget
        fi
        wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip
        unzip ngrok-v3-stable-linux-amd64.zip
        sudo mv ngrok /usr/local/bin/
        rm ngrok-v3-stable-linux-amd64.zip
    else
        echo "❌ Unsupported OS"
        echo "Download ngrok from: https://ngrok.com/download"
        exit 1
    fi
fi

echo "✅ ngrok ready\n"

# Check if app is running
echo "Checking if app is running on port 5000..."
sleep 1

if ! nc -z localhost 5000 2>/dev/null; then
    echo "\n⚠️  App not running on localhost:5000"
    echo "\nStarting app in background..."
    python3 app.py > app.log 2>&1 &
    APP_PID=$!
    echo "App PID: $APP_PID"
    sleep 3
fi

echo "\n✅ App is running\n"

# Start ngrok
echo "🚀 Starting ngrok tunnel..."
echo ""
echo "════════════════════════════════════════════"
echo ""

ngrok http 5000 --log stdout

echo ""
echo "════════════════════════════════════════════"
