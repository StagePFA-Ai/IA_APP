import React from "react";
import { Link } from "react-router-dom";

export default function Topbar({ onNewMeeting }) {
  return (
    <header className="bg-white border-b p-4 flex justify-between items-center">
      <div className="flex items-center gap-4">
        <button className="md:hidden" onClick={()=>{}}>
          ☰
        </button>
        <h1 className="text-lg font-semibold">Tableau de Bord</h1>
      </div>

      <div className="flex items-center gap-3">
        <button onClick={onNewMeeting} className="bg-blue-600 text-white px-3 py-1 rounded">Nouvelle Réunion</button>
        <Link to="/settings" className="text-sm text-gray-600">Profil</Link>
      </div>
    </header>
  );
}
