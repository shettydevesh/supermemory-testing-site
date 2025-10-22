from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from typing import List, Dict
from anthropic import Anthropic
from processor import DocumentProcessor
from pathlib import Path
import uuid
from dotenv import dotenv_values

config = dotenv_values(".env")
app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Initialize clients
anthropic_client = Anthropic(api_key=config["ANTHROPIC_API_KEY"])
doc_processor = DocumentProcessor()

# Store conversation history per session
conversations: Dict[str, List[Dict]] = {}

@app.route('/')
def index():
    """Serve the chatbot interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id')

        if not session_id:
            session_id = str(uuid.uuid4())

        # Initialize conversation history for new sessions
        if session_id not in conversations:
            conversations[session_id] = []

        # Add user message to history
        conversations[session_id].append({
            "role": "user",
            "content": user_message
        })

        # Call Claude API
        response = anthropic_client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=8096,
            messages=conversations[session_id]
        )

        # Extract assistant's response
        assistant_message = response.content[0].text

        # Add assistant response to history
        conversations[session_id].append({
            "role": "assistant",
            "content": assistant_message
        })

        return jsonify({
            'response': assistant_message,
            'session_id': session_id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-docs', methods=['POST'])
def upload_docs():
    """Upload all files from docs folder to Supermemory with 'brittannia' container"""
    try:
        docs_path = Path('/Users/devesh/Research/docs')

        if not docs_path.exists():
            return jsonify({'error': 'docs folder not found'}), 404

        results = []

        # Iterate through all files in docs folder
        for file_path in docs_path.iterdir():
            if file_path.is_file():
                try:
                    # Use filename without extension as additional container tag
                    filename = file_path.stem  # filename without extension
                    container_tags = ["brittannia", filename]

                    # Upload file
                    result = doc_processor.upload_files(
                        str(file_path),
                        container=container_tags
                    )

                    results.append({
                        'file': file_path.name,
                        'status': 'success',
                        'result': result
                    })

                except Exception as e:
                    results.append({
                        'file': file_path.name,
                        'status': 'error',
                        'error': str(e)
                    })

        return jsonify({
            'message': f'Processed {len(results)} files',
            'results': results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-single', methods=['POST'])
def upload_single():
    """Upload a single file with brittannia container"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Save file temporarily
        temp_path = Path('/tmp') / file.filename
        file.save(str(temp_path))

        # Get filename without extension for container tag
        filename = Path(file.filename).stem
        container_tags = ["brittannia", filename]

        # Upload to Supermemory
        result = doc_processor.upload_files(
            str(temp_path),
            container=container_tags
        )

        # Clean up temp file
        temp_path.unlink()

        return jsonify({
            'message': 'File uploaded successfully',
            'result': result
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear-session', methods=['POST'])
def clear_session():
    """Clear conversation history for a session"""
    try:
        data = request.json
        session_id = data.get('session_id')

        if session_id and session_id in conversations:
            del conversations[session_id]

        return jsonify({'message': 'Session cleared'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
