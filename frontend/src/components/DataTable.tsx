"use client";

interface DataTableProps {
  data: Record<string, any>[];
  maxRows?: number;
}

export function DataTable({ data, maxRows = 10 }: DataTableProps) {
  if (!data?.length) {
    return (
      <div className="p-6 text-center text-slate-500 text-sm rounded-xl bg-slate-50/80 border border-slate-100">
        No data to display
      </div>
    );
  }

  const columns = Object.keys(data[0]);
  const rows = data.slice(0, maxRows);

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200/80 bg-white shadow-sm">
      <div className="overflow-x-auto">
        <table className="w-full text-sm min-w-[320px]">
          <thead>
            <tr className="bg-slate-50/80 border-b border-slate-200/80">
              {columns.map((col) => (
                <th key={col} className="px-4 py-3 text-left font-medium text-slate-600">
                  {col.replace(/_/g, " ")}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {rows.map((row, idx) => (
              <tr key={idx} className="hover:bg-slate-50/60 transition-colors">
                {columns.map((col) => (
                  <td key={col} className="px-4 py-3 text-slate-600">
                    {formatValue(row[col])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {data.length > maxRows && (
        <div className="px-4 py-2.5 text-xs text-slate-500 bg-slate-50/60 border-t border-slate-100">
          Showing {maxRows} of {data.length} rows
        </div>
      )}
    </div>
  );
}

function formatValue(val: unknown): string {
  if (val === null || val === undefined) return "—";
  if (typeof val === "number") {
    if (val % 1 === 0) return val.toLocaleString();
    return val.toFixed(2);
  }
  return String(val);
}
