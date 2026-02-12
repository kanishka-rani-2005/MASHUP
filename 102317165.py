import sys
import os
from yt_dlp import YoutubeDL
from pydub import AudioSegment

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOADS_FOLDER = os.path.join(BASE_DIR, "downloads")

def validate_inputs(args):
    if len(args) != 5:
        print("Usage: python <program.py> <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>")
        sys.exit(1)

    singer = args[1]

    try:
        num_videos = int(args[2])
        duration = int(args[3])
    except ValueError:
        print("NumberOfVideos and AudioDuration must be integers.")
        sys.exit(1)

    if num_videos <= 10:
        print("NumberOfVideos must be greater than 10.")
        sys.exit(1)

    if duration <= 20:
        print("AudioDuration must be greater than 20 seconds.")
        sys.exit(1)

    return singer, num_videos, duration, args[4]


def clear_downloads_folder():
    os.makedirs(DOWNLOADS_FOLDER, exist_ok=True)

    for file in os.listdir(DOWNLOADS_FOLDER):
        file_path = os.path.join(DOWNLOADS_FOLDER, file)
        if os.path.isfile(file_path):
            os.remove(file_path)


def download_videos(singer, num_videos):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOADS_FOLDER, '%(title)s.%(ext)s'),
        'quiet': False,
        'noplaylist': True,
        'js_runtimes': {
            'node': {}
        }
    }

    search_query = f"ytsearch{num_videos}:{singer} songs"

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([search_query])


def trim_and_merge(duration, output_file):
    merged = AudioSegment.empty()
    os.makedirs(DOWNLOADS_FOLDER, exist_ok=True)


    for file in os.listdir(DOWNLOADS_FOLDER):
        if file.endswith((".webm", ".m4a", ".mp3", ".mp4")):
            file_path = os.path.join(DOWNLOADS_FOLDER, file)

            try:
                audio = AudioSegment.from_file(file_path)
                trimmed = audio[:duration * 1000]
                merged += trimmed
            except Exception as e:
                print(f"Skipping {file} due to error:", e)

    if len(merged) == 0:
        print("No audio files were processed.")
        sys.exit(1)

    merged.export(output_file, format="mp3")


def main():
    singer, num_videos, duration, output_file = validate_inputs(sys.argv)

    try:
        clear_downloads_folder()
        download_videos(singer, num_videos)
        trim_and_merge(duration, output_file)
        print("Mashup created successfully:", output_file)

    except Exception as e:
        print("Error occurred:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
