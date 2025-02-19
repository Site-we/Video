from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

# Directory to save downloaded videos
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template("index.html")  # Load frontend HTML page

@app.route('/get_dailymotion_link', methods=['POST'])
def get_dailymotion_link():
    data = request.json
    video_url = data.get("url")

    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # Generate a unique filename
        ydl_opts = {
            'quiet': True,
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),  # Save in the downloads folder
            'format': 'bestvideo+bestaudio/best',  # Download best quality video
            'merge_output_format': 'mp4',  # Merge video and audio into mp4
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)  # Download the video
            filename = ydl.prepare_filename(info).replace('.webm', '.mp4').replace('.mkv', '.mp4')  # Ensure MP4 format
            filename = os.path.basename(filename)  # Get only the file name

        download_url = f"/download/{filename}"  # Provide the download link

        return jsonify({"download_url": download_url}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
