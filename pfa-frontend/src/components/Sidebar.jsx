import React from "react";
import { NavLink } from "react-router-dom";


export default function Sidebar() {
  const linkClass = ({ isActive }) =>
    isActive ? "sidebar-link active" : "sidebar-link";

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-title">MeetingAI</div>
        <div className="sidebar-subtitle">Résumés intelligents</div>
      </div>
      <nav className="sidebar-nav sidebar-nav-space-y-1">
        <NavLink to="/dashboard" className={linkClass}>Tableau de bord</NavLink>
        <NavLink to="/meetings" className={linkClass}>Réunions</NavLink>
        <NavLink to="/calendar" className={linkClass}>Calendrier</NavLink>
        <NavLink to="/settings" className={linkClass}>Paramètres</NavLink>
      </nav>
      <div className="sidebar-footer">© 2025 Local</div>
    </aside>
  );
}