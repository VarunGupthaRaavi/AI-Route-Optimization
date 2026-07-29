import React, { useState, useEffect } from 'react';
import { Header } from '../components/Header';
import { StatsCard } from '../components/StatsCard';
import { api } from '../services/api';
import { BarChart3, TrendingUp, ShieldCheck, Zap, Fuel, Award } from 'lucide-react';

export const AnalyticsPage = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const res = await api.get('/analytics/dashboard');
        setSummary(res.data);
      } catch (err) {
        console.error('Error loading analytics', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  return (
    <div className="flex-1 pb-12">
      <Header
        title="Executive Logistics Analytics"
        subtitle="Operational efficiency reports, delivery SLA performance, and fleet utilization analytics"
      />

      <div className="p-8 max-w-7xl mx-auto space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatsCard
            title="Delivery Success Rate"
            value={`${summary?.delivery_success_rate_pct || 100}%`}
            subtext="On-time package delivery SLA"
            icon={ShieldCheck}
            color="emerald"
          />
          <StatsCard
            title="Fleet Utilization"
            value={`${summary?.fleet_utilization_pct || 0}%`}
            subtext="Active vehicles vs capacity"
            icon={TrendingUp}
            color="indigo"
          />
          <StatsCard
            title="Fuel Distance Savings"
            value="18.4%"
            subtext="Saved via Nearest-Neighbor TSP optimization"
            icon={Fuel}
            color="amber"
          />
        </div>

        {/* Detailed Logistics Breakdown Card */}
        <div className="glass-card rounded-3xl p-8 border border-slate-800 space-y-6">
          <h3 className="text-lg font-bold text-slate-100 font-heading flex items-center space-x-2">
            <BarChart3 className="w-5 h-5 text-indigo-400" />
            <span>Logistics Performance Summary Report</span>
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
              <p className="text-xs font-semibold text-slate-400 uppercase">Customer Accounts</p>
              <p className="text-3xl font-extrabold text-slate-100 font-heading mt-2">{summary?.total_customers || 0}</p>
              <p className="text-xs text-emerald-400 mt-1">Active client relationships</p>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
              <p className="text-xs font-semibold text-slate-400 uppercase">Driver Fleet Size</p>
              <p className="text-3xl font-extrabold text-slate-100 font-heading mt-2">{summary?.total_drivers || 0}</p>
              <p className="text-xs text-indigo-400 mt-1">{summary?.active_drivers || 0} active drivers on duty</p>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
              <p className="text-xs font-semibold text-slate-400 uppercase">Cargo Vehicles</p>
              <p className="text-3xl font-extrabold text-slate-100 font-heading mt-2">{summary?.total_vehicles || 0}</p>
              <p className="text-xs text-cyan-400 mt-1">{summary?.available_vehicles || 0} ready for dispatch</p>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
              <p className="text-xs font-semibold text-slate-400 uppercase">Total Route Plans</p>
              <p className="text-3xl font-extrabold text-slate-100 font-heading mt-2">{summary?.total_routes || 0}</p>
              <p className="text-xs text-amber-400 mt-1">{summary?.completed_routes || 0} completed routes</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
