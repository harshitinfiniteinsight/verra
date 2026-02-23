"use client";

import { useState } from "react";

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading?: boolean;
}

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [input, setInput] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSend(input);
      setInput("");
    }
  };

  return (
    <div className="shrink-0 border-t border-slate-200/80 bg-white/80 backdrop-blur-md px-4 py-4">
      <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
        <div className="flex gap-2 sm:gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about projects, momentum, velocity..."
            disabled={isLoading}
            className="flex-1 px-4 py-3.5 pr-12 rounded-2xl border border-slate-200 bg-white text-slate-900 placeholder-slate-400 shadow-sm focus:outline-none focus:ring-2 focus:ring-teal-500/25 focus:border-teal-500 transition-all disabled:opacity-60 text-[15px]"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="shrink-0 w-12 h-[46px] flex items-center justify-center rounded-2xl bg-gradient-to-br from-teal-500 to-teal-600 text-white shadow-md shadow-teal-500/25 hover:shadow-teal-500/30 hover:from-teal-600 hover:to-teal-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {isLoading ? (
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
            ) : (
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            )}
          </button>
        </div>
        <p className="text-center text-[11px] text-slate-400 mt-2">Verra VCU · 2,100+ projects · 98 countries</p>
      </form>
    </div>
  );
}
