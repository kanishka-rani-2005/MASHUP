# 🎵 Mashup Generator (Command Line + Web Service)

## 📌 Project Overview

This project implements a **Mashup Generator** using Python.  
It consists of two parts:

1. **Program 1 (Command Line Application)**
2. **Program 2 (Web Service using Flask)**

The application downloads multiple songs of a given singer from YouTube, extracts audio, trims the first Y seconds from each song, merges them into a single mashup file, and sends the result via email (Web version).

---

## 🚀 Features

- Download N videos of a singer from YouTube
- Convert videos to audio
- Trim first Y seconds from each audio
- Merge all trimmed audio files into one mashup
- Send mashup as ZIP file via email (Web version)
- Input validation & exception handling

---

## 🛠 Technologies Used

All required packages are installed via **PyPI (pypi.org)**:

- `yt-dlp` → Download YouTube videos
- `pydub` → Audio processing
- `Flask` → Web framework
- `python-dotenv` → Environment variables
- `smtplib` → Email sending
- `zipfile` → Create ZIP archive

---

## 📂 Project Structure
Mashup-Project/
│
├── 102317165.py # Program 1 (Command Line)
├── app.py # Program 2 (Web Service)
├── .env # Email credentials
├── requirements.txt
│
├── templates/
│ └── index.html
│
├── downloads/ # Temporary downloaded files
└── outputs/ # Final mashup output


---

# 🔹 Program 1: Command Line Application

## 📌 Usage

```bash
python <RollNumber>.py "<SingerName>" <NumberOfVideos> <AudioDuration> <OutputFileName>
```

# 🔹 Program 2: Web Service
## 📌 How It Works

#### User provides:

    Singer Name

    Number of Videos
    
    Duration of each video
    
    Email ID

#### System:

    Downloads videos
    
    Converts to audio
    
    Cuts first Y seconds
    
    Merges all audio
    
    Creates ZIP file
    
    Sends result via email
    
# Email Configuration

Create a .env file

``` bash
EMAIL=yourgmail@gmail.com
EMAIL_PASSWORD=your16digitapppassword
```

# Installation

Install required packages:
``` bash
pip install -r requirements.txt
```


 # Error Handling

### The program checks:

  Correct number of parameters
  
  Invalid input types
  
  Video download errors
  
  Audio processing errors
  
  Email authentication errors


  # Author - Kanishka Rani (102317165)
