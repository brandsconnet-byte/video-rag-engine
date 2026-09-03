#!/usr/bin/env python3
"""Web UI for Video RAG Engine using Flask."""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from loguru import logger
import threading
import json
from datetime import datetime

from src.pipeline import VideoPipeline

# Configuration
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'mkv', 'avi', 'webm'}
UPLOAD_FOLDER = './uploaded_videos'
OUTPUT_FOLDER = './extracted_clips'
MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024  # 5GB

# Create directories
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
Path(OUTPUT_FOLDER).mkdir(exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Global state
processing_state = {
    'status': 'idle',  # idle, processing, complete, error
    'progress': 0,
    'message': '',
    'video_name': '',
    'table_name': '',
    'num_scenes': 0,
    'elapsed_time': 0,
    'error': None
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_video():
    """Upload and process video."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    config = request.form.get('config', 'config/balanced.yaml')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: mp4, mov, mkv, avi, webm'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Save file
    file.save(filepath)
    logger.info(f"Video uploaded: {filename}")
    
    # Process in background
    thread = threading.Thread(
        target=process_video_background,
        args=(filepath, config, filename)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'status': 'processing',
        'filename': filename,
        'message': 'Video processing started...'
    })

def process_video_background(filepath, config, filename):
    """Process video in background thread."""
    global processing_state
    
    try:
        processing_state['status'] = 'processing'
        processing_state['video_name'] = filename
        processing_state['progress'] = 10
        processing_state['message'] = 'Initializing pipeline...'
        
        pipeline = VideoPipeline(config)
        
        processing_state['progress'] = 20
        processing_state['message'] = 'Processing video...'
        
        result = pipeline.process(filepath)
        
        processing_state['progress'] = 90
        processing_state['message'] = 'Finalizing...'
        processing_state['num_scenes'] = result['num_scenes']
        processing_state['table_name'] = result['table_name']
        processing_state['elapsed_time'] = result['elapsed_time']
        
        processing_state['status'] = 'complete'
        processing_state['progress'] = 100
        processing_state['message'] = f'✅ Complete! {result["num_scenes"]} scenes detected'
        
        logger.info(f"Video processing complete: {filename}")
        
    except Exception as e:
        processing_state['status'] = 'error'
        processing_state['error'] = str(e)
        processing_state['message'] = f'Error: {str(e)}'
        logger.error(f"Video processing failed: {e}")

@app.route('/api/status')
def get_status():
    """Get processing status."""
    return jsonify(processing_state)

@app.route('/api/search', methods=['POST'])
def search_scenes():
    """Search for scenes."""
    if processing_state['status'] != 'complete':
        return jsonify({'error': 'No video processed yet'}), 400
    
    query = request.json.get('query', '')
    table_name = processing_state['table_name']
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        pipeline = VideoPipeline('config/default.yaml')
        results = pipeline.search([query], table_name, batch_process=False)
        
        if results and results[0]:
            # Format results for frontend
            formatted_results = []
            for result in results[0][:20]:  # Limit to 20 results
                formatted_results.append({
                    'scene_id': result.get('scene_id'),
                    'start_time': f"{result.get('start_time', 0):.2f}s",
                    'end_time': f"{result.get('end_time', 0):.2f}s",
                    'duration': f"{result.get('duration', 0):.2f}s",
                    'tags': result.get('yolo_tags', []),
                })
            
            return jsonify({
                'query': query,
                'num_matches': len(formatted_results),
                'results': formatted_results
            })
        else:
            return jsonify({
                'query': query,
                'num_matches': 0,
                'results': [],
                'message': 'No matching scenes found'
            })
    
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/extract', methods=['POST'])
def extract_clips():
    """Extract matching clips."""
    if processing_state['status'] != 'complete':
        return jsonify({'error': 'No video processed yet'}), 400
    
    query = request.json.get('query', '')
    table_name = processing_state['table_name']
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], processing_state['video_name'])
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        pipeline = VideoPipeline('config/default.yaml')
        results = pipeline.search([query], table_name, batch_process=False)
        
        if results and results[0]:
            extracted = pipeline.extract_clips(results[0][:5], video_path, OUTPUT_FOLDER)  # Limit to 5 clips
            
            formatted_clips = []
            for clip in extracted:
                formatted_clips.append({
                    'scene_id': clip['scene_id'],
                    'route': clip['route'],
                    'duration': f"{clip['original_duration']:.2f}s",
                    'clip_path': clip['clip_path']
                })
            
            return jsonify({
                'query': query,
                'num_extracted': len(formatted_clips),
                'clips': formatted_clips
            })
        else:
            return jsonify({'error': 'No matching scenes found'}), 404
    
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset application state."""
    global processing_state
    processing_state = {
        'status': 'idle',
        'progress': 0,
        'message': '',
        'video_name': '',
        'table_name': '',
        'num_scenes': 0,
        'elapsed_time': 0,
        'error': None
    }
    
    # Clean up uploaded files
    for file in Path(UPLOAD_FOLDER).glob('*'):
        if file.is_file():
            file.unlink()
    
    return jsonify({'status': 'reset'})

if __name__ == '__main__':
    print("\n🌐 Video RAG Engine - Web UI")
    print("=" * 50)
    print("\n📱 Open your browser and go to:")
    print("   👉 http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
