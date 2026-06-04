from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter,
    FieldCondition, MatchValue
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from app.core.config import settings
import uuid

client = QdrantClient(
    url=settings.qdrant_url,
    api_key=settings.qdrant_api_key if settings.qdrant_api_key else None
)
embedder = SentenceTransformer("all-MiniLM-L6-v2")
VECTOR_SIZE = 384

def ensure_collection():
    collections = client.get_collections().collections
    names = [c.name for c in collections]
    if settings.qdrant_collection not in names:
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )

def embed_text(text: str) -> list:
    return embedder.encode(text).tolist()

def ingest_transcript(transcript: str, metadata: dict, video_id: str):
    ensure_collection()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )
    chunks = splitter.split_text(transcript)

    points = []
    for i, chunk in enumerate(chunks):
        embedding = embed_text(chunk)
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "video_id": video_id,
                "chunk_index": i,
                "text": chunk,
                "platform": metadata.get("platform"),
                "title": metadata.get("title"),
                "creator": metadata.get("creator"),
                "engagement_rate": metadata.get("engagement_rate"),
                "views": metadata.get("views"),
                "likes": metadata.get("likes"),
                "comments": metadata.get("comments"),
                "follower_count": metadata.get("follower_count"),
                "upload_date": metadata.get("upload_date"),
                "hashtags": metadata.get("hashtags", []),
            }
        ))

    client.upsert(
        collection_name=settings.qdrant_collection,
        points=points
    )
    return len(chunks)

def search_similar(query: str, video_id: str = None, top_k: int = 5):
    query_vector = embed_text(query)

    search_filter = None
    if video_id:
        search_filter = Filter(
            must=[FieldCondition(
                key="video_id",
                match=MatchValue(value=video_id)
            )]
        )

    results = client.search(
        collection_name=settings.qdrant_collection,
        query_vector=query_vector,
        limit=top_k,
        query_filter=search_filter,
        with_payload=True
    )
    return results