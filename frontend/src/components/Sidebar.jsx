import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  Truck,
  UserCheck,
  Package,
  MapPin,
  Bell,
  BarChart3,
  Route as RouteIcon,
  LogOut
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Sidebar = () => {
  const { user, logout } = useAuth();

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Deliveries', path: '/deliveries', icon: Package },
    { name: 'Route Optimization', path: '/routes', icon: RouteIcon },
    { name: 'Customers', path: '/customers', icon: Users },
    { name: 'Fleet Drivers', path: '/drivers', icon: UserCheck },
    { name: 'Fleet Vehicles', path: '/vehicles', icon: Truck },
    { name: 'Notifications', path: '/notifications', icon: Bell },
    { name: 'Analytics', path: '/analytics', icon: BarChart3 },
  ];

  return (
    <aside className="w-64 glass-panel border-r border-slate-800/80 flex flex-col h-screen sticky top-0 z-30">
      {/* Brand Header */}
      <div className="p-6 border-b border-slate-800/80 flex items-center space-x-3">
        <div className="p-2.5 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/30">
          <RouteIcon className="w-6 h-6" />
        </div>
        <div>
          <h1 className="text-xl font-extrabold text-white tracking-tight font-heading">RouteAI</h1>
          <p className="text-[10px] text-indigo-400 font-semibold tracking-wider uppercase">Logistics Platform</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 group ${
                isActive
                  ? 'bg-gradient-to-r from-indigo-600/30 to-purple-600/20 text-indigo-300 border border-indigo-500/30 font-semibold shadow-inner'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`
            }
          >
            <item.icon className="w-5 h-5 mr-3 transition-transform group-hover:scale-110" />
            <span>{item.name}</span>
          </NavLink>
        ))}
      </nav>

      {/* User Footer Profile */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/40">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3 overflow-hidden">
            <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center font-bold text-white text-sm shadow-md">
              {user?.full_name?.charAt(0) || 'U'}
            </div>
            <div className="truncate">
              <p className="text-xs font-semibold text-slate-200 truncate">{user?.full_name || 'User'}</p>
              <p className="text-[10px] text-indigo-400 font-medium truncate uppercase">{user?.role || 'DRIVER'}</p>
            </div>
          </div>
          <button
            onClick={logout}
            title="Sign Out"
            className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
};
