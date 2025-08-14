import React, { useEffect, useState } from "react";
import MeetingCard from "../components/MeetingCard";
import { fetchMeetings, createMeeting, uploadAudio, processMeeting, getMeeting } from "../services/api";

export default function Meetings() {
  const [meetings, setMeetings] = useState([]);
  const [title, setTitle] = useState("");
  const [filesById, setFilesById] = useState({});

  useEffect(()=>{ load() },[]);

  async function load() {
    try {
      const data = await fetchMeetings();
      setMeetings(data || []);
    } catch (err) {
      setMeetings([]);
    }
  }

  async function handleCreate() {
    if (!title) return alert("Donne un titre");
    await createMeeting({ title });
    setTitle("");
    load();
  }

  function handleFileSelect(id, file) {
    setFilesById(prev => ({ ...prev, [id]: file }));
  }

  async function handleUpload(id) {
    const file = filesById[id];
    if (!file) return alert("Choisis un fichier");
    await uploadAudio(id, file);
    await processMeeting(id);
    setTimeout(()=>load(), 1200);
  }

  async function handleView(id) {
    const m = await getMeeting(id);
    alert(`Résumé:\n\n${m.summary || "Aucun résumé"}`);
  }

  return (
    <div className="meetings-container">
      <div className="meeting-form">
        <input 
          value={title} 
          onChange={e=>setTitle(e.target.value)} 
          placeholder="Titre réunion" 
          className="meeting-input" 
        />
        <button onClick={handleCreate} className="create-button">
          Nouvelle réunion
        </button>
      </div>

      <div className="meetings-list">
        {meetings.length === 0 && <div className="no-meetings">Aucune réunion</div>}
        {meetings.map(m => (
          <MeetingCard
            key={m.id}
            meeting={m}
            onUpload={(id, file) => handleFileSelect(id, file)}
            onProcess={(id) => handleUpload(id)}
            onView={handleView}
          />
        ))}
      </div>
    </div>
  );
}
