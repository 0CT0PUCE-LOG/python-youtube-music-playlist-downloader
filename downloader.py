import os
import pytube
from moviepy.editor import *

# specify the playlist link
playlist_link = "PUT_YOUR_PLAYLIST_LINK_HERE"

# create a PyTube playlist object
playlist = pytube.Playlist(playlist_link)

# create a folder to store the downloaded songs
folder_name = playlist.title.replace(" ", "_").lower()
os.makedirs(folder_name, exist_ok=True)

# iterate over each video in the playlist and download the audio in mp3 format
for video in playlist.videos:
    # get the audio stream of the video
    audio_stream = video.streams.filter(only_audio=True, file_extension='mp4').first()

    # download the audio stream
    audio_stream.download(output_path=folder_name)

    # convert the mp4 file to mp3
    mp4_file = os.path.join(folder_name, audio_stream.default_filename)
    mp3_file = os.path.join(folder_name, video.title.replace(" ", "_").lower() + ".mp3")
    audio_clip = AudioFileClip(mp4_file)
    audio_clip.write_audiofile(mp3_file)

    # delete the mp4 file
    os.remove(mp4_file)
