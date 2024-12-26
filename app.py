import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pydub import AudioSegment

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = "uploads"
TRIMMED_FOLDER = "trimmed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRIMMED_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB limit

@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Trim Audio API!"})

@app.route("/upload", methods=["POST"])
def upload_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    audio_file = request.files["file"]
    if audio_file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_file.filename)
        audio_file.save(file_path)
        return jsonify({"file_path": file_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/trim", methods=["POST"])
def trim_audio():
    data = request.json
    file_path = data.get("file_path")
    start_time = data.get("start_time")
    end_time = data.get("end_time")

    if not file_path or start_time is None or end_time is None:
        return jsonify({"error": "Missing parameters"}), 400

    try:
        audio = AudioSegment.from_file(file_path)
        trimmed_audio = audio[start_time * 1000:end_time * 1000]
        trimmed_file_name = f"trimmed_{os.path.basename(file_path)}"
        trimmed_file_path = os.path.join(TRIMMED_FOLDER, trimmed_file_name)
        trimmed_audio.export(trimmed_file_path, format="mp3")
        return jsonify({"trimmed_file_path": trimmed_file_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/trimmed/<filename>", methods=["GET"])
def download_file(filename):
    return send_from_directory(TRIMMED_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
