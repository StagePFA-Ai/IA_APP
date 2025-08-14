import React, { useState } from "react";
import { useNavigate } from "react-router-dom"; 


export default function NouvelleReunion() {
  const [titre, setTitre] = useState("");
  const [date, setDate] = useState("");
  const [participants, setParticipants] = useState("");
  const navigate = useNavigate();

  const handleSave = () => {
    // TODO: envoyer vers ton backend Django
    console.log({
      titre,
      date,
      participants: participants.split(",").map(p => p.trim())
    });
    alert("Réunion enregistrée !");
    navigate("/dashboard");
  };

  const handleStart = () => {
    // TODO: enregistrer puis rediriger vers transcription
    console.log("Réunion démarrée !");
    navigate("/transcription");
  };

  return (
    <div className="form-container">
      <h2>Créer une Nouvelle Réunion</h2>
      <form onSubmit={(e) => e.preventDefault()}>
        <label>Titre</label>
        <input value={titre} onChange={(e) => setTitre(e.target.value)} required />

        <label>Date</label>
        <input type="datetime-local" value={date} onChange={(e) => setDate(e.target.value)} required />

        <label>Participants (séparés par des virgules)</label>
        <input value={participants} onChange={(e) => setParticipants(e.target.value)} required />

        <div className="form-buttons">
          <button type="button" onClick={handleSave}>Enregistrer</button>
          <button type="button" onClick={() => navigate("/transcription")} className="start-btn">Démarrer</button>
        </div>
      </form>
    </div>
  );
}
