import React, { useEffect, useState } from 'react';
import { Header } from '../components/Header';
import { StatsCard } from '../components/StatsCard';
import { StatusBadge } from '../components/StatusBadge';
import { api } from '../services/api';
import {
  Package,
  Truck,
  Users,
  Route as RouteIcon,
  CheckCircle2,
  AlertTriangle,
  Zap,
  TrendingUp,
  Clock
} from 'lucide-react';

export const DashboardPage = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const res = await api.get('/analytics/dashboard');
        setSummary(res.data);
      } catch (err) {
        console.error('Failed to load dashboard summary', err);
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, []);

  return (
    <div className="flex-1 pb-12">
      <Header
        title="Executive Logistics Dashboard"
        subtitle="Real-time AI fleet telemetry, route optimization metrics, and delivery status"
      />

      <div className="p-8 space-y-8 max-w-7xl mx-auto">
        {/* KPI Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="Total Deliveries"
            value={summary?.total_deliveries || 0}
            subtext={`${summary?.pending_deliveries || 0} pending optimization`}
            icon={Package}
            color="indigo"
            trend={{ value: '12%', label: 'vs last week', isPositive: true }}
          />
          <StatsCard
            title="Active Routes"
            value={summary?.active_routes || 0}
            subtext={`${summary?.completed_routes || 0} completed routes`}
            icon={RouteIcon}
            color="cyan"
            trend={{ value: '8.4%', label: 'vs target', isPositive: true }}
          />
          <StatsCard
            title="Fleet Vehicles"
            value={summary?.total_vehicles || 0}
            subtext={`${summary?.available_vehicles || 0} available for dispatch`}
            icon={Truck}
            color="emerald"
          />
          <StatsCard
            title="Success Rate"
            value={`${summary?.delivery_success_rate_pct || 100}%`}
            subtext={`${summary?.fleet_utilization_pct || 0}% fleet utilization`}
            icon={TrendingUp}
            color="amber"
            trend={{ value: '99.2%', label: 'on-time SLA', isPositive: true }}
          />
        </div>

        {/* AI Route Optimization Quick Action Banner */}
        <div className="glass-card rounded-3xl p-8 border border-indigo-500/30 relative overflow-hidden bg-gradient-to-r from-indigo-950/60 via-purple-950/40 to-slate-950">
          <div className="relative z-10 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
            <div>
              <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-semibold mb-3 border border-indigo-500/30">
                <Zap className="w-3.5 h-3.5 text-indigo-400" />
                <span>AI Nearest-Neighbor TSP Engine Active</span>
              </div>
              <h3 className="text-2xl font-bold text-slate-100 font-heading">
                Optimize Pending Fleet Routes
              </h3>
              <p className="text-sm text-slate-400 mt-1 max-w-2xl">
                Automatically calculate shortest multi-stop routes, minimize fuel consumption, and assign available drivers to delivery queues.
              </p>
            </div>
            <a
              href="/routes"
              className="px-6 py-3.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold text-sm shadow-xl shadow-indigo-600/30 hover:opacity-90 transition-opacity flex items-center space-x-2 whitespace-nowrap"
            >
              <span>Launch Route Optimizer</span>
              <RouteIcon className="w-4 h-4 ml-1" />
            </a>
          </div>
        </div>

        {/* Operational Status Breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Driver Fleet Status */}
          <div className="glass-card rounded-2xl p-6 border border-slate-800">
            <h4 className="text-base font-bold text-slate-100 font-heading mb-4 flex items-center justify-between">
              <span>Driver Fleet Telemetry</span>
              <Users className="w-4 h-4 text-slate-500" />
            </h4>

            <div className="space-y-4">
              <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="flex items-center space-x-3">
                  <StatusBadge status="ON_ROUTE" />
                  <span className="text-sm font-medium text-slate-300">Drivers Executing Routes</span>
                </div>
                <span className="text-lg font-bold text-slate-100 font-heading">{summary?.driver_status_counts?.ON_ROUTE || 0}</span>
              </div>

              <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="flex items-center space-x-3">
                  <StatusBadge status="IDLE" />
                  <span className="text-sm font-medium text-slate-300">Drivers Idle & Ready</span>
                </div>
                <span className="text-lg font-bold text-slate-100 font-heading">{summary?.driver_status_counts?.IDLE || 0}</span>
              </div>

              <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="flex items-center space-x-3">
                  <StatusBadge status="OFF_DUTY" />
                  <span className="text-sm font-medium text-slate-300">Drivers Off Duty</span>
                </div>
                <span className="text-lg font-bold text-slate-100 font-heading">{summary?.driver_status_counts?.OFF_DUTY || 0}</span>
              </div>
            </div>
          </div>

          {/* Delivery Priority Distribution */}
          <div className="glass-card rounded-2xl p-6 border border-slate-800">
            <h4 className="text-base font-bold text-slate-100 font-heading mb-4 flex items-center justify-between">
              <span>Delivery Priority Breakdown</span>
              <Clock className="w-4 h-4 text-slate-500" />
            </h4>

            <div className="space-y-4">
              <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="flex items-center space-x-3">
                  <StatusBadge status="URGENT" />
                  <span className="text-sm font-medium text-slate-300">Urgent Priority Orders</span>
                </div>
                <span className="text-lg font-bold text-slate-100 font-heading">{summary?.delivery_priority_counts?.URGENT || 0}</span>
              </div>

              <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="flex items-center space-x-3">
                  <StatusBadge status="HIGH" />
                  <span className="text-sm font-medium text-slate-300">High Priority Orders</span>
                </div>
                <span className="text-lg font-bold text-slate-100 font-heading">{summary?.delivery_priority_counts?.HIGH || 0}</span>
              </div>

              <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="flex items-center space-x-3">
                  <StatusBadge status="MEDIUM" />
                  <span className="text-sm font-medium text-slate-300">Standard Orders</span>
                </div>
                <span className="text-lg font-bold text-slate-100 font-heading">{summary?.delivery_priority_counts?.MEDIUM || 0}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
