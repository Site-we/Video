from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import yt_dlp

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)  # Allow frontend to make requests

# Serve the index.html page
@app.route("/")
def home():
    return render_template("index.html")

# API endpoint to fetch YouTube download link
@app.route("/get_link", methods=["POST"])
def get_download_link():
    data = request.get_json()
    video_url = data.get("url")

    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': 'downloaded_video.mp4'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            download_url = info.get("url")

        return jsonify({"download_url": download_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
