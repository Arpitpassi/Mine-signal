from flask import Flask, request, jsonify, render_template, Response
import os
import shutil
from video_processor import handle_video_processing, get_video_dimensions

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = "uploads"
ASCII_FOLDER = "static/frames"
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB limit
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'webm'}

# Create necessary folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ASCII_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clear_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify(error="No file part"), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify(error="No selected file"), 400
    
    if file and allowed_file(file.filename):
        # Clear previous frames
        clear_folder(ASCII_FOLDER)
        clear_folder(UPLOAD_FOLDER)
        
        # Save and process new video
        filename = file.filename
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        try:
            # Get video dimensions
            width, height = get_video_dimensions(file_path)
            
            # Process video
            handle_video_processing(file_path, ASCII_FOLDER)
            
            return jsonify({
                'success': True,
                'dimensions': {
                    'width': width,
                    'height': height
                }
            }), 200
            
        except Exception as e:
            return jsonify(error=str(e)), 500
        
    return jsonify(error="File type not allowed"), 400

@app.route('/stream')
def stream_ascii():
    try:
        def generate():
            frame_files = sorted(
                [f for f in os.listdir(ASCII_FOLDER) if f.endswith('.txt')],
                key=lambda x: int(x.split('_')[1].split('.')[0])
            )
            
            for filename in frame_files:
                with open(os.path.join(ASCII_FOLDER, filename), 'r') as f:
                    yield f.read() + '<!--frame-separator-->'
        
        return Response(generate(), mimetype='text/plain')
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to stream ASCII frames'
        }), 500

@app.after_request
def cleanup(response):
    if request.endpoint != 'stream_ascii':
        clear_folder(UPLOAD_FOLDER)
    return response

if __name__ == '__main__':
    app.run(
        host='192.168.233.170',  # IP address only
        port=5000,
        debug=True
    )