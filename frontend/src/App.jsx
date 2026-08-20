import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';

import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { UserDashboard } from './pages/UserDashboard';
import { AdminDashboard } from './pages/AdminDashboard';
import { ProductExplorer } from './pages/ProductExplorer';
import { ProductDetailPage } from './pages/ProductDetailPage';
import { EvidencePage } from './pages/EvidencePage';
import { ValidationPage } from './pages/ValidationPage';
import { ConfidencePage } from './pages/ConfidencePage';
import { ReviewQueuePage } from './pages/ReviewQueuePage';
import { DescriptionsPage } from './pages/DescriptionsPage';
import { FinalOutputsPage } from './pages/FinalOutputsPage';
import { ReportsPage } from './pages/ReportsPage';
import { PipelinePage } from './pages/PipelinePage';
import { EvaluationPage } from './pages/EvaluationPage';
import { UploadPage } from './pages/UploadPage';

// Protected App Layout Wrapper
const AppLayout = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-cyan-400 font-mono">
        Loading PRODEXA Session...
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Navbar />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar />
        <main className="flex-1 p-6 md:p-8 overflow-y-auto max-w-7xl mx-auto w-full">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

// Admin Protection Guard
const AdminGuard = () => {
  const { role } = useAuth();
  if (role !== 'ADMIN') {
    return <Navigate to="/user/dashboard" replace />;
  }
  return <Outlet />;
};

export function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* User Protected Routes */}
          <Route path="/user" element={<AppLayout />}>
            <Route path="dashboard" element={<UserDashboard />} />
            <Route path="products" element={<ProductExplorer />} />
            <Route path="products/:id" element={<ProductDetailPage />} />
            <Route path="evidence" element={<EvidencePage />} />
            <Route path="validation" element={<ValidationPage />} />
            <Route path="confidence" element={<ConfidencePage />} />
            <Route path="review" element={<ReviewQueuePage />} />
            <Route path="descriptions" element={<DescriptionsPage />} />
            <Route path="outputs" element={<FinalOutputsPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="pipeline" element={<PipelinePage />} />
            <Route path="evaluation" element={<EvaluationPage />} />
            <Route path="upload" element={<UploadPage />} />
          </Route>

          {/* Admin Protected Routes */}
          <Route path="/admin" element={<AppLayout />}>
            <Route element={<AdminGuard />}>
              <Route path="dashboard" element={<AdminDashboard />} />
              <Route path="system" element={<AdminDashboard />} />
              <Route path="users" element={<AdminDashboard />} />
              <Route path="audit" element={<AdminDashboard />} />
              <Route path="pipeline" element={<PipelinePage />} />
              <Route path="evaluation" element={<EvaluationPage />} />
            </Route>
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
