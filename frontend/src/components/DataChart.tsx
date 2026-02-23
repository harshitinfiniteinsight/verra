"use client";

import dynamic from "next/dynamic";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

interface DataChartProps {
  data: unknown;
  layout?: Record<string, unknown>;
}

export function DataChart({ data, layout }: DataChartProps) {
  if (!data) {
    return (
      <div className="p-8 text-center text-slate-500 text-sm rounded-xl bg-slate-50/80 border border-slate-100">
        No chart data
      </div>
    );
  }

  return (
    <div className="w-full overflow-hidden rounded-xl border border-slate-200/80 bg-white shadow-sm p-4">
      <Plot
        data={data}
        layout={{
          ...layout,
          autosize: true,
          margin: { l: 56, r: 32, t: 32, b: 56 },
          plot_bgcolor: "rgba(248, 250, 252, 0.6)",
          paper_bgcolor: "rgba(255, 255, 255, 1)",
          font: { family: "Inter, system-ui, sans-serif", size: 11 },
          xaxis: {
            gridcolor: "rgba(226, 232, 240, 0.6)",
            zeroline: false,
            showline: true,
            linecolor: "#e2e8f0",
          },
          yaxis: {
            gridcolor: "rgba(226, 232, 240, 0.6)",
            zeroline: false,
            showline: true,
            linecolor: "#e2e8f0",
          },
          hoverlabel: {
            bgcolor: "#0f172a",
            font: { color: "#fff", size: 11 },
            bordercolor: "transparent",
          },
        }}
        style={{ width: "100%", height: "360px" }}
        config={{
          responsive: true,
          displayModeBar: true,
          displaylogo: false,
          modeBarButtonsToRemove: ["lasso2d", "select2d"],
        }}
      />
    </div>
  );
}
