import React, { useState, useEffect } from 'react';
import { Header } from '../components/Header';
import { StatusBadge } from '../components/StatusBadge';
import { api } from '../services/api';
import { Bot, Sparkles, Users, Navigation, ShieldAlert, Cpu, CheckCircle2, Loader2, ArrowRight } from 'lucide-react';

export const AIRouteOptimizerPage = () => {
  const [pendingDeliveries, setPendingDeliveries] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [maxHours, setMaxHours] = useState(8.0);
  const [loading, setLoading] = useState(false);
  const [planResult, setPlanResult] = useState(null);

  useEffect(() => {
    const fetchPending = async () => {
      try {
        const res = await api.get('/deliveries?status=PENDING');
        const items = res.data.items || [];
        setPendingDeliveries(items);
        if (items.length > 0) {
          setSelectedIds(items.map(i => i.id));
        }
      } catch (err) {
        console.error('Error fetching pending deliveries', err);
      }
    };
    fetchPending();
  }, []);

  const handleRunMultiAgent = async (e) => {
    e.preventDefault();
    if (selectedIds.length === 0) {
      alert('Please select at least 1 pending delivery order.');
      return;
    }
    setLoading(true);
    try {
      const res = await api.post('/ai/agents/plan', {
        delivery_ids: selectedIds,
        max_driving_hours: parseFloat(maxHours)
      });
      setPlanResult(res.data);
    } catch (err) {
      alert(err.message || 'Multi-Agent planning failed');
    } finally {
      setLoading(false);
    }
  };

  const toggleSelect = (id) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter(item => item !== id));
    } else {
      setSelectedIds([...selectedIds, id]);
    }
  };

  return (
    <div className="flex-1 pb-12">
      <Header
        title="Multi-Agent Route Planning Studio"
        subtitle="Orchestrate Dispatcher, Traffic/Weather, and Fleet Allocator AI agents powered by Google Gemini"
      />

      <div className="p-8 max-w-7xl mx-auto space-y-8">
        {/* Agent Suite Header Banner */}
        <div className="glass-card rounded-3xl p-8 border border-indigo-500/30 bg-gradient-to-r from-indigo-950/70 via-purple-950/40 to-slate-950">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
            <div>
              <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-semibold mb-3 border border-indigo-500/30">
                <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                <span>3-Agent Orchestration Pipeline Active</span>
              </div>
              <h3 className="text-2xl font-bold text-slate-100 font-heading">
                Multi-Agent Autonomous Route Optimizer
              </h3>
              <p className="text-sm text-slate-400 mt-1 max-w-2xl">
                Collaborative AI agents sequentially evaluate priority SLAs, real-time traffic corridor congestion, and driver shift constraints to build optimal route plans.
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Controls Column */}
          <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-6">
            <h4 className="text-base font-bold text-slate-100 font-heading flex items-center justify-between">
              <span>Optimization Inputs</span>
              <Cpu className="w-4 h-4 text-indigo-400" />
            </h4>

            <form onSubmit={handleRunMultiAgent} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">
                  Select Target Orders ({selectedIds.length}/{pendingDeliveries.length})
                </label>
                <div className="max-h-60 overflow-y-auto space-y-2 pr-1">
                  {pendingDeliveries.length === 0 ? (
                    <p className="text-xs text-slate-500 py-6 text-center">No pending orders available.</p>
                  ) : (
                    pendingDeliveries.map((del) => (
                      <label key={del.id} className="flex items-center justify-between p-3 rounded-xl bg-slate-900/60 border border-slate-800 cursor-pointer hover:border-indigo-500/40">
                        <div className="flex items-center space-x-2.5">
                          <input
                            type="checkbox"
                            checked={selectedIds.includes(del.id)}
                            onChange={() => toggleSelect(del.id)}
                            className="rounded border-slate-700 bg-slate-950 text-indigo-600 focus:ring-indigo-500"
                          />
                          <div>
                            <div className="text-xs font-mono font-bold text-indigo-400">{del.tracking_number}</div>
                            <div className="text-[11px] text-slate-400 truncate max-w-[140px]">{del.delivery_address}</div>
                          </div>
                        </div>
                        <StatusBadge status={del.priority} />
                      </label>
                    ))
                  )}
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Max Shift Hours</label>
                <input
                  type="number"
                  step="0.5"
                  value={maxHours}
                  onChange={(e) => setMaxHours(e.target.value)}
                  className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <button
                type="submit"
                disabled={loading || selectedIds.length === 0}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 flex items-center justify-center space-x-2 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Executing Multi-Agent Pipeline...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-amber-300" />
                    <span>Launch 3-Agent Optimization</span>
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Results Column */}
          <div className="lg:col-span-2 space-y-6">
            {!planResult ? (
              <div className="glass-card rounded-2xl p-12 text-center text-slate-500 border border-slate-800">
                <Bot className="w-12 h-12 mx-auto mb-3 text-slate-600" />
                <p className="text-sm font-semibold text-slate-300">Multi-Agent Engine Standby</p>
                <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
                  Select pending package orders and click "Launch 3-Agent Optimization" to trigger collaborative AI reasoning.
                </p>
              </div>
            ) : (
              <div className="space-y-6 animate-fadeIn">
                {/* Metrics Header */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="glass-card rounded-2xl p-4 border border-slate-800 text-center">
                    <p className="text-[10px] text-slate-400 font-semibold uppercase">Total Travel Distance</p>
                    <p className="text-2xl font-bold text-slate-100 font-heading mt-1">{planResult.total_estimated_distance_km} km</p>
                  </div>
                  <div className="glass-card rounded-2xl p-4 border border-slate-800 text-center">
                    <p className="text-[10px] text-slate-400 font-semibold uppercase">Estimated Duration</p>
                    <p className="text-2xl font-bold text-slate-100 font-heading mt-1">{planResult.total_estimated_duration_minutes} mins</p>
                  </div>
                  <div className="glass-card rounded-2xl p-4 border border-slate-800 text-center">
                    <p className="text-[10px] text-slate-400 font-semibold uppercase">Route Efficiency Score</p>
                    <p className="text-2xl font-bold text-emerald-400 font-heading mt-1">{planResult.efficiency_score_pct}%</p>
                  </div>
                </div>

                {/* Agent Insights Cards */}
                <div className="space-y-4">
                  <h4 className="text-sm font-bold text-slate-100 font-heading">Collaborative Agent Insights</h4>
                  {planResult.agent_insights.map((agent, idx) => (
                    <div key={idx} className="glass-card rounded-2xl p-5 border border-slate-800 space-y-3">
                      <div className="flex items-center space-x-2">
                        <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse"></span>
                        <h5 className="text-xs font-bold text-indigo-300 uppercase tracking-wider">{agent.agent_name}</h5>
                      </div>
                      <p className="text-xs text-slate-300">{agent.summary}</p>
                      <ul className="space-y-1 pl-4 list-disc text-[11px] text-slate-400">
                        {agent.decisions.map((d, dIdx) => (
                          <li key={dIdx}>{d}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
