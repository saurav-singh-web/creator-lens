import axios from "axios";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export const api = axios.create({
  baseURL: BASE_URL,
});

export interface VideoMetadata {
  video_id: string;
  platform: string;
  url: string;
  title: string;
  creator: string;
  views: number;
  likes: number;
  comments: number;
  duration: number;
  upload_date: string;
  hashtags: string[];
  follower_count: number;
  engagement_rate: number;
}

export interface IngestResponse {
  success: boolean;
  message: string;
  video_a?: VideoMetadata;
  video_b?: VideoMetadata;
}

export const ingestVideos = async (
  youtube_url: string,
  instagram_url: string
): Promise<IngestResponse> => {
  const response = await api.post("/ingest", {
    youtube_url,
    instagram_url,
  });
  return response.data;
};

export const getVideos = async () => {
  const response = await api.get("/videos");
  return response.data;
};