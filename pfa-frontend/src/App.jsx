import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import "./App.css";
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Meetings from "./pages/Meetings";
import CalendarPage from "./pages/CalendarPage";
import Settings from "./pages/Settings";
import NouvelleReunion from "./pages/Information_reunions.jsx";
import TranscriptionResume from "./pages/TranscriptionResume";

const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem("access_token");
  return token ? children : <Navigate to="/login" />;
};

function AppLayout({ children }) {
  return (
    <div className="app-container">
      <Sidebar />
      <div className="main-content">
        <Topbar />
        <div className="page-content">
          {children}
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<Login />} />
      
      
      <Route path="/dashboard" element={
        <PrivateRoute>
          <AppLayout>
            <Dashboard />
          </AppLayout>
        </PrivateRoute>
      } />
      
      <Route path="/meetings" element={
        <PrivateRoute>
          <AppLayout>
            <Meetings />
          </AppLayout>
        </PrivateRoute>
      } />
      
      <Route path="/calendar" element={
        <PrivateRoute>
          <AppLayout>
            <CalendarPage />
          </AppLayout>
        </PrivateRoute>
      } />
      
      <Route path="/settings" element={
        <PrivateRoute>
          <AppLayout>
            <Settings />
          </AppLayout>
        </PrivateRoute>
      } />
      
      <Route path="*" element={<Navigate to="/" replace />} />
      <Route path="/nouvelle-reunion" element={<NouvelleReunion />} />
      <Route path="/transcription" element={<TranscriptionResume />} />
    </Routes>
  );
}
