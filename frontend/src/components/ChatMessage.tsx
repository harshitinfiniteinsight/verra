"use client";

import type { ChatMessage as ChatMessageType } from "@/lib/types";
import { DataChart } from "./DataChart";
import { DataTable } from "./DataTable";

interface ChatMessageProps {
  message: ChatMessageType;
}

function renderFormattedText(text: string) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i} className="font-semibold text-slate-900">{part.slice(2, -2)}</strong>;
    }
    return part;
  });
}

function formatContent(text: string) {
  const lines = text.split("\n");
  const elements: React.ReactNode[] = [];
  let listItems: string[] = [];

  const flushList = () => {
    if (listItems.length > 0) {
      elements.push(
        <ul key={elements.length} className="list-disc list-inside mb-2 space-y-0.5 text-slate-600">
          {listItems.map((item, i) => (
            <li key={i}>{renderFormattedText(item)}</li>
          ))}
        </ul>
      );
      listItems = [];
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.startsWith("• ") || line.match(/^[-*]\s/)) {
      listItems.push(line.replace(/^[-*•]\s*/, ""));
    } else {
      flushList();
      if (line.trim()) {
        elements.push(
          <p key={elements.length} className={elements.length ? "mt-2" : ""}>
            {renderFormattedText(line)}
          </p>
        );
      }
    }
  }
  flushList();
  return elements;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex animate-fade-in ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[85%] sm:max-w-2xl w-full ${isUser ? "flex justify-end" : ""}`}>
        <div
          className={
            isUser
              ? "rounded-2xl rounded-br-sm px-4 py-3 bg-gradient-to-br from-teal-500 to-teal-600 text-white shadow-md shadow-teal-500/20 hover:shadow-teal-500/25 transition-shadow"
              : "rounded-2xl rounded-bl-sm px-4 py-3.5 bg-white/95 backdrop-blur-sm border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow"
          }
        >
          <div className={`text-[15px] leading-relaxed ${isUser ? "text-white" : "text-slate-700"}`}>
            {typeof message.content === "string"
              ? formatContent(message.content)
              : message.content}
          </div>

          {message.chart && !isUser && (
            <div className="mt-4">
              <div className="text-[10px] uppercase tracking-wider text-slate-400 font-medium mb-2">Chart</div>
              <DataChart data={message.chart.data} layout={message.chart.layout} />
            </div>
          )}

          {message.data && !isUser && (
            <div className="mt-4">
              <div className="text-[10px] uppercase tracking-wider text-slate-400 font-medium mb-2">
                Results · {message.data.length} rows
              </div>
              <DataTable data={message.data} maxRows={5} />
            </div>
          )}

          {message.sql && !isUser && (
            <details className="mt-4 group">
              <summary className="cursor-pointer text-xs font-medium text-slate-400 hover:text-teal-600 transition-colors select-none flex items-center gap-1.5">
                <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
                SQL
              </summary>
              <div className="mt-2 p-3 bg-slate-900/5 rounded-xl overflow-x-auto border border-slate-100">
                <pre className="text-[11px] text-slate-500 font-mono leading-relaxed">{message.sql}</pre>
              </div>
            </details>
          )}
        </div>
      </div>
    </div>
  );
}
