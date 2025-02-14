from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

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
        ydl_opts = {
            'quiet': True,
            'extract_flat': False,  # Ensures we get full metadata
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)  # Extract info without downloading
            if 'url' in info:
                return jsonify({"download_url": info['url']}), 200  # Direct video URL
            elif 'formats' in info:
                return jsonify({"download_url": info['formats'][-1]['url']}), 200  # Highest quality format link

        return jsonify({"error": "Could not extract video URL"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
