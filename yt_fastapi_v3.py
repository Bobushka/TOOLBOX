from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, StreamingResponse
import subprocess
import os
from pathlib import Path

app = FastAPI()
DOWNLOADS_PATH = str(Path.home() / "Downloads")

HTML_FORM = """
<html>
<head><title>YouTube Downloader</title></head>
<body>
    <h2>Вставьте ссылку на YouTube</h2>
    <form action="/download" method="post">
        <input type="text" name="url" size="60" required>
        <button type="submit">Скачать</button>
    </form>
    <pre id="output"></pre>
    <script>
        const form = document.querySelector("form");
        const output = document.getElementById("output");

        form.onsubmit = async (e) => {
            e.preventDefault();
            output.textContent = "";
            const formData = new FormData(form);
            const res = await fetch("/download", {
                method: "POST",
                body: formData
            });

            const reader = res.body.getReader();
            const decoder = new TextDecoder("utf-8");

            let buffer = "";
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                buffer += decoder.decode(value, { stream: true });

                const lines = buffer.split("\n");
                if (lines.length > 1) {
                    output.textContent = lines[lines.length - 2];
                    buffer = lines[lines.length - 1];
                }
            }

            output.textContent = "✅ Скачивание завершено. Файл сохранён в папке Downloads.";

            setTimeout(() => {
                window.location.href = "/";
            }, 3000);
        };
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def form_page():
    return HTML_FORM

@app.post("/download")
def download_video(url: str = Form(...)):
    def stream():
        command = [
            "yt-dlp",
            "-f", "bestvideo+bestaudio/best",
            "-o", os.path.join(DOWNLOADS_PATH, "%(title)s.%(ext)s"),
            "--merge-output-format", "mp4",
            "--retries", "20",
            "--fragment-retries", "30",
            "--no-playlist",
            url
        ]

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True
        )

        for line in process.stdout:
            yield line

        process.stdout.close()
        process.wait()

    return StreamingResponse(stream(), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("yt_fastapi_v3:app", host="127.0.0.1", port=8000, reload=True)