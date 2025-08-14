import React from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Topbar() {
  const navigate = useNavigate();

  return (
    <header className="topbar">
      <div className="topbar-left">
        <button className="menu-button">☰</button>
        <h1 className="topbar-title">BIENVENUE</h1>
      </div>

      <div className="topbar-right">
        <button
          onClick={() => navigate("/nouvelle-reunion")}
          className="new-meeting-button"
        >
          Nouvelle Réunion
        </button>
        <Link to="/settings" className="profile-link">Profil</Link>
      </div>
    </header>
  );
}