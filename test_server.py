#!/usr/bin/env python3
"""Quick test to verify Flask server is accessible."""

from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>Video RAG Engine is Running!</h1>
    <p>If you see this, the server is working.</p>
    <p>Try: <a href="/api/status">/api/status</a></p>
    """

@app.route('/api/status')
def status():
    return jsonify({
        "status": "running",
        "lightning": os.environ.get('LIGHTNING_APP_STATE_URL') is not None,
        "port": 5000
    })

if __name__ == '__main__':
    print("Starting test server on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
