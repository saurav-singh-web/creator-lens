"use client";

import { useState, useRef, useEffect } from "react";
import { fetchEventSource } from "@microsoft/fetch-event-source";

interface Message {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
}

interface Citation {
  video_id: string;
  chunk_index: number;
  title: string;
}

export default function ChatPanel() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const sessionId = useRef("session-" + Date.now());
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    let assistantContent = "";
    let citations: Citation[] = [];

    setMessages((prev) => [
      ...prev,
      { role: "assistant", content: "", citations: [] },
    ]);

    await fetchEventSource("http://localhost:8000/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId.current,
        message: userMessage,
      }),
      onmessage(event) {
        const data = JSON.parse(event.data);
        if (data.type === "token") {
          assistantContent += data.content;
          setMessages((prev) => {
            const updated = [...prev];
            updated[updated.length - 1] = {
              role: "assistant",
              content: assistantContent,
              citations,
            };
            return updated;
          });
        } else if (data.type === "citations") {
          citations = data.content;
          setMessages((prev) => {
            const updated = [...prev];
            updated[updated.length - 1] = {
              role: "assistant",
              content: assistantContent,
              citations,
            };
            return updated;
          });
        } else if (data.type === "done") {
          setLoading(false);
        }
      },
      onerror() {
        setLoading(false);
      },
    });
  };

  return (
    <>
    <div className="flex flex-col h-full bg-gray-900 border border-gray-700 rounded-xl overflow-hidden">
      <div className="px-5 py-4 border-b border-gray-700">
        <h2 className="text-white font-semibold">Ask Creator Lens</h2>
        <p className="text-gray-400 text-xs mt-0.5">
          Ask anything about your videos
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
        {messages.length === 0 && (
          <div className="text-gray-500 text-sm text-center mt-10">
            Try asking: &quot;Why did Video A get more engagement?&quot;
          </div>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-xl px-4 py-3 text-sm ${
                msg.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-800 text-gray-100"
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
              {msg.citations && msg.citations.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {msg.citations.map((c, j) => (
                    <span
                      key={j}
                      className="text-xs bg-gray-700 text-blue-400 px-2 py-0.5 rounded-full"
                    >
                      Video {c.video_id} · chunk {c.chunk_index}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-800 rounded-xl px-4 py-3 text-sm text-gray-400">
              Thinking...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="p-4 border-t border-gray-700 flex gap-2">
        <input
          className="flex-1 bg-gray-800 text-white text-sm rounded-lg px-4 py-2.5 outline-none border border-gray-600 focus:border-blue-500"
          placeholder="Ask about your videos..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-medium px-4 py-2.5 rounded-lg"
        >
          Send
        </button>
      </div>
    </div>
    </>
  );
}