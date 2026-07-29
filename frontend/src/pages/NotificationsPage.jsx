import React, { useState, useEffect } from 'react';
import { Header } from '../components/Header';
import { StatusBadge } from '../components/StatusBadge';
import { api } from '../services/api';
import { Bell, CheckCheck, AlertTriangle, Info, CheckCircle2 } from 'lucide-react';

export const NotificationsPage = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const res = await api.get('/notifications');
      setNotifications(res.data || []);
    } catch (err) {
      console.error('Error fetching notifications', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  const handleMarkRead = async (id) => {
    try {
      await api.put(`/notifications/${id}/read`);
      fetchNotifications();
    } catch (err) {
      console.error('Error marking notification read', err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await api.put('/notifications/read-all');
      fetchNotifications();
    } catch (err) {
      console.error('Error marking all notifications read', err);
    }
  };

  return (
    <div className="flex-1 pb-12">
      <Header
        title="Notification Feed & System Alerts"
        subtitle="Real-time alerts, fleet updates, dispatch status warnings, and operational notifications"
      />

      <div className="p-8 max-w-4xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-slate-100 font-heading">Active Alerts</h3>
          <button
            onClick={handleMarkAllRead}
            className="px-3.5 py-1.5 rounded-xl bg-slate-800 text-indigo-400 hover:text-indigo-300 text-xs font-semibold flex items-center space-x-1.5 transition-colors border border-slate-700/60"
          >
            <CheckCheck className="w-4 h-4" />
            <span>Mark All as Read</span>
          </button>
        </div>

        <div className="space-y-3">
          {loading ? (
            <p className="text-center py-12 text-xs text-slate-500">Loading notifications...</p>
          ) : notifications.length === 0 ? (
            <div className="glass-card rounded-2xl p-12 text-center text-slate-500 text-xs border border-slate-800">
              <Bell className="w-8 h-8 mx-auto mb-2 text-slate-600" />
              <span>No notifications in feed. System running nominally.</span>
            </div>
          ) : (
            notifications.map((n) => (
              <div
                key={n.id}
                className={`glass-card rounded-2xl p-5 border transition-all flex items-start justify-between gap-4 ${
                  n.is_read ? 'border-slate-800/60 opacity-75' : 'border-indigo-500/30 bg-indigo-950/20'
                }`}
              >
                <div className="flex items-start space-x-3.5">
                  <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 mt-0.5">
                    {n.type === 'WARNING' || n.type === 'ALERT' ? <AlertTriangle className="w-5 h-5 text-amber-400" /> : <Info className="w-5 h-5 text-indigo-400" />}
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-100">{n.title}</h4>
                    <p className="text-xs text-slate-400 mt-1">{n.message}</p>
                    <span className="text-[10px] text-slate-500 mt-2 block">
                      {new Date(n.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>

                {!n.is_read && (
                  <button
                    onClick={() => handleMarkRead(n.id)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-indigo-400 hover:bg-slate-800 transition-colors"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
