import os
import subprocess
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
TRIMMED_FOLDER = "trimmed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRIMMED_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_audio():
    """Endpoint to handle audio uploads."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the uploaded file
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    return jsonify({"message": "File uploaded successfully", "file_path": file_path}), 200

@app.route('/trim', methods=['POST'])
def trim_audio():
    """Endpoint to trim a specific segment of an audio file."""
    data = request.get_json()
    file_path = data.get("file_path")
    start_time = data.get("start_time")  # in seconds
    end_time = data.get("end_time")      # in seconds

    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "Invalid or missing file path"}), 400

    if start_time is None or end_time is None:
        return jsonify({"error": "Start and end times must be provided"}), 400

    try:
        # Trim the audio using FFmpeg
        trimmed_file_path = os.path.join(TRIMMED_FOLDER, f"trimmed_{os.path.basename(file_path)}")
        subprocess.run([
            "ffmpeg", "-i", file_path,
            "-ss", str(start_time), "-to", str(end_time),
            "-c", "copy", trimmed_file_path
        ], check=True)

        return jsonify({"message": "Audio trimmed successfully", "trimmed_file_path": f"trimmed/{os.path.basename(trimmed_file_path)}"}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"FFmpeg error: {e}"}), 500

@app.route('/trimmed/<filename>', methods=['GET'])
def download_trimmed(filename):
    """Serve the trimmed file for download."""
    return send_from_directory(TRIMMED_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

