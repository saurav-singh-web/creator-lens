from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import httpx
import os

def extract_video_id(url: str) -> str:
    parsed = urlparse(url)
    if parsed.hostname in ("youtu.be",):
        return parsed.path[1:]
    if parsed.hostname in ("www.youtube.com", "youtube.com"):
        return parse_qs(parsed.query).get("v", [None])[0]
    raise ValueError(f"Invalid YouTube URL: {url}")

def get_transcript(video_id: str) -> str:
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join([entry["text"] for entry in transcript_list])

def get_metadata(video_id: str) -> dict:
    url = f"https://www.youtube.com/watch?v={video_id}"
    with httpx.Client() as client:
        response = client.get(url, headers={
            "User-Agent": "Mozilla/5.0"
        })
        html = response.text

    def extract(pattern, default="N/A"):
        import re
        match = re.search(pattern, html)
        return match.group(1) if match else default

    import re
    title = extract(r'"title":"([^"]+)"')
    views = extract(r'"viewCount":"(\d+)"')
    likes = extract(r'"defaultText":\{"simpleText":"([\d,KM]+) likes"\}')
    channel = extract(r'"ownerChannelName":"([^"]+)"')
    upload_date = extract(r'"uploadDate":"([^"]+)"')
    duration_text = extract(r'"lengthSeconds":"(\d+)"')
    hashtags_raw = re.findall(r'"#(\w+)"', html)

    views_int = int(views) if views.isdigit() else 0
    likes_clean = likes.replace(",", "")
    likes_int = int(likes_clean) if likes_clean.isdigit() else 0
    duration_int = int(duration_text) if duration_text.isdigit() else 0
    engagement = round((likes_int / views_int * 100), 2) if views_int > 0 else 0.0

    return {
        "platform": "youtube",
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "title": title,
        "creator": channel,
        "views": views_int,
        "likes": likes_int,
        "comments": 0,
        "duration": duration_int,
        "upload_date": upload_date,
        "hashtags": list(set(hashtags_raw[:10])),
        "follower_count": 0,
        "engagement_rate": engagement
    }