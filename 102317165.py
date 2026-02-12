import sys
import os
from yt_dlp import YoutubeDL
from pydub import AudioSegment

DOWNLOAD_FOLDER = "downloads"


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


def clear_downloads():
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    for file in os.listdir(DOWNLOAD_FOLDER):
        os.remove(os.path.join(DOWNLOAD_FOLDER, file))


def download_videos(singer, num_videos):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'quiet': True,
        'noplaylist': True
    }

    search_query = f"ytsearch{num_videos}:{singer} songs"

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([search_query])


def trim_and_merge(duration, output_file):
    merged = AudioSegment.empty()

    for file in os.listdir(DOWNLOAD_FOLDER):
        file_path = os.path.join(DOWNLOAD_FOLDER, file)
        try:
            audio = AudioSegment.from_file(file_path)
            trimmed = audio[:duration * 1000]
            merged += trimmed
        except Exception as e:
            print("Skipping file:", file)

    if len(merged) == 0:
        print("No audio files processed.")
        sys.exit(1)

    merged.export(output_file, format="mp3")


def main():
    singer, num_videos, duration, output_file = validate_inputs(sys.argv)

    try:
        clear_downloads()
        download_videos(singer, num_videos)
        trim_and_merge(duration, output_file)
        print("Mashup created successfully:", output_file)
    except Exception as e:
        print("Error occurred:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
