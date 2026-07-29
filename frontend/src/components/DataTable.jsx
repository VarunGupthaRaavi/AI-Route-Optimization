import React from 'react';
import { Search, ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';

export const DataTable = ({
  columns,
  data,
  loading,
  searchQuery,
  onSearchChange,
  page,
  totalPages,
  onPageChange,
  totalItems,
  actionButton
}) => {
  return (
    <div className="glass-card rounded-2xl border border-slate-800/80 overflow-hidden">
      {/* Table Header Controls */}
      <div className="p-5 border-b border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-900/40">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search records..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full bg-slate-950/60 border border-slate-800 rounded-xl pl-10 pr-4 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors"
          />
        </div>
        {actionButton && <div>{actionButton}</div>}
      </div>

      {/* Table Body */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-sm">
          <thead>
            <tr className="border-b border-slate-800/80 bg-slate-950/40 text-slate-400 font-medium text-xs tracking-wider uppercase">
              {columns.map((col, idx) => (
                <th key={idx} className="py-3.5 px-6">{col.header}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {loading ? (
              <tr>
                <td colSpan={columns.length} className="py-12 text-center text-slate-500">
                  <div className="flex items-center justify-center space-x-2">
                    <Loader2 className="w-5 h-5 animate-spin text-indigo-400" />
                    <span>Loading logistics data...</span>
                  </div>
                </td>
              </tr>
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="py-12 text-center text-slate-500">
                  No matching records found.
                </td>
              </tr>
            ) : (
              data.map((row, rowIdx) => (
                <tr key={rowIdx} className="hover:bg-slate-800/40 transition-colors">
                  {columns.map((col, colIdx) => (
                    <td key={colIdx} className="py-4 px-6">
                      {col.render ? col.render(row) : row[col.accessor]}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Table Pagination */}
      <div className="p-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400 bg-slate-900/30">
        <div>
          Showing page <span className="font-semibold text-slate-200">{page}</span> of <span className="font-semibold text-slate-200">{totalPages || 1}</span> ({totalItems || 0} items total)
        </div>
        <div className="flex items-center space-x-2">
          <button
            disabled={page <= 1 || loading}
            onClick={() => onPageChange(page - 1)}
            className="p-2 rounded-lg bg-slate-800/60 text-slate-300 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button
            disabled={page >= totalPages || loading}
            onClick={() => onPageChange(page + 1)}
            className="p-2 rounded-lg bg-slate-800/60 text-slate-300 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
