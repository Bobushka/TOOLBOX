from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.concurrency import run_in_threadpool
import yt_dlp
import os
from pathlib import Path
import socket


"""
✅ Что делает приложение:
- Отображает веб-страницу на http://localhost:8000
- Принимает ссылку на YouTube
- Скачивает видео в максимальном качестве (видео + аудио)
- Сохраняет результат в папку ~/Downloads

⚙️ Установка зависимостей:
pip install fastapi uvicorn yt-dlp python-multipart

▶️ Как запустить:
- python yt_fastapi_v2.py
- Затем открой в браузере http://localhost:8000

📂 Куда сохраняются файлы:
Скачанные видео сохраняются в стандартную папку Downloads текущего пользователя (~/Downloads).
"""


# Увеличить глобальный таймаут сокета
socket.setdefaulttimeout(60)

# Папка загрузки по умолчанию
DOWNLOADS_PATH = str(Path.home() / "Downloads")

app = FastAPI()

HTML_FORM = """
<html>
<head><title>YouTube Downloader</title></head>
<body>
    <h2>Вставьте ссылку на YouTube</h2>
    <form action="/download" method="post">
        <input type="text" name="url" size="60" required>
        <button type="submit">Скачать</button>
    </form>
    <p>{{ result }}</p>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def form_page():
    return HTML_FORM.replace("{{ result }}", "")

@app.post("/download", response_class=HTMLResponse)
async def download_video(url: str = Form(...)):
    def _download():
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(DOWNLOADS_PATH, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'merge_output_format': 'mp4',
            'retries': 30,  # увеличить количество попыток
            'fragment_retries': 30,
            'socket_timeout': 30,
            'continuedl': True,
            'concurrent_fragment_downloads': 1,  # важный параметр для стабильности
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return "✅ Скачивание завершено. Файл сохранён в папке Downloads."
        except Exception as e:
            return f"❌ Произошла ошибка: {e}"

    result = await run_in_threadpool(_download)
    return HTML_FORM.replace("{{ result }}", result)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("yt_fastapi_v2:app", host="127.0.0.1", port=8000, reload=True)