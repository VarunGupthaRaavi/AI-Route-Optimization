import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('routeai_user');
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem('routeai_access_token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          const res = await api.get('/auth/me');
          if (res.data) {
            setUser(res.data);
            localStorage.setItem('routeai_user', JSON.stringify(res.data));
          }
        } catch (err) {
          logout();
        }
      }
      setLoading(false);
    };
    initAuth();
  }, [token]);

  const login = async (email, password) => {
    const res = await api.post('/auth/login', { email, password });
    const { access_token, user: userProfile } = res.data;
    setToken(access_token);
    setUser(userProfile);
    localStorage.setItem('routeai_access_token', access_token);
    localStorage.setItem('routeai_user', JSON.stringify(userProfile));
    return userProfile;
  };

  const register = async (name, email, password, role) => {
    const res = await api.post('/auth/register', {
      full_name: name,
      email,
      password,
      role: role || 'CUSTOMER'
    });
    return res.data;
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('routeai_access_token');
    localStorage.removeItem('routeai_user');
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
