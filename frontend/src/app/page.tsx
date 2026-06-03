"use client";

import { useState } from "react";
import VideoCard from "@/components/VideoCard";
import ChatPanel from "@/components/ChatPanel";
import { ingestVideos, VideoMetadata } from "@/lib/api";

export default function Home() {
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [instagramUrl, setInstagramUrl] = useState("");
  const [videoA, setVideoA] = useState<VideoMetadata | null>(null);
  const [videoB, setVideoB] = useState<VideoMetadata | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [ingested, setIngested] = useState(false);

  const handleIngest = async () => {
        console.log("handleIngest called", youtubeUrl, instagramUrl);
    if (!youtubeUrl.trim() || !instagramUrl.trim()) {
      setError("Please enter both URLs");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const result = await ingestVideos(youtubeUrl, instagramUrl);
      if (result.success) {
        setVideoA(result.video_a || null);
        setVideoB(result.video_b || null);
        setIngested(true);
      } else {
        setError(result.message);
      }
    } catch (e) {
      setError("Failed to ingest videos. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-950 text-white">
      <div className="max-w-7xl mx-auto px-6 py-8">

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white">Creator Lens</h1>
          <p className="text-gray-400 mt-1">
            RAG-powered video analysis for content creators
          </p>
        </div>

        <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 mb-8">
          <h2 className="text-white font-semibold mb-4">Analyze Videos</h2>
          <div className="flex flex-col md:flex-row gap-3">
            <input
              className="flex-1 bg-gray-800 text-white text-sm rounded-lg px-4 py-3 outline-none border border-gray-600 focus:border-blue-500"
              placeholder="YouTube URL (Video A)"
              value={youtubeUrl}
              onChange={(e) => setYoutubeUrl(e.target.value)}
            />
            <input
              className="flex-1 bg-gray-800 text-white text-sm rounded-lg px-4 py-3 outline-none border border-gray-600 focus:border-blue-500"
              placeholder="Instagram Reel URL (Video B)"
              value={instagramUrl}
              onChange={(e) => setInstagramUrl(e.target.value)}
            />
            <button
              onClick={handleIngest}
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium px-6 py-3 rounded-lg text-sm"
            >
              {loading ? "Analyzing..." : "Analyze"}
            </button>
          </div>
          {error && (
            <p className="text-red-400 text-sm mt-3">{error}</p>
          )}
        </div>

        {ingested && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 flex flex-col gap-4">
              {videoA && <VideoCard video={videoA} label="A" />}
              {videoB && <VideoCard video={videoB} label="B" />}
            </div>
            <div className="lg:col-span-2 h-[600px]">
              <ChatPanel />
            </div>
          </div>
        )}

        {!ingested && (
          <div className="text-center text-gray-600 mt-20">
            <p className="text-lg">Enter two video URLs above to get started</p>
          </div>
        )}
      </div>
    </main>
  );
}