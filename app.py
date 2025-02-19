from flask import Flask, request, jsonify, render_template, send_from_directory from flask_cors import CORS import yt_dlp import os

app = Flask(name) CORS(app)

Create a directory to store downloaded videos

download_folder = "downloads" os.makedirs(download_folder, exist_ok=True)

@app.route('/') def index(): return render_template("index.html")  # Load frontend HTML page

@app.route('/get_dailymotion_link', methods=['POST']) def get_dailymotion_link(): data = request.json video_url = data.get("url")

if not video_url:
    return jsonify({"error": "No URL provided"}), 400

try:
    ydl_opts = {
        'quiet': True,
        'extract_flat': False,
        'noplaylist': True,
        'outtmpl': f'{download_folder}/%(title)s.%(ext)s',  # Save file with video title
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)  # Download the video
        filename = ydl.prepare_filename(info)  # Get the actual filename
        filename = os.path.basename(filename)  # Extract only filename from path

    return jsonify({"download_url": f"/downloads/{filename}"}), 200

except Exception as e:
    return jsonify({"error": str(e)}), 500

@app.route('/downloads/<filename>') def download_file(filename): return send_from_directory(download_folder, filename, as_attachment=True)

if name == 'main': app.run(host='0.0.0.0', port=5000, debug=True)
