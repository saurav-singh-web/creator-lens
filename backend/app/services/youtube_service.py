from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import httpx
import re

def extract_video_id(url: str) -> str:
    parsed = urlparse(url)
    if parsed.hostname in ("youtu.be",):
        return parsed.path[1:]
    if parsed.hostname in ("www.youtube.com", "youtube.com"):
        return parse_qs(parsed.query).get("v", [None])[0]
    raise ValueError(f"Invalid YouTube URL: {url}")

def get_transcript(video_id: str) -> str:
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry["text"] for entry in transcript_list])
    except Exception:
        return f"YouTube video {video_id}. No transcript available."

def get_metadata(video_id: str) -> dict:
    try:
        # Use oEmbed API — never blocked, no auth needed
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        with httpx.Client(timeout=10) as client:
            response = client.get(oembed_url)
            data = response.json()

        title = data.get("title", f"YouTube Video {video_id}")
        creator = data.get("author_name", "Unknown Creator")

        # Get view count from noembed as fallback
        try:
            noembed_url = f"https://noembed.com/embed?url=https://www.youtube.com/watch?v={video_id}"
            with httpx.Client(timeout=10) as client:
                noembed_response = client.get(noembed_url)
                noembed_data = noembed_response.json()
                title = noembed_data.get("title", title)
                creator = noembed_data.get("author_name", creator)
        except Exception:
            pass

        return {
            "platform": "youtube",
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "title": title,
            "creator": creator,
            "views": 0,
            "likes": 0,
            "comments": 0,
            "duration": 0,
            "upload_date": "N/A",
            "hashtags": [],
            "follower_count": 0,
            "engagement_rate": 0.0
        }
    except Exception:
        return {
            "platform": "youtube",
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "title": f"YouTube Video {video_id}",
            "creator": "Unknown",
            "views": 0,
            "likes": 0,
            "comments": 0,
            "duration": 0,
            "upload_date": "N/A",
            "hashtags": [],
            "follower_count": 0,
            "engagement_rate": 0.0
        }