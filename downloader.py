import os
import urllib.request
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
        try:
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
                try:
                    with urllib.request.urlopen(thumbnail_url) as response:
                        image_data = response.read()
                        cover_image = image_data

                        # add the cover image to the metadata
                        audio['images'] = [APIC(
                            encoding=3,
                            mime='image/jpeg',
                            type=3,
                            desc=u'Cover',
                            data=cover_image
                        )]
                except error:
                    print(f"Could not add cover image to {mp3_file}.")
                    print("error: ", error)

            # save the metadata
            audio.save()
        except:
            # if there is an error, skip the video and continue with the next one
            print(f"Could not download {video_dict['title']}. Skipping...")
            continue
