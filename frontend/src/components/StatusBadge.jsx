import React from 'react';

const statusStyles = {
  // Common Statuses
  AVAILABLE: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  IN_TRANSIT: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
  MAINTENANCE: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  
  IDLE: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
  ON_ROUTE: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  OFF_DUTY: 'bg-rose-500/10 text-rose-400 border-rose-500/20',

  PENDING: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  ASSIGNED: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  DELIVERED: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  FAILED: 'bg-rose-500/10 text-rose-400 border-rose-500/20',

  DRAFT: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
  OPTIMIZED: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
  IN_PROGRESS: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
  COMPLETED: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',

  LOW: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
  MEDIUM: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  HIGH: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  URGENT: 'bg-rose-500/10 text-rose-400 border-rose-500/20 font-bold animate-pulse',
};

export const StatusBadge = ({ status }) => {
  const style = statusStyles[status] || 'bg-slate-500/10 text-slate-400 border-slate-500/20';
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${style}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current mr-1.5"></span>
      {status}
    </span>
  );
};
