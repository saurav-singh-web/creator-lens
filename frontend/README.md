# Creator Lens 🎥

A full-stack RAG chatbot that analyzes YouTube and Instagram videos side-by-side, 
letting creators ask natural language questions about their content performance.

## What it does

- Ingests YouTube + Instagram videos (transcript + metadata)
- Computes engagement rate = (likes + comments) / views × 100
- Chunks and embeds transcripts into Qdrant vector DB
- LangGraph 3-node RAG chain (retrieve → augment → generate)
- Streaming chat responses with source citations
- Maintains conversation memory across turns

## Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Backend | FastAPI | Async, fast, auto Swagger docs |
| Orchestration | LangGraph | Stateful RAG graph with typed nodes |
| Embeddings | all-MiniLM-L6-v2 | Free, local, 384-dim, fast |
| Vector DB | Qdrant | Local Docker, payload filtering by video_id |
| LLM | Groq (llama-3.1-8b) | Free tier, 10x faster than OpenAI |
| Frontend | Next.js + Tailwind | SSE streaming, citation badges |
| Streaming | FastAPI SSE | Simpler than WebSockets for one-way stream |

## Architecture

YouTube URL → transcript API → chunk → embed → Qdrant (video_id: A)
Instagram URL → yt-dlp → chunk → embed → Qdrant (video_id: B)
User query → retrieve node → augment node → generate node → SSE stream

## Quick Start

### 1. Start Qdrant
```bash
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
```

### 2. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env   # Add your GROQ_API_KEY
python -m uvicorn app.main:app --reload
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## Cost Analysis (1,000 creators/day)

| Component | Cost |
|---|---|
| Embeddings | $0 (local model) |
| LLM inference | $0 (Groq free tier) |
| Vector DB | $0 (self-hosted Qdrant) |
| **Total** | **$0 for development** |

Production at scale: ~$50/month (Qdrant Cloud + Groq paid tier)

## Trade-offs

**Why Qdrant over Pinecone?**
Runs locally in Docker — zero cold start, no API key needed for demo.
Supports payload filtering (filter by video_id without dual queries).

**Why all-MiniLM-L6-v2 over OpenAI embeddings?**
Free, runs locally, 384 dimensions vs 1536 — faster search, lower memory.
Quality is sufficient for transcript similarity search.

**Why Groq over GPT-4o?**
10x faster inference, free tier available, llama-3.1-8b handles 
FAQ-style creator questions with high quality.

**Why chunk size 512/50 overlap?**
Big enough to preserve sentence context, small enough for precise retrieval.
Smaller chunks lose meaning, larger chunks dilute similarity scores.

**What breaks at 10,000 users/day?**
- In-memory chat sessions → replace with Redis
- Single Qdrant instance → replicated cluster
- Synchronous embedding → async batch processing