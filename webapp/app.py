import os
import zipfile
import smtplib
from flask import Flask, render_template, request
from email.message import EmailMessage
from yt_dlp import YoutubeDL
from pydub import AudioSegment

from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)

# Base directory of this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "downloads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)



def create_mashup(singer, num_videos, duration, output_file):

    # Clear old downloads
    for file in os.listdir(UPLOAD_FOLDER):
        os.remove(os.path.join(UPLOAD_FOLDER, file))

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(UPLOAD_FOLDER, '%(title)s.%(ext)s'),
        'quiet': False,
        'noplaylist': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android']
            }
        }
    }

    search_query = f"ytsearch{num_videos}:{singer} songs"

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([search_query])
    except Exception as e:
        print("Download error:", e)
        raise Exception("YouTube blocked the request. Try again after some time.")

    merged = AudioSegment.empty()

    for file in os.listdir(UPLOAD_FOLDER):
        if file.endswith((".webm", ".m4a", ".mp3",'.mp4')):
            path = os.path.join(UPLOAD_FOLDER, file)
            try:
                audio = AudioSegment.from_file(path)
                trimmed = audio[:duration * 1000]
                merged += trimmed
            except Exception as e:
                print("Skipping:", file, e)

    if len(merged) == 0:
        raise Exception("No audio files processed.")

    final_path = os.path.join(OUTPUT_FOLDER, output_file)
    merged.export(final_path, format="mp3")

    return final_path


def send_email(receiver_email, file_path):
    sender_email = os.getenv("EMAIL")
    sender_password = os.getenv("EMAIL_PASSWORD")


    msg = EmailMessage()
    msg["Subject"] = "Your Mashup File"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content("Your mashup file is attached.")

    with open(file_path, "rb") as f:
        file_data = f.read()

    msg.add_attachment(file_data, maintype="application", subtype="zip", filename="mashup.zip")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        singer = request.form["singer"]
        num_videos = int(request.form["num_videos"])
        duration = int(request.form["duration"])
        email = request.form["email"]

        output_file = "mashup.mp3"
        final_audio = create_mashup(singer, num_videos, duration, output_file)

        zip_path = os.path.join(OUTPUT_FOLDER, "mashup.zip")

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(final_audio)

        send_email(email, zip_path)

        return "Mashup sent to your email!"

    return render_template("index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

