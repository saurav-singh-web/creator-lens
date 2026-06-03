from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
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
        return f"Video ID: {video_id}. No transcript available."

def get_metadata(video_id: str) -> dict:
    try:
        import httpx
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        url = f"https://www.youtube.com/watch?v={video_id}"
        with httpx.Client(follow_redirects=True, timeout=15) as client:
            response = client.get(url, headers=headers)
            html = response.text

        def extract(pattern, default="N/A"):
            match = re.search(pattern, html)
            return match.group(1) if match else default

        title = extract(r'"title":"([^"]+)"')
        views = extract(r'"viewCount":"(\d+)"')
        channel = extract(r'"ownerChannelName":"([^"]+)"')
        upload_date = extract(r'"uploadDate":"([^"]+)"')
        duration_text = extract(r'"lengthSeconds":"(\d+)"')
        hashtags_raw = re.findall(r'"#(\w+)"', html)

        views_int = int(views) if views.isdigit() else 0
        duration_int = int(duration_text) if duration_text.isdigit() else 0

        return {
            "platform": "youtube",
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "title": title if title != "N/A" else f"YouTube Video {video_id}",
            "creator": channel if channel != "N/A" else "Unknown Creator",
            "views": views_int,
            "likes": 0,
            "comments": 0,
            "duration": duration_int,
            "upload_date": upload_date,
            "hashtags": list(set(hashtags_raw[:10])),
            "follower_count": 0,
            "engagement_rate": 0.0
        }
    except Exception as e:
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