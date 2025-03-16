from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import yt_dlp
import threading
import os

app = Flask(__name__)
CORS(app)

# Directory to store downloaded videos
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Dictionary to track download progress
download_progress = {}

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/get_dailymotion_link', methods=['POST'])
def get_dailymotion_link():
    data = request.json
    video_url = data.get("url")

    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': False,
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

            if 'formats' in info:
                formats = []
                for fmt in info["formats"]:
                    if 'url' in fmt:
                        quality_label = fmt.get("format_note", f"{fmt.get('height', 'Unknown')}p")
                        file_extension = fmt.get("ext", "mp4")
                        formats.append({
                            "quality": f"{quality_label} - {file_extension}",
                            "url": fmt["url"],
                            "format_id": fmt["format_id"]
                        })

                return jsonify({
                    "title": info.get("title", "Unknown Title"),
                    "thumbnail": info.get("thumbnail", ""),
                    "formats": formats
                }), 200

        return jsonify({"error": "Could not extract video details"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def download_video(video_url, format_id, video_title, download_id):
    global download_progress

    output_filename = f"{video_title}.mp4"
    output_path = os.path.join(DOWNLOAD_FOLDER, output_filename)

    ydl_opts = {
        'format': format_id,  # Select the format based on user selection
        'outtmpl': output_path,  # Save the file in the downloads directory
        'quiet': True,
        'progress_hooks': [lambda d: update_progress(d, download_id)],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([video_url])
            download_progress[download_id] = {"status": "completed", "link": f"/download/{output_filename}"}
        except Exception as e:
            download_progress[download_id] = {"status": "failed", "error": str(e)}

def update_progress(d, download_id):
    if d['status'] == 'downloading':
        download_progress[download_id] = {
            "status": "downloading",
            "progress": d.get("_percent_str", "0%"),
            "speed": d.get("_speed_str", "0 KB/s"),
            "eta": d.get("_eta_str", "--"),
        }

@app.route('/start_download', methods=['POST'])
def start_download():
    data = request.json
    video_url = data.get("url")
    format_id = data.get("format_id")
    video_title = data.get("title").replace(" ", "_").replace("/", "_")
    download_id = video_title  # Unique identifier for progress tracking

    if not video_url or not format_id:
        return jsonify({"error": "Invalid parameters"}), 400

    # Start the download in a separate thread
    threading.Thread(target=download_video, args=(video_url, format_id, video_title, download_id)).start()

    return jsonify({"message": "Download started", "download_id": download_id}), 200

@app.route('/download_progress/<download_id>')
def get_download_progress(download_id):
    return jsonify(download_progress.get(download_id, {"status": "unknown"}))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
