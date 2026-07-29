import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Route as RouteIcon, User, Mail, Lock, Shield, ArrowRight, AlertCircle, Loader2 } from 'lucide-react';

export const RegisterPage = () => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('DISPATCHER');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await register(fullName, email, password, role);
      navigate('/login');
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-purple-600/20 rounded-full blur-3xl pointer-events-none"></div>

      <div className="glass-panel w-full max-w-md rounded-3xl p-8 shadow-2xl relative z-10 border border-slate-800">
        <div className="text-center mb-8">
          <div className="inline-flex p-3 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 text-white shadow-xl shadow-indigo-500/30 mb-4">
            <RouteIcon className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-bold text-slate-100 font-heading">Create RouteAI Account</h2>
          <p className="text-xs text-slate-400 mt-1">Join the Enterprise Logistics Fleet</p>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase mb-1.5">Full Name</label>
            <div className="relative">
              <User className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Sarah Connor"
                className="w-full bg-slate-900/60 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-indigo-500 transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase mb-1.5">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="sarah@routeai.io"
                className="w-full bg-slate-900/60 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-indigo-500 transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase mb-1.5">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Minimum 8 characters"
                className="w-full bg-slate-900/60 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-indigo-500 transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase mb-1.5">Enterprise Role</label>
            <div className="relative">
              <Shield className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full bg-slate-900/60 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-indigo-500 transition-colors"
              >
                <option value="DISPATCHER">DISPATCHER (Logistics Operations)</option>
                <option value="ADMIN">ADMIN (System Administrator)</option>
                <option value="DRIVER">DRIVER (Fleet Operations)</option>
                <option value="CUSTOMER">CUSTOMER (External Client)</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 hover:opacity-90 transition-opacity flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : (
              <>
                <span>Register Account</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        <p className="text-center text-xs text-slate-500 mt-6">
          Already registered?{' '}
          <Link to="/login" className="text-indigo-400 hover:underline font-semibold">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
};
