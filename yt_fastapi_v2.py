from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import yt_dlp
import socket
import uvicorn
import os
from pathlib import Path

# Устанавливаем увеличенный таймаут
socket.setdefaulttimeout(60)

# Определяем путь к папке Downloads для текущего пользователя
DOWNLOADS_PATH = str(Path.home() / "Downloads")

app = FastAPI()

HTML_FORM = """
<!doctype html>
<html>
  <head>
    <title>YouTube Downloader</title>
  </head>
  <body>
    <h2>Скачать видео с YouTube</h2>
    <form action="/download" method="post">
      <input type="text" name="url" placeholder="Вставьте ссылку на YouTube" size="60">
      <input type="submit" value="Скачать">
    </form>
    <h3>Результат:</h3>
    <pre>{{ result }}</pre>
  </body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def form_page():
    return HTML_FORM.replace("{{ result }}", "")

@app.post("/download", response_class=HTMLResponse)
async def download_video(url: str = Form(...)):
    result = ""
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(DOWNLOADS_PATH, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'merge_output_format': 'mp4',
        'retries': 10,
        'fragment_retries': 10,
        'socket_timeout': 30,
        'continuedl': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        result = "✅ Скачивание завершено. Файл сохранён в папке Downloads."
    except Exception as e:
        result = f"❌ Произошла ошибка: {e}"
    return HTML_FORM.replace("{{ result }}", result)

if __name__ == "__main__":
    uvicorn.run("yt_fastapi_v2:app", host="127.0.0.1", port=8000, reload=True)