import React from "react";

export default function Settings(){
  return (
    <div className="settings-container">
      <h3 className="settings-title">Paramètres</h3>
      <div className="settings-options">
        <div className="option-group">
          <label className="option-label">Enregistrement automatique</label>
          <button className="option-button">Activer</button>
        </div>
        <div className="option-group">
          <label className="option-label">Modèle de transcription</label>
          <select className="option-select">
            <option>faster-whisper (local)</option>
            <option>whisper (local)</option>
          </select>
        </div>
        <div className="option-group">
          <label className="option-label">Options résumé</label>
          <select className="option-select">
            <option>mT5 (extractif)</option>
            <option>LLM local (abstractive)</option>
          </select>
        </div>
      </div>
    </div>
  );
}
