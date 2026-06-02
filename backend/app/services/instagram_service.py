import yt_dlp
import os
import tempfile
import re

def get_instagram_data(url: str) -> dict:
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    title = info.get("title", "Instagram Reel")
    description = info.get("description", "")
    duration = info.get("duration", 0)
    upload_date = info.get("upload_date", "N/A")
    like_count = info.get("like_count", 0) or 0
    view_count = info.get("view_count", 0) or 0
    comment_count = info.get("comment_count", 0) or 0
    uploader = info.get("uploader", "Unknown")
    follower_count = info.get("channel_follower_count", 0) or 0

    hashtags = re.findall(r"#(\w+)", description)

    engagement = round(
        ((like_count + comment_count) / view_count * 100), 2
    ) if view_count > 0 else 0.0

    transcript = description if description else title

    return {
        "metadata": {
            "platform": "instagram",
            "url": url,
            "title": title,
            "creator": uploader,
            "views": view_count,
            "likes": like_count,
            "comments": comment_count,
            "duration": duration,
            "upload_date": upload_date,
            "hashtags": hashtags[:10],
            "follower_count": follower_count,
            "engagement_rate": engagement
        },
        "transcript": transcript
    }