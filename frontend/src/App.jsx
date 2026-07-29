import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { AIChatCopilot } from './components/AIChatCopilot';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';
import { AIRouteOptimizerPage } from './pages/AIRouteOptimizerPage';
import { KnowledgeBaseRAGPage } from './pages/KnowledgeBaseRAGPage';
import { CustomersPage } from './pages/CustomersPage';
import { DriversPage } from './pages/DriversPage';
import { VehiclesPage } from './pages/VehiclesPage';
import { DeliveriesPage } from './pages/DeliveriesPage';
import { RoutesPage } from './pages/RoutesPage';
import { NotificationsPage } from './pages/NotificationsPage';
import { AnalyticsPage } from './pages/AnalyticsPage';

export function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Public Auth Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected Application Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/ai-studio" element={<AIRouteOptimizerPage />} />
            <Route path="/rag-console" element={<KnowledgeBaseRAGPage />} />
            <Route path="/customers" element={<CustomersPage />} />
            <Route path="/drivers" element={<DriversPage />} />
            <Route path="/vehicles" element={<VehiclesPage />} />
            <Route path="/deliveries" element={<DeliveriesPage />} />
            <Route path="/routes" element={<RoutesPage />} />
            <Route path="/notifications" element={<NotificationsPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
          </Route>

          {/* Fallback Redirect */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>

        {/* Global AI Copilot Assistant Widget */}
        <AIChatCopilot />
      </AuthProvider>
    </Router>
  );
}

export default App;
