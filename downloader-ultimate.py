import os
import requests
from io import BytesIO
from PIL import Image
import youtube_dl
from moviepy.editor import *
from mutagen.id3 import ID3, APIC, error
from mutagen.easyid3 import EasyID3

# Function to link the cover image to the audio file
def link_cover_to_audio(image_file, audio_file):
    try:
        # Open the audio file and get the ID3 tags
        audio = ID3(audio_file)

        # Open the image file and get the image data
        with open(image_file, 'rb') as f:
            image_data = f.read()

        # Add the image data to the ID3 tags as an APIC frame
        audio.add(APIC(
            encoding=3,
            mime='image/jpeg',
            type=3,
            desc=u'Cover',
            data=image_data
        ))

        # Save the ID3 tags
        audio.save()
    except error:
        print(f"Could not add cover image to {audio_file}. MutagenError: {error}")

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
            try:
                thumbnail_url = video_dict.get('thumbnail', playlist_dict.get('thumbnail'))
                if thumbnail_url:
                    response = requests.get(thumbnail_url)
                    if response.status_code == 200:
                        # resize and save the thumbnail as a JPEG file
                        image = Image.open(BytesIO(response.content))
                        image.thumbnail((500, 500))
                        image.save("thumbnail.jpg", "JPEG")

                        # add the JPEG file as a cover image to the MP3 file
                        link_cover_to_audio("thumbnail.jpg", mp3_file)

                        # delete the thumbnail file
                        os.remove("thumbnail.jpg")
                    else:
                        print(
                            f"Could not add cover image to {mp3_file}. HTTPError: {response.status_code} {response.reason}")
            except error:
                print(f"Could not add cover image to {mp3_file}. MutagenError: {error}")

            # save the metadata
            audio.save()
        except error:
            # if there is an error, skip the video and continue with the next one
            print(f"Could not download audio for {video_dict['title']}.")
            print("error: ", error)


def link_cover_to_audio(image_file, audio_file):
    try:
        # Open the audio file and get the ID3 tags
        audio = ID3(audio_file)

        # Open the image file and get the image data
        with open(image_file, 'rb') as f:
            image_data = f.read()

        # Add the image data to the ID3 tags as an APIC frame
        audio.add(APIC(
            encoding=3,
            mime='image/jpeg',
            type=3,
            desc=u'Cover',
            data=image_data
        ))

        # Save the ID3 tags
        audio.save()
        print(f"Cover image linked to {audio_file} successfully!")
    except error:
        print(f"Could not add cover image to {audio_file}. MutagenError: {error}")



