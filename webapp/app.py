import os
import zipfile
import smtplib
from flask import Flask, render_template, request
from email.message import EmailMessage
from pydub import AudioSegment
from dotenv import load_dotenv

# ==============================
# Setup
# ==============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(BASE_DIR, "downloads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"mp3", "wav", "m4a", "webm", "mp4"}


# ==============================
# Utility Functions
# ==============================

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def clear_folder(folder):
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        if os.path.isfile(file_path):
            os.remove(file_path)


def create_mashup_from_upload(files, duration, output_file):
    clear_folder(UPLOAD_FOLDER)
    clear_folder(OUTPUT_FOLDER)

    merged = AudioSegment.empty()

    for file in files:
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            try:
                audio = AudioSegment.from_file(filepath)
                trimmed = audio[:duration * 1000]
                merged += trimmed
            except Exception as e:
                print("Skipping invalid file:", file.filename)


    if len(merged) == 0:
        raise Exception("No valid audio files processed.")

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

    msg.add_attachment(
        file_data,
        maintype="application",
        subtype="zip",
        filename="mashup.zip"
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)


# ==============================
# Routes
# ==============================

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            duration = int(request.form["duration"])
            email = request.form["email"]
            files = request.files.getlist("songs")

            if not files:
                return "Please upload at least one audio file."

            if duration > 60:
                return "Maximum duration allowed is 60 seconds."

            final_audio = create_mashup_from_upload(
                files, duration, "mashup.mp3"
            )

            zip_path = os.path.join(OUTPUT_FOLDER, "mashup.zip")

            with zipfile.ZipFile(zip_path, "w") as zipf:
                zipf.write(final_audio, arcname="mashup.mp3")

            send_email(email, zip_path)

            return "Mashup created and sent successfully!"

        except Exception as e:
            return f"Error: {str(e)}"

    return render_template("index.html")


# ==============================
# Run App
# ==============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
