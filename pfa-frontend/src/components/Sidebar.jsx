import React from "react";
import { NavLink } from "react-router-dom";

export default function Sidebar() {
  const linkClass = ({ isActive }) =>
    isActive ? "block p-3 rounded bg-blue-50 text-blue-700" : "block p-3 rounded hover:bg-gray-100";

  return (
    <aside className="w-64 bg-white border-r min-h-screen hidden md:block">
      <div className="p-4 border-b">
        <div className="font-bold">MeetingAI</div>
        <div className="text-sm text-gray-500">Résumés intelligents</div>
      </div>
      <nav className="p-4 space-y-1">
        <NavLink to="/dashboard" className={linkClass}>Tableau de bord</NavLink>
        <NavLink to="/meetings" className={linkClass}>Réunions</NavLink>
        <NavLink to="/calendar" className={linkClass}>Calendrier</NavLink>
        <NavLink to="/settings" className={linkClass}>Paramètres</NavLink>
      </nav>
      <div className="p-4 mt-auto text-xs text-gray-400">© 2025 Local</div>
    </aside>
  );
}
