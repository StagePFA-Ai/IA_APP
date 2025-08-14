import React from "react";

export default function MeetingCard({ meeting, onUpload, onProcess, onView }) {
  return (
    <div className="meeting-card">
      <div className="meeting-content">
        <div className="meeting-title">{meeting.title || "Réunion sans titre"}</div>
        <div className="meeting-status">Status: {meeting.status || "pending"}</div>
        {meeting.summary && <div className="meeting-summary">Résumé: {meeting.summary}</div>}
      </div>

      <div className="meeting-actions">
        <input 
          type="file" 
          accept="audio/*" 
          onChange={e => onUpload(meeting.id, e.target.files[0])} 
          className="file-input" 
        />
        <div className="button-group">
          <button 
            onClick={() => onProcess(meeting.id)} 
            className="meeting-button process-button"
          >
            Traiter
          </button>
          <button 
            onClick={() => onView(meeting.id)} 
            className="meeting-button view-button"
          >
            Voir
          </button>
        </div>
      </div>
    </div>
  );
}
