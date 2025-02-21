function getQueryParameter(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}

async function fetchVideoDetails(url) {
    document.getElementById("status").textContent = "Fetching video details...";

    try {
        const response = await fetch("/get_dailymotion_link", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url })
        });

        const data = await response.json();

        if (data.error) {
            document.getElementById("status").textContent = "Error: " + data.error;
            return;
        }

        document.getElementById("title").textContent = data.title;
        document.getElementById("thumbnail").src = data.thumbnail;

        const qualitySelect = document.getElementById("quality");
        qualitySelect.innerHTML = "";

        let defaultSelected = false;
        data.formats.forEach((format) => {
            const option = document.createElement("option");
            option.value = format.url;
            option.textContent = format.quality;

            if (format.quality.includes("480p") && !defaultSelected) {
                option.selected = true;
                defaultSelected = true;
            }

            qualitySelect.appendChild(option);
        });

        document.getElementById("status").textContent = "Ready to download!";
    } catch (error) {
        document.getElementById("status").textContent = "An error occurred.";
        console.error(error);
    }
}

function startDownload() {
    document.getElementById("downloadBtn").style.display = "none";
    document.getElementById("quality").style.display = "none";
    document.getElementById("progressBar").style.display = "block";

    const downloadUrl = document.getElementById("quality").value;
    const videoTitle = document.getElementById("title").textContent.replace(/[<>:"/\\|?*]+/g, "");

    if (downloadUrl.endsWith(".m3u8")) {
        downloadM3U8(downloadUrl, videoTitle);
    } else {
        downloadMP4(downloadUrl, videoTitle);
    }
}

function downloadMP4(url, title) {
    const a = document.createElement("a");
    a.href = url;
    a.download = title + ".mp4";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    document.getElementById("status").textContent = "Saving...";
    setTimeout(() => {
        document.getElementById("status").textContent = "Video saved!";
        document.getElementById("progressBar").style.display = "none";
    }, 3000);
}

async function downloadM3U8(m3u8Url, title) {
    document.getElementById("status").textContent = "Preparing download...";
    document.getElementById("progress").style.width = "0%";
    document.getElementById("progress").textContent = "0%";
    document.getElementById("speed").textContent = "Download Speed: 0 MB/s";

    try {
        const startTime = Date.now();
        const response = await fetch(m3u8Url);
        const playlistText = await response.text();

        const baseUrl = m3u8Url.substring(0, m3u8Url.lastIndexOf("/") + 1);
        const tsFiles = playlistText.match(/(.*\.ts)/g) || [];

        if (tsFiles.length === 0) {
            document.getElementById("status").textContent = "Error: No video found.";
            return;
        }

        let blobParts = [];
        let downloadedSize = 0;

        for (let i = 0; i < tsFiles.length; i += 30) {
            let chunk = tsFiles.slice(i, i + 30);
            await Promise.all(chunk.map(async (tsUrl, index) => {
                if (!tsUrl.startsWith("http")) {
                    tsUrl = baseUrl + tsUrl;
                }
                const tsResponse = await fetch(tsUrl);
                const tsBlob = await tsResponse.blob();
                blobParts[i + index] = tsBlob;

                downloadedSize += tsBlob.size;
                const elapsedTime = (Date.now() - startTime) / 1000; // seconds
                const speed = (downloadedSize / 1024 / 1024 / elapsedTime).toFixed(2); // MB/s

                const progressPercent = ((i + index + 1) / tsFiles.length) * 100;
                document.getElementById("progress").style.width = progressPercent + "%";
                document.getElementById("progress").textContent = Math.round(progressPercent) + "%";
                document.getElementById("speed").textContent = `Download Speed: ${speed} MB/s`;
            }));
        }

        const mergedBlob = new Blob(blobParts, { type: "video/mp4" });
        const downloadUrl = URL.createObjectURL(mergedBlob);

        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = title + ".mp4";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        document.getElementById("status").textContent = "Saving...";
        setTimeout(() => {
            document.getElementById("status").textContent = "Video saved!";
            document.getElementById("progressBar").style.display = "none";
        }, 3000);
    } catch (error) {
        document.getElementById("status").textContent = "Error downloading video.";
        console.error(error);
    }
}

window.onload = () => {
    const videoUrl = getQueryParameter("url");
    if (videoUrl) {
        fetchVideoDetails(videoUrl);
    } else {
        document.getElementById("status").textContent = "No video URL provided.";
    }
};
