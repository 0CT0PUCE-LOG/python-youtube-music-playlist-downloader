import os
import requests
from io import BytesIO
from PIL import Image
import youtube_dl
from moviepy.editor import *
from mutagen.id3 import ID3, APIC, error
from mutagen.easyid3 import EasyID3

# specify the playlist link
playlist_link = "https://www.youtube.com/playlist?list=PLAteN_LndFJOikYpp4aABMhEJAY6A1_Oc"

# set the options for youtube_dl
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

# create a youtube_dl object
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    # get the playlist info
    playlist_dict = ydl.extract_info(playlist_link, download=False)

    # create a folder to store the downloaded songs
    folder_name = playlist_dict['title'].replace(" ", "_").lower()
    os.makedirs(folder_name, exist_ok=True)

    # iterate over each video in the playlist and download the audio in mp3 format
    for video_dict in playlist_dict['entries']:
        # download the audio stream
        ydl.download([video_dict['webpage_url']])

        # convert the downloaded file to mp3
        mp4_file = f"{video_dict['title']}.mp3"
        mp3_file = os.path.join(folder_name, video_dict['title'].replace(" ", "_").lower() + ".mp3")
        audio_clip = AudioFileClip(mp4_file)
        audio_clip.write_audiofile(mp3_file)

        # delete the mp4 file
        os.remove(mp4_file)

        # add metadata to the mp3 file
        audio = EasyID3(mp3_file)
        audio['artist'] = video_dict.get('artist', playlist_dict.get('uploader', 'Unknown artist'))
        audio['title'] = video_dict['title']

        # download the cover image
        thumbnail_url = video_dict.get('thumbnail', playlist_dict.get('thumbnail'))
        if thumbnail_url:
            response = requests.get(thumbnail_url)
            if response.status_code == 200:
                # resize and save the thumbnail as a JPEG file
                image = Image.open(BytesIO(response.content))
                image.thumbnail((500, 500))
                image.save("thumbnail.jpg", "JPEG")

                # add the JPEG file as a cover image to the MP3 file
                with open("thumbnail.jpg", "rb") as f:
                    audio['APIC'] = APIC(
                        encoding=3,
                        mime='image/jpeg',
                        type=3,
                        desc=u'Cover',
                        data=f.read()
                    )

                # delete the thumbnail file
                os.remove("thumbnail.jpg")
            else:
                print(
                    f"Could not add cover image to {mp3_file}. HTTPError: {response.status_code} {response.reason}")

        # save the metadata
        audio.save()


