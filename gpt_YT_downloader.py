import yt_dlp
import socket

# Устанавливаем увеличенный таймаут
socket.setdefaulttimeout(60)  # 60 секунд

# Замените ссылку на нужную
url = "https://www.youtube.com/watch?v=q8Oq8725Fr4"

# Настройки загрузки
ydl_opts = {
    'format': 'bestvideo+bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'noplaylist': True,
    'merge_output_format': 'mp4',
    'retries': 10,  # Количество повторов при ошибках
    'fragment_retries': 10,  # Повторы для фрагментов HLS
    'socket_timeout': 30,  # Время ожидания сокета
    'continuedl': True  # Продолжать загрузку после обрыва
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print("Скачивание завершено.")
except Exception as e:
    print(f"Произошла ошибка: {e}")