import os
import zipfile
import smtplib
from flask import Flask, render_template, request
from email.message import EmailMessage
from yt_dlp import YoutubeDL
from pydub import AudioSegment
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"), override=True)

app = Flask(__name__)

DOWNLOAD_FOLDER = os.path.join(BASE_DIR, "downloads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def clear_folder(folder):
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        if os.path.isfile(file_path):
            os.remove(file_path)


def download_videos(singer, num_videos):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
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
        except:
            continue

    if len(merged) == 0:
        raise Exception("No audio files processed.")

    final_path = os.path.join(OUTPUT_FOLDER, output_file)
    merged.export(final_path, format="mp3")

    return final_path


def send_email(receiver_email, file_path):
    sender_email = os.getenv("EMAIL")
    sender_password = os.getenv("EMAIL_PASSWORD")
    print(sender_email)
    print(sender_password)

    msg = EmailMessage()
    msg["Subject"] = "Your Mashup File"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content("Your mashup file is attached.")

    with open(file_path, "rb") as f:
        file_data = f.read()

    msg.add_attachment(
        file_data,
        maintype="application",
        subtype="zip",
        filename="mashup.zip"
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            singer = request.form["singer"]
            num_videos = int(request.form["num_videos"])
            duration = int(request.form["duration"])
            email = request.form["email"]

            if num_videos <= 10:
                return "Number of videos must be greater than 10."

            if duration <= 20:
                return "Duration must be greater than 20 seconds."

            clear_folder(DOWNLOAD_FOLDER)
            clear_folder(OUTPUT_FOLDER)

            download_videos(singer, num_videos)

            final_audio = trim_and_merge(duration, "mashup.mp3")

            zip_path = os.path.join(OUTPUT_FOLDER, "mashup.zip")

            with zipfile.ZipFile(zip_path, "w") as zipf:
                zipf.write(final_audio, arcname="mashup.mp3")

            send_email(email, zip_path)

            return "Mashup created and sent successfully!"

        except Exception as e:
            return f"Error: {str(e)}"

    return render_template("index.html")



if __name__ == "__main__":
    app.run(debug=True)
