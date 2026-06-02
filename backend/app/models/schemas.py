from pydantic import BaseModel
from typing import Optional

class VideoIngestRequest(BaseModel):
    youtube_url: str
    instagram_url: str

class VideoMetadata(BaseModel):
    video_id: str
    platform: str
    url: str
    title: str
    creator: str
    views: int
    likes: int
    comments: int
    duration: int
    upload_date: str
    hashtags: list[str]
    follower_count: int
    engagement_rate: float

class ChatMessage(BaseModel):
    session_id: str
    message: str

class IngestResponse(BaseModel):
    success: bool
    message: str
    video_a: Optional[VideoMetadata] = None
    video_b: Optional[VideoMetadata] = None