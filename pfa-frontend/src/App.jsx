import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import "./App.css"; // Assuming you have some global styles
import "./index.css"; // Tailwind CSS styles
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Meetings from "./pages/Meetings";
import CalendarPage from "./pages/CalendarPage";
import Settings from "./pages/Settings";

function AppLayout({ children }) {
  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1 min-h-screen">
        <Topbar />
        <main className="p-6 app-container">{children}</main>
      </div>
    </div>
  );
}

export default function App() {
  // pour demo on ne gère pas l'auth réelle; redirect Login -> Dashboard
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/dashboard" element={<AppLayout><Dashboard /></AppLayout>} />
      <Route path="/meetings" element={<AppLayout><Meetings /></AppLayout>} />
      <Route path="/calendar" element={<AppLayout><CalendarPage /></AppLayout>} />
      <Route path="/settings" element={<AppLayout><Settings /></AppLayout>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
