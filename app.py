from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template("index.html")  # Load the frontend HTML page

@app.route('/get_dailymotion_link', methods=['POST'])
def get_dailymotion_link():
    data = request.json
    video_url = data.get("url")

    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'outtmpl': f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s",  # Save in downloads folder
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)  # Download video
            file_path = ydl.prepare_filename(info)  # Get downloaded file path

        return jsonify({"file_path": file_path}), 200  # Send file path to frontend

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download_video')
def download_video():
    file_path = request.args.get("file")
    if not file_path or not os.path.exists(file_path):
        return "File not found!", 404
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
