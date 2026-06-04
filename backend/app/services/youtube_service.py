from urllib.parse import parse_qs, urlparse

import httpx
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> str:
    parsed = urlparse(url)

    if parsed.hostname == "youtu.be":
        video_id = parsed.path.strip("/").split("/")[0]
        if video_id:
            return video_id

    if parsed.hostname in ("www.youtube.com", "youtube.com", "m.youtube.com"):
        video_id = parse_qs(parsed.query).get("v", [None])[0]
        if video_id:
            return video_id

        path_parts = [part for part in parsed.path.split("/") if part]
        if len(path_parts) >= 2 and path_parts[0] in ("shorts", "embed", "live"):
            return path_parts[1]

    raise ValueError(f"Invalid YouTube URL: {url}")


def get_transcript(video_id: str) -> str:
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry["text"] for entry in transcript_list])
    except Exception:
        return f"YouTube video {video_id}. No transcript available."


def _default_metadata(
    video_id: str,
    title: str | None = None,
    creator: str | None = None,
) -> dict:
    return {
        "video_id": video_id,
        "platform": "youtube",
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "title": title or f"YouTube Video {video_id}",
        "creator": creator or "Unknown Creator",
        "views": 0,
        "likes": 0,
        "comments": 0,
        "duration": 0,
        "upload_date": "N/A",
        "hashtags": [],
        "follower_count": 0,
        "engagement_rate": 0.0,
    }


def _format_upload_date(raw_date: str | None) -> str:
    if not raw_date or len(raw_date) != 8:
        return "N/A"
    return f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"


def _hashtags_from_info(info: dict) -> list[str]:
    tags = info.get("tags") or []
    if tags:
        return [str(tag).lstrip("#") for tag in tags[:10]]

    description = info.get("description") or ""
    return [
        word.lstrip("#")
        for word in description.split()
        if word.startswith("#")
    ][:10]


def get_metadata(video_id: str) -> dict:
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "extract_flat": False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

        views = info.get("view_count") or 0
        likes = info.get("like_count") or 0
        comments = info.get("comment_count") or 0
        engagement = (
            round(((likes + comments) / views * 100), 2)
            if views > 0
            else 0.0
        )

        return {
            "video_id": video_id,
            "platform": "youtube",
            "url": video_url,
            "title": info.get("title") or f"YouTube Video {video_id}",
            "creator": info.get("uploader")
            or info.get("channel")
            or "Unknown Creator",
            "views": views,
            "likes": likes,
            "comments": comments,
            "duration": info.get("duration") or 0,
            "upload_date": _format_upload_date(info.get("upload_date")),
            "hashtags": _hashtags_from_info(info),
            "follower_count": info.get("channel_follower_count") or 0,
            "engagement_rate": engagement,
        }
    except Exception:
        pass

    try:
        oembed_url = f"https://www.youtube.com/oembed?url={video_url}&format=json"
        with httpx.Client(timeout=10) as client:
            response = client.get(oembed_url)
            response.raise_for_status()
            data = response.json()

        return _default_metadata(
            video_id,
            data.get("title"),
            data.get("author_name"),
        )
    except Exception:
        return _default_metadata(video_id)
