from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/get_link', methods=['POST'])
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
            'cookies_from_browser': ('chrome',)  # Automatically fetch cookies from Chrome
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            video_link = info["url"]

        return jsonify({"download_url": video_link}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
