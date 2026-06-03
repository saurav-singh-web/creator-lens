import { VideoMetadata } from "../lib/api";

interface Props {
  video: VideoMetadata;
  label: string;
}

export default function VideoCard({ video, label }: Props) {
  return (
    <>
    <div className="bg-gray-900 border border-gray-700 rounded-xl p-5 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-full">
          Video {label}
        </span>
        <span className="text-xs text-gray-400 uppercase">{video.platform}</span>
      </div>

      <h2 className="text-white font-semibold text-sm leading-snug line-clamp-2">
        {video.title}
      </h2>

      <div className="text-gray-400 text-xs">
        By <span className="text-white font-medium">{video.creator}</span>
        {video.follower_count > 0 && (
          <span> · {video.follower_count.toLocaleString()} followers</span>
        )}
      </div>

      <div className="grid grid-cols-3 gap-2 mt-1">
        <Stat label="Views" value={video.views.toLocaleString()} />
        <Stat label="Likes" value={video.likes.toLocaleString()} />
        <Stat label="Comments" value={video.comments.toLocaleString()} />
      </div>

      <div className="bg-gray-800 rounded-lg p-3 flex items-center justify-between">
        <span className="text-gray-400 text-xs">Engagement Rate</span>
        <span className="text-green-400 font-bold text-sm">
          {video.engagement_rate}%
        </span>
      </div>

      <div className="text-xs text-gray-500">
        {video.upload_date} · {Math.floor(video.duration / 60)}m {video.duration % 60}s
      </div>

      {video.hashtags.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {video.hashtags.slice(0, 5).map((tag) => (
            <span
              key={tag}
              className="text-xs bg-gray-800 text-blue-400 px-2 py-0.5 rounded-full"
            >
              #{tag}
            </span>
          ))}
        </div>
      )}
    </div>
    </>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-800 rounded-lg p-2 text-center">
      <div className="text-white text-xs font-bold">{value}</div>
      <div className="text-gray-500 text-xs">{label}</div>
    </div>
  );
}