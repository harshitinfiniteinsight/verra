"use client";

import { useEffect, useState } from "react";
import { getDataSummary, getSuggestedQuestions } from "@/lib/api";
import type { DataSummary, SuggestedQuestionsData } from "@/lib/types";

interface SidebarProps {
  onSelectQuestion: (question: string) => void;
  isLoading?: boolean;
}

const quadrantStyles: Record<string, string> = {
  Hot: "bg-gradient-to-r from-amber-400 to-orange-500 text-white shadow-md shadow-amber-500/30",
  Dormant: "bg-gradient-to-r from-indigo-400 to-violet-500 text-white shadow-md shadow-indigo-500/25",
  Stable: "bg-gradient-to-r from-emerald-400 to-green-500 text-white shadow-md shadow-emerald-500/25",
  Emerging: "bg-gradient-to-r from-cyan-400 to-teal-500 text-white shadow-md shadow-cyan-500/25",
};

const categoryColors: Record<string, string> = {
  Momentum: "from-amber-500/20 to-orange-500/20 border-amber-400/30 text-amber-200",
  Supply: "from-teal-500/20 to-cyan-500/20 border-teal-400/30 text-teal-200",
  "Market Intelligence": "from-violet-500/20 to-purple-500/20 border-violet-400/30 text-violet-200",
  Analytics: "from-emerald-500/20 to-green-500/20 border-emerald-400/30 text-emerald-200",
  "Project Deep Dive": "from-blue-500/20 to-indigo-500/20 border-blue-400/30 text-blue-200",
};

export function Sidebar({ onSelectQuestion, isLoading }: SidebarProps) {
  const [summary, setSummary] = useState<DataSummary | null>(null);
  const [questions, setQuestions] = useState<SuggestedQuestionsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  useEffect(() => {
    Promise.all([getDataSummary(), getSuggestedQuestions()])
      .then(([s, q]) => {
        setSummary(s);
        setQuestions(q);
        if (q) setExpanded({ [Object.keys(q.categories)[0]]: true });
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const toggle = (cat: string) => setExpanded((p) => ({ ...p, [cat]: !p[cat] }));

  const getCatStyle = (cat: string) => categoryColors[cat] || "from-slate-500/20 to-slate-600/20 border-slate-400/30 text-slate-200";

  return (
    <aside className="w-[300px] sm:w-[320px] shrink-0 flex flex-col bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 border-r border-slate-600/40 overflow-hidden shadow-xl shadow-black/20">
      <header className="p-5 border-b border-slate-600/40 bg-gradient-to-r from-teal-600/20 to-cyan-600/10">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-teal-400 via-cyan-500 to-teal-600 shadow-lg shadow-cyan-500/40 ring-2 ring-cyan-400/30">
            <svg className="h-6 w-6 text-white drop-shadow-sm" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
            </svg>
          </div>
          <div>
            <h1 className="text-lg font-bold text-white drop-shadow-sm">Verra AI</h1>
            <p className="text-xs text-cyan-200/90">Carbon Credit Analysis</p>
          </div>
        </div>
      </header>

      {loading ? (
        <div className="p-5 space-y-4 flex-1">
          <div className="h-20 bg-gradient-to-r from-slate-700/50 to-slate-600/30 rounded-xl animate-pulse-soft" />
          <div className="h-20 bg-gradient-to-r from-slate-700/50 to-slate-600/30 rounded-xl animate-pulse-soft" />
          <div className="h-24 bg-gradient-to-r from-slate-700/50 to-slate-600/30 rounded-xl animate-pulse-soft" />
        </div>
      ) : summary ? (
        <div className="p-4 flex-1 overflow-y-auto space-y-5">
          {/* Metrics - colorful cards */}
          <div className="grid grid-cols-2 gap-2">
            <div className="rounded-xl bg-gradient-to-br from-teal-500/25 to-cyan-600/15 p-4 border border-teal-400/30 hover:from-teal-500/30 hover:to-cyan-600/25 transition-all shadow-lg shadow-teal-500/10">
              <p className="text-[10px] uppercase tracking-widest text-teal-300/90 font-semibold mb-1">Projects</p>
              <p className="text-2xl font-bold text-white tabular-nums drop-shadow-sm">{summary.total_projects.toLocaleString()}</p>
            </div>
            <div className="rounded-xl bg-gradient-to-br from-violet-500/25 to-purple-600/15 p-4 border border-violet-400/30 hover:from-violet-500/30 hover:to-purple-600/25 transition-all shadow-lg shadow-violet-500/10">
              <p className="text-[10px] uppercase tracking-widest text-violet-300/90 font-semibold mb-1">Countries</p>
              <p className="text-2xl font-bold text-white tabular-nums drop-shadow-sm">{summary.total_countries}</p>
            </div>
          </div>

          <div className="rounded-xl bg-gradient-to-br from-amber-500/25 to-orange-600/15 p-4 border border-amber-400/30 shadow-lg shadow-amber-500/10">
            <p className="text-[10px] uppercase tracking-widest text-amber-300/90 font-semibold mb-1">Credits Issued</p>
            <p className="text-xl font-bold text-white tabular-nums drop-shadow-sm">{(summary.total_credits_issued / 1_000_000).toFixed(1)}M</p>
          </div>

          {/* Quadrants - vibrant pills */}
          <div>
            <p className="text-[10px] uppercase tracking-widest text-slate-400 font-semibold mb-2">Quadrants</p>
            <div className="flex flex-wrap gap-2">
              {Object.entries(summary.quadrant_distribution).map(([q, c]) => (
                <span
                  key={q}
                  className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold ${quadrantStyles[q] || "bg-slate-600/50 text-slate-300"}`}
                >
                  <span className="w-2 h-2 rounded-full bg-white/80" />
                  {q} · {c}
                </span>
              ))}
            </div>
          </div>

          {/* Suggested - colorful category chips */}
          <div className="pt-1">
            <p className="text-[10px] uppercase tracking-widest text-slate-400 font-semibold mb-3">Suggested Questions</p>
            {questions && (
              <div className="space-y-2">
                {Object.entries(questions.categories).map(([cat, qs]) => (
                  <div key={cat} className="rounded-xl overflow-hidden">
                    <button
                      onClick={() => toggle(cat)}
                      className={`w-full flex items-center justify-between px-4 py-3 text-left text-sm font-semibold rounded-xl bg-gradient-to-r ${getCatStyle(cat)} border transition-all hover:brightness-110 ${expanded[cat] ? "rounded-b-none" : ""}`}
                    >
                      {cat}
                      <svg className={`h-4 w-4 transition-transform duration-200 ${expanded[cat] ? "rotate-180" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    {expanded[cat] && (
                      <div className="space-y-1 pt-1 pb-2 px-2 bg-slate-800/40 rounded-b-xl border border-t-0 border-slate-600/40">
                        {qs.map((q, i) => (
                          <button
                            key={i}
                            onClick={() => onSelectQuestion(q)}
                            disabled={isLoading}
                            className="w-full text-left px-4 py-2.5 text-[13px] text-slate-300 bg-slate-700/40 hover:bg-teal-500/30 hover:text-teal-100 rounded-lg transition-all disabled:opacity-50 border border-transparent hover:border-teal-400/30"
                          >
                            {q}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      ) : null}
    </aside>
  );
}
