import React from 'react';
import { Bell, Shield, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Header = ({ title, subtitle }) => {
  const { user } = useAuth();

  return (
    <header className="py-6 px-8 border-b border-slate-800/80 flex items-center justify-between bg-slate-950/40 backdrop-blur-md sticky top-0 z-20">
      <div>
        <h2 className="text-2xl font-bold text-slate-100 font-heading tracking-tight">{title}</h2>
        {subtitle && <p className="text-xs text-slate-400 mt-1">{subtitle}</p>}
      </div>

      <div className="flex items-center space-x-4">
        <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Supabase DB Connected</span>
        </div>

        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-medium">
          <Shield className="w-3.5 h-3.5" />
          <span>{user?.role || 'CUSTOMER'}</span>
        </div>
      </div>
    </header>
  );
};
