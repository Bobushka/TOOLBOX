from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.concurrency import run_in_threadpool
import yt_dlp
import os
from pathlib import Path
from contextlib import asynccontextmanager
from threading import Event
import signal
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
- python yt_download.py
- Затем открой в браузере http://localhost:8000

📂 Куда сохраняются файлы:
Скачанные видео сохраняются в стандартную папку Downloads текущего пользователя (~/Downloads).
"""


# Увеличить глобальный таймаут сокета
socket.setdefaulttimeout(60)

# Папка загрузки по умолчанию
DOWNLOADS_PATH = str(Path.home() / "Downloads")

# Событие для безопасной отмены скачивания между потоками
shutdown_event_trigger = Event()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управляет жизненным циклом приложения. Код до `yield` выполняется при запуске,
    код после `yield` — при завершении.
    """
    # Код, выполняемый при запуске (startup)
    print("Приложение запускается. Устанавливаю обработчик Ctrl+C.")
    original_sigint_handler = signal.getsignal(signal.SIGINT)

    def custom_sigint_handler(signum, frame):
        print("\nОбнаружено нажатие Ctrl+C. Отправляю сигнал на отмену скачивания...")
        shutdown_event_trigger.set()
        if callable(original_sigint_handler):
            original_sigint_handler(signum, frame)

    signal.signal(signal.SIGINT, custom_sigint_handler)
    
    yield  # Здесь приложение работает

    # Код, выполняемый при завершении (shutdown)
    print("Приложение завершает работу.")

app = FastAPI(lifespan=lifespan)
HTML_TEMPLATE = """
<html>
<head>
    <title>YouTube Downloader</title>
    <style>
        body {
            background-color: #121212;
            color: #e0e0e0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }
        h2 {
            color: #ffffff;
        }
        form {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        input[type="text"] {
            background-color: #2c2c2c;
            color: #e0e0e0;
            border: 1px solid #444;
            padding: 10px;
            border-radius: 4px;
            font-size: 16px;
        }
        button {
            background-color: #bb86fc;
            color: #121212;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }
        button:hover {
            background-color: #a76ef4;
        }
        p {
            font-size: 16px;
        }
        a.button-link {
            display: block;
            margin-bottom: 20px;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <h2>Вставьте ссылку на YouTube</h2>
    {{ form_section }}
    <p>{{ result }}</p>
    <script>
        const form = document.getElementById('download-form');
        if (form) {
            const button = document.getElementById('download-button');
            const urlInput = form.querySelector('input[name="url"]');

            form.addEventListener('submit', (event) => {
                // Проверяем, что поле ввода не пустое (хотя 'required' уже это делает)
                if (urlInput && urlInput.value.trim() !== '') {
                    button.disabled = true;
                    button.style.backgroundColor = '#555'; // Делаем кнопку серой
                    button.innerText = 'Скачивание...';
                }
            });
        }
    </script>
</body>
</html>
"""

FORM_SECTION_HTML = """
<form id="download-form" action="/download" method="post">
    <input type="text" name="url" size="60" required>
    <button id="download-button" type="submit">Скачать</button>
</form>
"""

RESULT_SECTION_HTML = '<a href="/" class="button-link"><button>Скачать еще</button></a>'

@app.get("/", response_class=HTMLResponse)
async def form_page():
    page = HTML_TEMPLATE.replace("{{ form_section }}", FORM_SECTION_HTML)
    return page.replace("{{ result }}", "")

def _download_task(url: str, cancel_event: Event):
    """Функция скачивания, выполняемая в отдельном потоке."""
    def progress_hook(_):
        if cancel_event.is_set():
            raise yt_dlp.utils.DownloadCancelled('Download cancelled by server shutdown.')

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(DOWNLOADS_PATH, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'merge_output_format': 'mp4',
        'retries': 30,
        'fragment_retries': 50,
        'socket_timeout': 10,
        'continuedl': True,
        'concurrent_fragment_downloads': 1,
        'progress_hooks': [progress_hook],  # Добавляем хук для отслеживания прогресса
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return "✅ Скачивание завершено. Файл сохранён в папке Downloads."
    except yt_dlp.utils.DownloadCancelled:
        return "ℹ️ Скачивание было прервано пользователем."
    except Exception as e:
        return f"❌ Произошла ошибка: {e}"

@app.post("/download", response_class=HTMLResponse)
async def download_video(url: str = Form(...)):
    shutdown_event_trigger.clear()  # Сбрасываем флаг перед началом новой загрузки
    result = await run_in_threadpool(_download_task, url, shutdown_event_trigger)
    page = HTML_TEMPLATE.replace("{{ form_section }}", RESULT_SECTION_HTML)
    return page.replace("{{ result }}", result)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("yt_download:app", host="127.0.0.1", port=8000, reload=True)