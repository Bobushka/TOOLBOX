## Инструкция по использованию FastAPI веб-приложения для скачивания видео с YouTube

Скрипт: yt_download.py

✅ Что делает приложение:
- Отображает веб-страницу на http://localhost:8000
- Принимает ссылку на YouTube
- Скачивает видео в максимальном качестве (видео + аудио)
- Сохраняет результат в папку ~/Downloads

⚙️ Установка зависимостей:
pip install fastapi uvicorn yt-dlp python-multipart

▶️ Как запустить:
- python yt_download.py
- Затем открой в браузере http://localhost:8000 (или сходи в Хроме по букмарку mail/YouTube Downloader)

📂 Куда сохраняются файлы:
Скачанные видео сохраняются в стандартную папку Downloads текущего пользователя (~/Downloads).