import React from 'react';

export const StatsCard = ({ title, value, subtext, icon: Icon, trend, color = 'indigo' }) => {
  const colorMap = {
    indigo: 'from-indigo-500/20 to-purple-500/10 text-indigo-400 border-indigo-500/30',
    emerald: 'from-emerald-500/20 to-teal-500/10 text-emerald-400 border-emerald-500/30',
    amber: 'from-amber-500/20 to-orange-500/10 text-amber-400 border-amber-500/30',
    cyan: 'from-cyan-500/20 to-blue-500/10 text-cyan-400 border-cyan-500/30',
    rose: 'from-rose-500/20 to-pink-500/10 text-rose-400 border-rose-500/30',
  };

  const selectedColor = colorMap[color] || colorMap.indigo;

  return (
    <div className="glass-card rounded-2xl p-6 relative overflow-hidden transition-all duration-300 hover:translate-y-[-2px] hover:border-slate-700/60">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold text-slate-400 tracking-wider uppercase">{title}</p>
          <h3 className="text-3xl font-bold text-slate-100 font-heading mt-2">{value}</h3>
          {subtext && <p className="text-xs text-slate-400 mt-1">{subtext}</p>}
        </div>
        {Icon && (
          <div className={`p-3.5 rounded-xl bg-gradient-to-br border ${selectedColor}`}>
            <Icon className="w-6 h-6" />
          </div>
        )}
      </div>
      {trend && (
        <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center text-xs">
          <span className={trend.isPositive ? 'text-emerald-400 font-medium' : 'text-rose-400 font-medium'}>
            {trend.isPositive ? '+' : ''}{trend.value}
          </span>
          <span className="text-slate-500 ml-2">{trend.label}</span>
        </div>
      )}
    </div>
  );
};
