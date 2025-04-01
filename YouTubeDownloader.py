from pytube import Playlist, YouTube
from pytube.cli import on_progress
import os


YouTube('https://youtu.be/2lAe1cqCOXo').streams.first().download()
yt = YouTube('http://youtube.com/watch?v=2lAe1cqCOXo')
yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download()
