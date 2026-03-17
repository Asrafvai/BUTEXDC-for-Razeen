import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { Toaster } from './components/ui/sonner';
import { checkSetupStatus } from './lib/api';
import './App.css';

// Pages
import SetupPage from './pages/SetupPage';
import HomePage from './pages/HomePage';
import LeadershipPage from './pages/LeadershipPage';
import PreviousSuccessPage from './pages/PreviousSuccessPage';
import AnnouncementsPage from './pages/AnnouncementsPage';
import CoursesPage from './pages/CoursesPage';
import AlumniPage from './pages/AlumniPage';
import EventsPage from './pages/EventsPage';
import BeAMemberPage from './pages/BeAMemberPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import StudentDashboard from './pages/StudentDashboard';
import CourseDetailPage from './pages/CourseDetailPage';
import ModulePlayerPage from './pages/ModulePlayerPage';
import CoachPage from './pages/CoachPage';
import FlagshipEventPage from './pages/FlagshipEventPage';
import AdminDashboard from './pages/admin/AdminDashboard';

// Setup check wrapper
const SetupCheck = ({ children }) => {
  const [checking, setChecking] = useState(true);
  const [needsSetup, setNeedsSetup] = useState(false);

  useEffect(() => {
    checkSetup();
  }, []);

  const checkSetup = async () => {
    try {
      const response = await checkSetupStatus();
      setNeedsSetup(!response.data.is_setup_complete);
    } catch (error) {
      console.error('Failed to check setup:', error);
    } finally {
      setChecking(false);
    }
  };

  if (checking) {
    return (
      <div className="min-h-screen bg-[#1A1A1A] flex items-center justify-center">
        <div className="text-[#FF7F00]">Loading...</div>
      </div>
    );
  }

  if (needsSetup) {
    return <Navigate to="/setup" replace />;
  }

  return children;
};

// Protected route for authenticated users
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-[#1A1A1A] flex items-center justify-center">
        <div className="text-[#FF7F00]">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

// Admin route
const AdminRoute = ({ children }) => {
  const { user, loading, isAdmin } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-[#1A1A1A] flex items-center justify-center">
        <div className="text-[#FF7F00]">Loading...</div>
      </div>
    );
  }

  if (!user || !isAdmin) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Setup */}
            <Route path="/setup" element={<SetupPage />} />

            {/* Public routes */}
            <Route path="/" element={<SetupCheck><HomePage /></SetupCheck>} />
            <Route path="/alumni" element={<SetupCheck><AlumniPage /></SetupCheck>} />
            <Route path="/events" element={<SetupCheck><EventsPage /></SetupCheck>} />
            <Route path="/be-a-member" element={<SetupCheck><BeAMemberPage /></SetupCheck>} />
            <Route path="/leadership" element={<SetupCheck><LeadershipPage /></SetupCheck>} />
            <Route path="/success" element={<SetupCheck><PreviousSuccessPage /></SetupCheck>} />
            <Route path="/announcements" element={<SetupCheck><AnnouncementsPage /></SetupCheck>} />
            <Route path="/courses" element={<SetupCheck><CoursesPage /></SetupCheck>} />
            <Route path="/course/:courseId" element={<SetupCheck><CourseDetailPage /></SetupCheck>} />
            <Route path="/coach" element={<SetupCheck><CoachPage /></SetupCheck>} />
            <Route path="/flagship/:eventId" element={<SetupCheck><FlagshipEventPage /></SetupCheck>} />

            {/* Auth routes */}
            <Route path="/login" element={<SetupCheck><LoginPage /></SetupCheck>} />
            <Route path="/signup" element={<SetupCheck><SignupPage /></SetupCheck>} />

            {/* Protected student routes */}
            <Route path="/dashboard" element={<ProtectedRoute><StudentDashboard /></ProtectedRoute>} />
            <Route path="/course/:courseId/module/:moduleId" element={<ProtectedRoute><ModulePlayerPage /></ProtectedRoute>} />

            {/* Protected admin routes */}
            <Route path="/admin/*" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
          </Routes>
          <Toaster position="top-right" />
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
