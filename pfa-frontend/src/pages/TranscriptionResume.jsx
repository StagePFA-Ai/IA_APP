import React, { useState } from "react";


export default function TranscriptionResume() {
  const [transcription, setTranscription] = useState("");
  const [summary, setSummary] = useState("");
  const [isRecording, setIsRecording] = useState(false);

  const handleStart = () => {
    setIsRecording(true);
    // Ici on pourrait appeler une fonction backend pour commencer la transcription
    console.log("Transcription démarrée...");
  };

  const handleStop = () => {
    setIsRecording(false);
    // Ici on pourrait récupérer la transcription finale et le résumé
    console.log("Transcription arrêtée...");
    setTranscription("Ceci est un exemple de transcription en direct...");
    setSummary("Résumé automatique de la réunion...");
  };

  return (
    <div className="transcription-container">
      <header className="transcription-header">
        <h1>📄 Transcription & Résumé</h1>
        <div className="header-buttons">
          {!isRecording ? (
            <button className="start-btn" onClick={handleStart}>▶ Démarrer</button>
          ) : (
            <button className="stop-btn" onClick={handleStop}>⏹ Arrêter</button>
          )}
        </div>
      </header>

      <main className="transcription-main">
        <section className="transcription-section">
          <h2>Transcription en direct</h2>
          <div className="transcription-box">
            {transcription || "La transcription apparaîtra ici..."}
          </div>
        </section>

        <section className="summary-section">
          <h2>Résumé automatique</h2>
          <div className="summary-box">
            {summary || "Le résumé sera généré ici après l'arrêt de la réunion."}
          </div>
        </section>
      </main>

      <footer className="transcription-footer">
        <button className="save-btn">💾 Enregistrer</button>
        <button className="export-btn">📤 Exporter</button>
        <button className="return-btn">⬅ Retour</button>
      </footer>
    </div>
  );
}
