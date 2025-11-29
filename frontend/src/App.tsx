import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { DashboardLayout } from './routes/DashboardLayout';
import { OverviewPage } from './routes/OverviewPage';
import { PredictivePage } from './routes/PredictivePage';
import { LandingPage } from './routes/LandingPage';
import LoginPage from './pages/LoginPage';
import { AuthProvider } from './context/AuthContext';
import './App.css';

import { useAuth } from './context/AuthContext';

const RequireAuth = ({ children }: { children: JSX.Element }) => {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-blue-500">
        Loading...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

const RoleGuard = ({ children, roles }: { children: JSX.Element, roles: string[] }) => {
  const { user, isLoading } = useAuth();

  if (isLoading) return null;

  if (!user || !roles.includes(user.role)) {
    // Redirect to their allowed dashboard if they try to access unauthorized route
    if (user?.role === 'RECEPTION') return <Navigate to="/dashboard/reception" replace />;
    if (user?.role === 'PHARMACIST') return <Navigate to="/dashboard/pharmacy" replace />;
    return <Navigate to="/dashboard/overview" replace />;
  }

  return children;
};

import UserManagement from './pages/UserManagement';
import NotificationSettings from './pages/NotificationSettings';
import PharmacyView from './pages/PharmacyView';
import ReceptionView from './pages/ReceptionView';

// ... imports ...

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          {/* Landing Page */}
          <Route path="/" element={<LandingPage />} />

          {/* Dashboard Routes */}
          <Route path="/dashboard" element={
            <RequireAuth>
              <DashboardLayout />
            </RequireAuth>
          }>
            <Route index element={<Navigate to="/dashboard/overview" replace />} />
            <Route path="overview" element={<OverviewPage />} />
            <Route path="predictive" element={<PredictivePage />} />

            {/* Role Protected Routes */}
            <Route path="users" element={<RoleGuard roles={['SUPER_ADMIN']}><UserManagement /></RoleGuard>} />
            <Route path="notifications" element={<RoleGuard roles={['SUPER_ADMIN']}><NotificationSettings /></RoleGuard>} />
            <Route path="pharmacy" element={<RoleGuard roles={['PHARMACIST', 'ADMIN', 'SUPER_ADMIN']}><PharmacyView /></RoleGuard>} />
            <Route path="reception" element={<RoleGuard roles={['RECEPTION', 'ADMIN', 'SUPER_ADMIN']}><ReceptionView /></RoleGuard>} />

            {/* Admin Dashboard Route Mapping */}
            <Route path="super-admin" element={<Navigate to="/dashboard/users" replace />} />
            <Route path="admin" element={<Navigate to="/dashboard/overview" replace />} />
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
