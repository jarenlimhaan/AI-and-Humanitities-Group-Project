url = "https://www.youtube.com/watch?v=1yT710yREZw&pp=ygUMREJTIGRpZ2liYW5r"

from pytubefix import YouTube
from pytubefix.cli import on_progress
 
yt = YouTube(url, on_progress_callback = on_progress)
print(yt.title)
 
ys = yt.streams.get_highest_resolution()
ys.download()