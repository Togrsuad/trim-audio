import os
from flask import Flask, request, jsonify, send_file
from pydub import AudioSegment
import io

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return "Welcome to Trim Audio! The server is running successfully."

@app.route('/trim', methods=['POST'])
def trim_audio():
    try:
        # Check if a file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        # Ensure the file has a valid filename
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Save the uploaded file to the UPLOAD_FOLDER
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Extract start and end times from the request
        try:
            start_time = int(request.form.get('start_time', 0))
            end_time = int(request.form.get('end_time', 0))
        except ValueError:
            return jsonify({'error': 'Invalid time format. Please provide integers for start_time and end_time.'}), 400

        if start_time >= end_time:
            return jsonify({'error': 'start_time must be less than end_time'}), 400

        # Load the audio file and trim it
        audio = AudioSegment.from_file(file_path)
        trimmed_audio = audio[start_time * 1000:end_time * 1000]

        # Save the trimmed audio to the OUTPUT_FOLDER
        output_path = os.path.join(OUTPUT_FOLDER, f'trimmed_{file.filename}')
        trimmed_audio.export(output_path, format="mp3")

        # Send the trimmed audio file back to the client
        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
