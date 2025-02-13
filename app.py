from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__, template_folder="templates")  # Serve HTML from 'templates/' folder
CORS(app)

# Ensure cookies.txt exists for authentication
COOKIES_FILE = "cookies.txt"
if os.path.exists(COOKIES_FILE):
    print("✅ Using cookies.txt for authentication")
else:
    print("⚠️ Warning: No cookies.txt found. Some videos may fail.")

# Serve the main HTML page
@app.route("/")
def home():
    return render_template("index.html")

# API to fetch the YouTube video download link
@app.route("/get_link", methods=["POST"])
def get_video_link():
    data = request.json
    video_url = data.get("url")

    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'quiet': True,
            'noplaylist': True,
            'cookiefile': COOKIES_FILE if os.path.exists(COOKIES_FILE) else None,  # Use cookies if available
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            video_link = info.get("url")

        return jsonify({"download_url": video_link}), 200

    except yt_dlp.utils.DownloadError as e:
        return jsonify({"error": f"Download error: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
