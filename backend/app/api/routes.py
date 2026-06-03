from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.models.schemas import VideoIngestRequest, ChatMessage
from app.services.youtube_service import extract_video_id, get_transcript, get_metadata
from app.services.instagram_service import get_instagram_data
from app.services.vector_service import ingest_transcript
from app.services.rag_service import rag_chain
import json

router = APIRouter()

video_store = {}
chat_sessions = {}

@router.post("/ingest")
async def ingest_videos(request: VideoIngestRequest):
    try:
        # YouTube ingestion
        yt_id = extract_video_id(request.youtube_url)
        yt_transcript = get_transcript(yt_id)
        yt_metadata = get_metadata(yt_id)
        yt_chunks = ingest_transcript(yt_transcript, yt_metadata, "A")
        video_store["A"] = yt_metadata

        # Instagram ingestion — uses fallback internally, never raises
        ig_data = get_instagram_data(request.instagram_url)
        ig_chunks = ingest_transcript(
            ig_data["transcript"],
            ig_data["metadata"],
            "B"
        )
        video_store["B"] = ig_data["metadata"]

        return {
            "success": True,
            "message": f"Ingested Video A ({yt_chunks} chunks) and Video B ({ig_chunks} chunks)",
            "video_a": yt_metadata,
            "video_b": ig_data["metadata"]
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "message": str(e)}

@router.post("/chat")
async def chat(message: ChatMessage):
    session_id = message.session_id
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []

    history = chat_sessions[session_id]

    async def stream_response():
        state = {
            "query": message.message,
            "history": history,
            "retrieved_chunks": [],
            "answer": "",
            "citations": [],
            "augmented_prompt": ""
        }

        result = rag_chain.invoke(state)
        answer = result["answer"]
        citations = result["citations"]

        for char in answer:
            yield f"data: {json.dumps({'type': 'token', 'content': char})}\n\n"

        yield f"data: {json.dumps({'type': 'citations', 'content': citations})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

        history.append({"role": "user", "content": message.message})
        history.append({"role": "assistant", "content": answer})
        chat_sessions[session_id] = history[-20:]

    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream"
    )

@router.get("/videos")
async def get_videos():
    return {"videos": video_store}