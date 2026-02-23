"use client";

import { useEffect, useRef, useState } from "react";
import { sendMessage } from "@/lib/api";
import type { ChatMessage as ChatMessageType, ChatResponse } from "@/lib/types";
import { ChatMessage } from "@/components/ChatMessage";
import { ChatInput } from "@/components/ChatInput";
import { Sidebar } from "@/components/Sidebar";

const WELCOME_MESSAGE = {
  role: "assistant" as const,
  content:
    "Hi! I'm your Verra carbon credit analyst. I can help you explore 2,100+ projects across 98 countries—whether you're looking for **hot projects** with rising momentum, **emerging opportunities**, or market trends.\n\nJust ask in plain English. For example:\n• \"Which projects are heating up?\"\n• \"Show me top intermediaries\"\n• \"Where are the best opportunities in energy?\"\n\nOr click any suggested question to jump right in.",
};

export default function Home() {
  const [messages, setMessages] = useState<ChatMessageType[]>([
    WELCOME_MESSAGE,
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [backendReady, setBackendReady] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/health", {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        });
        if (!response.ok) setBackendReady(false);
      } catch {
        setBackendReady(false);
      }
    };
    checkBackend();
  }, []);

  const handleSendMessage = async (userMessage: string) => {
    const userMsg: ChatMessageType = { role: "user", content: userMessage };
    setMessages((prev) => [...prev, userMsg]);

    if (!backendReady) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "⚠️ Backend server is not ready. Please ensure it's running on http://localhost:5000" },
      ]);
      return;
    }

    setIsLoading(true);

    try {
      const history = messages.slice(-10).map((m) => ({ role: m.role, content: m.content }));
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000);

      const response: ChatResponse = await sendMessage(userMessage, history);
      clearTimeout(timeoutId);

      let chartData = null;
      if (response.chart_spec) {
        try {
          chartData = typeof response.chart_spec === "string"
            ? JSON.parse(response.chart_spec)
            : response.chart_spec;
        } catch {
          /* ignore */
        }
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.text || "No response from server.",
          sql: response.sql,
          data: response.data,
          chart: chartData,
        },
      ]);
      if (!backendReady) setBackendReady(true);
    } catch (error) {
      let errorMessage = "Sorry, I encountered an error processing your request.";
      if (error instanceof Error) {
        if (error.name === "AbortError") errorMessage = "Request timed out. Please try again.";
        else if (error.message.includes("Failed to fetch")) {
          errorMessage = "Cannot connect to backend. Make sure it's running on http://localhost:5000";
          setBackendReady(false);
        } else errorMessage += ` (${error.message})`;
      }
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `❌ ${errorMessage}\n\nTip: Backend: http://localhost:5000 · Frontend: http://localhost:3000` },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const isWelcomeOnly = messages.length === 1 && messages[0].role === "assistant";

  return (
    <div className="flex h-screen bg-slate-50/90 min-h-0">
      <Sidebar onSelectQuestion={handleSendMessage} isLoading={isLoading} />

      <div className="flex-1 flex flex-col overflow-hidden min-w-0">
        {!backendReady && (
          <div className="shrink-0 flex items-center gap-3 px-5 py-2.5 bg-amber-500/10 border-b border-amber-500/20 text-amber-800 text-sm">
            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-amber-500/20">
              <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <span className="font-medium">Backend not responding</span>
            <code className="ml-1 px-1.5 py-0.5 bg-amber-500/20 rounded text-xs font-mono">cd backend && python3 main.py</code>
          </div>
        )}

        <div className="flex-1 overflow-y-auto overscroll-contain">
          <div className="max-w-3xl mx-auto px-5 sm:px-6 py-6 sm:py-8">
            {isWelcomeOnly ? (
              <div className="flex flex-col items-center text-center min-h-[50vh] pt-4">
                <div
                  className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-teal-500/20 to-cyan-500/20 ring-1 ring-teal-500/20 mb-6 animate-fade-in"
                  style={{ animationDelay: "0.05s" }}
                >
                  <svg className="h-8 w-8 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75m15.75 0h.75a.75.75 0 00.75-.75V15m-1.5 1.5v.75c0 .414.336.75.75.75h.75" />
                  </svg>
                </div>
                <h2 className="text-xl font-semibold text-slate-800 mb-1.5">How can I help?</h2>
                <p className="text-slate-500 text-sm max-w-sm mb-8">
                  Ask about projects, momentum, or market trends. Click a suggested question to start.
                </p>
                <div className="w-full max-w-2xl space-y-3 animate-slide-up">
                  {messages.map((msg, idx) => (
                    <ChatMessage key={idx} message={msg} />
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((msg, idx) => (
                  <ChatMessage key={idx} message={msg} />
                ))}
              </div>
            )}
            {isLoading && (
              <div className="flex items-center gap-2 mt-4 text-slate-500 text-sm animate-pulse-soft">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <span>Thinking...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
}
