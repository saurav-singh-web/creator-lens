from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from app.services.vector_service import search_similar
from app.core.config import settings
from typing import TypedDict, List

llm = ChatOpenAI(
    model=settings.llm_model,
    api_key=settings.openai_api_key,
    streaming=True,
    temperature=0.7
)

class RAGState(TypedDict):
    query: str
    history: List[dict]
    retrieved_chunks: List[dict]
    answer: str
    citations: List[dict]
    augmented_prompt: str

def retrieve_node(state: RAGState) -> RAGState:
    query = state["query"]
    results = search_similar(query, top_k=6)
    chunks = []
    for r in results:
        chunks.append({
            "text": r.payload.get("text", ""),
            "video_id": r.payload.get("video_id", ""),
            "chunk_index": r.payload.get("chunk_index", 0),
            "title": r.payload.get("title", ""),
            "creator": r.payload.get("creator", ""),
            "engagement_rate": r.payload.get("engagement_rate", 0),
            "views": r.payload.get("views", 0),
            "likes": r.payload.get("likes", 0),
            "comments": r.payload.get("comments", 0),
            "follower_count": r.payload.get("follower_count", 0),
            "score": r.score
        })
    state["retrieved_chunks"] = chunks
    return state

def augment_node(state: RAGState) -> RAGState:
    chunks = state["retrieved_chunks"]
    history = state["history"]

    context = ""
    citations = []
    for i, chunk in enumerate(chunks):
        context += "\n[Video " + chunk["video_id"] + " | Chunk " + str(chunk["chunk_index"]) + "]\n"
        context += "Title: " + chunk["title"] + "\n"
        context += "Creator: " + chunk["creator"] + "\n"
        context += "Views: " + str(chunk["views"]) + " | Likes: " + str(chunk["likes"]) + " | "
        context += "Comments: " + str(chunk["comments"]) + "\n"
        context += "Engagement Rate: " + str(chunk["engagement_rate"]) + "%\n"
        context += "Follower Count: " + str(chunk["follower_count"]) + "\n"
        context += "Content: " + chunk["text"] + "\n"
        citations.append({
            "video_id": chunk["video_id"],
            "chunk_index": chunk["chunk_index"],
            "title": chunk["title"]
        })

    history_text = ""
    for msg in history[-6:]:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        history_text += role.upper() + ": " + content + "\n"

    prompt = (
        "You are Creator Lens, an AI analyst helping content creators understand their video performance.\n\n"
        "Use the context below to answer the question. Always cite which video (A or B) your insights come from.\n"
        "Be specific with numbers — mention exact engagement rates, view counts, likes when relevant.\n\n"
        "CONTEXT:\n" + context + "\n\n"
        "CONVERSATION HISTORY:\n" + history_text + "\n\n"
        "QUESTION: " + state["query"] + "\n\n"
        "Answer with clear insights, cite [Video A] or [Video B] where relevant:"
    )

    state["augmented_prompt"] = prompt
    state["citations"] = citations
    return state

def generate_node(state: RAGState) -> RAGState:
    prompt = state.get("augmented_prompt", state["query"])
    response = llm.invoke(prompt)
    state["answer"] = response.content
    return state

def build_rag_graph():
    graph = StateGraph(RAGState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("augment", augment_node)
    graph.add_node("generate", generate_node)
    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "augment")
    graph.add_edge("augment", "generate")
    graph.add_edge("generate", END)
    return graph.compile()

rag_chain = build_rag_graph()