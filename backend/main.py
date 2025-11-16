import os
import requests
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("YOUTUBE_CODE")

# --------------------------------------------------
# STEP 1 — Get trending topic
# --------------------------------------------------

def get_trending_topic():
    url = "https://trends.google.com/trending/rss?geo=US"
    r = requests.get(url)

    # VERY simple extraction
    if "<title>" in r.text:
        start = r.text.find("<title>") + len("<title>")
        end = r.text.find("</title>", start)
        topic = r.text[start:end]
        return topic.replace("Google Trends", "").strip()

    return "Viral News Today"

# --------------------------------------------------
# STEP 2 — Download video clip from Pexels
# --------------------------------------------------

def download_video(query):
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=1"

    r = requests.get(url, headers=headers)
    data = r.json()

    video_url = data["videos"][0]["video_files"][0]["link"]

    video_data = requests.get(video_url).content
    filename = "short.mp4"

    with open(filename, "wb") as f:
        f.write(video_data)

    return filename

# --------------------------------------------------
# STEP 3 — Authenticate YouTube
# --------------------------------------------------

def authenticate_youtube():
    creds = Credentials(
        token=None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )
    creds.refresh(google.auth.transport.requests.Request())
    return build("youtube", "v3", credentials=creds)

# --------------------------------------------------
# STEP 4 — Upload video
# --------------------------------------------------

def upload_short(youtube, filename, title):
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": f"Auto-generated video about {title}",
                "tags": ["Trending", "Shorts", "AI Generated"],
            },
            "status": {"privacyStatus": "public"},
        },
        media_body=filename,
        media_mime_type="video/mp4"
    )

    response = request.execute()
    print("Uploaded video ID:", response["id"])

# --------------------------------------------------
# MAIN SCRIPT
# --------------------------------------------------

def main():
    print("Fetching trending topic...")
    topic = get_trending_topic()

    print("Downloading video...")
    video_file = download_video(topic)

    print("Authenticating YouTube...")
    youtube = authenticate_youtube()

    print("Uploading short...")
    upload_short(youtube, video_file, topic)

    print("DONE!")

if __name__ == "__main__":
    main()
